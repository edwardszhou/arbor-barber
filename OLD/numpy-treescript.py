from math import pi, sin, cos, radians
import numpy as np
import random

tree = None
seed = 0
numFrames = 0

trunkLen = 100
trunkWidth = 8
minBranchingSize = 0.5 
maxBranchingSize = 0.9
minNumBranch = 2
maxNumBranch = 4
minSplitAngle = pi/12
maxSplitAngle = pi/4
maxLevel = 6

windStrength = 15
windVariation = 0.5
windChaos = 1

PERLIN_OCTAVES = 4

# P: 50% redution per octave
PERLIN_FALLOFF = 0.5

PERLIN_YWRAPB = 4
PERLIN_YWRAP = 1 << PERLIN_YWRAPB
PERLIN_ZWRAPB = 8
PERLIN_ZWRAP = 1 << PERLIN_ZWRAPB
PERLIN_SIZE = 4095

# P: [toxi 031112]
# P: new vars needed due to recent change of cos table in PGraphics
PERLIN_COS_TABLE = [cos(radians(d) * 0.5) for d in range(720)]
PERLIN_TWO_PI = 720
PERLIN_PI = PERLIN_TWO_PI
PERLIN_PI >>= 1

PERLIN = None


def noise(x, y=0, z=0):
    """Return perlin noise value at the given location.
    :param x: x-coordinate in noise space.
    :type x: float
    :param y: y-coordinate in noise space.
    :type y: float
    :param z: z-coordinate in noise space.
    :type z: float
    :returns: The perlin noise value.
    :rtype: float
    """

    global PERLIN

    # P: [toxi 031112]
    # P: now adjusts to the size of the cosLUT used via
    # P: the new variables, defined above
    def noise_fsc(i):
        # P: using bagel's cosine table instead
        return 0.5 * (1 - PERLIN_COS_TABLE[int(i * PERLIN_PI) % PERLIN_TWO_PI])

    # P: [toxi 031112]
    # P: noise broke due to recent change of cos table in PGraphics
    # P: this will take care of it
    if PERLIN is None:
        PERLIN = [random.random() for _ in range(PERLIN_SIZE + 1)]

    x = (-1 * x) if x < 0 else x
    xi = int(x)
    xf = x - xi

    y = (-1 * y) if y < 0 else y
    yi = int(y)
    yf = y - yi

    z = (-1 * z) if z < 0 else z
    zi = int(z)
    zf = z - zi

    r = 0
    ampl = 0.5

    for i in range(PERLIN_OCTAVES):
        rxf = noise_fsc(xf)
        ryf = noise_fsc(yf)

        of = int(xi + (yi << PERLIN_YWRAPB) + (zi << PERLIN_ZWRAPB))
        n1 = PERLIN[of % PERLIN_SIZE]
        n1 += rxf * (PERLIN[(of + 1) % PERLIN_SIZE] - n1)
        n2 = PERLIN[(of + PERLIN_YWRAP) % PERLIN_SIZE]
        n2 += rxf * (PERLIN[(of + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n2)
        n1 += ryf * (n2 - n1)

        of += PERLIN_ZWRAP
        n2 = PERLIN[of & PERLIN_SIZE]
        n2 += rxf * (PERLIN[(of + 1) % PERLIN_SIZE] - n2)
        n3 = PERLIN[(of + PERLIN_YWRAP) % PERLIN_SIZE]
        n3 += rxf * (PERLIN[(of + PERLIN_YWRAP + 1) % PERLIN_SIZE] - n3)

        n2 += ryf * (n3 - n2)
        n1 += noise_fsc(zf) * (n2 - n1)

        r += n1 * ampl
        ampl *= PERLIN_FALLOFF

        xi *= 2
        xf *= 2

        yi *= 2
        yf *= 2

        zi *= 2
        zf *= 2

        if xf >= 1:
            xi = xi + 1
            xf = xf - 1

        if yf >= 1:
            yi = yi + 1
            yf = yf - 1

        if zf >= 1:
            zi = zi + 1
            zf = zf - 1

    return r

def rotateAround(vect, axis, angle):
  
  axis = axis/np.linalg.norm(axis)
  termOne = vect * cos(angle)
  termTwoPart = np.cross(axis,vect)
  termTwo = termTwoPart * sin(angle)
  termThreePartOne = np.dot(axis,vect)
  termThreePartTwo = termThreePartOne * (1-cos(angle))
  termThree = axis * termThreePartTwo
  return termOne + termTwo + termThree

# from Arduino reference
def remap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def generateTree():
    random.seed(seed)
    global tree
    tree = Tree(trunkLen, trunkWidth, minBranchingSize, maxBranchingSize, minNumBranch, maxNumBranch, minSplitAngle, maxSplitAngle, maxLevel)
    while not tree.hasLeaves:
        tree.grow()

class Branch:
  
    def __init__(self, begin, end, level, maxWidth):
        self.begin = begin
        self.end = end
        self.endStill = np.copy(end)
        self.endWind = np.copy(end)
        self.children = []
        self.leaves = []
        self.level = level
        self.maxWidth = maxWidth

        self.thickness = max(remap(self.level, 0, 5, self.maxWidth, 1), 1)
        self.randomOffset = random.uniform(0, 1.5) * level * 1000
  
    def branch(self, num, split, length):
        newBranches = []

        # direction of current branch
        dir = self.end - self.begin

        # finds perpendicular axis to branch
        initAxis = np.cross(np.array([1, 0, 0]), dir)
        # rotates around perpendicular axis to get split angle via Rodrigues' formula
        firstBranchDir = rotateAround(dir, initAxis, split)

        
        # sets number of branches
        branchAngle = 2*pi/num
        
        for i in np.arange(random.uniform(0, branchAngle), 2*pi, branchAngle):

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
        rootBegin = np.array([0, 0, 0])
        rootEnd = np.array([0, -self.trunkLen, 0])
        self.branches.append(Branch(rootBegin, rootEnd, 0, trunkWidth))
        self.growthLevel = 0
        self.hasLeaves = False
        
        self.timeOffset = 0

    def grow(self):
        # if self.growthLevel == 1:
        #     for branch in self.branches:
        #         print(branch.end)
        if len(self.leaves) != 0:
            return
        if self.growthLevel == self.maxLevel:
            self.growLeaves()
            self.hasLeaves = True
            return

        for i in range(len(self.branches)-1, -1, -1):
            branch = self.branches[i]
            if len(branch.children) == 0:
                randNum = random.randint(self.minNumBranch, self.maxNumBranch)
                randSplit = random.uniform(self.maxSplitAngle, self.minSplitAngle)
                randLen = random.uniform(self.maxSize, self.minSize)

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
            branch.end[1] = branch.endStill[1] + movementY * (branch.level + 1)
            branch.end[0] = branch.endWind[0] + movementX * (branch.level + 1)

    def applyWind(self, strength, variation, chaos):
        for branch in self.branches:
            noiseValue = noise(self.timeOffset*chaos + branch.level / 100)
            movement = remap(variation, 0, 1, 0.5, noiseValue) * strength
            branch.end[0] = branch.endStill[0] + movement * (branch.level + 1)
            branch.endWind = branch.end.copy()

        distFromStill = abs(self.branches[-1].end[0] - self.branches[-1].endStill[0])
        rustleValue = min(remap(distFromStill, 0, 150, 0.5, 2), 2)
        self.rustle(rustleValue * (1 + chaos), rustleValue * 2)

generateTree()

print(len(tree.branches))
while numFrames < 300:

    numFrames += 1
    tree.timeOffset += 0.01
    tree.applyWind(windStrength, windVariation, windChaos)
    

