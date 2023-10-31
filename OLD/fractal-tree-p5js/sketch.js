let tree;

let seed = 0;
let cameraZoom = 600;
let cameraSpin = 150;
let cameraSlider, cameraSpinSlider;

var trunkLenSlider;
var trunkWidthSlider;
var minBranchingSizeSlider;
var maxBranchingSizeSlider;
var minNumBranchSlider;
var maxNumBranchSlider;
var minSplitAngleSlider;
var maxSplitAngleSlider;
var maxLevelSlider;
var windStrengthSlider;
var windVariationSlider;
var windChaosSlider;

var trunkLen;
var trunkWidth;
var minBranchingSize;
var maxBranchingSize;
var minNumBranch;
var maxNumBranch;
var minSplitAngle;
var maxSplitAngle;
var maxLevel;
var windStrength;
var windVariation;
var windChaos;

function setup() {
  createCanvas(800, 800, WEBGL);
  strokeCap(PROJECT);
  strokeJoin(BEVEL);
  
  trunkLen = 100;
  trunkWidth = 8;
  minBranchingSize = 0.5; 
  maxBranchingSize = 0.9;
  minNumBranch = 2;
  maxNumBranch = 4;
  minSplitAngle = PI/12;
  maxSplitAngle = PI/4;
  maxLevel = 6;
  
  windStrength = 15;
  windVariation = 0.5;
  windChaos = 1;
  
  treeSliderSetup();
  windSliderSetup();
  cameraSliderSetup();
  
  generateTree();
  print(tree.branches.length)
}

function draw() {
  camera(0, -200, cameraZoom, 0, -200, 0);
  background(220);
  if(cameraSpin < 500) {
    rotateY(frameCount/cameraSpin);
  }

  
  tree.timeOffset += 0.01
  tree.applyWind(windStrength, windVariation, windChaos); // strength, var, chaos
  tree.show();
}

function keyPressed() {
  if(keyCode == 32) {
    seed++;
    generateTree();
  }
}

function generateTree() {
  randomSeed(seed);
  
  tree = new Tree(trunkLen, trunkWidth, minBranchingSize, maxBranchingSize, minNumBranch, maxNumBranch, minSplitAngle, maxSplitAngle, maxLevel);
  
  while(!tree.hasLeaves) {
    tree.grow();
  }
}

function treeSliderSetup() {
  trunkLenSlider = createSlider(1, 300, trunkLen);
  trunkLenSlider.position(10, 10);
  trunkLenSlider.input(function(){
    trunkLen = trunkLenSlider.value();
    generateTree();
  })
  
  let trunkLenP = createP("Trunk Length");
  trunkLenP.position(160, -5);
  
  trunkWidthSlider = createSlider(1, 32, trunkWidth);
  trunkWidthSlider.position(10, 30);
  trunkWidthSlider.input(function(){
    trunkWidth = trunkWidthSlider.value();
    generateTree();
  })
  
  let trunkWidthP = createP("Trunk Width");
  trunkWidthP.position(160, 15);
  
  minBranchingSizeSlider = createSlider(0.1, 1, minBranchingSize, 0.001);
  minBranchingSizeSlider.position(10, 50);
  minBranchingSizeSlider.input(function(){
    minBranchingSize = minBranchingSizeSlider.value();
    maxBranchingSize = maxBranchingSizeSlider.value()+minBranchingSizeSlider.value();
    generateTree();
  })
  
  let minBranchingSizeP = createP("Min Branching Size Multiplier");
  minBranchingSizeP.position(160, 35);
  
  maxBranchingSizeSlider = createSlider(0, 1, maxBranchingSize-minBranchingSize, 0.001);
  maxBranchingSizeSlider.position(10, 70);
  maxBranchingSizeSlider.input(function(){
    maxBranchingSize = maxBranchingSizeSlider.value()+minBranchingSizeSlider.value();
    generateTree();
  })
  
  let maxBranchingSizeP = createP("Branching Size Multiplier AV");
  maxBranchingSizeP.position(160, 55);
  
  minNumBranchSlider = createSlider(1, 5, minNumBranch, 1);
  minNumBranchSlider.position(10, 90);
  minNumBranchSlider.input(function(){
    minNumBranch = minNumBranchSlider.value();
    maxNumBranch = maxNumBranchSlider.value()+minNumBranchSlider.value();
    generateTree();
  })
  
  let minNumBranchP = createP("Min Number Per Branch");
  minNumBranchP.position(160, 75);
  
  maxNumBranchSlider = createSlider(0, 5, maxNumBranch-minNumBranch, 1);
  maxNumBranchSlider.position(10, 110);
  maxNumBranchSlider.input(function(){
    maxNumBranch = maxNumBranchSlider.value()+minNumBranchSlider.value();
    generateTree();
  })
  
  let maxNumBranchP = createP("Number Per Branch AV");
  maxNumBranchP.position(160, 95);
  
  minSplitAngleSlider = createSlider(0, PI/2, minSplitAngle, 0.01);
  minSplitAngleSlider.position(10, 130);
  minSplitAngleSlider.input(function(){
    minSplitAngle = minSplitAngleSlider.value();
    maxSplitAngle = maxSplitAngleSlider.value()+minSplitAngleSlider.value();
    generateTree();
  })
  
  let minSplitAngleP = createP("Min Branch Split Angle");
  minSplitAngleP.position(160, 115);
  
  maxSplitAngleSlider = createSlider(0, PI/2, maxSplitAngle-minSplitAngle, 0.01);
  maxSplitAngleSlider.position(10, 150);
  maxSplitAngleSlider.input(function(){
    maxSplitAngle = maxSplitAngleSlider.value()+minSplitAngleSlider.value();
    generateTree();
  })
  
  let maxSplitAngleP = createP("Branch Split Angle AV");
  maxSplitAngleP.position(160, 135);

  maxLevelSlider = createSlider(0, 10, maxLevel, 1);
  maxLevelSlider.position(10, 170);
  maxLevelSlider.input(function(){
    maxLevel = maxLevelSlider.value();
    generateTree();
  })
  
  let maxLevelP = createP("Max Tree Level");
  maxLevelP.position(160, 155);
  
  let infoBlurb = createP("AV = Additional Variation");
  infoBlurb.position(75, 200);
}

function windSliderSetup() {
  windStrengthSlider = createSlider(0, 40, windStrength, 1);
  windStrengthSlider.position(width-140, 10);
  windStrengthSlider.input(function(){
    windStrength = windStrengthSlider.value();
  })
  
  let windStrengthP = createP("Wind Strength");
  windStrengthP.position(width-240, -5);
    
  windVariationSlider = createSlider(0.01, 1, windVariation, 0.01);
  windVariationSlider.position(width-140, 30);
  windVariationSlider.input(function(){
    windVariation = windVariationSlider.value();
  })
  
  let windVariationP = createP("Wind Variation");
  windVariationP.position(width-240, 15);
    
  windChaosSlider = createSlider(0, 2, windChaos, 0.01);
  windChaosSlider.position(width-140, 50);
  windChaosSlider.input(function(){
    windChaos = windChaosSlider.value();
  })
  
  let windChaosP = createP("Wind Chaos");
  windChaosP.position(width-240, 35);
}

function cameraSliderSetup() {
  
  cameraSlider = createSlider(200, 3200, cameraZoom, 1);
  cameraSlider.position(10, height-30);
  cameraSlider.style('width: 85%');
  cameraSlider.input(function() {
    cameraZoom = cameraSlider.value();
  })
  
  let cameraP = createP('Camera Zoom');
  cameraP.position(10, height-65);
  
  cameraSpinSlider = createSlider(50, 500, cameraSpin, 1);
  cameraSpinSlider.position(10, height-70);
  cameraSpinSlider.changed(function() {
    cameraSpin = cameraSpinSlider.value();
  })
  
  let cameraSpinP = createP('Camera Spin Speed');
  cameraSpinP.position(10, height-105);
}

// Rodrigues' rotation formula
// v_rot = v*cos(theta) + (axis x v) * sin(theta) + axis * (axis . v) * (1-cos(theta))
function rotateAround(vect, axis, angle) {
  
  axis = p5.Vector.normalize(axis);
  termOne = p5.Vector.mult(vect, cos(angle));
  termTwoPart = p5.Vector.cross(axis, vect)
  termTwo = p5.Vector.mult(termTwoPart, sin(angle));
  termThreePartOne = p5.Vector.dot(axis, vect);
  termThreePartTwo = termThreePartOne * (1-cos(angle));
  termThree = p5.Vector.mult(axis, termThreePartTwo);
  return p5.Vector.add(p5.Vector.add(termOne, termTwo), termThree);
}