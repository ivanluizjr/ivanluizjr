// =====================================================
// BRIGADEIRO MOLD — WHALE
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
// 2D WHALE SILHOUETTE
// =====================================================
module whale_2d() {
    union() {
        scale([1.25, 1.0]) circle(r=17, $fn=80);
        translate([24, 5])  circle(r=7, $fn=50);
        translate([24,-5])  circle(r=7, $fn=50);
        hull() {
            translate([14, 0]) circle(r=5, $fn=30);
            translate([22, 0]) circle(r=3, $fn=30);
        }
        hull() {
            translate([-2, 17]) circle(r=3, $fn=30);
            translate([ 5, 24]) circle(r=2, $fn=25);
            translate([ 9, 17]) circle(r=3, $fn=30);
        }
        translate([-14, -8]) rotate([0,0,-20])
            scale([1.6, 0.9]) circle(r=6, $fn=40);
    }
}

module whale_cutter_wall_2d() {
    difference() {
        offset(r=wall_t) whale_2d();
        whale_2d();
    }
}

module whale_press_wall_2d() {
    difference() {
        whale_2d();
        offset(r=-(wall_t + clearance)) whale_2d();
    }
}

// =====================================================
// WHALE FACE & BODY DETAILS
// =====================================================
module whale_details() {
    h = detail_h + 0.5;
    translate([-8, 5, 0]) cylinder(d=4, h=h*0.6, $fn=30);
    translate([-8, 5, 0]) cylinder(d=2, h=h, $fn=25);
    translate([-6.8, 6.2, 0]) cylinder(d=0.9, h=h+0.3, $fn=15);
    for(a=[-40:8:40]) {
        translate([-3 + 6*sin(a), -1 + 6*(cos(a)-1), 0])
            cylinder(d=1.0, h=h*0.7, $fn=12);
    }
    translate([0, 16, 0]) cylinder(d=3, h=h*0.8, $fn=25);
    for(d=[-1,0,1]) {
        translate([d*3, 21+abs(d)*1.5, 0]) cylinder(d=1.8, h=h*0.6, $fn=15);
    }
    for(a=[-60:10:60]) {
        translate([14*sin(a), -10 + 8*(cos(a)-1), 0])
            cylinder(d=0.8, h=h*0.4, $fn=10);
    }
}

// =====================================================
// PART 1: CUTTER
// =====================================================
module cutter() {
    linear_extrude(height=cutter_h)
        whale_cutter_wall_2d();
}

module whale_cutter() { cutter(); }

// =====================================================
// PART 2: PRESS
// =====================================================
module press() {
    union() {
        linear_extrude(height=press_wall_h)
            whale_press_wall_2d();
        translate([0, 0, press_wall_h])
            linear_extrude(height=top_t)
                offset(r=-clearance) whale_2d();
        whale_details();
    }
}

module whale_press() { press(); }

translate([-80, 0, 0]) cutter();
translate([ 80, 0, 0]) press();
