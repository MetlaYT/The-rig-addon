# thebuff_ui.py - UI панели для TheBuff
# RigId: TODO - ожидаем список от Метлы
import bpy

RIG_ID = "TheBuffA"  # Временный ID, заменим позже


class THEBUFF_PT_MainPanel(bpy.types.Panel):
    """Главная панель для TheBuff"""
    bl_label = "TheBuff"
    bl_idname = "THEBUFF_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheBuff"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'ARMATURE':
            return obj.data.get("RigId") == RIG_ID
        return False

    def draw(self, context):
        layout = self.layout
        rig = context.active_object
        layout.label(text=f"Active: {rig.name}", icon='ARMATURE_DATA')


classes = [
    THEBUFF_PT_MainPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
