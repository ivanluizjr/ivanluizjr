// =====================================================
// BRIGADEIRO MOLD — OCTOPUS
// PART 1: cutter  — tall animal-shaped walls, no base
// PART 2: press   — walls + top plate + raised details
// =====================================================

$fn = 80;

wall_t        = 1.8;
cutter_h      = 20;
press_wall_h  = 9;
top_t         = 2.5;
detail_h      = 1.2;

// =====================================================
// 2D OCTOPUS SILHOUETTE
// Large round head + 8 tentacles at bottom
// =====================================================
module octopus_2d() {
    union() {
        // Head (slightly oval)
        scale([1.0, 1.05]) circle(r=17, $fn=80);
        // 8 tentacle blobs evenly spread at bottom
        for(i=[0:7]) {
            a = 200 + i * (140/7);  // spread across bottom 140°
            tx = 20 * cos(a);
            ty = 20 * sin(a);
            translate([tx, ty]) circle(r=5.5, $fn=40);
            // Tentacle arms connecting blob to head
            hull() {
                translate([tx*0.5, ty*0.5]) circle(r=3.5, $fn=20);
                translate([tx,     ty    ]) circle(r=4.0, $fn=20);
            }
        }
    }
}

module octopus_wall_2d() {
    difference() {
        offset(r=wall_t) octopus_2d();
        octopus_2d();
    }
}

// =====================================================
// OCTOPUS FACE DETAILS (raised on press)
// =====================================================
module octopus_face() {
    h = detail_h + 0.5;
    // Big cute eyes
    translate([-6.5, 4, 0]) cylinder(d=7, h=h*0.6, $fn=40);
    translate([ 6.5, 4, 0]) cylinder(d=7, h=h*0.6, $fn=40);
    // Pupils (taller nub)
    translate([-6.5, 4, 0]) cylinder(d=3.5, h=h, $fn=30);
    translate([ 6.5, 4, 0]) cylinder(d=3.5, h=h, $fn=30);
    // Eye shine
    translate([-4.8, 5.5, 0]) cylinder(d=1.0, h=h+0.3, $fn=15);
    translate([ 8.0, 5.5, 0]) cylinder(d=1.0, h=h+0.3, $fn=15);
    // Smile arc
    for(a=[-50:10:50]) {
        translate([6.5*sin(a), -2 + 6.5*(cos(a)-1), 0])
            cylinder(d=1.1, h=h*0.7, $fn=12);
    }
    // Blush circles
    translate([-12, -1, 0]) cylinder(d=4, h=h*0.4, $fn=30);
    translate([ 12, -1, 0]) cylinder(d=4, h=h*0.4, $fn=30);
    // Tentacle sucker dots (3 per side visible on head)
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
        octopus_wall_2d();
}

// =====================================================
// PART 2: PRESS
// =====================================================
module press() {
    union() {
        linear_extrude(height=press_wall_h)
            octopus_wall_2d();
        translate([0, 0, press_wall_h])
            linear_extrude(height=top_t)
                offset(r=wall_t) octopus_2d();
        octopus_face();
    }
}

translate([-70, 0, 0]) cutter();
translate([ 70, 0, 0]) press();
