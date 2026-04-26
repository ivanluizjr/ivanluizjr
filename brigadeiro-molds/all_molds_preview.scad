// =====================================================
// ALL 4 BRIGADEIRO MOLDS — GRID PREVIEW
// Octopus | Whale | Crab | Turtle
// =====================================================
// Run this file in OpenSCAD to preview all molds
// Press F6 to render, then File > Export > STL
// =====================================================

use <octopus_mold.scad>
use <whale_mold.scad>
use <crab_mold.scad>
use <turtle_mold.scad>

spacing_x = 65;
spacing_y = 100;

// Row labels (use echo for terminal output)
echo("TOP ROW:    Base Molds");
echo("MID ROW:    Detail Plates");
echo("BOT ROW:    Top Press/Ejectors");

// ---- OCTOPUS (column 0) ----
translate([0 * spacing_x,  0,         0]) base_mold_oct();
translate([0 * spacing_x,  spacing_y, 0]) detail_plate_oct();
translate([0 * spacing_x,  spacing_y*2, 0]) top_press_oct();

// ---- WHALE (column 1) ----
translate([1 * spacing_x,  0,         0]) base_mold_whl();
translate([1 * spacing_x,  spacing_y, 0]) detail_plate_whl();
translate([1 * spacing_x,  spacing_y*2, 0]) top_press_whl();

// ---- CRAB (column 2) ----
translate([2 * spacing_x,  0,         0]) base_mold_crb();
translate([2 * spacing_x,  spacing_y, 0]) detail_plate_crb();
translate([2 * spacing_x,  spacing_y*2, 0]) top_press_crb();

// ---- TURTLE (column 3) ----
translate([3 * spacing_x,  0,         0]) base_mold_trt();
translate([3 * spacing_x,  spacing_y, 0]) detail_plate_trt();
translate([3 * spacing_x,  spacing_y*2, 0]) top_press_trt();
