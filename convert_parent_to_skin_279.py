# coding: utf-8
import bpy
import os
import re, fnmatch, glob
from mathutils import Vector
C = bpy.context
D = bpy.data
scn = C.scene

def VertexGroupToBone(ob, targetRig, targetBone, context):
    '''
    Add a vertex group to the object named afer the given bone
    assign full weight to this vertex group
    return a list of bypassed object (due to vertex group already existed)
    '''

    #if the vertex group related to the chosen bone is'nt here, create i and Skin parent (full weight)
    if not targetBone in [i.name for i in ob.vertex_groups]:
        vg = ob.vertex_groups.new(name=targetBone)

    else: #vertex group exist, or weight it (leave it untouched ?)
        vg = ob.vertex_groups[targetBone]

    verts = [i.index for i in ob.data.vertices]
    vg.add(verts, 1, "ADD")


def CreateArmatureModifier(ob, targetRig):
    '''
    Create armature modifier if necessary and place it on top of stack
    or just after the first miror modifier
    return a list of bypassed objects
    '''

    #get object from armature data with a loop (only way to get armature's owner)
    for obArm in bpy.data.objects:
        if obArm.type == 'ARMATURE' and obArm.data.name == targetRig:
            ArmatureObject = obArm

    #add armature modifier that points to designated rig:
    if not 'ARMATURE' in [m.type for m in ob.modifiers]:
        mod = ob.modifiers.new('Armature', 'ARMATURE')
        mod.object = ArmatureObject#bpy.data.objects[targetRig]

        #bring Armature modifier to the top of the stack
        pos = 1
        if 'MIRROR' in [m.type for m in ob.modifiers]:
            #if mirror, determine it's position
            for mod in ob.modifiers:
                if mod.type == 'MIRROR':
                    pos += 1
                    break
                else:
                    pos += 1

        if len(ob.modifiers) > 1:
            for i in range(len(ob.modifiers) - pos):
                bpy.ops.object.modifier_move_up(modifier="Armature")

    else: #armature already exist
        for m in ob.modifiers:
            if m.type == 'ARMATURE':
                m.object = ArmatureObject#bpy.data.objects[targetRig]


keep_transform = 1

print('-'*5)
for ob in bpy.context.selected_objects:
    if ob.parent:
        print("ob has parent", ob.parent.name)
        targetRig = ob.parent.data.name
        if ob.parent_type == 'BONE':
            print("is bone parented to")
            if ob.parent_bone:
                targetBone = ob.parent_bone
                print("ob.parent_bone", ob.parent_bone)#Dbg

                if keep_transform:
                    #Clear and keep transform (matrix reattribution)
                    matrixcopy = ob.matrix_world.copy()
                    ob.parent = None
                    ob.matrix_world = matrixcopy
                else:
                    ob.parent = None

                #replace by armature
                CreateArmatureModifier(ob, targetRig)
                VertexGroupToBone(ob, targetRig, targetBone, bpy.context)