# therig_ui.py - UI panels for TheRig
import bpy
import os
from bpy_extras.io_utils import ImportHelper

# RigId for this file
RIG_ID = "TheRigA"
SKIN_TEXTURE_NAME = "Skin"  # Base name for skin texture


def is_this_rig(context):
    """Check if active object is the correct rig by RigId"""
    obj = context.active_object
    if obj and obj.type == 'ARMATURE':
        return obj.data.get("RigId") == RIG_ID
    return False


def get_face_color_bone(context):
    """Get Face Color bone"""
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Face Color")
    return None


def get_head_settings_bone(context):
    """Get Head_Settings bone"""
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Head_Settings")
    return None


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
                            if SKIN_TEXTURE_NAME in node.image.name:
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


# ===== SKIN CHANGE OPERATOR =====
# ===== DOWNLOAD SKIN BY USERNAME =====
class THERIG_OT_DownloadSkin(bpy.types.Operator):
    """Download skin by Minecraft username"""
    bl_idname = "therig.download_skin"
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
        
        import urllib.request
        import tempfile
        
        rig = context.active_object
        texture = find_skin_texture(rig)
        
        if not texture:
            self.report({'ERROR'}, "No skin texture found on rig!")
            return {'CANCELLED'}
        
        # Check if multiple rigs use this texture
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
            texture = new_texture
        
        # Download skin from Minotar API
        url = f"https://minotar.net/skin/{self.username}"
        
        try:
            # Create temp file
            temp_path = os.path.join(tempfile.gettempdir(), f"{self.username}_skin.png")
            urllib.request.urlretrieve(url, temp_path)
            
            # Load downloaded image
            new_image = bpy.data.images.load(temp_path)
            
            # Check size and copy pixels
            if texture.size[0] == new_image.size[0] and texture.size[1] == new_image.size[1]:
                texture.pixels[:] = new_image.pixels[:]
                texture.update()
                bpy.data.images.remove(new_image)
                self.report({'INFO'}, f"Skin '{self.username}' applied to {rig.name}!")
            else:
                self.report({'ERROR'}, f"Size mismatch! Expected {texture.size[0]}x{texture.size[1]}")
                bpy.data.images.remove(new_image)
                return {'CANCELLED'}
            
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to download skin: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class THERIG_OT_ChangeSkin(bpy.types.Operator, ImportHelper):
    """Change skin texture"""
    bl_idname = "therig.change_skin"
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
        
        # Check if multiple rigs use this texture
        if count_rigs_using_texture(texture) > 1:
            # Make a copy for this rig
            new_texture = texture.copy()
            new_texture.name = f"{SKIN_TEXTURE_NAME}_{rig.name}"
            
            # Update material to use new texture
            for child in rig.children:
                if child.type == 'MESH':
                    for mat in child.data.materials:
                        if mat and mat.use_nodes:
                            for node in mat.node_tree.nodes:
                                if node.type == 'TEX_IMAGE' and node.image == texture:
                                    node.image = new_texture
            texture = new_texture
        
        # Load new image
        try:
            new_image = bpy.data.images.load(self.filepath)
            
            # Copy pixels to existing texture (keeps name)
            if texture.size[0] == new_image.size[0] and texture.size[1] == new_image.size[1]:
                texture.pixels[:] = new_image.pixels[:]
                texture.update()
                bpy.data.images.remove(new_image)
                self.report({'INFO'}, f"Skin updated for {rig.name}!")
            else:
                self.report({'ERROR'}, f"Image size mismatch! Expected {texture.size[0]}x{texture.size[1]}")
                bpy.data.images.remove(new_image)
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load image: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class THERIG_PT_MainPanel(bpy.types.Panel):
    """Main panel for TheRig"""
    bl_label = "TheRig"
    bl_idname = "THERIG_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"

    @classmethod
    def poll(cls, context):
        return is_this_rig(context)

    def draw(self, context):
        layout = self.layout
        
        # Info
        box = layout.box()
        icon_id = get_icon('therigicon')
        if icon_id:
            box.label(text="TheRig", icon_value=icon_id)
        else:
            box.label(text="TheRig", icon='ARMATURE_DATA')
        box.label(text="Author: TheRatmir")
        box.operator("wm.url_open", text="Portfolio", icon='URL').url = "https://theratmir.github.io/TheRatmir-Portfolio/"


# ===== SKIN PANEL =====
class THERIG_PT_SkinPanel(bpy.types.Panel):
    """Skin settings panel"""
    bl_label = "Skin"
    bl_idname = "THERIG_PT_skin"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_main"
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
            layout.operator("therig.change_skin", text="Change Skin", icon='FILE_IMAGE')
            layout.operator("therig.download_skin", text="Download by Username", icon='URL')
        else:
            layout.label(text="No skin texture found", icon='ERROR')


class THERIG_PT_FacePanel(bpy.types.Panel):
    """Face settings panel"""
    bl_label = "Face"
    bl_idname = "THERIG_PT_face"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context)

    def draw(self, context):
        pass  # Content in subpanels


# ===== EYE (Sclera) =====
class THERIG_PT_FaceEye(bpy.types.Panel):
    """Eye sclera settings"""
    bl_label = "Eye"
    bl_idname = "THERIG_PT_face_eye"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        # Headers
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        # On/Off
        row = layout.row()
        if "17_Right Eye" in bone:
            row.prop(bone, '["17_Right Eye"]', text="On/Off")
        if "20_Left Eye" in bone:
            row.prop(bone, '["20_Left Eye"]', text="On/Off")
        
        # Color1
        row = layout.row()
        if "18_Right Eye Color1" in bone:
            row.prop(bone, '["18_Right Eye Color1"]', text="")
        if "21_Left Eye Color1" in bone:
            row.prop(bone, '["21_Left Eye Color1"]', text="")
        
        # Color2
        row = layout.row()
        if "19_Right Eye Color2" in bone:
            row.prop(bone, '["19_Right Eye Color2"]', text="")
        if "22_Left Eye Color2" in bone:
            row.prop(bone, '["22_Left Eye Color2"]', text="")


# ===== PUPIL =====
class THERIG_PT_FacePupil(bpy.types.Panel):
    """Pupil settings"""
    bl_label = "Pupil"
    bl_idname = "THERIG_PT_face_pupil"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        # Headers
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        # On/Off
        row = layout.row()
        if "24_Right Pupil" in bone:
            row.prop(bone, '["24_Right Pupil"]', text="On/Off")
        if "30_Left Pupil" in bone:
            row.prop(bone, '["30_Left Pupil"]', text="On/Off")
        
        layout.separator()
        layout.label(text="Iris")
        
        # Pupil Color1
        row = layout.row()
        if "25_Right Pupil Color1" in bone:
            row.prop(bone, '["25_Right Pupil Color1"]', text="")
        if "31_Left Pupil Color1" in bone:
            row.prop(bone, '["31_Left Pupil Color1"]', text="")
        
        # Pupil Color2
        row = layout.row()
        if "26_Right Pupil Color2" in bone:
            row.prop(bone, '["26_Right Pupil Color2"]', text="")
        if "32_Left Pupil Color2" in bone:
            row.prop(bone, '["32_Left Pupil Color2"]', text="")
        
        layout.separator()
        layout.label(text="Pupil")
        
        # Pupil2 Color1
        row = layout.row()
        if "27_Right Pupil2 Color1" in bone:
            row.prop(bone, '["27_Right Pupil2 Color1"]', text="")
        if "33_Left Pupil2 Color1" in bone:
            row.prop(bone, '["33_Left Pupil2 Color1"]', text="")
        
        # Pupil2 Color2
        row = layout.row()
        if "28_Right Pupil2 Color2" in bone:
            row.prop(bone, '["28_Right Pupil2 Color2"]', text="")
        if "34_Left Pupil2 Color2" in bone:
            row.prop(bone, '["34_Left Pupil2 Color2"]', text="")
        
        layout.separator()
        layout.label(text="Spark")
        
        # Spark Color
        row = layout.row()
        if "29_Right Spark Color" in bone:
            row.prop(bone, '["29_Right Spark Color"]', text="")
        if "35_Left Spark Color" in bone:
            row.prop(bone, '["35_Left Spark Color"]', text="")
        
        layout.separator()
        layout.label(text="Glow")
        
        # Pupil Glow On/Off
        if "43_Pupil Glow" in bone:
            layout.prop(bone, '["43_Pupil Glow"]', text="Pupil Glow")
        
        # Glow Strength
        row = layout.row()
        if "44_Right Pupil Glow Strength" in bone:
            row.prop(bone, '["44_Right Pupil Glow Strength"]', text="Right")
        if "45_Left Pupil Glow Strength" in bone:
            row.prop(bone, '["45_Left Pupil Glow Strength"]', text="Left")


# ===== BROWS =====
class THERIG_PT_FaceBrows(bpy.types.Panel):
    """Eyebrow settings"""
    bl_label = "Brows"
    bl_idname = "THERIG_PT_face_brows"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        # Headers
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        # On/Off
        row = layout.row()
        if "03_Right Eyebrow" in bone:
            row.prop(bone, '["03_Right Eyebrow"]', text="On/Off")
        if "06_Left Eyebrow" in bone:
            row.prop(bone, '["06_Left Eyebrow"]', text="On/Off")
        
        # Colors - 04, 05 | 07, 08 on one row
        row = layout.row()
        if "04_Right Eyebrow Color1" in bone:
            row.prop(bone, '["04_Right Eyebrow Color1"]', text="")
        if "05_Right Eyebrow Color2" in bone:
            row.prop(bone, '["05_Right Eyebrow Color2"]', text="")
        row.separator()
        if "07_Left Eyebrow Color1" in bone:
            row.prop(bone, '["07_Left Eyebrow Color1"]', text="")
        if "08_Left Eyebrow Color2" in bone:
            row.prop(bone, '["08_Left Eyebrow Color2"]', text="")


# ===== MOUTH =====
class THERIG_PT_FaceMouth(bpy.types.Panel):
    """Mouth settings"""
    bl_label = "Mouth"
    bl_idname = "THERIG_PT_face_mouth"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        # Mouth On/Off
        if "36_Mouth" in bone:
            layout.prop(bone, '["36_Mouth"]', text="Mouth")
        
        layout.separator()
        
        # Teeth Colors
        layout.label(text="Teeth")
        row = layout.row()
        if "37_Teeth Color1" in bone:
            row.prop(bone, '["37_Teeth Color1"]', text="")
        if "38_Teeth Color2" in bone:
            row.prop(bone, '["38_Teeth Color2"]', text="")
        
        layout.separator()
        
        # Mouth & Tongue Colors
        if "40_Mouth Color" in bone:
            layout.prop(bone, '["40_Mouth Color"]', text="Mouth Color")
        if "39_Tongue Color" in bone:
            layout.prop(bone, '["39_Tongue Color"]', text="Tongue Color")
        
        layout.separator()
        
        # Lips On/Off
        if "41_Lips" in bone:
            layout.prop(bone, '["41_Lips"]', text="Lips")


# ===== SETTINGS =====
class THERIG_PT_FaceSettings(bpy.types.Panel):
    """Additional face settings"""
    bl_label = "Settings"
    bl_idname = "THERIG_PT_face_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_head_settings_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_head_settings_bone(context)
        
        if not bone:
            layout.label(text="Head_Settings bone not found", icon='ERROR')
            return
        
        col = layout.column(align=True)
        
        if "1px eyes" in bone:
            col.prop(bone, '["1px eyes"]', text="1px Eyes")
        if "Double Eyes" in bone:
            col.prop(bone, '["Double Eyes"]', text="Double Eyes")
        if "Eyelashes" in bone:
            col.prop(bone, '["Eyelashes"]', text="Eyelashes")
        if "Textured Pupils" in bone:
            col.prop(bone, '["Textured Pupils"]', text="Textured Pupils")


# Classes to register
classes = [
    THERIG_OT_DownloadSkin,
    THERIG_OT_ChangeSkin,
    THERIG_PT_MainPanel,
    THERIG_PT_SkinPanel,
    THERIG_PT_FacePanel,
    THERIG_PT_FaceEye,
    THERIG_PT_FacePupil,
    THERIG_PT_FaceBrows,
    THERIG_PT_FaceMouth,
    THERIG_PT_FaceSettings,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
