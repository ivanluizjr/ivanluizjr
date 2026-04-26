// =====================================================
// BRIGADEIRO MOLD — BALEIA (WHALE)
// Ref: MaliLab3D style
// PART 1: cutter  — animal-shaped walls, open
// PART 2: press   — walls + solid top + raised details
// =====================================================
$fn = 80;

wall_t       = 1.8;
cutter_h     = 30;
press_wall_h = 30;
top_t        = 3.0;
dh           = 1.4;
clearance    = 0.3;

// =====================================================
// 2D SILHOUETTE
// =====================================================
module whale_2d() {
    union() {
        // main chubby body
        scale([1.3, 1.0]) circle(r=16);
        // snout bump
        translate([-19, -2]) scale([0.9,0.7]) circle(r=7);
        // tail flukes
        translate([22,  6]) rotate([0,0,-15]) scale([1.2,0.8]) circle(r=7);
        translate([22, -6]) rotate([0,0, 15]) scale([1.2,0.8]) circle(r=7);
        // tail stock connector
        hull() {
            translate([13, 0]) circle(r=5);
            translate([21, 0]) circle(r=3);
        }
        // dorsal fin
        hull() {
            translate([-1, 16]) circle(r=3);
            translate([ 4, 24]) circle(r=2);
            translate([ 9, 16]) circle(r=3);
        }
        // pectoral fin
        translate([-10, -14]) rotate([0,0,15]) scale([1.5,0.8]) circle(r=7);
    }
}

module whale_cutter_wall_2d() {
    difference() { offset(r=wall_t) whale_2d(); whale_2d(); }
}
module whale_press_wall_2d() {
    difference() { whale_2d(); offset(r=-(wall_t+clearance)) whale_2d(); }
}

// =====================================================
// BODY DETAIL LINES
// =====================================================
module whale_body_details_2d() {
    lw = 0.8;
    // belly line (long arc along bottom)
    for(i=[0:8]) {
        a1 = -100 + i*15;
        a2 = -100 + (i+1)*15;
        hull() {
            translate([17*cos(a1)*1.3, 11*sin(a1)]) circle(r=lw/2,$fn=8);
            translate([17*cos(a2)*1.3, 11*sin(a2)]) circle(r=lw/2,$fn=8);
        }
    }
    // tail crease
    hull() {
        translate([13, 0]) circle(r=lw/2,$fn=8);
        translate([18, 3]) circle(r=lw/2,$fn=8);
    }
    hull() {
        translate([13, 0]) circle(r=lw/2,$fn=8);
        translate([18,-3]) circle(r=lw/2,$fn=8);
    }
    // dorsal fin line
    hull() {
        translate([2, 16]) circle(r=lw/2,$fn=8);
        translate([5, 22]) circle(r=lw/2,$fn=8);
    }
    // pectoral fin line
    hull() {
        translate([-10,-12]) circle(r=lw/2,$fn=8);
        translate([-16,-18]) circle(r=lw/2,$fn=8);
    }
}

// =====================================================
// FACE DETAILS
// =====================================================
module whale_face() {
    // eye — left side (head points left)
    translate([-16, 4, 0]) {
        cylinder(d=5.5, h=dh*0.65, $fn=35);
        cylinder(d=3.0, h=dh*1.2, $fn=25);
        translate([0.8, 0.8, 0]) cylinder(d=1.0, h=dh*1.5, $fn=12);
    }
    // smile
    for(a=[-45:9:45]) {
        translate([-12 + 5*sin(a), 0.5 + 4.5*(cos(a)-1), 0])
            cylinder(d=1.2, h=dh*0.8, $fn=12);
    }
    // cheek blush
    translate([-14, -1, 0]) cylinder(d=4.5, h=dh*0.3, $fn=28);
    // blowhole
    translate([2, 15, 0]) cylinder(d=3.5, h=dh*0.9, $fn=25);
    // water spray drops
    translate([-1.5, 20, 0]) cylinder(d=2.0, h=dh*0.7, $fn=15);
    translate([ 2.0, 22, 0]) cylinder(d=2.5, h=dh*0.9, $fn=15);
    translate([ 5.5, 21, 0]) cylinder(d=1.8, h=dh*0.7, $fn=15);
    // fluke mid groove
    translate([21.5, 0, 0])
        linear_extrude(height=dh*0.6)
            hull() {
                circle(r=0.6,$fn=8);
                translate([3,0]) circle(r=0.4,$fn=8);
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
        translate([0,0,press_wall_h])
            linear_extrude(height=top_t)
                offset(r=-clearance) whale_2d();
        // body lines
        linear_extrude(height=dh*0.7)
            whale_body_details_2d();
        // face
        whale_face();
    }
}
module whale_press() { press(); }

// =====================================================
// DISPLAY
// =====================================================
translate([-85, 0, 0]) cutter();
translate([ 85, 0, 0]) press();
