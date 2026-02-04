import bpy
from . import operators, ui, updater, custom_rigs

bl_info = {
    "name": "The Rig addon",
    "author": "Metla",
    "version": (2, 1, 0),
    "blender": (4, 5, 0),
    "location": "Shift+A > Armature, View3D > Sidebar",
    "description": "An addon to easily use The rig and you can easily use The Plush from the author TheRatmir ",
    "category": "Rigging",
    "warning": "",
    "doc_url": "",
}


class THRIG_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    def draw(self, context):
        layout = self.layout
        
        custom_rigs.draw_custom_rigs_panel(self, context)


def register():
    bpy.utils.register_class(THRIG_AddonPreferences)
    operators.register()
    ui.register()
    updater.register()
    custom_rigs.register()
    print("THE RIG addon registered successfully!")


def unregister():
    custom_rigs.unregister()
    updater.unregister()
    ui.unregister()
    operators.unregister()
    bpy.utils.unregister_class(THRIG_AddonPreferences)


if __name__ == "__main__":
    register()
