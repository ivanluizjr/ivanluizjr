// =====================================================
// ALL 4 BRIGADEIRO MOLDS — GRID PREVIEW
// =====================================================
// Layout:
//   Row y=0:    Cutters
//   Row y=160:  Presses
//
//   Col 0: Turtle | Col 1: Octopus | Col 2: Whale | Col 3: Crab
// =====================================================

use <turtle_mold.scad>
use <octopus_mold.scad>
use <whale_mold.scad>
use <crab_mold.scad>

col   = [0, 120, 250, 390];
row_p = 160;

// Row 1 — Cutters
translate([col[0], 0,     0]) turtle_cutter();
translate([col[1], 0,     0]) octopus_cutter();
translate([col[2], 0,     0]) whale_cutter();
translate([col[3], 0,     0]) crab_cutter();

// Row 2 — Presses
translate([col[0], row_p, 0]) turtle_press();
translate([col[1], row_p, 0]) octopus_press();
translate([col[2], row_p, 0]) whale_press();
translate([col[3], row_p, 0]) crab_press();
