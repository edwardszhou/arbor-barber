class Tree {
  constructor(trunkLen, trunkWidth, minBranchingSize, maxBranchingSize, minNumBranch, maxNumBranch, minSplitAngle, maxSplitAngle, maxLevel) {
    this.trunkLen = trunkLen; // inital length of trunk
    this.trunkWidth = trunkWidth; // inital width of trunk
    this.minSize = minBranchingSize; // min/max branching size multiplier
    this.maxSize = maxBranchingSize;
    this.minNumBranch = minNumBranch; // min/max number of branches per
    this.maxNumBranch = maxNumBranch;
    this.minSplitAngle = minSplitAngle; // min/max angle of branch split
    this.maxSplitAngle = maxSplitAngle;
    this.maxLevel = maxLevel // max num of branches before no more growth

    
    this.branches = [];
    this.leaves = [];
    let rootBegin = createVector(0, 0, 0);
    let rootEnd = createVector(0, -this.trunkLen, 0);
    this.branches.push(new Branch(rootBegin, rootEnd, 0, trunkWidth));
    this.growthLevel = 0;
    this.hasLeaves = false;
    
    this.timeOffset = 0;
  }
  
  show() {
    for(let branch of this.branches) {
      branch.show();

    }
    
    for(let leaf of this.leaves) {
      fill(0, 150, 0);
      noStroke();
      push();
      translate(leaf.x, leaf.y, leaf.z);
      sphere(5, 5, 5);
      pop();
    }
  }
  
  grow() {
    if(this.leaves.length != 0) {
      return;
    }
    
    if(this.growthLevel == this.maxLevel) {
      this.growLeaves();
      this.hasLeaves = true;
      return;
    }
    
    for(let i = this.branches.length-1; i >= 0; i--) {
      let branch = this.branches[i];
      if(branch.children.length == 0) {
        
        let randNum = floor(random(this.minNumBranch, this.maxNumBranch+1));
        let randSplit = random(this.minSplitAngle, this.maxSplitAngle);
        let randLen = random(this.minSize, this.maxSize);
            
        let newBranches = branch.branch(randNum, randSplit, randLen);
    
        for(let newBranch of newBranches) {
          this.branches.push(newBranch);
        }
      } else {
        print("counted")
      }
    }
    this.growthLevel++;
  }
  
  growLeaves() {
    for(let branch of this.branches) {
      if(branch.children.length == 0) {
        let leaf = branch.end
        branch.leaves.push(leaf);
        this.leaves.push(leaf);
      }
    }
  }
  rustle(strength, speed) {
    for(let branch of this.branches) {
      let movementY = (noise(this.timeOffset*speed + branch.randomOffset)-0.5) * strength;
      let movementX = (noise(this.timeOffset*speed + branch.randomOffset + 100)-0.5) * strength;
      branch.end.y = branch.endStill.y + movementY * (branch.level+1);
      branch.end.x = branch.endWind.x + movementX * (branch.level+1);
    }
  }
  applyWind(strength, variation, chaos) {
    for(let branch of this.branches) {
      let movement = map(variation, 0, 1, 0.5, noise(this.timeOffset*chaos + branch.level/100), true) * strength;
      branch.end.x = branch.endStill.x + movement * (branch.level + 1);
      branch.endWind = branch.end.copy();
    }
    
    let referenceBranch = this.branches[this.branches.length-1];
    let distFromStill = referenceBranch.end.x - referenceBranch.endStill.x;
    
    let rustleValue = map(distFromStill, 0, 150, 0.5, 2, true);
    // print(distFromStill)
    this.rustle(rustleValue * (1+chaos), rustleValue*2);
  }
}