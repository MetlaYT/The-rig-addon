# theplush_ui.py - UI panels for ThePlush
import bpy
import os
import tempfile
import urllib.request
from bpy_extras.io_utils import ImportHelper

# RigId for this file
RIG_ID = "ThePlushA"
SKIN_TEXTURE_NAME = "Skin_plush"  # Base name for plush skin texture


def is_this_rig(context):
    """Check if active object is the correct rig by RigId"""
    obj = context.active_object
    if obj and obj.type == 'ARMATURE':
        return obj.data.get("RigId") == RIG_ID
    return False


def get_icon(icon_name):
    """Get icon from preview collection"""
    from . import operators
    return operators.get_icon(icon_name)


def find_skin_texture(rig):
    """Find skin texture for this rig"""
    for child in rig.children:
        if child.type == 'MESH':
            for mat in child.data.materials:
                if mat and mat.use_nodes:
                    for node in mat.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            if SKIN_TEXTURE_NAME in node.image.name or "Skin" in node.image.name:
                                return node.image
    return None


def count_rigs_using_texture(texture):
    """Count how many rigs use this texture"""
    count = 0
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and obj.data.get("RigId") == RIG_ID:
            tex = find_skin_texture(obj)
            if tex and tex == texture:
                count += 1
    return count


def protect_texture_if_shared(rig, texture):
    """Make a copy if texture is shared between multiple rigs"""
    if count_rigs_using_texture(texture) > 1:
        new_texture = texture.copy()
        new_texture.name = f"{SKIN_TEXTURE_NAME}_{rig.name}"
        for child in rig.children:
            if child.type == 'MESH':
                for mat in child.data.materials:
                    if mat and mat.use_nodes:
                        for node in mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image == texture:
                                node.image = new_texture
        return new_texture
    return texture


def convert_skin_64_to_56(source, target):
    """Convert 64x64 Minecraft skin to 56x56 plush skin
    
    Based on converter.html logic:
    - Top region (0,0 - 64x16) -> scaled to (0,0 - 56x14)
    - Bottom region (0,16 - 64x48) -> scaled to (0,14 - 32x24)
    """
    src_w, src_h = 64, 64
    tgt_w, tgt_h = target.size[0], target.size[1]
    
    src_pixels = list(source.pixels[:])
    tgt_pixels = list(target.pixels[:])
    
    def get_src_pixel(x, y):
        blender_y = src_h - 1 - y
        idx = (blender_y * src_w + x) * 4
        return src_pixels[idx:idx+4]
    
    def set_tgt_pixel(x, y, rgba):
        blender_y = tgt_h - 1 - y
        idx = (blender_y * tgt_w + x) * 4
        for i in range(4):
            tgt_pixels[idx + i] = rgba[i]
    
    def scale_and_draw(src_x, src_y, src_w_r, src_h_r, dst_x, dst_y, dst_w, dst_h):
        for dy in range(dst_h):
            for dx in range(dst_w):
                sx = int(((dx + 0.5) * src_w_r) / dst_w)
                sy = int(((dy + 0.5) * src_h_r) / dst_h)
                sx = min(sx, src_w_r - 1)
                sy = min(sy, src_h_r - 1)
                pixel = get_src_pixel(src_x + sx, src_y + sy)
                set_tgt_pixel(dst_x + dx, dst_y + dy, pixel)
    
    scale_and_draw(0, 0, 64, 16, 0, 0, 56, 14)
    scale_and_draw(0, 16, 64, 48, 0, 14, 32, 24)
    
    target.pixels[:] = tgt_pixels
    target.update()


def apply_skin_auto(rig, texture, source_image, report_func):
    """Auto-detect skin format and apply (convert if needed)"""
    src_w, src_h = source_image.size[0], source_image.size[1]
    tgt_w, tgt_h = texture.size[0], texture.size[1]
    
    # Same size - direct copy
    if src_w == tgt_w and src_h == tgt_h:
        texture.pixels[:] = source_image.pixels[:]
        texture.update()
        report_func({'INFO'}, f"Skin applied to {rig.name}!")
        return True
    
    # 64x64 source - need to convert
    if src_w == 64 and src_h == 64:
        convert_skin_64_to_56(source_image, texture)
        report_func({'INFO'}, f"Skin converted and applied to {rig.name}!")
        return True
    
    # Unknown format
    report_func({'ERROR'}, f"Unsupported skin size: {src_w}x{src_h}. Expected 64x64 or {tgt_w}x{tgt_h}")
    return False


# ===== SKIN CHANGE OPERATOR =====
class THEPLUSH_OT_ChangeSkin(bpy.types.Operator, ImportHelper):
    """Change skin texture (auto-converts 64x64 to plush format)"""
    bl_idname = "theplush.change_skin"
    bl_label = "Change Skin"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: bpy.props.StringProperty(default='*.png;*.jpg;*.jpeg', options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return is_this_rig(context)
    
    def execute(self, context):
        rig = context.active_object
        texture = find_skin_texture(rig)
        
        if not texture:
            self.report({'ERROR'}, "No skin texture found on rig!")
            return {'CANCELLED'}
        
        texture = protect_texture_if_shared(rig, texture)
        
        try:
            new_image = bpy.data.images.load(self.filepath)
            
            if apply_skin_auto(rig, texture, new_image, self.report):
                bpy.data.images.remove(new_image)
                return {'FINISHED'}
            else:
                bpy.data.images.remove(new_image)
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load image: {str(e)}")
            return {'CANCELLED'}


# ===== DOWNLOAD SKIN BY USERNAME =====
class THEPLUSH_OT_DownloadSkin(bpy.types.Operator):
    """Download skin by Minecraft username (auto-converts to plush format)"""
    bl_idname = "theplush.download_skin"
    bl_label = "Download Skin by Username"
    bl_options = {'REGISTER', 'UNDO'}
    
    username: bpy.props.StringProperty(
        name="Username",
        description="Minecraft username",
        default=""
    )
    
    @classmethod
    def poll(cls, context):
        return is_this_rig(context)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "username", text="Username")
    
    def execute(self, context):
        if not self.username:
            self.report({'ERROR'}, "Please enter a username!")
            return {'CANCELLED'}
        
        rig = context.active_object
        texture = find_skin_texture(rig)
        
        if not texture:
            self.report({'ERROR'}, "No skin texture found on rig!")
            return {'CANCELLED'}
        
        texture = protect_texture_if_shared(rig, texture)
        
        url = f"https://minotar.net/skin/{self.username}"
        
        try:
            temp_path = os.path.join(tempfile.gettempdir(), f"{self.username}_skin.png")
            urllib.request.urlretrieve(url, temp_path)
            
            new_image = bpy.data.images.load(temp_path)
            
            if apply_skin_auto(rig, texture, new_image, self.report):
                bpy.data.images.remove(new_image)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return {'FINISHED'}
            else:
                bpy.data.images.remove(new_image)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to download skin: {str(e)}")
            return {'CANCELLED'}


class THEPLUSH_PT_MainPanel(bpy.types.Panel):
    """Main panel for ThePlush"""
    bl_label = "ThePlush"
    bl_idname = "THEPLUSH_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ThePlush"

    @classmethod
    def poll(cls, context):
        return is_this_rig(context)

    def draw(self, context):
        layout = self.layout
        
        # Info
        box = layout.box()
        icon_id = get_icon('theplushicon')
        if icon_id:
            box.label(text="ThePlush", icon_value=icon_id)
        else:
            box.label(text="ThePlush", icon='ARMATURE_DATA')
        box.label(text="Author: TheRatmir")
        box.operator("wm.url_open", text="Portfolio", icon='URL').url = "https://theratmir.github.io/TheRatmir-Portfolio/"


# ===== SKIN PANEL =====
class THEPLUSH_PT_SkinPanel(bpy.types.Panel):
    """Skin settings panel"""
    bl_label = "Skin"
    bl_idname = "THEPLUSH_PT_skin"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ThePlush"
    bl_parent_id = "THEPLUSH_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context)

    def draw(self, context):
        layout = self.layout
        rig = context.active_object
        
        texture = find_skin_texture(rig)
        if texture:
            layout.label(text=f"Current: {texture.name}", icon='TEXTURE')
            layout.operator("theplush.change_skin", text="Change Skin", icon='FILE_IMAGE')
            layout.operator("theplush.download_skin", text="Download by Username", icon='URL')
        else:
            layout.label(text="No skin texture found", icon='ERROR')


classes = [
    THEPLUSH_OT_ChangeSkin,
    THEPLUSH_OT_DownloadSkin,
    THEPLUSH_PT_MainPanel,
    THEPLUSH_PT_SkinPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
