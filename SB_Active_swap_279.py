'''
Copyright (C) 2016 Samuel B
bernou.samuel@gmail.com

Created by Samuel B

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Active swap",
    "description": "allow to iterate active object over selected with shortcuts (shift+`: next, ctrl+shift+` : prev)",
    "author": "Samuel Bernou",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }

import bpy

def AS_SwapObject(state):
    '''swap Active object to next or previous according to parameter (1 or -1)'''
    
    ###control > what to do if only one object selected
    ###find selection order (selection history)
    if bpy.context.selected_objects: 
        if len(bpy.context.selected_objects) == 1:
            print("only one object selected (needs at least two to swap active)")
        else:
            #objs = bpy.context.selected_objects
            #act = bpy.context.active_object
            #pos =  objs.index(act)
            #bpy.context.scene.objects.active = objs[(pos+1) % len(objs)]
            bpy.context.scene.objects.active = bpy.context.selected_objects[\
            (bpy.context.selected_objects.index(bpy.context.active_object)+state) % len(bpy.context.selected_objects)]
     
    else:
        print("no object selected")
    
    

class AS_ActiveNext(bpy.types.Operator):
    bl_idname = "view3d.as_active_next"
    bl_label = "Active Next"
    bl_description = "Active next object in selection"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        AS_SwapObject(1)
        return {"FINISHED"}


class AS_ActivePrev(bpy.types.Operator):
    bl_idname = "view3d.as_active_prev"
    bl_label = "Active Prev"
    bl_description = "Active previous object in selection"
    bl_options = {"REGISTER"}
 
    @classmethod
    def poll(cls, context):
        return True
 
    def execute(self, context):
        AS_SwapObject(-1)
        return {"FINISHED"}

###---keymap---------------

addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    kmi = km.keymap_items.new("view3d.as_active_next", type = "ACCENT_GRAVE", value = "PRESS", shift = True)
    kmi = km.keymap_items.new("view3d.as_active_prev", type = "ACCENT_GRAVE", value = "PRESS", shift = True, ctrl = True)
    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


###---register--------------

def register():
    register_keymaps()
    bpy.utils.register_module(__name__)

def unregister():
    unregister_keymaps()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
