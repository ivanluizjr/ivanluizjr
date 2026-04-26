// =====================================================
// BRIGADEIRO MOLD — WHALE
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
        translate([0,0,r])       cylinder(d=d-2*r, h=h-2*r);
        translate([0,0,0])       cylinder(d=d, h=r);
        translate([0,0,h-r])     cylinder(d=d, h=r);
    }
}

// =====================================================
// MODULE: whale_silhouette
// Cute whale: round body + tail + fin
// =====================================================
module whale_silhouette(scale=1) {
    s = scale;
    union() {
        // Body (wide ellipse)
        scale([s*1.1, s*0.85, 1]) circle(r=9, $fn=60);
        // Tail (two flukes)
        translate([10*s, 0, 0]) {
            rotate([0,0,30])  scale([s,s,1]) fluke();
            rotate([0,0,-30]) scale([s,s,1]) mirror([0,1,0]) fluke();
        }
        // Dorsal fin
        translate([-1*s, 8*s, 0])
            scale([s, s, 1]) dorsal_fin();
        // Belly line
        translate([0, -3*s, 0])
            scale([s*1.0, s*0.3, 1]) circle(r=6, $fn=40);
    }
}

module fluke() {
    hull() {
        circle(r=1.5, $fn=20);
        translate([4, 3, 0])  circle(r=1.2, $fn=20);
        translate([4, -3, 0]) circle(r=1.2, $fn=20);
    }
}

module dorsal_fin() {
    polygon(points=[[0,0],[3,5],[6,0]]);
}

// =====================================================
// MODULE: whale_face
// =====================================================
module whale_face(depth=emb_d) {
    // Eye
    translate([-5, 2, 0]) {
        cylinder(d=2.5, h=depth+0.1, $fn=30);
        translate([0.5, 0.8, 0]) cylinder(d=0.7, h=depth+0.1, $fn=20);
    }
    // Smile
    translate([-3, -1, 0])
        rotate_extrude(angle=150, $fn=40)
            translate([3, 0, 0]) circle(r=0.5, $fn=20);
    // Blowhole
    translate([0, 7, 0]) cylinder(d=1.5, h=depth+0.1, $fn=20);
    // Water spray lines
    for(i=[-1,0,1]) {
        translate([i*1.5, 9, 0])
            rotate([0,0,i*15])
                scale([0.3, 1, 1])
                    cylinder(d=0.8, h=depth+0.1, $fn=10);
    }
}

// =====================================================
// PART 1: BASE MOLD
// =====================================================
module base_mold() {
    difference() {
        rounded_cylinder(d=mold_d, h=wall_h, r=0.8);
        translate([0, 0, base_t])
            cylinder(d=mold_d - 2*wall_t, h=wall_h, $fn=80);
        translate([0, 0, base_t - emb_d])
            linear_extrude(height=emb_d + 0.1)
                whale_silhouette(scale=1);
        translate([0, 0, base_t - emb_d])
            whale_face();
    }
}

// =====================================================
// PART 2: DETAIL PLATE
// =====================================================
module detail_plate() {
    inner_d = mold_d - 2*wall_t - 0.4;
    cylinder(d=inner_d, h=base_t, $fn=80);
    translate([0, 0, base_t])
        linear_extrude(height=emb_d)
            whale_silhouette(scale=1);
    translate([0, 0, base_t])
        whale_face(depth=emb_d);
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
            translate([0, 0, -emb_d])
                linear_extrude(height=emb_d)
                    whale_silhouette(scale=1);
    }
}

translate([-60, 0, 0]) base_mold();
translate([0,  0, 0])  detail_plate();
translate([60, 0, 0])  top_press();
