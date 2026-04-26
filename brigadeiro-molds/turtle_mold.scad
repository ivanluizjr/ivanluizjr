// =====================================================
// BRIGADEIRO MOLD — TURTLE
// Ref: MaliLab3D style — animal-shaped walls
//
// PART 1: cutter  — tall walls shaped like turtle, no base
// PART 2: press   — same walls (shorter) + solid top plate
//                   + raised shell & face details on bottom
// =====================================================

$fn = 80;

// --- Parameters ---
wall_t        = 1.8;   // wall thickness (mm)
cutter_h      = 20;    // cutter wall height
press_wall_h  = 9;     // press inner wall height
top_t         = 2.5;   // press top plate thickness
detail_h      = 1.2;   // raised detail height on press face

// =====================================================
// 2D TURTLE SILHOUETTE
// Body + head + 4 flippers + tail
// =====================================================
module turtle_2d() {
    union() {
        circle(r=18, $fn=80);                          // body
        translate([ 0,  22]) circle(r=7,  $fn=50);    // head
        translate([-21, 10]) circle(r=8,  $fn=50);    // front-left flipper
        translate([ 21, 10]) circle(r=8,  $fn=50);    // front-right flipper
        translate([-19,-13]) circle(r=7,  $fn=50);    // back-left flipper
        translate([ 19,-13]) circle(r=7,  $fn=50);    // back-right flipper
        translate([ 0, -23]) circle(r=4,  $fn=40);    // tail
    }
}

// 2D wall ring = offset shell minus inner silhouette
module turtle_wall_2d() {
    difference() {
        offset(r=wall_t) turtle_2d();
        turtle_2d();
    }
}

// =====================================================
// SHELL PATTERN — raised line art on press face
// =====================================================
module shell_lines_2d() {
    lw = 0.85; // line width
    union() {
        // Central hexagon ring
        difference() { circle(r=10, $fn=6); circle(r=10-lw, $fn=6); }
        // 6 surrounding hexagons
        for(i=[0:5]) {
            translate([15*cos(i*60+30), 15*sin(i*60+30)])
                difference() { circle(r=6.5,$fn=6); circle(r=6.5-lw,$fn=6); }
        }
        // Radial divider lines between hexagons
        for(i=[0:5]) {
            a = i*60+30;
            hull() {
                translate([10*cos(a), 10*sin(a)])   circle(r=lw/2, $fn=8);
                translate([8.5*cos(a), 8.5*sin(a)]) circle(r=lw/2, $fn=8);
            }
        }
    }
}

// =====================================================
// FACE DETAILS — raised nubs & smile on press face
// =====================================================
module face_details() {
    h = detail_h + 0.5;
    // Eyes (round nubs)
    translate([-4.5, 23, 0]) cylinder(d=3.2, h=h, $fn=25);
    translate([ 4.5, 23, 0]) cylinder(d=3.2, h=h, $fn=25);
    // Eye shine dots
    translate([-3.3, 24.2, 0]) cylinder(d=0.9, h=h+0.3, $fn=15);
    translate([ 5.7, 24.2, 0]) cylinder(d=0.9, h=h+0.3, $fn=15);
    // Nose nubs
    translate([-1.8, 20.5, 0]) cylinder(d=1.6, h=h-0.3, $fn=18);
    translate([ 1.8, 20.5, 0]) cylinder(d=1.6, h=h-0.3, $fn=18);
    // Smile — row of tiny cylinders along arc
    for(a=[-45:9:45]) {
        translate([5.5*sin(a), 18.5 + 5.5*(cos(a)-1), 0])
            cylinder(d=1.0, h=h*0.7, $fn=12);
    }
}

// =====================================================
// PART 1: CUTTER
// Tall animal-shaped walls, open top and bottom
// =====================================================
module cutter() {
    linear_extrude(height=cutter_h)
        turtle_wall_2d();
}

// =====================================================
// PART 2: PRESS
// Shorter walls + solid top plate + raised details below
// =====================================================
module press() {
    union() {
        // Walls
        linear_extrude(height=press_wall_h)
            turtle_wall_2d();
        // Solid top plate (acts as handle surface)
        translate([0, 0, press_wall_h])
            linear_extrude(height=top_t)
                offset(r=wall_t) turtle_2d();
        // Raised shell pattern on bottom face (z=0 upward)
        linear_extrude(height=detail_h)
            shell_lines_2d();
        // Face details
        face_details();
    }
}

// =====================================================
// DISPLAY — cutter left, press right
// =====================================================
translate([-65, 0, 0]) cutter();
translate([ 65, 0, 0]) press();
