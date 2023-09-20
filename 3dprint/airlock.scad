
$fa = 1;
$fs = 0.4;


boxdepth = 10;
boxwidth = 22.5;
wallthickness = 1;
ringheight = 6;
braceoffset = 16;
tubediameter = 11;

module lid() {
  difference () {
    cube([boxwidth-2*wallthickness,boxdepth-1*wallthickness,2],center=true);
    translate([0,boxdepth/2-3.5,1]) cube([20.5,1.5,1],center=true); // slot
    translate([0,-boxdepth/2,0]) cube([boxwidth-2*wallthickness,7*wallthickness,2],center=true); //space for bow
  }
}

module topbox(
  boxwidth=boxwidth,
  boxdepth=boxdepth,
  wallthickness=wallthickness,
  tbheight = 17
  ) {
  difference () {
    cube([boxwidth,boxdepth,tbheight],center=true);
    translate([0,-1,6]) cube([boxwidth-2*wallthickness,boxdepth,10],center=true);
    cube([boxwidth-2*wallthickness,boxdepth-2*wallthickness,tbheight],center=true);
  }  
}
module cardslot (boxwidth=boxwidth,boxdepth=boxdepth,wallthickness=wallthickness, csheight=8) {
  difference () {
    cube([boxwidth,boxdepth,csheight],center=true);
    translate([0,boxdepth/2-3.5,0]) cube([boxwidth-2*wallthickness,1.5,csheight],center=true);
    cube([10,boxdepth-2*wallthickness,csheight],center=true);
  }  
}  

module compressionring(ringheight=ringheight,tubediam=11,ringwall=2) {
  difference() {
    cylinder(h=ringheight,d=tubediam+2*ringwall,center=true);
    cylinder(h=ringheight,d=tubediam,center=true);
    translate([0,-ringheight,0]) cube([1,3,ringheight],center=true);
    
  }
}


module prism(l, w, h) {
       polyhedron(points=[
               [0,0,h],           // 0    front top corner
               [-w,0,0],[w,0,0],   // 1, 2 front left & right bottom corners
               [0,l,h],           // 3    back top corner
               [-w,l,0],[w,l,0]    // 4, 5 back left & right bottom corners
       ], faces=[ // points for all faces must be ordered clockwise when looking in
               [0,2,1],    // top face
               [3,4,5],    // base face
               [0,1,4,3],  // h face
               [1,2,5,4],  // w face
               [0,3,5,2],  // hypotenuse face
       ]);
}

module bottombox(
  boxwidth=boxwidth,
  boxdepth=boxdepth,
  wallthickness=wallthickness,
  ringheight = ringheight, 
  braceoffset=braceoffset, 
  tubediam=tubediameter, 
  ringwall=2, 
  bboxh=13
  ) {
  
  difference () {
    cube([boxwidth,boxdepth,bboxh],center=true);
    cube([boxwidth-2*wallthickness,boxdepth-2*wallthickness,13],center=true);
    //Create a notch for the cable connector
    translate([0,-boxdepth/2+wallthickness,0]) cube([10,wallthickness,bboxh],center=true);
  }
  difference () {
    translate([0,-boxdepth/2,-bboxh/2]) rotate([90,0,0]) prism(ringheight, boxwidth/2, braceoffset*2);
    translate([0,-boxdepth/2-braceoffset,-bboxh/2]) cylinder(d=tubediam + ringwall*2, h=ringheight);
    // This is a little hackish, wanted to make the brace a little wider so needed to make it longer and cut off the tip
    translate([0,-boxdepth/2-braceoffset-tubediam,-bboxh/2+ringheight/2]) cube([braceoffset,braceoffset,ringheight],center=true);
  }
  translate([0,-boxdepth/2-braceoffset,-bboxh/2+ringheight/2]) compressionring(ringheight,tubediam,ringwall);
}

module sensorbox(
  boxwidth = boxwidth,
  boxdepth = boxdepth,
  wallthickness = wallthickness,
  ringheight = ringheight, 
  braceoffset=braceoffset, 
  tubediam=tubediameter, 
  ringwall=2
  ) {
    bboxh=13;
    csheight=8;
    tbheight = 18;
    bottombox(boxwidth,boxdepth,wallthickness,ringheight, braceoffset, tubediam, ringwall, bboxh);
    translate([0,0,bboxh/2+csheight/2]) cardslot(boxwidth,boxdepth,wallthickness,csheight);
    translate([0,0,bboxh/2+csheight+tbheight/2]) topbox(boxwidth,boxdepth,wallthickness,tbheight);
}
//bottombox();
//topbox();  
//cardslot(); 

sensorbox();
translate ([40,0,0])  lid();
