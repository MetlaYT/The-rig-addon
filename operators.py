import os
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
import bpy.utils.previews

preview_collections = {}

def get_asset_path(filename):
    return os.path.join(os.path.dirname(__file__), "assets", filename)

def get_icon(icon_name):
    pcoll = preview_collections.get("main")
    if pcoll and icon_name in pcoll:
        return pcoll[icon_name].icon_id
    return 0

def get_skin_texture_name(rig_name):
    base_name = "Skin_plush.png" if "ThePlush" in rig_name else "Skin.png"
    
    # Check if rig has a number suffix like .001, .002, etc.
    if '.' in rig_name:
        parts = rig_name.rsplit('.', 1)
        if parts[1].isdigit():
            base_name = f"{base_name}.{parts[1]}"
    
    return base_name

def find_rig_mesh(rig):
    return next((c for c in rig.children if c.type == 'MESH'), None)

def find_existing_skin_texture(base_name):
    """Find existing skin texture, including duplicates like .001, .002, etc."""
    # First check if exact name exists
    if base_name in bpy.data.images:
        return bpy.data.images[base_name]
    
    return None

class THRIG_OT_AppendMain(bpy.types.Operator):
    bl_idname = "thrig.append_main"
    bl_label = "THE RIG Main"
    bl_description = "Add THE RIG character to the scene"
    bl_options = {'REGISTER', 'UNDO'}

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

class THSIMPLE_OT_AppendSimple(bpy.types.Operator):
    bl_idname = "thsimple.append_simple"
    bl_label = "THE SIMPLE"
    bl_description = "Add THE SIMPLE character to the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            bpy.ops.wm.append(
                filepath=os.path.join(get_asset_path("TheSimple.blend"), "Collection", "TheSimple(Append)"),
                directory=os.path.join(get_asset_path("TheSimple.blend"), "Collection"),
                filename="TheSimple(Append)"
            )
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

class THCAMERA_OT_AppendCamera(bpy.types.Operator):
    bl_idname = "thcamera.append_camera"
    bl_label = "THE CAMERA"
    bl_description = "Add THE CAMERA to the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            bpy.ops.wm.append(
                filepath=os.path.join(get_asset_path("TheCamera.blend"), "Collection", "TheCamera(Append)"),
                directory=os.path.join(get_asset_path("TheCamera.blend"), "Collection"),
                filename="TheCamera(Append)"
            )
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

class THBUFF_OT_AppendBuff(bpy.types.Operator):
    bl_idname = "thbuff.append_buff"
    bl_label = "THE BUFF"
    bl_description = "Add THE BUFF character to the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            bpy.ops.wm.append(
                filepath=os.path.join(get_asset_path("TheBuff.blend"), "Collection", "TheBufff(Append)"),
                directory=os.path.join(get_asset_path("TheBuff.blend"), "Collection"),
                filename="TheBufff(Append)"
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
            correct_texture_name = get_skin_texture_name(rig.name)
            
            # Find and remove existing texture
            existing_img = find_existing_skin_texture(correct_texture_name)
            if existing_img:
                bpy.data.images.remove(existing_img)
            
            # Load new texture
            img = bpy.data.images.load(skin_path)
            img.name = correct_texture_name
            tex_node.image = img
            
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
            correct_texture_name = get_skin_texture_name(rig.name)
            
            # Find and remove existing texture
            existing_img = find_existing_skin_texture(correct_texture_name)
            if existing_img:
                bpy.data.images.remove(existing_img)
            
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

            # Load new texture
            img = bpy.data.images.load(self.filepath)
            img.name = correct_texture_name
            tex_node.image = img
            
            self.report({'INFO'}, f"Custom skin loaded to {rig.name}!")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load skin: {str(e)}")
            return {'CANCELLED'}

def menu_func_root(self, context):
    self.layout.separator()
    self.layout.operator(THRIG_OT_AppendMain.bl_idname, text="THE RIG", icon_value=get_icon('therigicon'))
    self.layout.operator(THPLUSH_OT_AppendPlush.bl_idname, text="THE PLUSH", icon_value=get_icon('theplushicon'))
    self.layout.operator(THSIMPLE_OT_AppendSimple.bl_idname, text="THE SIMPLE", icon_value=get_icon('thesimpleicon'))
    self.layout.operator(THCAMERA_OT_AppendCamera.bl_idname, text="THE CAMERA", icon='CAMERA_DATA')
    self.layout.operator(THBUFF_OT_AppendBuff.bl_idname, text="THE BUFF", icon_value=get_icon('thebufficon'))

def register():
    pcoll = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")
    
    pcoll.load("therigicon", os.path.join(icons_dir, "therigicon.png"), 'IMAGE')
    pcoll.load("theplushicon", os.path.join(icons_dir, "theplushicon.png"), 'IMAGE')
    pcoll.load("thesimpleicon", os.path.join(icons_dir, "thesimpleicon.png"), 'IMAGE')
    pcoll.load("thebufficon", os.path.join(icons_dir, "TheBuff.png"), 'IMAGE')
    
    preview_collections["main"] = pcoll
    
    bpy.utils.register_class(THRIG_OT_AppendMain)
    bpy.utils.register_class(THPLUSH_OT_AppendPlush)
    bpy.utils.register_class(THSIMPLE_OT_AppendSimple)
    bpy.utils.register_class(THCAMERA_OT_AppendCamera)
    bpy.utils.register_class(THBUFF_OT_AppendBuff)
    bpy.utils.register_class(THRIG_OT_ChangeSkin)
    bpy.utils.register_class(THRIG_OT_LoadCustomSkin)
    bpy.types.VIEW3D_MT_add.append(menu_func_root)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func_root)
    bpy.utils.unregister_class(THRIG_OT_LoadCustomSkin)
    bpy.utils.unregister_class(THRIG_OT_ChangeSkin)
    bpy.utils.unregister_class(THBUFF_OT_AppendBuff)
    bpy.utils.unregister_class(THCAMERA_OT_AppendCamera)
    bpy.utils.unregister_class(THSIMPLE_OT_AppendSimple)
    bpy.utils.unregister_class(THPLUSH_OT_AppendPlush)
    bpy.utils.unregister_class(THRIG_OT_AppendMain)
    
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()