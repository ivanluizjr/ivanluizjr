#!/usr/bin/env python3
"""
Brigadeiro Ejector Mold Generator
====================================
Reads PNG/JPG images from an input folder, vectorizes each one to SVG,
then calls Blender (headless) to produce a pair of STL files per image:

    NOME_luva.stl   — outer sleeve / cutter  (animal-shaped hollow tube)
    NOME_embolo.stl — inner plunger / press  (solid piece + tapered handle)

Usage:
    python generate_molds.py [options]

Run  python generate_molds.py --help  for all options.

Dependencies:
    pip install vtracer
    Blender 3.6+ or 4.x installed (added to PATH or passed via --blender)
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path


# ---------------------------------------------------------------------------
# Common Windows install locations for Blender (newest first)
# ---------------------------------------------------------------------------
_BLENDER_WIN_PATHS = [
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
    r"C:\Program Files (x86)\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files (x86)\Blender Foundation\Blender 4.1\blender.exe",
    r"C:\Program Files (x86)\Blender Foundation\Blender 4.0\blender.exe",
    r"C:\Program Files (x86)\Blender Foundation\Blender 3.6\blender.exe",
]


def find_blender(explicit_path: str | None = None) -> str | None:
    """Return path to blender.exe, or None if not found."""
    if explicit_path and os.path.isfile(explicit_path):
        return explicit_path
    found = shutil.which("blender")
    if found:
        return found
    for p in _BLENDER_WIN_PATHS:
        if os.path.isfile(p):
            return p
    return None


# ---------------------------------------------------------------------------
# PNG / JPG  →  SVG  (vectorization via vtracer)
# ---------------------------------------------------------------------------

def convert_image_to_svg(image_path: Path, svg_path: Path, verbose: bool = False) -> None:
    """Vectorize an image file to SVG using vtracer (binary / silhouette mode)."""
    try:
        import vtracer
    except ImportError:
        print(
            "\nERRO: vtracer não está instalado.\n"
            "  Execute:  pip install vtracer\n"
        )
        sys.exit(1)

    if verbose:
        print(f"    Vetorizando {image_path.name} → {svg_path.name} ...")

    vtracer.convert_image_to_svg_py(
        str(image_path),
        str(svg_path),
        colormode="binary",       # preto e branco (silhueta)
        hierarchical="stacked",
        mode="spline",            # curvas bezier suaves
        filter_speckle=4,
        color_precision=6,
        layer_difference=16,
        corner_threshold=60,
        length_threshold=4.0,
        max_iterations=10,
        splice_threshold=45,
        path_precision=3,
    )


# ---------------------------------------------------------------------------
# SVG  →  STL pair  (via Blender headless)
# ---------------------------------------------------------------------------

def generate_stl_pair(
    blender_exe: str,
    svg_path: Path,
    output_dir: Path,
    name: str,
    size_mm: float,
    height_mm: float,
    wall_mm: float,
    clearance_mm: float,
    handle_height_mm: float,
    verbose: bool = False,
) -> bool:
    """
    Call Blender in background mode running blender_worker.py.
    Returns True on success.
    """
    worker = Path(__file__).parent / "blender_worker.py"
    if not worker.exists():
        print(f"ERRO: blender_worker.py não encontrado em {worker}")
        return False

    cmd = [
        blender_exe,
        "--background",
        "--python", str(worker),
        "--",
        "--svg", str(svg_path),
        "--output-dir", str(output_dir),
        "--name", name,
        "--size-mm", str(size_mm),
        "--height-mm", str(height_mm),
        "--wall-mm", str(wall_mm),
        "--clearance-mm", str(clearance_mm),
        "--handle-height-mm", str(handle_height_mm),
    ]

    if verbose:
        print(f"    Comando: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if verbose or result.returncode != 0:
        for line in result.stdout.splitlines():
            if "[blender_worker]" in line or result.returncode != 0:
                print(f"    {line}")
        if result.returncode != 0 and result.stderr:
            print(f"    STDERR (últimas 40 linhas):")
            for line in result.stderr.splitlines()[-40:]:
                print(f"      {line}")

    return result.returncode == 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="generate_molds.py",
        description=(
            "Gera pares de STL para ejetores de brigadeiro a partir de imagens PNG/JPG.\n"
            "Cada imagem gera:  NOME_luva.stl  e  NOME_embolo.stl"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python generate_molds.py
  python generate_molds.py --input minhas_imagens --output moldes_stl
  python generate_molds.py --size-mm 35 --height-mm 30 --verbose
  python generate_molds.py --blender "C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe"
""",
    )

    parser.add_argument(
        "--input", "-i",
        default="input_images",
        metavar="PASTA",
        help="Pasta com imagens PNG/JPG (padrão: input_images)",
    )
    parser.add_argument(
        "--output", "-o",
        default="output_stl",
        metavar="PASTA",
        help="Pasta de saída para STL (padrão: output_stl)",
    )
    parser.add_argument(
        "--size-mm",
        type=float, default=30.0, metavar="MM",
        help="Largura máxima final em mm (padrão: 30)",
    )
    parser.add_argument(
        "--height-mm",
        type=float, default=30.0, metavar="MM",
        help="Altura do ejetor em mm — luva e êmbolo terão a MESMA altura (padrão: 30)",
    )
    parser.add_argument(
        "--wall-mm",
        type=float, default=1.8, metavar="MM",
        help="Espessura da parede da luva em mm (padrão: 1.8)",
    )
    parser.add_argument(
        "--clearance-mm",
        type=float, default=0.3, metavar="MM",
        help="Folga entre êmbolo e luva em mm (padrão: 0.3)",
    )
    parser.add_argument(
        "--handle-height-mm",
        type=float, default=12.0, metavar="MM",
        help="Altura do pegador do êmbolo em mm (padrão: 12)",
    )
    parser.add_argument(
        "--blender",
        default=None, metavar="CAMINHO",
        help="Caminho completo para blender.exe (auto-detectado se não informado)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Exibir saída detalhada do Blender",
    )

    args = parser.parse_args()

    # ── Find Blender ──────────────────────────────────────────────────────────
    blender_exe = find_blender(args.blender)
    if not blender_exe:
        print(
            "\nERRO: Blender não encontrado!\n\n"
            "Soluções:\n"
            "  1. Instale o Blender: https://www.blender.org/download/\n"
            "  2. Adicione o Blender ao PATH do Windows, OU\n"
            '  3. Passe o caminho diretamente:\n'
            '     python generate_molds.py --blender "C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe"\n'
        )
        sys.exit(1)
    print(f"Blender: {blender_exe}")

    # ── Locate images ─────────────────────────────────────────────────────────
    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"\nAVISO: Pasta '{input_dir}' não existe — criando...")
        input_dir.mkdir(parents=True)
        print(
            f"Coloque suas imagens PNG/JPG em  '{input_dir.resolve()}'\n"
            "e execute o script novamente.\n"
        )
        sys.exit(0)

    image_exts = {".png", ".jpg", ".jpeg"}
    images = sorted(
        p for p in input_dir.iterdir()
        if p.suffix.lower() in image_exts
    )
    if not images:
        print(f"Nenhuma imagem PNG/JPG encontrada em '{input_dir.resolve()}'.")
        sys.exit(1)

    # ── Prepare output dirs ───────────────────────────────────────────────────
    output_dir = Path(args.output)
    svg_dir = output_dir / "_svg_temp"
    output_dir.mkdir(parents=True, exist_ok=True)
    svg_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"\nProcessando {len(images)} imagem(ns) em '{input_dir}'...\n"
        f"  Tamanho: {args.size_mm} mm | Altura: {args.height_mm} mm\n"
        f"  Parede:  {args.wall_mm} mm | Folga: {args.clearance_mm} mm | "
        f"Pegador: {args.handle_height_mm} mm\n"
    )

    ok_count = 0
    for image_path in images:
        name = image_path.stem
        print(f"  [{name}]")

        # Step 1: vectorize image → SVG
        svg_path = svg_dir / f"{name}.svg"
        try:
            convert_image_to_svg(image_path, svg_path, verbose=args.verbose)
        except Exception as exc:
            print(f"    ERRO na vetorização: {exc}")
            continue

        if not svg_path.exists():
            print("    ERRO: SVG não foi criado por vtracer.")
            continue

        # Step 2: Blender generates STL pair
        ok = generate_stl_pair(
            blender_exe=blender_exe,
            svg_path=svg_path,
            output_dir=output_dir,
            name=name,
            size_mm=args.size_mm,
            height_mm=args.height_mm,
            wall_mm=args.wall_mm,
            clearance_mm=args.clearance_mm,
            handle_height_mm=args.handle_height_mm,
            verbose=args.verbose,
        )

        luva_stl = output_dir / f"{name}_luva.stl"
        embolo_stl = output_dir / f"{name}_embolo.stl"

        if ok and luva_stl.exists() and embolo_stl.exists():
            print(f"    ✓  {luva_stl.name}")
            print(f"    ✓  {embolo_stl.name}")
            ok_count += 1
        else:
            print(
                f"    ✗  Falha ao gerar STL para '{name}'.\n"
                "       Execute com --verbose para ver detalhes do erro."
            )

    print(
        f"\n{'=' * 50}\n"
        f"Concluído: {ok_count} / {len(images)} imagem(ns) processadas.\n"
        f"Arquivos STL em: {output_dir.resolve()}\n"
    )


if __name__ == "__main__":
    main()
