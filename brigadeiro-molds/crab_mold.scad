// =====================================================
// BRIGADEIRO MOLD — CARANGUEJO (CRAB)
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
module crab_2d() {
    union() {
        // body
        scale([1.1, 0.9]) circle(r=16);

        // LEFT claw arm
        hull() {
            translate([-15,  8]) circle(r=5);
            translate([-24, 16]) circle(r=4.5);
        }
        // left upper pincer
        hull() {
            translate([-24, 16]) circle(r=4.5);
            translate([-31, 23]) circle(r=5);
        }
        // left lower pincer
        hull() {
            translate([-24, 16]) circle(r=4);
            translate([-30,  8]) circle(r=4.5);
        }

        // RIGHT claw arm
        hull() {
            translate([ 15,  8]) circle(r=5);
            translate([ 24, 16]) circle(r=4.5);
        }
        // right upper pincer
        hull() {
            translate([ 24, 16]) circle(r=4.5);
            translate([ 31, 23]) circle(r=5);
        }
        // right lower pincer
        hull() {
            translate([ 24, 16]) circle(r=4);
            translate([ 30,  8]) circle(r=4.5);
        }

        // 3 walking legs each side
        for(i=[0:2]) {
            oy = -1 - i*7;
            hull() { translate([-15,oy]) circle(r=3.5); translate([-25,oy-5])  circle(r=2.5); }
            hull() { translate([-25,oy-5]) circle(r=2.5); translate([-30,oy-13]) circle(r=2); }
            hull() { translate([ 15,oy]) circle(r=3.5); translate([ 25,oy-5])  circle(r=2.5); }
            hull() { translate([ 25,oy-5]) circle(r=2.5); translate([ 30,oy-13]) circle(r=2); }
        }

        // eye stalks
        hull() { translate([-7,15]) circle(r=3); translate([-9,23]) circle(r=4.5); }
        hull() { translate([ 7,15]) circle(r=3); translate([ 9,23]) circle(r=4.5); }
    }
}

module crab_cutter_wall_2d() {
    difference() { offset(r=wall_t) crab_2d(); crab_2d(); }
}
module crab_press_wall_2d() {
    difference() { crab_2d(); offset(r=-(wall_t+clearance)) crab_2d(); }
}

// =====================================================
// BODY DETAIL LINES
// =====================================================
module crab_body_details_2d() {
    lw = 0.85;
    // carapace segments — 3 arcs
    for(i=[1:3]) {
        r = i * 4.5;
        for(j=[0:8]) {
            a1 = -100 + j*25;
            a2 = -100 + (j+1)*25;
            hull() {
                translate([r*cos(a1)*1.1, r*sin(a1)*0.9]) circle(r=lw/2,$fn=6);
                translate([r*cos(a2)*1.1, r*sin(a2)*0.9]) circle(r=lw/2,$fn=6);
            }
        }
    }
    // claw opening gap lines
    hull() {
        translate([-28,14]) circle(r=0.7,$fn=8);
        translate([-25,19]) circle(r=0.5,$fn=8);
    }
    hull() {
        translate([ 28,14]) circle(r=0.7,$fn=8);
        translate([ 25,19]) circle(r=0.5,$fn=8);
    }
}

// =====================================================
// FACE DETAILS
// =====================================================
module crab_face() {
    // LEFT eye stalk nub
    translate([-9, 23, 0]) {
        cylinder(d=6.5, h=dh*0.6, $fn=35);
        cylinder(d=3.8, h=dh*1.1, $fn=25);
        translate([0.9, 0.9, 0]) cylinder(d=1.1, h=dh*1.5, $fn=12);
    }
    // RIGHT eye stalk nub
    translate([ 9, 23, 0]) {
        cylinder(d=6.5, h=dh*0.6, $fn=35);
        cylinder(d=3.8, h=dh*1.1, $fn=25);
        translate([0.9, 0.9, 0]) cylinder(d=1.1, h=dh*1.5, $fn=12);
    }
    // smile
    for(a=[-55:11:55]) {
        translate([7.5*sin(a), -4 + 7*(cos(a)-1), 0])
            cylinder(d=1.3, h=dh*0.8, $fn=12);
    }
    // cheek blush
    translate([-10, 1, 0]) cylinder(d=5.5, h=dh*0.3, $fn=30);
    translate([ 10, 1, 0]) cylinder(d=5.5, h=dh*0.3, $fn=30);
    // blush dots
    for(d=[-1,1]) {
        translate([-10+d*2,  2.5, 0]) cylinder(d=1.0, h=dh*0.6, $fn=10);
        translate([ 10+d*2,  2.5, 0]) cylinder(d=1.0, h=dh*0.6, $fn=10);
    }
    // antenna dots on top of head
    translate([-3, 13, 0]) cylinder(d=1.5, h=dh*0.8, $fn=15);
    translate([ 3, 13, 0]) cylinder(d=1.5, h=dh*0.8, $fn=15);
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
        translate([0,0,press_wall_h])
            linear_extrude(height=top_t)
                offset(r=-clearance) crab_2d();
        // body lines
        linear_extrude(height=dh*0.7)
            crab_body_details_2d();
        // face
        crab_face();
    }
}
module crab_press() { press(); }

// =====================================================
// DISPLAY
// =====================================================
translate([-95, 0, 0]) cutter();
translate([ 95, 0, 0]) press();
