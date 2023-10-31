bl_info = {
    "name": "Arbor Barber",
    "author": "Edward Zhou",
    "version": (1, 0),
    "blender": (3,2,2),
    "location": "View3D > Toolbar > Arbor Barber",
    "description": "Adds custom procedural trees",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh"
}


import bpy
from math import pi, sin, cos, radians
import numpy as np
import random

tree = None
seed = random.randint(0, 100)
numFrames = 0

# initial values of tree
trunkLen = 2
trunkWidth = 8
minBranchingSize = 0.5 
maxBranchingSize = 0.9
minNumBranch = 2
maxNumBranch = 4
minSplitAngle = pi/12
maxSplitAngle = pi/4
maxLevel = 6

windStrength = 0
windVariation = 0
windChaos = 0

# Perlin noise function pasted from p5py

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
    def noise_fsc(i):

        return 0.5 * (1 - PERLIN_COS_TABLE[int(i * PERLIN_PI) % PERLIN_TWO_PI])

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

# Rodriguez' rotation formula
def rotateAround(vect, axis, angle):
    """Return rotation around a vector for a given axis and angle.
    :param vect: vector to rotate around
    :type vect: 
    :param axis: axis to rotate
    :type axis: 
    :param angle: angle to rotate
    :type angle: 
    :returns: 
    :rtype: 
    """
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

def generateTreeDefault():
    random.seed(seed)
    global tree
    tree = Tree(trunkLen, trunkWidth, minBranchingSize, maxBranchingSize, minNumBranch, maxNumBranch, minSplitAngle, maxSplitAngle, maxLevel)
    while not tree.hasLeaves:
        tree.grow()

def generateTreeBlender():
    random.seed(seed)
    treeProperties = bpy.context.scene.tree_adjust
    global tree
    tree = Tree(treeProperties.trunk_len, treeProperties.trunk_width, treeProperties.min_branching_size, treeProperties.min_branching_size+treeProperties.max_branching_size, treeProperties.min_num_branch, treeProperties.min_num_branch+treeProperties.max_num_branch, treeProperties.min_split_angle, treeProperties.min_split_angle+treeProperties.max_split_angle, treeProperties.max_level)
    while not tree.hasLeaves:
        tree.grow()

class Branch:
  
    def __init__(self, begin, end, level, maxWidth):
        self.begin = begin
        self.end = end
        self.endStill = np.copy(end)
        self.endWind = np.copy(end)
        self.parent = None
        self.leaves = []
        self.level = level
        self.maxWidth = maxWidth
        self.hasBranches = False

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
            newBranch.parent = self
            newBranches.append(newBranch)
        
        self.hasBranches = True
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
            if not branch.hasBranches:
                randNum = random.randint(self.minNumBranch, self.maxNumBranch)
                randSplit = random.uniform(self.maxSplitAngle, self.minSplitAngle)
                randLen = random.uniform(self.maxSize, self.minSize)

                newBranches = branch.branch(randNum, randSplit, randLen)

                for branch in newBranches:
                    self.branches.append(branch)
        
        self.growthLevel += 1

    def growLeaves(self):
        for branch in self.branches:
            if not branch.hasBranches:
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
        rustleValue = min(remap(distFromStill, 0, 150, 0.05, 0.2), 2)
        print(rustleValue)
        self.rustle(rustleValue * (1 + chaos), rustleValue * 2)



def createLeaf(x, y, z):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=3, ring_count=6, radius=0.07)
    leaf = bpy.context.active_object
    leaf.location = (x, y, z)
    leaf.scale = (1, 1, 1.3)
    leaf.rotation_euler = (random.uniform(0, pi),random.uniform(0, pi),random.uniform(0, 2*pi))
    return leaf
    
class TreeProperties(bpy.types.PropertyGroup):
    trunk_len : bpy.props.FloatProperty(name="Trunk Length", min=0, soft_min=0, soft_max=4, step=1)
    trunk_width: bpy.props.FloatProperty(name="Trunk Width", min=0.1, soft_min=0.1, soft_max=32, step=1)
    min_branching_size: bpy.props.FloatProperty(name="Min Branch Size", min=0.1, soft_min=0.1, soft_max=1, step=1)
    max_branching_size: bpy.props.FloatProperty(name="Branch Size Var", min=0, soft_min=0, soft_max=1, step=1)
    min_num_branch: bpy.props.IntProperty(name="Min Split Number", min=1, soft_min=1, soft_max=5)
    max_num_branch: bpy.props.IntProperty(name="Split Number Var", min=0, soft_min=0, soft_max=5)
    min_split_angle: bpy.props.FloatProperty(name="Min Split Angle", min=0, soft_min=0, soft_max=(pi/2), subtype="ANGLE")
    max_split_angle: bpy.props.FloatProperty(name="Split Angle Var", min=0, soft_min=0, soft_max=(pi/2), subtype="ANGLE")
    max_level: bpy.props.IntProperty(name="Max Tree Level", min=0, soft_min=0, soft_max=10)
    
    wind_strength: bpy.props.FloatProperty(name="Wind Strength", min=0, soft_min=0, soft_max=1, step=1)
    has_leaves: bpy.props.BoolProperty(name="Has Leaves")
    
class AddTreeOperator(bpy.types.Operator):
    bl_idname = "tree.add_tree"
    bl_label = "Add Tree Mesh Object"
    
    
    def execute(self, context):
        generateTreeBlender()
        tree.applyWind(bpy.context.scene.tree_adjust.wind_strength, windVariation, windChaos)
        
        verts = []
        edges = []
        for i in range(len(tree.branches)):
            branch = tree.branches[i]
            if i == 0:
                verts.append(branch.begin.tolist())
            verts.append(branch.end.tolist())
            
        
        for branch in tree.branches:

            branchEnd = branch.end.tolist()
            branchEndIndex = verts.index(branchEnd)
            
            if branch.parent != None:
                parentEnd = branch.parent.end.tolist()
                parentEndIndex = verts.index(parentEnd)
                edges.append([branchEndIndex, parentEndIndex])
            else:
                branchStart = branch.begin.tolist()
                branchStartIndex = verts.index(branchStart)
                edges.append([branchStartIndex, branchEndIndex])

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None
        
        mesh = bpy.data.meshes.new("Tree")
        obj = bpy.data.objects.new("TreeObject", mesh)
        bpy.context.collection.objects.link(obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        mesh.from_pydata(verts, edges, [])
        
        obj.rotation_euler[0] = 3*pi/2
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
        objSkin = obj.modifiers.new("thickness", 'SKIN')
        
        for i in range(len(obj.data.skin_vertices[0].data)):
            v = obj.data.skin_vertices[0].data[i]
            if i == 0:
                branchLevel = -1
            else:
                branchLevel = tree.branches[i-1].level
            thickness = max(remap(branchLevel, 0, 5, tree.trunkWidth, 1), 1)
            v.radius = [0.01 * thickness, 0.01 * thickness]
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="thickness", report=True)
        
        newLeaves = []
        if bpy.context.scene.tree_adjust.has_leaves == True:
            for leaf in tree.leaves:
                newLeaf = createLeaf(leaf[0], leaf[2], -leaf[1])
                newLeaves.append(newLeaf)
            for leaf in newLeaves:
                leaf.select_set(True)
            obj.select_set(True)
            bpy.ops.object.join()
        
        return {"FINISHED"}
        
        
class RandomizeSeedOperator(bpy.types.Operator):
    bl_idname = "tree.randomize_seed"
    bl_label = "Randomize Tree Seed"
    
    def execute(self, context):
        global seed
        seed += random.randint(0,100)
        return {"FINISHED"}
    
class InitializeValuesOperator(bpy.types.Operator):
    bl_idname = "tree.reset_values"
    bl_label = "Reset Tree Settings"
    
    def execute(self, context):
        bpy.context.scene.tree_adjust.trunk_len = trunkLen
        bpy.context.scene.tree_adjust.trunk_width = trunkWidth
        bpy.context.scene.tree_adjust.min_branching_size = minBranchingSize
        bpy.context.scene.tree_adjust.max_branching_size = maxBranchingSize-minBranchingSize
        bpy.context.scene.tree_adjust.min_num_branch = minNumBranch
        bpy.context.scene.tree_adjust.max_num_branch = maxNumBranch-minNumBranch
        bpy.context.scene.tree_adjust.min_split_angle = minSplitAngle
        bpy.context.scene.tree_adjust.max_split_angle = maxSplitAngle-minSplitAngle
        bpy.context.scene.tree_adjust.max_level = maxLevel

        bpy.context.scene.tree_adjust.wind_strength = 0
        bpy.context.scene.tree_adjust.has_leaves = True
        return {"FINISHED"}
    
class MainPanel(bpy.types.Panel):
    bl_label = "Arbor Barber"
    bl_idname = "PT_ArborBarber"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Arbor Barber'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        treetool = scene.tree_adjust
        
        row = layout.row()
        row.label(text="Add Tree", icon='CUBE')
        row = layout.row()
        row.operator("tree.add_tree")
        row = layout.row()
        row.operator("tree.randomize_seed")
        row = layout.row()
        row.operator("tree.reset_values")

class PanelOptions(bpy.types.Panel):
    bl_label = "Tree Settings"
    bl_idname = "PT_TreeSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tree Settings'
    bl_parent_id = 'PT_ArborBarber'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        treetool = scene.tree_adjust
        
        row = layout.prop(treetool, "trunk_len")
        row = layout.prop(treetool, "trunk_width")
        row = layout.prop(treetool, "min_branching_size")
        row = layout.prop(treetool, "min_num_branch")
        row = layout.prop(treetool, "min_split_angle")
        row = layout.prop(treetool, "max_level")
        row = layout.prop(treetool, "has_leaves")


class PanelVariations(bpy.types.Panel):
    bl_label = "Tree Variation"
    bl_idname = "PT_TreeVariation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tree Variation'
    bl_parent_id = 'PT_ArborBarber'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        treetool = scene.tree_adjust

        row = layout.prop(treetool, "max_branching_size")
        row = layout.prop(treetool, "max_num_branch")
        row = layout.prop(treetool, "max_split_angle")

class PanelWind(bpy.types.Panel):
    bl_label = "Wind Settings"
    bl_idname = "PT_WindSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Wind Settings'
    bl_parent_id = 'PT_ArborBarber'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        treetool = scene.tree_adjust

        row = layout.prop(treetool, "wind_strength")
    
#bpy.context.scene.tree_adjust.trunk_len = trunkLen
#bpy.context.scene.tree_adjust.trunk_width = trunkWidth
#bpy.context.scene.tree_adjust.min_branching_size = minBranchingSize
#bpy.context.scene.tree_adjust.max_branching_size = maxBranchingSize-minBranchingSize
#bpy.context.scene.tree_adjust.min_num_branch = minNumBranch
#bpy.context.scene.tree_adjust.max_num_branch = maxNumBranch-minNumBranch
#bpy.context.scene.tree_adjust.min_split_angle = minSplitAngle
#bpy.context.scene.tree_adjust.max_split_angle = maxSplitAngle-minSplitAngle
#bpy.context.scene.tree_adjust.max_level = maxLevel

#bpy.context.scene.tree_adjust.wind_strength = 0
#bpy.context.scene.tree_adjust.has_leaves = True

classes = [TreeProperties, AddTreeOperator, RandomizeSeedOperator, InitializeValuesOperator, MainPanel, PanelOptions, PanelVariations, PanelWind,]


def register():

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.tree_adjust = bpy.props.PointerProperty(type=TreeProperties)
    print(bpy.types.Scene.tree_adjust)

def unregister():
    
    del bpy.types.Scene.tree_adjust
    for cls in classes:
        bpy.utils.unregister_class(cls)

    
if __name__ == "__main__":
    register()