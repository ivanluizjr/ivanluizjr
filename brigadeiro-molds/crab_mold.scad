// =====================================================
// BRIGADEIRO MOLD — CRAB
// PART 1: cutter  — tall animal-shaped walls, no base
// PART 2: press   — walls + top plate + raised details
// =====================================================

$fn = 80;

wall_t        = 1.8;
cutter_h      = 30;
press_wall_h  = 30;
top_t         = 3.0;
detail_h      = 1.2;
clearance     = 0.3;

// =====================================================
// 2D CRAB SILHOUETTE
// =====================================================
module crab_2d() {
    union() {
        scale([1.1, 0.95]) circle(r=16, $fn=80);
        hull() {
            translate([-16, 8])  circle(r=5, $fn=30);
            translate([-26, 14]) circle(r=4, $fn=30);
        }
        hull() {
            translate([-26, 14]) circle(r=4, $fn=30);
            translate([-33, 20]) circle(r=4.5, $fn=35);
        }
        hull() {
            translate([-26, 14]) circle(r=3.5, $fn=30);
            translate([-32,  7]) circle(r=4,   $fn=30);
        }
        hull() {
            translate([ 16,  8]) circle(r=5, $fn=30);
            translate([ 26, 14]) circle(r=4, $fn=30);
        }
        hull() {
            translate([26, 14]) circle(r=4, $fn=30);
            translate([33, 20]) circle(r=4.5, $fn=35);
        }
        hull() {
            translate([26, 14]) circle(r=3.5, $fn=30);
            translate([32,  7]) circle(r=4,   $fn=30);
        }
        for(i=[0:2]) {
            offset_y = -2 - i*7;
            hull() {
                translate([-16, offset_y])    circle(r=3.5, $fn=20);
                translate([-26, offset_y-5])  circle(r=2.5, $fn=20);
            }
            hull() {
                translate([-26, offset_y-5])  circle(r=2.5, $fn=20);
                translate([-30, offset_y-12]) circle(r=2,   $fn=20);
            }
            hull() {
                translate([ 16, offset_y])    circle(r=3.5, $fn=20);
                translate([ 26, offset_y-5])  circle(r=2.5, $fn=20);
            }
            hull() {
                translate([ 26, offset_y-5])  circle(r=2.5, $fn=20);
                translate([ 30, offset_y-12]) circle(r=2,   $fn=20);
            }
        }
        hull() {
            translate([-7, 15]) circle(r=3, $fn=20);
            translate([-9, 22]) circle(r=4, $fn=25);
        }
        hull() {
            translate([ 7, 15]) circle(r=3, $fn=20);
            translate([ 9, 22]) circle(r=4, $fn=25);
        }
    }
}

module crab_cutter_wall_2d() {
    difference() {
        offset(r=wall_t) crab_2d();
        crab_2d();
    }
}

module crab_press_wall_2d() {
    difference() {
        crab_2d();
        offset(r=-(wall_t + clearance)) crab_2d();
    }
}

// =====================================================
// CRAB FACE & BODY DETAILS
// =====================================================
module crab_details() {
    h = detail_h + 0.5;
    translate([-9, 22, 0]) cylinder(d=5, h=h, $fn=30);
    translate([ 9, 22, 0]) cylinder(d=5, h=h, $fn=30);
    translate([-9, 22, 0]) cylinder(d=2.5, h=h+0.4, $fn=20);
    translate([ 9, 22, 0]) cylinder(d=2.5, h=h+0.4, $fn=20);
    translate([-7.5, 23.2, 0]) cylinder(d=0.9, h=h+0.7, $fn=12);
    translate([ 10.5, 23.2, 0]) cylinder(d=0.9, h=h+0.7, $fn=12);
    for(a=[-50:10:50]) {
        translate([6*sin(a), -4 + 6*(cos(a)-1), 0])
            cylinder(d=1.0, h=h*0.7, $fn=12);
    }
    translate([-11,  2, 0]) cylinder(d=5, h=h*0.4, $fn=30);
    translate([ 11,  2, 0]) cylinder(d=5, h=h*0.4, $fn=30);
    for(a=[-30:15:30]) {
        for(r=[6,11]) {
            translate([r*sin(a), r*cos(a)-5, 0])
                cylinder(d=1.0, h=h*0.4, $fn=10);
        }
    }
    translate([-29, 13, 0]) rotate([0,0,-20])
        linear_extrude(height=h*0.5)
            hull() { circle(r=0.6,$fn=8); translate([5,1]) circle(r=0.4,$fn=8); }
    translate([ 29, 13, 0]) rotate([0,0,20]) mirror([1,0,0])
        linear_extrude(height=h*0.5)
            hull() { circle(r=0.6,$fn=8); translate([5,1]) circle(r=0.4,$fn=8); }
}

// =====================================================
// PART 1: CUTTER
// =====================================================
module cutter() {
    linear_extrude(height=cutter_h)
        crab_cutter_wall_2d();
}

module crab_cutter() { cutter(); }

// =====================================================
// PART 2: PRESS
// =====================================================
module press() {
    union() {
        linear_extrude(height=press_wall_h)
            crab_press_wall_2d();
        translate([0, 0, press_wall_h])
            linear_extrude(height=top_t)
                offset(r=-clearance) crab_2d();
        crab_details();
    }
}

module crab_press() { press(); }

translate([-90, 0, 0]) cutter();
translate([ 90, 0, 0]) press();
