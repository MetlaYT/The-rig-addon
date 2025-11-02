import os
import bpy

# Папка скинов вне аддона — путь: ~/Documents/TheRigSkins
USER_SKIN_FOLDER = os.path.expanduser("~/Documents/TheRigSkins")

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

        # --- Skin System ---
        box = layout.box()
        box.label(text="Skin System", icon='MATERIAL')

        skin_dir = USER_SKIN_FOLDER
        if os.path.exists(skin_dir):
            for skin in sorted(os.listdir(skin_dir)):
                if skin.lower().endswith(('.png', '.jpg', '.jpeg')):
                    op = box.operator("thrig.change_skin", text=os.path.splitext(skin)[0])
                    op.skin_name = skin
        else:
            box.label(text=f"No skins in: {skin_dir}", icon='ERROR')

        box.operator("thrig.load_custom_skin", icon='FILE_FOLDER')


class THRIG_PT_FaceTogglePanel(bpy.types.Panel):
    bl_label = "Face Toggle"
    bl_idname = "THRIG_PT_face_toggle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rig Tools"

    @classmethod
    def poll(cls, context):
        rig = context.active_object
        return rig and rig.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("thrig.show_face", text="Face", depress=self.is_face_on(context))
        row.operator("thrig.hide_face", text="No Face", depress=not self.is_face_on(context))

    def is_face_on(self, context):
        rig = context.active_object
        if rig and rig.type == 'ARMATURE':
            bone = rig.pose.bones.get("Face Color")
            if bone and "01_Face Off" in bone:
                return bone["01_Face Off"] == 0
        return False


def register():
    bpy.utils.register_class(THRIG_PT_MainPanel)
    bpy.utils.register_class(THRIG_PT_FaceTogglePanel)

def unregister():
    bpy.utils.unregister_class(THRIG_PT_FaceTogglePanel)
    bpy.utils.unregister_class(THRIG_PT_MainPanel)
