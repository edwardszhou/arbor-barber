from p5 import *
from numpy import arange

tree = None
seed = 0
cameraZoom = 600
cameraRotInc = 0.01

trunkLen = 100
trunkWidth = 8
minBranchingSize = 0.5 
maxBranchingSize = 0.9
minNumBranch = 2
maxNumBranch = 4
minSplitAngle = PI/12
maxSplitAngle = PI/4
maxLevel = 6

windStrength = 15
windVariation = 0.5
windChaos = 1

def setup():
    size(800, 800)
    stroke_cap(PROJECT)
    stroke_join(BEVEL)

    generateTree()

def draw():
    global cameraRotInc
    camera(0, -200, cameraZoom, 0, -200, 0, 0, -1, 0)
    background(220)
    rotate_y(cameraRotInc)
    cameraRotInc += 0.01

    tree.timeOffset += 0.01
    tree.applyWind(windStrength, windVariation, windChaos)
    tree.show()

def mouse_pressed():
    global seed
    seed += 1
    generateTree()

def rotateAround(vect, axis, angle):
  
  axis.normalize()
  termOne = vect * cos(angle)
  termTwoPart = axis.cross(vect)
  termTwo = termTwoPart * sin(angle)
  termThreePartOne = axis.dot(vect)
  termThreePartTwo = termThreePartOne * (1-cos(angle))
  termThree = axis * termThreePartTwo
  return termOne + termTwo + termThree

def generateTree():
    random_seed(seed)
    global tree
    tree = Tree(trunkLen, trunkWidth, minBranchingSize, maxBranchingSize, minNumBranch, maxNumBranch, minSplitAngle, maxSplitAngle, maxLevel)
    while not tree.hasLeaves:
        tree.grow()

class Branch:
  
    def __init__(self, begin, end, level, maxWidth):
        self.begin = begin
        self.end = end
        self.endStill = end.copy()
        self.endWind = end.copy()
        self.children = []
        self.leaves = []
        self.level = level
        self.maxWidth = maxWidth

        self.thickness = max(remap(self.level, (0, 5), (self.maxWidth, 1)), 1)
        self.randomOffset = random_uniform(1.5) * level * 1000

  
    def show(self):
        stroke(0)
        stroke_weight(self.thickness)
        begin_shape()
        vertex(self.begin.x, self.begin.y, self.begin.z)
        vertex(self.end.x, self.end.y, self.end.z)
        end_shape()
  
    def branch(self, num, split, length):
        newBranches = []

        # direction of current branch
        dir = self.end - self.begin

        # finds perpendicular axis to branch
        initAxis = Vector(1, 0, 0).cross(dir)
        # rotates around perpendicular axis to get split angle via Rodrigues' formula
        firstBranchDir = rotateAround(dir, initAxis, split)
        
        # sets number of branches
        branchAngle = 2*PI/num
        
        for i in arange(random_uniform(branchAngle), 2*PI, branchAngle):

            # rotates around axis of current branch
            branchDir = rotateAround(firstBranchDir, dir, i)
            branchDir *= length

            newEnd = self.end + branchDir
            newBranch = Branch(self.end, newEnd, self.level + 1, self.maxWidth)
            newBranches.append(newBranch)
            self.children.append(newBranch)
        
        return newBranches
  
class Tree:
    def __init__(self, trunkLen, trunkWidth, minBranchingSize, maxBranchingSize, minNumBranch, maxNumBranch, minSplitAngle, maxSplitAngle, maxLevel):
        self.trunkLen = trunkLen # inital length of trunk
        self.trunkWidth = trunkWidth # inital width of trunk
        self.minSize = minBranchingSize # min/max branching size multiplier
        self.maxSize = maxBranchingSize
        self.minNumBranch = minNumBranch # min/max number of branches per
        self.maxNumBranch = maxNumBranch
        self.minSplitAngle = minSplitAngle # min/max angle of branch split
        self.maxSplitAngle = maxSplitAngle
        self.maxLevel = maxLevel # max num of branches before no more growth

        
        self.branches = []
        self.leaves = []
        rootBegin = Vector(0, 0, 0)
        rootEnd = Vector(0, -self.trunkLen, 0)
        self.branches.append(Branch(rootBegin, rootEnd, 0, trunkWidth))
        self.growthLevel = 0
        self.hasLeaves = False
        
        self.timeOffset = 0

    def show(self):
        for branch in self.branches:
            branch.show()
        
        for leaf in self.leaves:
            fill(0, 150, 0)
            no_stroke()
            
            with push_matrix():
                translate(leaf.x, leaf.y, leaf.z)
                sphere(5, 4, 4)
                

    def grow(self):
        if len(self.leaves) != 0:
            return
        if self.growthLevel == self.maxLevel:
            self.growLeaves()
            self.hasLeaves = True
            return

        for i in range(len(self.branches)-1, -1, -1):
            branch = self.branches[i]
            if len(branch.children) == 0:
                randNum = floor(random_uniform(self.maxNumBranch+1, self.minNumBranch))
                randSplit = random_uniform(self.maxSplitAngle, self.minSplitAngle)
                randLen = random_uniform(self.maxSize, self.minSize)

                newBranches = branch.branch(randNum, randSplit, randLen)

                for branch in newBranches:
                    self.branches.append(branch)
        
        self.growthLevel += 1

    def growLeaves(self):
        for branch in self.branches:
            if len(branch.children) == 0:
                leaf = branch.end
                branch.leaves.append(leaf)
                self.leaves.append(leaf)

    def rustle(self, strength, speed):
        for branch in self.branches:
            movementY = strength * (noise(self.timeOffset * speed + branch.randomOffset) - 0.5)
            movementX = strength * (noise(self.timeOffset * speed + branch.randomOffset + 100) - 0.5)
            branch.end.y = branch.endStill.y + movementY * (branch.level + 1)
            branch.end.x = branch.endWind.x + movementX * (branch.level + 1)

    def applyWind(self, strength, variation, chaos):
        for branch in self.branches:
            noiseValue = noise(self.timeOffset*chaos + branch.level / 100)
            movement = remap(variation, (0, 1), (0.5, noiseValue)) * strength
            branch.end.x = branch.endStill.x + movement * (branch.level + 1)
            branch.endWind = branch.end.copy()

        distFromStill = abs(self.branches[-1].end.x - self.branches[-1].endStill.x)
        rustleValue = min(remap(distFromStill, (0, 150), (0.5, 2)), 2)
        self.rustle(rustleValue * (1 + chaos), rustleValue * 2)


run(mode='P3D')