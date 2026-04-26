// =====================================================
// BRIGADEIRO MOLD — TARTARUGA (TURTLE)
// Ref: MaliLab3D style
// PART 1: cutter  — animal-shaped walls, open
// PART 2: press   — walls + solid top + raised details
// =====================================================
$fn = 80;

wall_t       = 1.8;
cutter_h     = 30;
press_wall_h = 30;
top_t        = 3.0;
dh           = 1.4;   // detail raise height
clearance    = 0.3;

// =====================================================
// 2D SILHOUETTE
// =====================================================
module turtle_2d() {
    union() {
        scale([1.05, 1.0]) circle(r=17);           // body
        translate([0,  21]) circle(r=8);            // head
        // front flippers
        translate([-23,  9]) rotate([0,0, 30]) scale([1.4,0.75]) circle(r=9);
        translate([ 23,  9]) rotate([0,0,-30]) scale([1.4,0.75]) circle(r=9);
        // back flippers
        translate([-20,-13]) rotate([0,0,-20]) scale([1.2,0.7]) circle(r=8);
        translate([ 20,-13]) rotate([0,0, 20]) scale([1.2,0.7]) circle(r=8);
        // tail
        translate([0,-26]) circle(r=4);
    }
}

module turtle_cutter_wall_2d() {
    difference() { offset(r=wall_t) turtle_2d(); turtle_2d(); }
}
module turtle_press_wall_2d() {
    difference() { turtle_2d(); offset(r=-(wall_t+clearance)) turtle_2d(); }
}

// =====================================================
// SHELL HEXAGONAL PATTERN
// =====================================================
module shell_hex_pattern() {
    lw = 1.0;
    // center hex
    difference() { circle(r=9,$fn=6); circle(r=9-lw,$fn=6); }
    // 6 surrounding
    for(i=[0:5]) {
        translate([16*cos(i*60+30), 16*sin(i*60+30)])
            difference() { circle(r=7,$fn=6); circle(r=7-lw,$fn=6); }
    }
    // lines connecting center to outer
    for(i=[0:5]) {
        a = i*60+30;
        hull() {
            translate([9*cos(a),   9*sin(a)])   circle(r=lw/2,$fn=8);
            translate([9.3*cos(a),9.3*sin(a)]) circle(r=lw/2,$fn=8);
        }
        hull() {
            translate([9.5*cos(a), 9.5*sin(a)]) circle(r=lw/2,$fn=8);
            translate([9*cos(a),   9*sin(a)])   circle(r=lw/2,$fn=8);
        }
    }
    // partial outer hex ring (shows shell edge)
    for(i=[0:5]) {
        a = i*60+30;
        x1 = 16*cos(a); y1 = 16*sin(a);
        hull() {
            translate([x1, y1]) circle(r=lw/2,$fn=8);
            translate([9*cos(a), 9*sin(a)]) circle(r=lw/2,$fn=8);
        }
    }
}

// =====================================================
// FACE DETAILS
// =====================================================
module turtle_face() {
    // LEFT eye — large round
    translate([-4.5, 22, 0]) {
        cylinder(d=5.5, h=dh*0.7, $fn=40);       // eye white area
        cylinder(d=3.2, h=dh*1.2, $fn=30);       // pupil
        translate([0.8,0.8,0]) cylinder(d=1.0, h=dh*1.5, $fn=15); // shine
    }
    // RIGHT eye
    translate([ 4.5, 22, 0]) {
        cylinder(d=5.5, h=dh*0.7, $fn=40);
        cylinder(d=3.2, h=dh*1.2, $fn=30);
        translate([0.8,0.8,0]) cylinder(d=1.0, h=dh*1.5, $fn=15);
    }
    // nose dots
    translate([-1.5, 19.5, 0]) cylinder(d=1.5, h=dh*0.8, $fn=20);
    translate([ 1.5, 19.5, 0]) cylinder(d=1.5, h=dh*0.8, $fn=20);
    // smile — arc of bumps
    for(a=[-50:10:50]) {
        translate([6*sin(a), 17.2 + 5.5*(cos(a)-1), 0])
            cylinder(d=1.2, h=dh*0.8, $fn=12);
    }
    // cheek blush
    translate([-7.5, 19, 0]) cylinder(d=4.5, h=dh*0.35, $fn=30);
    translate([ 7.5, 19, 0]) cylinder(d=4.5, h=dh*0.35, $fn=30);
}

// =====================================================
// FLIPPER LINES (raised veins)
// =====================================================
module flipper_details() {
    // front-left flipper line
    translate([-23, 9, 0]) rotate([0,0,120])
        hull() {
            circle(r=0.6,$fn=8);
            translate([7,0]) circle(r=0.4,$fn=8);
        }
    // front-right
    translate([ 23, 9, 0]) rotate([0,0,60]) mirror([1,0,0])
        hull() {
            circle(r=0.6,$fn=8);
            translate([7,0]) circle(r=0.4,$fn=8);
        }
    // back-left
    translate([-20,-13, 0]) rotate([0,0,150])
        hull() {
            circle(r=0.6,$fn=8);
            translate([6,0]) circle(r=0.4,$fn=8);
        }
    // back-right
    translate([ 20,-13, 0]) rotate([0,0,30]) mirror([1,0,0])
        hull() {
            circle(r=0.6,$fn=8);
            translate([6,0]) circle(r=0.4,$fn=8);
        }
}

// =====================================================
// PART 1: CUTTER
// =====================================================
module cutter() {
    linear_extrude(height=cutter_h)
        turtle_cutter_wall_2d();
}
module turtle_cutter() { cutter(); }

// =====================================================
// PART 2: PRESS
// =====================================================
module press() {
    union() {
        // walls
        linear_extrude(height=press_wall_h)
            turtle_press_wall_2d();
        // solid top plate
        translate([0,0,press_wall_h])
            linear_extrude(height=top_t)
                offset(r=-clearance) turtle_2d();
        // shell hex pattern
        linear_extrude(height=dh)
            shell_hex_pattern();
        // face
        turtle_face();
        // flipper lines
        linear_extrude(height=dh*0.6)
            flipper_details();
    }
}
module turtle_press() { press(); }

// =====================================================
// DISPLAY
// =====================================================
translate([-70, 0, 0]) cutter();
translate([ 70, 0, 0]) press();
