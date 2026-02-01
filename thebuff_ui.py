import bpy
import os
import tempfile
import urllib.request
from bpy_extras.io_utils import ImportHelper

RIG_ID = "TheBuffA"
SKIN_TEXTURE_NAME = "Skin_buff"


def is_this_rig(context):
    obj = context.active_object
    if obj and obj.type == 'ARMATURE':
        return obj.data.get("RigId") == RIG_ID
    return False


def get_r_arm_settings_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("R_Arm_Settings")
    return None


def get_l_arm_settings_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("L_Arm_Settings")
    return None


def get_r_leg_settings_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("R_Leg_Settings")
    return None


def get_l_leg_settings_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("L_Leg_Settings")
    return None


def get_icon(icon_name):
    from . import operators
    return operators.get_icon(icon_name)


def find_skin_texture(rig):
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
    count = 0
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and obj.data.get("RigId") == RIG_ID:
            tex = find_skin_texture(obj)
            if tex and tex == texture:
                count += 1
    return count


def protect_texture_if_shared(rig, texture):
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


def apply_skin_direct(rig, texture, source_image, report_func):
    src_w, src_h = source_image.size[0], source_image.size[1]
    tgt_w, tgt_h = texture.size[0], texture.size[1]
    
    if src_w == tgt_w and src_h == tgt_h:
        texture.pixels[:] = source_image.pixels[:]
        texture.update()
        report_func({'INFO'}, f"Skin applied to {rig.name}!")
        return True
    
    report_func({'ERROR'}, f"Skin size mismatch! Expected {tgt_w}x{tgt_h}, got {src_w}x{src_h}")
    return False


class THEBUFF_OT_ChangeSkin(bpy.types.Operator, ImportHelper):
    bl_idname = "thebuff.change_skin"
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
            
            if apply_skin_direct(rig, texture, new_image, self.report):
                bpy.data.images.remove(new_image)
                return {'FINISHED'}
            else:
                bpy.data.images.remove(new_image)
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load image: {str(e)}")
            return {'CANCELLED'}


class THEBUFF_OT_DownloadSkin(bpy.types.Operator):
    bl_idname = "thebuff.download_skin"
    bl_label = "Download Skin by Username"
    bl_options = {'REGISTER', 'UNDO'}
    
    username: bpy.props.StringProperty(name="Username", description="Minecraft username", default="")
    
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
            
            if apply_skin_direct(rig, texture, new_image, self.report):
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


class THEBUFF_PT_MainPanel(bpy.types.Panel):
    bl_label = "TheBuff"
    bl_idname = "THEBUFF_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheBuff"

    @classmethod
    def poll(cls, context):
        return is_this_rig(context)

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        icon_id = get_icon('thebufficon')
        if icon_id:
            box.label(text="TheBuff", icon_value=icon_id)
        else:
            box.label(text="TheBuff", icon='ARMATURE_DATA')
        box.label(text="Author: TheRatmir")
        box.operator("wm.url_open", text="Portfolio", icon='URL').url = "https://theratmir.github.io/TheRatmir-Portfolio/"


class THEBUFF_PT_SkinPanel(bpy.types.Panel):
    bl_label = "Skin"
    bl_idname = "THEBUFF_PT_skin"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheBuff"
    bl_parent_id = "THEBUFF_PT_main"
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
            layout.operator("thebuff.change_skin", text="Change Skin", icon='FILE_IMAGE')
            layout.operator("thebuff.download_skin", text="Download by Username", icon='URL')
        else:
            layout.label(text="No skin texture found", icon='ERROR')


class THEBUFF_PT_ArmsPanel(bpy.types.Panel):
    bl_label = "Arms"
    bl_idname = "THEBUFF_PT_arms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheBuff"
    bl_parent_id = "THEBUFF_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and (get_r_arm_settings_bone(context) or get_l_arm_settings_bone(context))

    def draw(self, context):
        layout = self.layout
        r_bone = get_r_arm_settings_bone(context)
        l_bone = get_l_arm_settings_bone(context)
        
        row = layout.row()
        row.label(text="Right", icon='LOOP_FORWARDS')
        row.label(text="Left", icon='LOOP_BACK')
        
        layout.separator()
        
        row = layout.row(align=True)
        if r_bone and "FK/IK" in r_bone:
            row.prop(r_bone, '["FK/IK"]', text="FK/IK")
        if l_bone and "FK/IK" in l_bone:
            row.prop(l_bone, '["FK/IK"]', text="FK/IK")


class THEBUFF_PT_LegsPanel(bpy.types.Panel):
    bl_label = "Legs"
    bl_idname = "THEBUFF_PT_legs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheBuff"
    bl_parent_id = "THEBUFF_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and (get_r_leg_settings_bone(context) or get_l_leg_settings_bone(context))

    def draw(self, context):
        layout = self.layout
        r_bone = get_r_leg_settings_bone(context)
        l_bone = get_l_leg_settings_bone(context)
        
        row = layout.row()
        row.label(text="Right", icon='LOOP_FORWARDS')
        row.label(text="Left", icon='LOOP_BACK')
        
        layout.separator()
        
        row = layout.row(align=True)
        if r_bone and "IK/FK" in r_bone:
            row.prop(r_bone, '["IK/FK"]', text="IK/FK")
        if l_bone and "IK/FK" in l_bone:
            row.prop(l_bone, '["IK/FK"]', text="IK/FK")
        
        row = layout.row(align=True)
        if r_bone and "Ankle Lock" in r_bone:
            row.prop(r_bone, '["Ankle Lock"]', text="Ankle Lock")
        if l_bone and "Ankle Lock" in l_bone:
            row.prop(l_bone, '["Ankle Lock"]', text="Ankle Lock")


classes = [
    THEBUFF_OT_ChangeSkin,
    THEBUFF_OT_DownloadSkin,
    THEBUFF_PT_MainPanel,
    THEBUFF_PT_SkinPanel,
    THEBUFF_PT_ArmsPanel,
    THEBUFF_PT_LegsPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
