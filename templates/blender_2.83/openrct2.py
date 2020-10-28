bl_info = {
    "name": "OpenRCT2 Add-on",
    "blender": (2, 83, 0),
    "category": "Object",
}

import bpy
import mathutils
import subprocess
from math import radians

class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "objects.test"
    bl_label = "Render"

    #@classmethod
    #def poll(cls, context):
        #return 0

    def execute(self, context):
        #set the output path
        
        #set the cursor at the center of the world
        bpy.context.scene.cursor.location = mathutils.Vector((0,0,0))
        
        #find the origin object
        collection = bpy.data.collections['Rig']
        rigOrigin = collection.all_objects['RigOrigin']
        
        outputPath = bpy.path.abspath("//output//")
        palette = bpy.path.abspath("//palettes//")
        paletteFile = palette + "WTRCYAN.bmp"
        renders = []
        
        
        #rotate 90 degrees all objects in rig
        for index in range(4):
            bpy.data.scenes[0].render.filepath = bpy.path.abspath("//output//" + "render" + str(index) + ".png")
            if context.scene.renderBox == True:
                bpy.ops.render.render(write_still=True)
            rigOrigin.rotation_euler[2] += radians(90)
            renders.append(bpy.data.scenes[0].render.filepath)
        
        for index in range(4):
            filePath = outputPath + str(index) + ".png"
            testPath = outputPath + "test" + str(index) + ".png"
            mask = outputPath + "mask.png"
            outputFile = outputPath + str(index) + ".bmp"
            
            args = []
            subprocess.run("powershell magick.exe " + renders[index] + " -background 'sRGB(57,59,57)' -alpha Extract " + mask)
            
            args = []
            subprocess.run("powershell magick.exe " + renders[index] + " -background 'sRGB(57,59,57)' -alpha Background " + filePath)
            
            args = []
            subprocess.run("powershell magick.exe convert " + mask + " -threshold " + context.scene.my_string_prop + "% " + mask)
            
            args = []
            subprocess.run("powershell magick.exe convert " + filePath + " -fill 'sRGB(57,59,57)' -draw 'color 1,1 reset' " + testPath)
            
            #subprocess.run("powershell magick.exe composite -compose src-over " + filePath + " " + testPath + " " + filePath)
            subprocess.run("powershell magick.exe composite -compose src-over " + filePath + " " + testPath + " " + filePath)
            subprocess.run("powershell magick.exe composite -compose multiply " + mask + " " + filePath + " " + filePath)

            
            args = []
            subprocess.run("powershell magick.exe " + filePath + " -fuzz 0% -opaque 'sRGB(57,59,57)' " + filePath)
            
            args = []
            args.append("magick.exe")
            args.append(filePath)
            args.append("-trim")
            args.append("-dither")
            args.append("FloydSteinberg")
            args.append("-define")
            args.append("dither:diffusion-amount=30%")
            args.append("-remap")
            args.append(paletteFile)
            args.append(outputFile)
            subprocess.call(args)
            
            
        return {'FINISHED'}

class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "OpenRCT2 Render"
    bl_idname = "panel.OpenRCT2"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    

    def draw(self, context):
        self.layout.operator("objects.test",text="Render OpenRCT2")
        col = self.layout.column(align = True)
        col.prop(context.scene, "my_string_prop")
        col.prop(context.scene, "renderBox")
        


def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_class(HelloWorldPanel)
    bpy.types.Scene.my_string_prop = bpy.props.StringProperty(name = "Alpha threshold", description = "This threshold determines how much the transparent pixels are cut out", default = "5")
    bpy.types.Scene.renderBox = bpy.props.BoolProperty(name = "Render", default=True)

def unregister():
    bpy.utils.unregister_class(HelloWorldPanel)
    bpy.utils.unregister_class(SimpleOperator)
    del bpy.types.Scene.my_string_prop


if __name__ == "__main__":
    register()