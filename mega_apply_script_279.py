import bpy, os

C = bpy.context
scn = C.scene

all = [ob for ob in C.selected_editable_objects]
muser = []
unscale = []
single = []
blacklist = []

def printlist(dispname,li):
    if li:
        print(dispname+ ":")
        for el in li:
            print(el.name)
        print("\n")

#print("*"*12) #Start
bpy.ops.object.select_all(action='SELECT')

cwd = os.path.dirname(bpy.context.blend_data.filepath)
doc = os.path.join(cwd, "muser.txt")

bckdoc = open(doc, 'w')
count = 1
for obj in all:
    if obj.data.users > 1:
        if not obj.data.name in blacklist:
            temp = []
            mesh = obj.data.name
            size = obj.dimensions
            # check if other users have same scale values
            for o in all:
                if o.data.name == mesh and o.dimensions == size:
                    temp.append(o)
                                            
            if len(temp) == obj.data.users:
                bckdoc.write("group" + str(count) + "\n")
                for i in temp:
                    bckdoc.write(i.name + "\n")
                count += 1
                blacklist.append(obj.data.name)
                muser.append(obj)
            else:
                unscale.append(obj)
    else:
        if obj.scale[0] == 1 and obj.scale[1] == 1 and obj.scale[2] == 1:
            print (obj.name, "already at scale 1")
        else:
            single.append(obj)

bckdoc.write("EOF\n")
bckdoc.close()
        
bpy.ops.object.select_all(action='DESELECT')

printlist ("same scaled linked", muser)
printlist ("unscalable", unscale)

printlist ("single-user", single)

if single:
    for s in single:
        s.select = True
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    print ("scale applied on all single-user object")
    
#------------------

bckdoc = open(doc, 'r')
lines = bckdoc.read().splitlines()

def apply(li):
    if li:
        bpy.ops.object.select_all(action='DESELECT')
        for name in li:
            bpy.data.objects[name].select = True
            bpy.context.scene.objects.active = bpy.data.objects[name]
            
        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, texture=False, animation=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.make_links_data(type='OBDATA')

tmp = []
for l in lines:
    if l.startswith("EOF"):
        apply(tmp)
        break
    
    if l.startswith("group"):
        apply(tmp)
        tmp = []
        print ("\n")
        print(l, ">>")

    else:
        print(l)
        tmp.append(l)

bckdoc.close()

if unscale:
    bpy.ops.object.select_all(action='DESELECT')
    print("!!! following linked object (selected) have different scale and have not changed:")
    for i in unscale:
        print(i.name)
        i.select = True
        

print ("finish")