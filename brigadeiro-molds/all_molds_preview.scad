// =====================================================
// ALL 4 BRIGADEIRO MOLDS — GRID PREVIEW
// =====================================================
// Layout:
//   Row 1 (y=0):    Cutters
//   Row 2 (y=130):  Presses
//
//   Col 0: Turtle  | Col 1: Octopus
//   Col 2: Whale   | Col 3: Crab
// =====================================================
// Open each individual .scad to export STL per piece.
// Press F6 to render, File > Export > STL
// =====================================================

use <turtle_mold.scad>
use <octopus_mold.scad>
use <whale_mold.scad>
use <crab_mold.scad>

col = [0, 120, 250, 380];
row_press = 140;

// Row 1 — Cutters
translate([col[0], 0, 0]) cutter_turtle();
translate([col[1], 0, 0]) cutter_octopus();
translate([col[2], 0, 0]) cutter_whale();
translate([col[3], 0, 0]) cutter_crab();

// Row 2 — Presses
translate([col[0], row_press, 0]) press_turtle();
translate([col[1], row_press, 0]) press_octopus();
translate([col[2], row_press, 0]) press_whale();
translate([col[3], row_press, 0]) press_crab();
