bl_info = {
    "name": "OpenRCT2 Add-on",
    "blender": (2, 83, 0),
    "category": "Object",
}

import bpy
import mathutils
import subprocess
from math import radians

class OpenRCT2Operator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "objects.openrct2"
    bl_label = "Render"

    #@classmethod
    #def poll(cls, context):
        #return 0

    def setHoldout(self, greenMasked, purpleMasked, noRemapMasked):
        holdout = bpy.data.materials.get("HoldOut")
        greenMaterials = []
        for obj in bpy.data.collections["Green"].all_objects:
            objectMaterials = []
            for i in range(len(obj.data.materials)):
                objectMaterials.append(obj.data.materials[i].copy())  
                if greenMasked == True:
                    obj.data.materials[i] = holdout
            greenMaterials.append(objectMaterials)
        
        purpleMaterials = []
        for obj in bpy.data.collections["Purple"].all_objects:
            objectMaterials = []
            for i in range(len(obj.data.materials)):
                objectMaterials.append(obj.data.materials[i].copy())
                if purpleMasked == True:
                    obj.data.materials[i] = holdout
            purpleMaterials.append(objectMaterials)
                    
        noRemapMaterials = []
        for obj in bpy.data.collections["NoRemap"].all_objects:
            objectMaterials = []
            for i in range(len(obj.data.materials)):
                objectMaterials.append(obj.data.materials[i].copy())
                if noRemapMasked == True:
                    obj.data.materials[i] = holdout
            noRemapMaterials.append(objectMaterials)
                    
        return [greenMaterials, purpleMaterials, noRemapMaterials]
    
    def restoreMaterials(self, materials):
        greenMaterials = materials[0]
        purpleMaterials = materials[1]
        noremapMaterials = materials[2]
        
        index = 0
        for obj in bpy.data.collections["Green"].all_objects:
            objectMaterials = greenMaterials[index]
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = objectMaterials[i]
            index = index + 1
        
        index = 0
        for obj in bpy.data.collections["Purple"].all_objects:
            objectMaterials = purpleMaterials[index]
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = objectMaterials[i]
            index = index + 1
        
        index = 0
        for obj in bpy.data.collections["NoRemap"].all_objects:
            objectMaterials = noremapMaterials[index]
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = objectMaterials[i]
            index = index + 1
        
        
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
        
        #rotate 90 degrees all objects in rig
        
        for index in range(4):
            #add the no-remap, green layer and purple layers together
            #first, remap the no-remap to the full palette and set hold out for green and purple layers
            bpy.ops.render.render(write_still=True, layer="NoRemap")
            paletteFile = bpy.path.abspath("//palettes//WTRCYAN.bmp")
            filePath = bpy.path.abspath("//output//noremap//Image0001.png")
            outputPath = bpy.path.abspath("//output//noremap.bmp")
            subprocess.run("powershell magick.exe " + filePath + " -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap " + paletteFile + " " + outputPath)
            
            bpy.ops.render.render(write_still=True, layer="Green")
            paletteFile = bpy.path.abspath("//palettes//paletteremap1.png")
            filePath = bpy.path.abspath("//output//green//Image0001.png")
            outputPath = bpy.path.abspath("//output//green.bmp")
            subprocess.run("powershell magick.exe " + filePath + " -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap " + paletteFile + " " + outputPath)
            
            bpy.ops.render.render(write_still=True, layer="Purple")
            paletteFile = bpy.path.abspath("//palettes//paletteremap2.png")
            filePath = bpy.path.abspath("//output//purple//Image0001.png")
            outputPath = bpy.path.abspath("//output//purple.bmp")
            subprocess.run("powershell magick.exe " + filePath + " -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap " + paletteFile + " " + outputPath)
            
            #sum those 3 images together
            noRemap = bpy.path.abspath("//output//noremap.bmp")
            green = bpy.path.abspath("//output//green.bmp")
            purple = bpy.path.abspath("//output//purple.bmp")
            outputPath = bpy.path.abspath("//output//" + str(index) + ".bmp")
            subprocess.run("powershell magick.exe -compose add " + green + " " + purple + " -composite " + outputPath);
            
            #make sure the green and purple layers are only on the 2 color maps
            paletteFile = bpy.path.abspath("//palettes//purplepink.png")
            filePath = bpy.path.abspath("//output//" + str(index) + ".bmp")
            outputPath = bpy.path.abspath("//output//" + str(index) + ".bmp")
            subprocess.run("powershell magick.exe " + filePath + " -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap " + paletteFile + " " + outputPath)
            
            #add the noremap image
            subprocess.run("powershell magick.exe -compose add " + noRemap + " " + outputPath + " -composite " + outputPath);
            
            #make sure that the image is mapped in the rct2 palette
            paletteFile = bpy.path.abspath("//palettes//palette.png")
            filePath = bpy.path.abspath("//output//" + str(index) + ".bmp")
            outputPath = bpy.path.abspath("//output//" + str(index) + ".bmp")
            #subprocess.run("powershell magick.exe " + filePath + " -dither FloydSteinberg -define dither:diffusion-amount=" + str(ditherThreshold) + "% -remap " + paletteFile + " " + outputPath)
            
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
        


def register():
    bpy.utils.register_class(OpenRCT2Operator)
    bpy.utils.register_class(OpenRCT2Panel)
    bpy.types.Scene.ditherThreshold = bpy.props.FloatProperty(name = "Dithering threshold", description = "This threshold tells how much quantization error to propagate in the dithering process", soft_min=0.0, soft_max=100.0)

def unregister():
    bpy.utils.unregister_class(OpenRCT2Panel)
    bpy.utils.unregister_class(OpenRCT2Operator)
    del bpy.types.Scene.my_string_prop


if __name__ == "__main__":
    register()