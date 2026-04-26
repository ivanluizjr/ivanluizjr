// =====================================================
// ALL 4 BRIGADEIRO MOLDS — GRID PREVIEW
// =====================================================
// Row y=0:    Cutters  (open walls)
// Row y=170:  Presses  (solid top + face details)
//
// Col 0: Tartaruga | Col 1: Polvo | Col 2: Baleia | Col 3: Caranguejo
// =====================================================
// Press F6 to render, then File > Export > STL
// Export each animal file individually for STL output.
// =====================================================

use <turtle_mold.scad>
use <octopus_mold.scad>
use <whale_mold.scad>
use <crab_mold.scad>

col   = [0, 130, 270, 420];
row_p = 170;

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
