class Branch {
  
  constructor(begin, end, level, maxWidth) {
    this.begin = begin;
    this.end = end;
    this.endStill = end.copy();
    this.endWind = end.copy();
    this.children = [];
    this.leaves = [];
    this.level = level;
    this.maxWidth = maxWidth;
    
    this.thickness = map(this.level, 0, 5, this.maxWidth, 1, true)
    
    this.randomOffset = random(1.5) + level*1000;
  }
  
  show() {
    stroke(0);
    strokeWeight(this.thickness);  
    line(this.begin.x, this.begin.y, this.begin.z, this.end.x, this.end.y, this.end.z)
  }
  
  branch(num, split, len) {
    let newBranches = [];
    
    // direction of current branch
    let dir = p5.Vector.sub(this.end, this.begin);
    // let initAxis = findPerpendicular(dir);
    
    // finds perpendicular axis to the branch
    let initAxis = p5.Vector.cross(createVector(1, 0, 0), dir);
    // rotates around perpendicular axis to get split angle via Rodrigues' formula
    let firstBranchDir = rotateAround(dir, initAxis, split); // PARAM split
    
    // sets number of branches
    let branchAngle = 2*PI/num // PARAM num
    
    for(let i = random(0, branchAngle); i < TWO_PI; i += branchAngle) { 
      
      // rotates around axis of current branch
      let branchDir = rotateAround(firstBranchDir, dir, i);
      branchDir.mult(len); // shortens branch PARAM len
      
      let newEnd = p5.Vector.add(this.end, branchDir)
      let newBranch = new Branch(this.end, newEnd, this.level + 1, this.maxWidth);
      newBranches.push(newBranch);
      this.children.push(newBranch);
    }
    
    return newBranches;
  }
  
  
  
}