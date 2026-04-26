// =====================================================
// BRIGADEIRO MOLD — POLVO (OCTOPUS)
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
module octopus_2d() {
    union() {
        // head
        scale([1.0,1.08]) circle(r=16);
        // 8 tentacles — curving outward and downward
        for(i=[0:7]) {
            base_a = 200 + i*(140.0/7);
            // tentacle arm
            hull() {
                translate([12*cos(base_a), 12*sin(base_a)]) circle(r=4.5);
                translate([20*cos(base_a), 20*sin(base_a)]) circle(r=3.5);
            }
            // curl blob at tip
            translate([22*cos(base_a), 22*sin(base_a)]) circle(r=5);
            // secondary curl
            translate([24*cos(base_a+12), 24*sin(base_a+12)]) circle(r=3.5);
        }
    }
}

module octopus_cutter_wall_2d() {
    difference() { offset(r=wall_t) octopus_2d(); octopus_2d(); }
}
module octopus_press_wall_2d() {
    difference() { octopus_2d(); offset(r=-(wall_t+clearance)) octopus_2d(); }
}

// =====================================================
// TENTACLE SWIRL DETAILS (raised on press face)
// =====================================================
module tentacle_swirl(angle) {
    rotate([0,0,angle]) {
        // arm line
        hull() {
            translate([8,0]) circle(r=0.7,$fn=8);
            translate([16,0]) circle(r=0.5,$fn=8);
        }
        // curl spiral
        for(j=[0:3]) {
            r1 = 16 + j*1.5;
            a1 = j*70;
            r2 = 16 + (j+1)*1.5;
            a2 = (j+1)*70;
            hull() {
                translate([r1*cos(a1),r1*sin(a1)]) circle(r=0.6,$fn=8);
                translate([r2*cos(a2),r2*sin(a2)]) circle(r=0.5,$fn=8);
            }
        }
        // suction cups along arm
        for(k=[0:2]) {
            translate([10+k*2.5, -1.5]) circle(r=0.8,$fn=12);
        }
    }
}

module octopus_body_details() {
    // all 8 tentacle swirls
    for(i=[0:7]) {
        base_a = 200 + i*(140.0/7);
        rotate([0,0,base_a]) tentacle_swirl(0);
    }
    // head texture — small dots
    for(i=[0:5]) {
        a = i*60;
        translate([8*cos(a), 8*sin(a)]) circle(r=0.9,$fn=15);
    }
}

// =====================================================
// FACE DETAILS
// =====================================================
module octopus_face() {
    // LEFT eye
    translate([-6, 5, 0]) {
        cylinder(d=7.5, h=dh*0.6, $fn=40);   // outer eye
        cylinder(d=4.5, h=dh*1.1, $fn=30);   // pupil
        translate([1.0, 1.2, 0]) cylinder(d=1.3, h=dh*1.5, $fn=15); // shine
    }
    // RIGHT eye
    translate([ 6, 5, 0]) {
        cylinder(d=7.5, h=dh*0.6, $fn=40);
        cylinder(d=4.5, h=dh*1.1, $fn=30);
        translate([1.0, 1.2, 0]) cylinder(d=1.3, h=dh*1.5, $fn=15);
    }
    // eyebrows (raised arcs)
    translate([-6, 9.5, 0]) rotate([0,0,-10])
        linear_extrude(height=dh*0.8)
            hull() { circle(r=0.7,$fn=8); translate([4,0]) circle(r=0.7,$fn=8); }
    translate([ 6, 9.5, 0]) rotate([0,0, 10])
        linear_extrude(height=dh*0.8)
            hull() { circle(r=0.7,$fn=8); translate([4,0]) circle(r=0.7,$fn=8); }
    // smile
    for(a=[-55:11:55]) {
        translate([7.5*sin(a), -1.5 + 7*(cos(a)-1), 0])
            cylinder(d=1.3, h=dh*0.9, $fn=12);
    }
    // cheek blush
    translate([-12, 1, 0]) cylinder(d=5, h=dh*0.3, $fn=30);
    translate([ 12, 1, 0]) cylinder(d=5, h=dh*0.3, $fn=30);
    // tiny blush dots
    for(d=[-1,1]) {
        translate([12+d*1.5,  2.5, 0]) cylinder(d=1, h=dh*0.6, $fn=10);
        translate([-12+d*1.5, 2.5, 0]) cylinder(d=1, h=dh*0.6, $fn=10);
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
        translate([0,0,press_wall_h])
            linear_extrude(height=top_t)
                offset(r=-clearance) octopus_2d();
        // body & tentacle details
        linear_extrude(height=dh*0.8)
            octopus_body_details();
        // face
        octopus_face();
    }
}
module octopus_press() { press(); }

// =====================================================
// DISPLAY
// =====================================================
translate([-75, 0, 0]) cutter();
translate([ 75, 0, 0]) press();
