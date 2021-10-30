bl_info = {
    "name": "bg images from cam name",
    "description": "set background images on the view according to active camera",
    "author": "Samuel Bernou",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "",
    "category": "Object" }

import bpy, os

def setResolution(context):
    C = context
    try:
        bpy.context.scene.render.resolution_x = C.area.spaces[0].background_images[0].image.size[0]
        bpy.context.scene.render.resolution_y = C.area.spaces[0].background_images[0].image.size[1]
        return 1
    except:
        #print ("no image found in BGimage to define resolution")
        return 0

def setImage(context):
    camset = {"Camera.front" : "Face",
    "Camera.3_4" : "3_4",
    "Camera.side" : "Profil",
    "Camera.back" : "Dos" }

    C = context

    blendloc = bpy.path.abspath('//')
    cam = C.area.spaces[0].camera
    if not cam:
        cam = bpy.context.scene.camera

    print(cam.name)

    if cam.name in camset.keys():
        view = camset[cam.name]
        print (view)

        fp = False
        for root, folders, files in os.walk(blendloc):
            for f in files:
                if os.path.splitext(f)[0].endswith(view):
                # if root.endswith('refs'):
                    fp = os.path.join(root, f)
                    print(fp)
                    break

        if fp:
            if os.path.exists(fp):
                #img = D.images.new(fp,oh_config.BL_OUTPUT_WIDTH,oh_config.BL_OUTPUT_HEIGHT)
                img = bpy.data.images.load(fp, check_existing=True)
                print (img)
                # img.filepath = fp

                C.area.spaces[0].show_background_images = True

                for bgImg in C.area.spaces[0].background_images:
                    C.area.spaces[0].background_images.remove(bgImg)

                bgImg = C.area.spaces[0].background_images.new()
                bgImg.view_axis = 'CAMERA'
                bgImg.draw_depth = 'BACK'
                bgImg.opacity = 1.0
                bgImg.image = img

                bgImg2 = C.area.spaces[0].background_images.new()
                bgImg2.view_axis = 'CAMERA'
                bgImg2.draw_depth = 'FRONT'
                bgImg2.opacity = 0.25
                bgImg2.image = img

                return (1, '')
        else:
            return (0, "no image reference found for view : " + view)

    else:
        print ("cam must be name after the view (in english) like this:", camset)
        return (0, "cam must be name after the view (see console for exemple)")


class bg_image_to_camera(bpy.types.Operator):
    bl_idname = "bgimage.bg_image_to_camera"
    bl_label = "set bg images from camera name"
    bl_description = "load bg according to camera name"
    bl_options = {"REGISTER"}


    def execute(self, context):
        val, message = setImage(context)
        if not val:
            self.report({'ERROR'}, message)
        return {"FINISHED"}

class resolutionFromBGimage(bpy.types.Operator):
    bl_idname = "bgimage.scene_resolution_from_image"
    bl_label = "scene resolution from BG image"
    bl_description = "Set scene resolution according to first backgound image in the 3D view"
    bl_options = {"REGISTER"}


    def execute(self, context):
        val = setResolution(context)
        if not val:
            self.report({'ERROR'}, "no image found in BGimage in current view to define resolution")
        return {"FINISHED"}


class bgimgfromcamera(bpy.types.Panel):
    bl_idname = "bgimgfromcamera"
    bl_label = "Auto BG imgs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"

    def draw(self, context):
        layout = self.layout
        layout.operator("bgimage.bg_image_to_camera", text='load BG img')
        layout.operator("bgimage.scene_resolution_from_image", text='scn resolution from BGimg')


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
