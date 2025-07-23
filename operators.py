import os
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

def get_asset_path(filename):
    return os.path.join(os.path.dirname(__file__), "assets", filename)

def get_skin_texture_name(rig_name):
    return "Skin" if "TheRig" in rig_name else "Skin_plush.png"

def find_rig_mesh(rig):
    return next((c for c in rig.children if c.type == 'MESH'), None)

class THRIG_OT_AppendMain(bpy.types.Operator):
    bl_idname = "thrig.append_main"
    bl_label = "THE RIG Main"
    bl_description = "Add THE RIG character to the scene"
    bl_options = {'REGISTER', 'UNDO'}
    bl_icon = 'OUTLINER_OB_ARMATURE'

    def execute(self, context):
        try:
            bpy.ops.wm.append(
                filepath=os.path.join(get_asset_path("TheRig.blend"), "Collection", "TheRig(Append)"),
                directory=os.path.join(get_asset_path("TheRig.blend"), "Collection"),
                filename="TheRig(Append)"
            )
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

class THPLUSH_OT_AppendPlush(bpy.types.Operator):
    bl_idname = "thplush.append_plush"
    bl_label = "THE PLUSH"
    bl_description = "Add THE PLUSH character to the scene"
    bl_options = {'REGISTER', 'UNDO'}
    bl_icon = 'OUTLINER_OB_ARMATURE'

    def execute(self, context):
        try:
            bpy.ops.wm.append(
                filepath=os.path.join(get_asset_path("ThePlush.blend"), "Collection", "ThePlush(Append)"),
                directory=os.path.join(get_asset_path("ThePlush.blend"), "Collection"),
                filename="ThePlush(Append)"
            )
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

class THRIG_OT_ChangeSkin(bpy.types.Operator):
    bl_idname = "thrig.change_skin"
    bl_label = "Change Skin"
    bl_options = {'REGISTER', 'UNDO'}
    skin_name: StringProperty(name="Skin Name", default="")

    def execute(self, context):
        rig = context.active_object
        body = find_rig_mesh(rig)
        if not body:
            self.report({'ERROR'}, "Body mesh not found!")
            return {'CANCELLED'}

        mat = body.data.materials[0] if body.data.materials else None
        if not mat:
            mat = bpy.data.materials.new(name="MinecraftSkin")
            body.data.materials.append(mat)

        mat.use_nodes = True
        tex_node = next((n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'), None)
        if not tex_node:
            tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            if bsdf := mat.node_tree.nodes.get('Principled BSDF'):
                mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])

        skin_path = os.path.join(os.path.dirname(__file__), "skins", self.skin_name)
        if os.path.exists(skin_path):
            tex_node.image = bpy.data.images.load(skin_path)
            self.report({'INFO'}, f"Skin applied to {rig.name}!")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Skin file not found: {self.skin_name}")
            return {'CANCELLED'}

class THRIG_OT_LoadCustomSkin(bpy.types.Operator, ImportHelper):
    bl_idname = "thrig.load_custom_skin"
    bl_label = "Load Custom Skin"
    bl_options = {'REGISTER', 'UNDO'}
    filter_glob: StringProperty(default='*.png;*.jpg;*.jpeg', options={'HIDDEN'})

    def execute(self, context):
        rig = context.active_object
        body = find_rig_mesh(rig)
        if not body:
            self.report({'ERROR'}, "Body mesh not found!")
            return {'CANCELLED'}

        try:
            img = bpy.data.images.load(self.filepath)
            mat = body.data.materials[0] if body.data.materials else None
            if not mat:
                mat = bpy.data.materials.new(name="MinecraftSkin")
                body.data.materials.append(mat)

            mat.use_nodes = True
            tex_node = next((n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'), None)
            if not tex_node:
                tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                if bsdf := mat.node_tree.nodes.get('Principled BSDF'):
                    mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])

            tex_node.image = img
            self.report({'INFO'}, f"Custom skin loaded to {rig.name}!")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load skin: {str(e)}")
            return {'CANCELLED'}

def menu_func_armature(self, context):
    self.layout.operator(THRIG_OT_AppendMain.bl_idname, icon='OUTLINER_OB_ARMATURE')
    self.layout.operator(THPLUSH_OT_AppendPlush.bl_idname, icon='OUTLINER_OB_ARMATURE')

def menu_func_root(self, context):
    self.layout.separator()
    self.layout.operator(THRIG_OT_AppendMain.bl_idname, text="THE RIG", icon='OUTLINER_OB_ARMATURE')
    self.layout.operator(THPLUSH_OT_AppendPlush.bl_idname, text="THE PLUSH", icon='OUTLINER_OB_ARMATURE')

def register():
    bpy.utils.register_class(THRIG_OT_AppendMain)
    bpy.utils.register_class(THPLUSH_OT_AppendPlush)
    bpy.utils.register_class(THRIG_OT_ChangeSkin)
    bpy.utils.register_class(THRIG_OT_LoadCustomSkin)
    bpy.types.VIEW3D_MT_armature_add.append(menu_func_armature)
    bpy.types.VIEW3D_MT_add.append(menu_func_root)

def unregister():
    bpy.types.VIEW3D_MT_armature_add.remove(menu_func_armature)
    bpy.types.VIEW3D_MT_add.remove(menu_func_root)
    bpy.utils.unregister_class(THRIG_OT_LoadCustomSkin)
    bpy.utils.unregister_class(THRIG_OT_ChangeSkin)
    bpy.utils.unregister_class(THPLUSH_OT_AppendPlush)
    bpy.utils.unregister_class(THRIG_OT_AppendMain)