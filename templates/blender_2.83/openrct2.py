bl_info = {
    "name": "OpenRCT2 Add-on",
    "blender": (2, 83, 0),
    "category": "Object",
}

import bpy
import mathutils
import subprocess
import platform
from math import radians

class OpenRCT2Operator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "objects.openrct2"
    bl_label = "Render"
        
        
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
        ditherThreshold = bpy.context.scene.ditherThreshold
        isAnimation = bpy.context.scene.isAnimation
        
        frameStart = bpy.context.scene.frame_start
        frameEnd = bpy.context.scene.frame_end
        
        #we want to render only one frame if isAnimation is not checked
        if isAnimation == False:
            frameEnd = frameStart
        
        command = ""
        if platform.system() == 'Windows':
            #use powershell
            command = "powershell magick"
        else:
            command = "magick"
            
        #rotate 90 degrees all objects in rig
        for index in range(4):
            #add the no-remap, green layer and purple layers together
            #first, remap the no-remap to the full palette and set hold out for green and purple layers
            bpy.ops.render.render(write_still=not isAnimation, animation=isAnimation, layer="NoRemap1")
            
            for animationFrame in range(frameStart, frameEnd+1):
                paletteFile = bpy.path.abspath("//palettes//WTRCYAN.bmp")
                filePath = bpy.path.abspath("//output//noremap1//Image" + str(animationFrame).zfill(4) + ".png")
                outputPath = bpy.path.abspath("//output//noremap1_" + str(animationFrame) + ".bmp")
                subprocess.run(command + " '" + filePath + "' -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap '" + paletteFile + "' '" + outputPath + "'")
            
            bpy.ops.render.render(write_still=not isAnimation, animation=isAnimation, layer="NoRemap2")
            
            for animationFrame in range(frameStart, frameEnd+1):
                paletteFile = bpy.path.abspath("//palettes//WTRCYAN.bmp")
                filePath = bpy.path.abspath("//output//noremap2//Image" + str(animationFrame).zfill(4) + ".png")
                outputPath = bpy.path.abspath("//output//noremap2_" + str(animationFrame) + ".bmp")
                subprocess.run(command + " '" + filePath + "' -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap '" + paletteFile + "' '" + outputPath + "'")
            
            bpy.ops.render.render(write_still=not isAnimation, animation=isAnimation, layer="Green")
            
            for animationFrame in range(frameStart, frameEnd+1):
                paletteFile = bpy.path.abspath("//palettes//paletteremap1.png")
                filePath = bpy.path.abspath("//output//green//Image" + str(animationFrame).zfill(4) + ".png")
                outputPath = bpy.path.abspath("//output//green" + str(animationFrame) + ".bmp")
                subprocess.run(command + " '" + filePath + "' -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap '" + paletteFile + "' '" + outputPath + "'")
            
            bpy.ops.render.render(write_still=not isAnimation, animation=isAnimation, layer="Purple")
            
            for animationFrame in range(frameStart, frameEnd+1):
                paletteFile = bpy.path.abspath("//palettes//paletteremap2.png")
                filePath = bpy.path.abspath("//output//purple//Image" + str(animationFrame).zfill(4) + ".png")
                outputPath = bpy.path.abspath("//output//purple" + str(animationFrame) + ".bmp")
                subprocess.run(command + " '" + filePath + "' -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap '" + paletteFile + "' '" + outputPath + "'")
            
            #sum those 3 images together
            for animationFrame in range(frameStart, frameEnd+1):
                noRemap1 = bpy.path.abspath("//output//noremap1_" + str(animationFrame) + ".bmp")
                noRemap2 = bpy.path.abspath("//output//noremap2_" + str(animationFrame) + ".bmp")
                green = bpy.path.abspath("//output//green" + str(animationFrame) + ".bmp")
                purple = bpy.path.abspath("//output//purple" + str(animationFrame) + ".bmp")
                outputPath = bpy.path.abspath("//output//" + str(index) + "_" + str(animationFrame) + ".bmp")
                subprocess.run(command + " -compose plus '" + green + "' '" + purple + "' -composite '" + outputPath + "'");
            
                #make sure the green and purple layers are only on the 2 color maps
                paletteFile = bpy.path.abspath("//palettes//purplepink.png")
                filePath = bpy.path.abspath("//output//" + str(index) + "_" + str(animationFrame) + ".bmp")
                outputPath = bpy.path.abspath("//output//" + str(index) + "_" + str(animationFrame) + ".bmp")
                subprocess.run(command + " '" + filePath + "' -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap '" + paletteFile + "' '" + outputPath + "'")
            
                #add the noremap image
                subprocess.run(command + " -compose plus '" + noRemap1 + "' '" + outputPath + "' -composite '" + outputPath + "'");
                subprocess.run(command + " -compose plus '" + noRemap2 + "' '" + outputPath + "' -composite '" + outputPath + "'");
            
            rigOrigin.rotation_euler[2] += radians(90)

        return {'FINISHED'}

class OpenRCT2Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "objects.openrct2"
    bl_idname = "panel.OpenRCT2"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    

    def draw(self, context):
        self.layout.operator("objects.openrct2",text="Render OpenRCT2")
        col = self.layout.column(align = True)
        col.prop(context.scene, "ditherThreshold")
        col.prop(context.scene, "isAnimation")
        


def register():
    bpy.utils.register_class(OpenRCT2Operator)
    bpy.utils.register_class(OpenRCT2Panel)
    bpy.types.Scene.ditherThreshold = bpy.props.FloatProperty(name = "Dithering threshold", 
        description = "This threshold tells how much quantization error to propagate in the dithering process", soft_min=0.0, soft_max=100.0)
    bpy.types.Scene.isAnimation = bpy.props.BoolProperty(name="Animation Toggle")
    

def unregister():
    bpy.utils.unregister_class(OpenRCT2Panel)
    bpy.utils.unregister_class(OpenRCT2Operator)
    del bpy.types.Scene.my_string_prop


if __name__ == "__main__":
    register()