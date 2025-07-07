import os
import bpy

class THRIG_PT_MainPanel(bpy.types.Panel):
    bl_label = "THE RIG Tools"
    bl_idname = "THRIG_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rig Tools"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and any(x in obj.name for x in ['TheRig', 'ThePlush'])

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        layout.label(text=f"Active: {obj.name}", icon='ARMATURE_DATA')
        
        box = layout.box()
        box.label(text="Skin System", icon='MATERIAL')
        
        skin_dir = os.path.join(os.path.dirname(__file__), "skins")
        if os.path.exists(skin_dir):
            for skin in sorted(os.listdir(skin_dir)):
                if skin.lower().endswith(('.png', '.jpg', '.jpeg')):
                    op = box.operator("thrig.change_skin", text=os.path.splitext(skin)[0])
                    op.skin_name = skin
        else:
            box.label(text="No skins folder found!", icon='ERROR')
        
        box.operator("thrig.load_custom_skin", icon='FILE_FOLDER')

def register():
    bpy.utils.register_class(THRIG_PT_MainPanel)

def unregister():
    bpy.utils.unregister_class(THRIG_PT_MainPanel)