// =====================================================
// BRIGADEIRO MOLD — OCTOPUS
// Parts: base_mold | detail_plate | top_press
// =====================================================

// --- PARAMETERS ---
mold_d      = 50;   // outer diameter (mm)
wall_h      = 18;   // wall height (mm)
wall_t      = 1.4;  // wall thickness (mm)
base_t      = 1.2;  // base thickness (mm)
press_h     = 6;    // press body height (mm)
handle_h    = 12;   // handle height (mm)
handle_d    = 14;   // handle diameter (mm)
emb_d       = 0.6;  // emboss depth (mm)
$fn         = 80;

// =====================================================
// MODULE: rounded_cylinder
// =====================================================
module rounded_cylinder(d, h, r=0.8) {
    hull() {
        translate([0,0,r])       cylinder(d=d-2*r, h=h-2*r);
        translate([0,0,0])       cylinder(d=d,     h=r);
        translate([0,0,h-r])     cylinder(d=d,     h=r);
    }
}

// =====================================================
// MODULE: octopus_silhouette
// Cute octopus outline — head + 8 tentacles
// =====================================================
module octopus_silhouette(scale=1) {
    s = scale;
    union() {
        // Head (oval)
        scale([s,s,1]) ellipse_shape(rx=9, ry=10);
        // 8 tentacles around bottom
        for(i=[0:7]) {
            angle = -90 + i * (180/7);
            r_off = 9 * s;
            tx = r_off * cos(angle);
            ty = (10 * s) - 5*s + r_off * sin(angle) * 0.6;
            translate([tx, ty - 8*s, 0])
                scale([s, s, 1])
                    tentacle_shape();
        }
    }
}

module ellipse_shape(rx, ry) {
    scale([rx, ry, 1]) circle(r=1, $fn=60);
}

module tentacle_shape() {
    // Wavy tentacle via hull of small circles
    hull() {
        for(j=[0:4]) {
            tx = sin(j*40) * 1.5;
            ty = -j * 2.5;
            translate([tx, ty, 0]) circle(r=1.2, $fn=20);
        }
    }
}

// =====================================================
// MODULE: octopus_eyes
// =====================================================
module octopus_eyes(depth=emb_d) {
    // Left eye
    translate([-3.5, 1, 0]) {
        cylinder(d=3, h=depth+0.1, $fn=30);
        translate([0,1.5,0]) cylinder(d=0.8, h=depth+0.1, $fn=20); // shine
    }
    // Right eye
    translate([3.5, 1, 0]) {
        cylinder(d=3, h=depth+0.1, $fn=30);
        translate([0,1.5,0]) cylinder(d=0.8, h=depth+0.1, $fn=20);
    }
    // Smile
    translate([0,-2,0])
        rotate_extrude(angle=180, $fn=40)
            translate([3,0,0]) circle(r=0.6, $fn=20);
}

// =====================================================
// PART 1: BASE MOLD
// =====================================================
module base_mold() {
    difference() {
        // Outer wall (circular)
        rounded_cylinder(d=mold_d, h=wall_h, r=0.8);
        // Inner cutout
        translate([0, 0, base_t])
            cylinder(d=mold_d - 2*wall_t, h=wall_h, $fn=80);
        // Embossed octopus on base (recessed into floor)
        translate([0, 2, base_t - emb_d])
            linear_extrude(height=emb_d + 0.1)
                octopus_silhouette(scale=1);
        // Eyes embossed
        translate([0, 2, base_t - emb_d])
            octopus_eyes();
    }
}

// =====================================================
// PART 2: DETAIL PLATE
// (thin disc with raised octopus on top)
// =====================================================
module detail_plate() {
    inner_d = mold_d - 2*wall_t - 0.4; // slight clearance
    difference() {
        cylinder(d=inner_d, h=base_t, $fn=80);
    }
    // Raised octopus features on top
    translate([0, 2, base_t])
        linear_extrude(height=emb_d)
            octopus_silhouette(scale=1);
    translate([0, 2, base_t])
        octopus_eyes(depth=emb_d);
}

// =====================================================
// PART 3: TOP PRESS / EJECTOR
// =====================================================
module top_press() {
    inner_d = mold_d - 2*wall_t - 0.6; // fits inside walls
    union() {
        // Press disc
        rounded_cylinder(d=inner_d, h=press_h, r=0.6);
        // Handle on top
        translate([0, 0, press_h])
            rounded_cylinder(d=handle_d, h=handle_h, r=1.5);
        // Raised octopus on press bottom (mirror)
        translate([0, 2, 0])
            mirror([0,0,1])
                translate([0, 0, -emb_d])
                    linear_extrude(height=emb_d)
                        octopus_silhouette(scale=1);
    }
}

// =====================================================
// LAYOUT — show all 3 parts side by side
// =====================================================
translate([-60, 0, 0]) base_mold();      // LEFT
translate([0, 0, 0])   detail_plate();   // CENTER
translate([60, 0, 0])  top_press();      // RIGHT
