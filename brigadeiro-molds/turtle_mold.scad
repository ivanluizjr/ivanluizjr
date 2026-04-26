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
cutter_h      = 30;    // cutter wall height
press_wall_h  = 30;    // press inner wall height
top_t         = 3.0;   // press top plate thickness
detail_h      = 1.2;   // raised detail height on press face
clearance     = 0.3;   // fit gap: press outer = animal_2d offset(-clearance)

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

// Cutter wall ring
module turtle_cutter_wall_2d() {
    difference() {
        offset(r=wall_t) turtle_2d();
        turtle_2d();
    }
}

// Press wall ring (offset inward by clearance so it fits inside cutter)
module turtle_press_wall_2d() {
    difference() {
        turtle_2d();
        offset(r=-(wall_t + clearance)) turtle_2d();
    }
}

// =====================================================
// SHELL PATTERN — raised line art on press face
// =====================================================
module shell_lines_2d() {
    lw = 0.85;
    union() {
        difference() { circle(r=10, $fn=6); circle(r=10-lw, $fn=6); }
        for(i=[0:5]) {
            translate([15*cos(i*60+30), 15*sin(i*60+30)])
                difference() { circle(r=6.5,$fn=6); circle(r=6.5-lw,$fn=6); }
        }
        for(i=[0:5]) {
            a = i*60+30;
            hull() {
                translate([10*cos(a), 10*sin(a)])    circle(r=lw/2, $fn=8);
                translate([8.5*cos(a), 8.5*sin(a)]) circle(r=lw/2, $fn=8);
            }
        }
    }
}

// =====================================================
// FACE DETAILS
// =====================================================
module face_details() {
    h = detail_h + 0.5;
    translate([-4.5, 23, 0]) cylinder(d=3.2, h=h, $fn=25);
    translate([ 4.5, 23, 0]) cylinder(d=3.2, h=h, $fn=25);
    translate([-3.3, 24.2, 0]) cylinder(d=0.9, h=h+0.3, $fn=15);
    translate([ 5.7, 24.2, 0]) cylinder(d=0.9, h=h+0.3, $fn=15);
    translate([-1.8, 20.5, 0]) cylinder(d=1.6, h=h-0.3, $fn=18);
    translate([ 1.8, 20.5, 0]) cylinder(d=1.6, h=h-0.3, $fn=18);
    for(a=[-45:9:45]) {
        translate([5.5*sin(a), 18.5 + 5.5*(cos(a)-1), 0])
            cylinder(d=1.0, h=h*0.7, $fn=12);
    }
}

// =====================================================
// PART 1: CUTTER  (30mm tall, open top & bottom)
// =====================================================
module cutter() {
    linear_extrude(height=cutter_h)
        turtle_cutter_wall_2d();
}

// Named alias for preview grid
module turtle_cutter() { cutter(); }

// =====================================================
// PART 2: PRESS  (30mm tall walls + solid top + details)
// =====================================================
module press() {
    union() {
        linear_extrude(height=press_wall_h)
            turtle_press_wall_2d();
        translate([0, 0, press_wall_h])
            linear_extrude(height=top_t)
                offset(r=-clearance) turtle_2d();
        linear_extrude(height=detail_h)
            shell_lines_2d();
        face_details();
    }
}

// Named alias for preview grid
module turtle_press() { press(); }

// =====================================================
// DISPLAY — cutter left, press right
// =====================================================
translate([-65, 0, 0]) cutter();
translate([ 65, 0, 0]) press();
