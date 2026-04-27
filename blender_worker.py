"""
blender_worker.py — Brigadeiro Mold STL Generator (Blender-side script)
========================================================================
This script runs INSIDE Blender (headless) and is called by generate_molds.py:

    blender --background --python blender_worker.py -- [args]

For each image it generates two STL files:
    NAME_luva.stl   — hollow tube in the shape of the silhouette (sleeve / cutter)
    NAME_embolo.stl — solid piece that fits inside the luva with a tapered handle

Geometry:
    Luva  = outer solid (silhouette offset +wall_mm)
            minus inner solid (silhouette, same height + epsilon)
            → thin-walled open tube

    Embolo = solid (silhouette offset -clearance_mm) extruded to height
             + tapered cylinder handle on top

Blender version: 3.6 LTS or 4.x
"""

import bpy
import sys
import os
import argparse
from mathutils import Vector


# Extra height (in metres) added to the inner solid before the Boolean
# subtraction so that it protrudes beyond the outer solid on both ends,
# preventing co-planar face artefacts in the Boolean solver.
_BOOL_EPSILON_M = 0.002


# ---------------------------------------------------------------------------
# Argument parsing  (args come after the '--' separator in the Blender call)
# ---------------------------------------------------------------------------

def _parse_args():
    argv = sys.argv
    try:
        argv = argv[argv.index("--") + 1:]
    except ValueError:
        argv = []

    p = argparse.ArgumentParser(description="Blender worker: SVG → STL mold pair")
    p.add_argument("--svg",              required=True)
    p.add_argument("--output-dir",       required=True)
    p.add_argument("--name",             required=True)
    p.add_argument("--size-mm",          type=float, default=30.0)
    p.add_argument("--height-mm",        type=float, default=30.0)
    p.add_argument("--wall-mm",          type=float, default=1.8)
    p.add_argument("--clearance-mm",     type=float, default=0.3)
    p.add_argument("--handle-height-mm", type=float, default=12.0)
    return p.parse_args(argv)


def _log(msg):
    print(f"[blender_worker] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Scene helpers
# ---------------------------------------------------------------------------

def _clear_scene():
    """Delete every object and orphan data block."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for col in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for item in list(col):
            col.remove(item)


def _import_svg(svg_path):
    """Import SVG and return the list of newly created CURVE objects."""
    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_curve.svg(filepath=svg_path)
    return [
        o for o in bpy.data.objects
        if o.name not in before and o.type == 'CURVE'
    ]


# ---------------------------------------------------------------------------
# Bounding-box utilities
# ---------------------------------------------------------------------------

def _bbox(objects):
    """
    Return (center: Vector, max_dim: float) of the world-space bounding
    box that encloses all given objects.
    """
    mn = Vector((float('inf'),) * 3)
    mx = Vector((float('-inf'),) * 3)
    for obj in objects:
        for corner in obj.bound_box:
            wc = obj.matrix_world @ Vector(corner)
            for i in range(3):
                mn[i] = min(mn[i], wc[i])
                mx[i] = max(mx[i], wc[i])
    center = (mn + mx) / 2.0
    max_dim = max(mx[i] - mn[i] for i in range(3))
    return center, max_dim


def _center_and_scale(objects, target_mm):
    """
    Translate + scale all objects so the longest bounding-box axis equals
    target_mm millimetres.  Blender stores geometry in metres, so we convert.
    """
    center, current_m = _bbox(objects)
    if current_m < 1e-12:
        _log("WARNING: bounding box near zero — cannot scale")
        return

    scale = (target_mm * 0.001) / current_m          # target in metres

    for obj in objects:
        obj.location -= center
        obj.scale = (
            obj.scale[0] * scale,
            obj.scale[1] * scale,
            obj.scale[2] * scale,
        )

    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, scale=True, rotation=False)


def _main_curve(curves):
    """
    Return (main_curve, [detail_curves]) where main_curve is the object with
    the largest world-space bounding-box (the animal silhouette).
    """
    def _area(obj):
        _, dim = _bbox([obj])
        return dim * dim   # proportional to area

    ranked = sorted(curves, key=_area, reverse=True)
    return ranked[0], ranked[1:]


# ---------------------------------------------------------------------------
# Curve → solid-mesh conversion
# ---------------------------------------------------------------------------

def _dup(src):
    """Duplicate src and return the new object."""
    bpy.ops.object.select_all(action='DESELECT')
    src.select_set(True)
    bpy.context.view_layer.objects.active = src
    bpy.ops.object.duplicate(linked=False)
    return bpy.context.active_object


def _make_solid(curve_obj, height_m, offset_m, name):
    """
    Produce a closed 3D mesh from a 2D curve by:
      • setting curve offset (expand / contract the outline)
      • setting curve extrude (height in Z)
      • fill_mode = BOTH  (caps top + bottom → solid)
      • converting to mesh and cleaning up
    Returns the mesh object.
    """
    dup = _dup(curve_obj)
    dup.name = name

    d = dup.data
    d.dimensions = '2D'
    d.fill_mode  = 'BOTH'
    d.offset     = offset_m
    d.extrude    = height_m

    bpy.ops.object.select_all(action='DESELECT')
    dup.select_set(True)
    bpy.context.view_layer.objects.active = dup
    bpy.ops.object.convert(target='MESH')

    # Basic mesh cleanup
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=1e-5)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    return dup


# ---------------------------------------------------------------------------
# Boolean subtraction
# ---------------------------------------------------------------------------

def _bool_diff(target, cutter):
    """Subtract cutter from target (DIFFERENCE Boolean modifier, applied)."""
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target

    cutter.hide_viewport = False
    cutter.hide_render   = False

    mod = target.modifiers.new('BoolDiff', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object    = cutter
    try:
        mod.solver = 'EXACT'          # Blender 3.0+
    except AttributeError:
        pass

    bpy.ops.object.modifier_apply(modifier='BoolDiff')


# ---------------------------------------------------------------------------
# STL export
# ---------------------------------------------------------------------------

def _export_stl(obj, filepath):
    """
    Export a single object as STL in millimetres.
    Blender stores geometry in metres → global_scale = 1000 converts to mm.
    Handles both Blender 3.x (export_mesh.stl) and 4.x (wm.stl_export).
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        # Blender 4.x
        bpy.ops.wm.stl_export(
            filepath=filepath,
            export_selected_objects=True,
            global_scale=1000.0,
        )
    except (AttributeError, TypeError):
        try:
            # Blender 3.x
            bpy.ops.export_mesh.stl(
                filepath=filepath,
                use_selection=True,
                global_scale=1000.0,
            )
        except TypeError:
            bpy.ops.export_mesh.stl(
                filepath=filepath,
                use_selection=True,
            )


# ---------------------------------------------------------------------------
# Geometry builders
# ---------------------------------------------------------------------------

def _build_luva(curve, wall_m, height_m, out_path):
    """
    Luva = outer solid (silhouette + wall_m) MINUS inner solid (silhouette).
    Result: thin-walled open tube, open on top and bottom.
    """
    _log(f"  outer solid  offset=+{wall_m*1e3:.2f} mm  height={height_m*1e3:.1f} mm")
    # Outer solid is slightly shorter than the inner so that after the Boolean
    # subtraction the resulting tube is open on both ends (no co-planar caps).
    outer = _make_solid(curve, height_m + _BOOL_EPSILON_M / 2, wall_m, "luva_outer")

    _log(
        f"  inner solid  offset=0  height={height_m*1e3:.1f} mm "
        f"(+{_BOOL_EPSILON_M*1e3:.1f} mm epsilon for clean Boolean)"
    )
    # Inner solid is taller on both ends so the Boolean punch goes all the way
    # through, preventing co-planar face artefacts in the Boolean solver.
    inner = _make_solid(curve, height_m + _BOOL_EPSILON_M, 0.0, "luva_inner")

    _log("  boolean  outer - inner")
    _bool_diff(outer, inner)
    bpy.data.objects.remove(inner, do_unlink=True)

    _log(f"  export → {out_path}")
    _export_stl(outer, out_path)
    bpy.data.objects.remove(outer, do_unlink=True)


def _build_embolo(curve, clearance_m, height_m, handle_h_m, out_path):
    """
    Embolo = solid body (silhouette − clearance_m) extruded to height_m
             + tapered cylinder handle on top.
    """
    _log(f"  body solid  offset=-{clearance_m*1e3:.2f} mm  height={height_m*1e3:.1f} mm")
    body = _make_solid(curve, height_m, -clearance_m, "embolo_body")

    # Center of the body (should be near origin after centering)
    center, _ = _bbox([body])
    cx, cy = center.x, center.y

    # Tapered handle: base radius 8 mm, top 60 % of that
    r_base = 0.008          # 8 mm in metres
    r_top  = r_base * 0.60

    _log(f"  handle  r={r_base*1e3:.0f}mm → {r_top*1e3:.0f}mm  h={handle_h_m*1e3:.0f}mm")
    bpy.ops.mesh.primitive_cone_add(
        vertices=32,
        radius1=r_base,
        radius2=r_top,
        depth=handle_h_m,
        location=(cx, cy, height_m + handle_h_m / 2.0),
    )
    handle = bpy.context.active_object
    handle.name = "embolo_handle"

    # Join body + handle into one object
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    handle.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    embolo = bpy.context.active_object
    embolo.name = "embolo"

    _log(f"  export → {out_path}")
    _export_stl(embolo, out_path)
    bpy.data.objects.remove(embolo, do_unlink=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = _parse_args()

    _log(f"SVG          : {args.svg}")
    _log(f"Output dir   : {args.output_dir}")
    _log(f"Name         : {args.name}")
    _log(
        f"Parameters   : size={args.size_mm} mm  height={args.height_mm} mm  "
        f"wall={args.wall_mm} mm  clearance={args.clearance_mm} mm  "
        f"handle={args.handle_height_mm} mm"
    )

    os.makedirs(args.output_dir, exist_ok=True)

    # Convert scalar parameters to metres (Blender's native unit)
    height_m    = args.height_mm        * 0.001
    wall_m      = args.wall_mm          * 0.001
    clearance_m = args.clearance_mm     * 0.001
    handle_h_m  = args.handle_height_mm * 0.001

    luva_path   = os.path.join(args.output_dir, f"{args.name}_luva.stl")
    embolo_path = os.path.join(args.output_dir, f"{args.name}_embolo.stl")

    # ── LUVA ──────────────────────────────────────────────────────────────────
    _log("=== LUVA ===")
    _clear_scene()
    curves = _import_svg(args.svg)
    if not curves:
        _log("ERROR: no CURVE objects found after SVG import")
        sys.exit(1)
    _log(f"Imported {len(curves)} curve object(s)")

    _center_and_scale(curves, args.size_mm)
    main_c, details = _main_curve(curves)
    _log(f"Main silhouette: '{main_c.name}'  |  {len(details)} detail curve(s) ignored")
    for c in details:
        bpy.data.objects.remove(c, do_unlink=True)

    _build_luva(main_c, wall_m, height_m, luva_path)

    # ── EMBOLO ────────────────────────────────────────────────────────────────
    _log("=== EMBOLO ===")
    _clear_scene()
    curves = _import_svg(args.svg)
    _center_and_scale(curves, args.size_mm)
    main_c, details = _main_curve(curves)
    for c in details:
        bpy.data.objects.remove(c, do_unlink=True)

    _build_embolo(main_c, clearance_m, height_m, handle_h_m, embolo_path)

    # ── Summary ───────────────────────────────────────────────────────────────
    _log("=== Done ===")
    _log(f"  {luva_path}")
    _log(f"  {embolo_path}")


main()
