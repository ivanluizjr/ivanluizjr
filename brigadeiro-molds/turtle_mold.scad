// =====================================================
// BRIGADEIRO MOLD — TURTLE
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
// MODULE: turtle_silhouette
// Round shell + head + 4 flippers + tail
// =====================================================
module turtle_silhouette(scale=1) {
    s = scale;
    union() {
        // Shell (circle)
        scale([s, s, 1]) circle(r=9, $fn=60);
        // Head
        translate([0, 11*s, 0])
            scale([s, s, 1]) ellipse_shape(3.5, 4);
        // Front left flipper
        translate([-9*s, 5*s, 0]) rotate([0,0,140])
            scale([s,s,1]) flipper_shape();
        // Front right flipper
        translate([ 9*s, 5*s, 0]) rotate([0,0,40])
            mirror([1,0,0]) scale([s,s,1]) flipper_shape();
        // Back left flipper
        translate([-8*s, -5*s, 0]) rotate([0,0,220])
            scale([s,s,1]) flipper_shape();
        // Back right flipper
        translate([ 8*s, -5*s, 0]) rotate([0,0,-40])
            mirror([1,0,0]) scale([s,s,1]) flipper_shape();
        // Tail
        translate([0, -11*s, 0])
            scale([s,s,1]) hull() {
                circle(r=2, $fn=20);
                translate([0, -3, 0]) circle(r=0.8, $fn=15);
            }
    }
}

module ellipse_shape(rx, ry) {
    scale([rx, ry, 1]) circle(r=1, $fn=50);
}

module flipper_shape() {
    hull() {
        circle(r=2.2, $fn=20);
        translate([4, 1, 0])  circle(r=1.2, $fn=20);
        translate([3, -2, 0]) circle(r=0.8, $fn=15);
    }
}

// =====================================================
// MODULE: turtle_shell_pattern
// Hexagonal scute pattern on shell
// =====================================================
module turtle_shell_pattern(depth=emb_d) {
    // Central scute
    translate([0, 0, 0]) hex_scute(3.5, depth);
    // Ring of 6 scutes
    for(i=[0:5]) {
        translate([6*cos(i*60), 6*sin(i*60), 0])
            hex_scute(2.8, depth);
    }
}

module hex_scute(r, depth) {
    linear_extrude(height=depth+0.1)
        difference() {
            circle(r=r, $fn=6);
            circle(r=r-0.5, $fn=6);
        }
}

// =====================================================
// MODULE: turtle_face
// =====================================================
module turtle_face(depth=emb_d) {
    // Eyes
    translate([-1.8, 11.5, 0]) cylinder(d=1.8, h=depth+0.1, $fn=25);
    translate([ 1.8, 11.5, 0]) cylinder(d=1.8, h=depth+0.1, $fn=25);
    // Eye shine
    translate([-1.2, 12, 0]) cylinder(d=0.5, h=depth+0.1, $fn=15);
    translate([ 2.4, 12, 0]) cylinder(d=0.5, h=depth+0.1, $fn=15);
    // Smile
    translate([0, 9.5, 0])
        rotate_extrude(angle=180, $fn=40)
            translate([2, 0, 0]) circle(r=0.4, $fn=15);
}

// =====================================================
// PART 1: BASE MOLD
// =====================================================
module base_mold() {
    difference() {
        rounded_cylinder(d=mold_d, h=wall_h, r=0.8);
        translate([0, 0, base_t])
            cylinder(d=mold_d - 2*wall_t, h=wall_h, $fn=80);
        // Turtle silhouette recessed
        translate([0, 0, base_t - emb_d])
            linear_extrude(height=emb_d + 0.1)
                turtle_silhouette(scale=1);
        // Shell pattern
        translate([0, 0, base_t - emb_d])
            turtle_shell_pattern();
        // Face
        translate([0, 0, base_t - emb_d])
            turtle_face();
    }
}

// =====================================================
// PART 2: DETAIL PLATE
// =====================================================
module detail_plate() {
    inner_d = mold_d - 2*wall_t - 0.4;
    cylinder(d=inner_d, h=base_t, $fn=80);
    translate([0, 0, base_t]) {
        linear_extrude(height=emb_d)
            turtle_silhouette(scale=1);
        turtle_shell_pattern(depth=emb_d);
        turtle_face(depth=emb_d);
    }
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
                    turtle_silhouette(scale=1);
    }
}

translate([-60, 0, 0]) base_mold();
translate([0,  0, 0])  detail_plate();
translate([60, 0, 0])  top_press();
