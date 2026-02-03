import bpy

RIG_ID = "TheCameraCA"


def is_this_rig(context):
    obj = context.active_object
    if obj and obj.type == 'ARMATURE':
        return obj.data.get("RigId") == RIG_ID
    return False


def get_camera_settings_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Camera Settings")
    return None


class THECAMERA_PT_MainPanel(bpy.types.Panel):
    bl_label = "TheCamera"
    bl_idname = "THECAMERA_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheCamera"

    @classmethod
    def poll(cls, context):
        return is_this_rig(context)

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="TheCamera", icon='CAMERA_DATA')
        box.label(text="Author: TheRatmir")
        box.operator("wm.url_open", text="Portfolio", icon='URL').url = "https://theratmir.github.io/TheRatmir-Portfolio/"


class THECAMERA_PT_SettingsPanel(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "THECAMERA_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheCamera"
    bl_parent_id = "THECAMERA_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_camera_settings_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_camera_settings_bone(context)
        
        if not bone:
            layout.label(text="Camera Settings bone not found", icon='ERROR')
            return
        
        if "01_Passepartout" in bone:
            layout.prop(bone, '["01_Passepartout"]', text="Passepartout")
        if "02_Thirds" in bone:
            layout.prop(bone, '["02_Thirds"]', text="Thirds")
        if "03_Center" in bone:
            layout.prop(bone, '["03_Center"]', text="Center")
        if "04_Depth of Field" in bone:
            layout.prop(bone, '["04_Depth of Field"]', text="Depth of Field")
        if "05_F-Stop" in bone:
            layout.prop(bone, '["05_F-Stop"]', text="F-Stop")


classes = [
    THECAMERA_PT_MainPanel,
    THECAMERA_PT_SettingsPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
