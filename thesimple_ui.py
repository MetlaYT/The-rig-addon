# thesimple_ui.py - UI панели для TheSimple
# RigId: TODO - ожидаем список от Метлы
import bpy

RIG_ID = "TheSimpleA"  # Временный ID, заменим позже


class THESIMPLE_PT_MainPanel(bpy.types.Panel):
    """Главная панель для TheSimple"""
    bl_label = "TheSimple"
    bl_idname = "THESIMPLE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'ARMATURE':
            return obj.data.get("RigId") == RIG_ID
        return False

    def draw(self, context):
        layout = self.layout
        layout.label(text="Coming soon...", icon='INFO')


classes = [
    THESIMPLE_PT_MainPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
