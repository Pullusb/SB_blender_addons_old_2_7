# coding: utf-8

bl_info = {
    "name": "Set origin to Bottom",
    "description": "On all selected objects set origin to bottom of bouding box",
    "author": "Samuel Bernou",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "",
    "category": "Object" }
    

import bpy, bmesh
import os
import re, fnmatch, glob
import mathutils
from mathutils import *
C = bpy.context
D = bpy.data
scn = C.scene

def get_align_matrix(location, normal):
    up = Vector((0,0,1))
    angle = normal.angle(up)
    axis = up.cross(normal)
    mat_rot = Matrix.Rotation(angle, 4, axis)
    mat_loc = Matrix.Translation(location)
    mat_align = mat_rot * mat_loc
    return mat_align

def transform_ground_to_world(sc, ground):
    tmpMesh = ground.to_mesh(sc, True, 'PREVIEW')
    tmpMesh.transform(ground.matrix_world)
    tmp_ground = bpy.data.objects.new('tmpGround', tmpMesh)
    sc.objects.link(tmp_ground)
    sc.update()
    return tmp_ground

def get_lowest_world_co_from_mesh(ob, mat_parent=None):
    bme = bmesh.new()
    bme.from_mesh(ob.data)
    mat_to_world = ob.matrix_world.copy()
    if mat_parent:
        mat_to_world = mat_parent * mat_to_world
    lowest=None
    #bme.verts.index_update() #probably not needed
    for v in bme.verts:
        if not lowest:
            lowest = v
        if (mat_to_world * v.co).z < (mat_to_world * lowest.co).z:
            lowest = v
    lowest_co = mat_to_world * lowest.co
    bme.free()
    return lowest_co

def get_lowest_world_co(context, ob, mat_parent=None):
    if ob.type == 'MESH':
        return get_lowest_world_co_from_mesh(ob)

    elif ob.type == 'EMPTY' and ob.dupli_type == 'GROUP':
        if not ob.dupli_group:
            return None

        else:
            lowest_co = None
            for ob_l in ob.dupli_group.objects:
                if ob_l.type == 'MESH':
                    lowest_ob_l = get_lowest_world_co_from_mesh(ob_l, ob.matrix_world)
                    if not lowest_co:
                        lowest_co = lowest_ob_l
                    if lowest_ob_l.z < lowest_co.z:
                        lowest_co = lowest_ob_l

            return lowest_co



def get_lowest_from_bbox(obj):
    mat = obj.matrix_world
    if obj.parent:
        #mat = obj.parent.matrix_world.copy() * mat
        mat = obj.matrix_parent_inverse * mat
    bbox_z = [(mat * Vector(corner))[2] for corner in obj.bound_box]
    #print("bbox_z", bbox_z)#Dbg
    return min(bbox_z)
    #print("bottom", bottom)#Dbg
    
    #if ob.type == 'EMPTY' and ob.dupli_type == 'GROUP':
        
        

'''
def set_origin_to_bottom():
    #DATA WAY 
    for obj in C.selected_objects:
        print(obj.name)
        #get lowest point of bounding box
        #OPt : maybe raycast to the bounding box plane to find intersection (instad of just lowest point)
        bbox_z = [(obj.matrix_world * Vector(corner))[2] for corner in obj.bound_box]
        print("bbox_z", bbox_z)#Dbg
        
        bottom = min(bbox_z)
        print("bottom", bottom)#Dbg
        
        if obj.parent:
            cur_pos = (obj.parent.matrix_world * obj.location)[2]
        else:
            cur_pos = obj.location[2]

        #get differential between this point and origin pt.
        move = bottom - cur_pos
        print("move", move)#Dbg
        movevector = Vector((0,0,move))
        movevectorinverse = Vector((0,0,-move))
        
        movemat = mathutils.Matrix.Translation(movevectorinverse)
        
        #movemat = mathutils.Matrix.Translation(movevectorinverse)
        
        ### change origin and translate mesh to opposite direction with matrix
        
        #obj.data.transform(mathutils.Matrix.Translation(-movevector))#move in local space
        
        
        ## move in local space according to world space
        ##local_mat_move = obj.matrix_world * movemat #dont work
        
        #local_mat_move = obj.convert_space(pose_bone=None, matrix=movemat, from_space='WORLD', to_space='LOCAL')
        
        #### move mesh according to a given matrix
        #obj.data.transform(local_mat_move)
        
        
        #obj.data.transform(obj.convert_space(matrix=movemat, from_space='LOCAL', to_space='WORLD')##NUL#
        obj.data.transform(obj.convert_space(matrix=movemat, from_space='LOCAL', to_space='WORLD'))##NUL#
        #obj.data.transform(obj.convert_space(matrix=movemat, from_space='WORLD', to_space='LOCAL'))#
        
        #obj.data.transform(obj.matrix_local * movemat)
        
        
        #newvector = Vector.cross(movevectorinverse, Vector(obj.rotation_euler) )
        #obj.data.transform(mathutils.Matrix.Translation(newvector))
        
        
        
        
        #how to rotate a vector
        obj.data.update()
        #obj.matrix_world.translation += movevector#move in world space
'''

def set_origin_to_bottom_ops():
    #OPS WAY
    cursor_org = scn.cursor_location
    old_select = [i for i in C.selected_objects]
    old_active = C.scene.objects.active
    selection = [i for i in C.selected_objects if not i.dupli_group]

    for obj in selection:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        print(obj.name)
        
        #get lowest point of bounding box
        #OPt : maybe raycast to the bounding box plane to find intersection (instad of just lowest point)
        
        bottom = get_lowest_from_bbox(obj) 
        #bottom = get_lowest_world_co(bpy.context, obj)[2]
        if obj.parent:
            #cur_pos = (obj.location - obj.parent.location )[2] #(obj.parent.matrix_world * obj.location)[2]
            cur_pos = (obj.matrix_parent_inverse * obj.location)[2]
        else:
            cur_pos = obj.location[2]
        
        #get differential between this point and origin pt.
        move = bottom - cur_pos
        print("move", move)#Dbg
        movevector = Vector((0,0,move))
        
        #set with ops
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.view3d.snap_cursor_to_selected()
        #bpy.ops.object.mode_set(mode='EDIT')#do in object mode
        scn.cursor_location[2] += move
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


    #restore
    scn.cursor_location = cursor_org
    for o in old_select: o.select = True
    C.scene.objects.active = old_active
    del old_select
    del selection
    print('Done')
        
#set_origin_to_bottom_ops()



class OriginToBottom(bpy.types.Operator):
    bl_idname = "object.origin_to_bottom"
    bl_label = "Set origin to bottom"
    bl_description = "Set origin point to bottm of object bouding box"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        set_origin_to_bottom_ops()
        return {"FINISHED"}



'''
class Test_operator_Panel(bpy.types.Panel):
    bl_idname = "test_operator"
    bl_label = "Test Operator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"ù

    def draw(self, context):
        layout = self.layout
        layout.operator('my_operator.test_op')
'''

def OriginToBottomButton(self, context):
    """Origin to bottom panel"""
    layout = self.layout
    layout.operator(OriginToBottom.bl_idname, text = "Set origin to bounding box bottom", icon = '')


def register():
    bpy.utils.register_module(__name__)
    #bpy.types.OBJECT_OT_origin_set.append(OriginToBottomButton)

def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.types.OBJECT_OT_origin_set.remove(OriginToBottomButton)

if __name__ == "__main__":
    register()