import bpy
from . import operators, ui, updater

bl_info = {
    "name": "The Rig addon",
    "author": "Metla",
    "version": (2, 0, 1),
    "blender": (4, 5, 0),
    "location": "Shift+A > Armature, View3D > Sidebar",
    "description": "An addon to easily use The rig and you can easily use The Plush from the author TheRatmir ",
    "category": "Rigging",
    "warning": "",
    "doc_url": "",
}


def register():
    operators.register()
    ui.register()
    updater.register()
    print("THE RIG addon registered successfully!")


def unregister():
    updater.unregister()
    ui.unregister()
    operators.unregister()


if __name__ == "__main__":
    register()
