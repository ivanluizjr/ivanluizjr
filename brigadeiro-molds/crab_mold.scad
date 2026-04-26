// =====================================================
// BRIGADEIRO MOLD — CRAB
// Parts: base_mold | detail_plate | top_press
// =====================================================

$fn         = 80;
mold_d      = 50;
wall_h      = 18;
wall_t      = 1.4;
base_t      = 1.2;
press_h     = 6;
handle_h    = 12;
handle_d    = 14;
emb_d       = 0.6;

module rounded_cylinder(d, h, r=0.8) {
    hull() {
        translate([0,0,r])   cylinder(d=d-2*r, h=h-2*r);
        translate([0,0,0])   cylinder(d=d,     h=r);
        translate([0,0,h-r]) cylinder(d=d,     h=r);
    }
}

// =====================================================
// MODULE: crab_silhouette
// Round body + 2 big claws + 6 legs
// =====================================================
module crab_silhouette(scale=1) {
    s = scale;
    union() {
        // Body
        scale([s*1.05, s*0.85, 1]) circle(r=8, $fn=60);
        // Left claw
        translate([-11*s, 2*s, 0]) rotate([0,0,20])
            scale([s,s,1]) claw_shape();
        // Right claw
        translate([11*s, 2*s, 0]) mirror([1,0,0]) rotate([0,0,20])
            scale([s,s,1]) claw_shape();
        // 3 legs each side
        for(i=[0:2]) {
            angle_l = 130 + i*20;
            angle_r = 50  - i*20;
            translate([8*s*cos(angle_l), 8*s*sin(angle_l), 0])
                rotate([0,0,angle_l-90])
                    scale([s,s,1]) leg_shape();
            translate([8*s*cos(angle_r), 8*s*sin(angle_r), 0])
                rotate([0,0,angle_r-90])
                    scale([s,s,1]) leg_shape();
        }
        // Eyes on stalks
        translate([-4*s, 7*s, 0]) eye_stalk(s);
        translate([ 4*s, 7*s, 0]) eye_stalk(s);
    }
}

module claw_shape() {
    hull() {
        circle(r=2.5, $fn=30);
        translate([4, 3, 0])  circle(r=1.8, $fn=25);
        translate([4, -2, 0]) circle(r=1.5, $fn=25);
    }
    // Claw gap
    translate([4, 0.5, 0]) rotate([0,0,10])
        hull() {
            circle(r=0.5, $fn=10);
            translate([2,1,0]) circle(r=0.3, $fn=10);
        }
}

module leg_shape() {
    hull() {
        circle(r=1, $fn=15);
        translate([0, 5, 0]) circle(r=0.6, $fn=15);
    }
}

module eye_stalk(s) {
    // Stalk
    hull() {
        circle(r=0.8*s, $fn=15);
        translate([0, 2.5*s, 0]) circle(r=0.8*s, $fn=15);
    }
    // Eye ball
    translate([0, 3.5*s, 0]) circle(r=1.8*s, $fn=25);
}

// =====================================================
// MODULE: crab_face
// =====================================================
module crab_face(depth=emb_d) {
    // Eyes (filled pupils)
    translate([-4, 9.5, 0]) cylinder(d=1.2, h=depth+0.1, $fn=20);
    translate([ 4, 9.5, 0]) cylinder(d=1.2, h=depth+0.1, $fn=20);
    // Smile
    translate([0, -1, 0])
        rotate_extrude(angle=160, $fn=40)
            translate([3.5, 0, 0]) circle(r=0.5, $fn=20);
    // Bubble cheeks
    translate([-5.5, 0, 0]) cylinder(d=2, h=depth+0.1, $fn=20);
    translate([ 5.5, 0, 0]) cylinder(d=2, h=depth+0.1, $fn=20);
}

// =====================================================
// PART 1: BASE MOLD
// =====================================================
module base_mold() {
    difference() {
        rounded_cylinder(d=mold_d, h=wall_h, r=0.8);
        translate([0, 0, base_t])
            cylinder(d=mold_d - 2*wall_t, h=wall_h, $fn=80);
        translate([0, -1, base_t - emb_d])
            linear_extrude(height=emb_d + 0.1)
                crab_silhouette(scale=1);
        translate([0, -1, base_t - emb_d])
            crab_face();
    }
}

// =====================================================
// PART 2: DETAIL PLATE
// =====================================================
module detail_plate() {
    inner_d = mold_d - 2*wall_t - 0.4;
    cylinder(d=inner_d, h=base_t, $fn=80);
    translate([0, -1, base_t])
        linear_extrude(height=emb_d)
            crab_silhouette(scale=1);
    translate([0, -1, base_t])
        crab_face(depth=emb_d);
}

// =====================================================
// PART 3: TOP PRESS
// =====================================================
module top_press() {
    inner_d = mold_d - 2*wall_t - 0.6;
    union() {
        rounded_cylinder(d=inner_d, h=press_h, r=0.6);
        translate([0, 0, press_h])
            rounded_cylinder(d=handle_d, h=handle_h, r=1.5);
        mirror([0,0,1])
            translate([0, -1, -emb_d])
                linear_extrude(height=emb_d)
                    crab_silhouette(scale=1);
    }
}

translate([-60, 0, 0]) base_mold();
translate([0,  0, 0])  detail_plate();
translate([60, 0, 0])  top_press();
