// =====================================================
// BRIGADEIRO MOLD — OCTOPUS
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
// 2D OCTOPUS SILHOUETTE
// =====================================================
module octopus_2d() {
    union() {
        scale([1.0, 1.05]) circle(r=17, $fn=80);
        for(i=[0:7]) {
            a = 200 + i * (140/7);
            tx = 20 * cos(a);
            ty = 20 * sin(a);
            translate([tx, ty]) circle(r=5.5, $fn=40);
            hull() {
                translate([tx*0.5, ty*0.5]) circle(r=3.5, $fn=20);
                translate([tx,     ty    ]) circle(r=4.0, $fn=20);
            }
        }
    }
}

module octopus_cutter_wall_2d() {
    difference() {
        offset(r=wall_t) octopus_2d();
        octopus_2d();
    }
}

module octopus_press_wall_2d() {
    difference() {
        octopus_2d();
        offset(r=-(wall_t + clearance)) octopus_2d();
    }
}

// =====================================================
// OCTOPUS FACE DETAILS
// =====================================================
module octopus_face() {
    h = detail_h + 0.5;
    translate([-6.5, 4, 0]) cylinder(d=7, h=h*0.6, $fn=40);
    translate([ 6.5, 4, 0]) cylinder(d=7, h=h*0.6, $fn=40);
    translate([-6.5, 4, 0]) cylinder(d=3.5, h=h, $fn=30);
    translate([ 6.5, 4, 0]) cylinder(d=3.5, h=h, $fn=30);
    translate([-4.8, 5.5, 0]) cylinder(d=1.0, h=h+0.3, $fn=15);
    translate([ 8.0, 5.5, 0]) cylinder(d=1.0, h=h+0.3, $fn=15);
    for(a=[-50:10:50]) {
        translate([6.5*sin(a), -2 + 6.5*(cos(a)-1), 0])
            cylinder(d=1.1, h=h*0.7, $fn=12);
    }
    translate([-12, -1, 0]) cylinder(d=4, h=h*0.4, $fn=30);
    translate([ 12, -1, 0]) cylinder(d=4, h=h*0.4, $fn=30);
    for(i=[-1,0,1]) {
        translate([-18 + i*2, -8 + abs(i)*3, 0])
            cylinder(d=1.4, h=h*0.5, $fn=15);
        translate([ 18 - i*2, -8 + abs(i)*3, 0])
            cylinder(d=1.4, h=h*0.5, $fn=15);
    }
}

// =====================================================
// PART 1: CUTTER
// =====================================================
module cutter() {
    linear_extrude(height=cutter_h)
        octopus_cutter_wall_2d();
}

module octopus_cutter() { cutter(); }

// =====================================================
// PART 2: PRESS
// =====================================================
module press() {
    union() {
        linear_extrude(height=press_wall_h)
            octopus_press_wall_2d();
        translate([0, 0, press_wall_h])
            linear_extrude(height=top_t)
                offset(r=-clearance) octopus_2d();
        octopus_face();
    }
}

module octopus_press() { press(); }

translate([-70, 0, 0]) cutter();
translate([ 70, 0, 0]) press();
