import bpy
import os
from bpy_extras.io_utils import ImportHelper

RIG_ID = "TheRigAold"
SKIN_TEXTURE_NAME = "Skin"


def is_this_rig(context):
    obj = context.active_object
    if obj and obj.type == 'ARMATURE':
        return obj.data.get("RigId") == RIG_ID
    return False


def get_face_color_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Face Color")
    return None


def is_face_enabled(context):
    bone = get_face_color_bone(context)
    if bone:
        face_off = bone.get("01_Face Off", 0)
        return face_off == 0 or face_off == False
    return True


def get_head_settings_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Head_Settings")
    return None


def get_body_settings_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Body_Settings")
    return None


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


def get_armor_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Armor")
    return None


def get_taper_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Taper")
    return None


def get_therig_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("TheRig")
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
                            if SKIN_TEXTURE_NAME in node.image.name:
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


class THERIG_OT_DownloadSkin(bpy.types.Operator):
    bl_idname = "therig.download_skin"
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
        
        import urllib.request
        import tempfile
        
        rig = context.active_object
        texture = find_skin_texture(rig)
        
        if not texture:
            self.report({'ERROR'}, "No skin texture found on rig!")
            return {'CANCELLED'}
        
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
        
        url = f"https://minotar.net/skin/{self.username}"
        
        try:
            temp_path = os.path.join(tempfile.gettempdir(), f"{self.username}_skin.png")
            urllib.request.urlretrieve(url, temp_path)
            
            new_image = bpy.data.images.load(temp_path)
            
            if texture.size[0] == new_image.size[0] and texture.size[1] == new_image.size[1]:
                texture.pixels[:] = new_image.pixels[:]
                texture.update()
                bpy.data.images.remove(new_image)
                self.report({'INFO'}, f"Skin '{self.username}' applied to {rig.name}!")
            else:
                self.report({'ERROR'}, f"Size mismatch! Expected {texture.size[0]}x{texture.size[1]}")
                bpy.data.images.remove(new_image)
                return {'CANCELLED'}
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to download skin: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class THERIG_OT_ChangeSkin(bpy.types.Operator, ImportHelper):
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
        
        try:
            new_image = bpy.data.images.load(self.filepath)
            
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
        
        box = layout.box()
        icon_id = get_icon('therigicon')
        if icon_id:
            box.label(text="TheRig", icon_value=icon_id)
        else:
            box.label(text="TheRig", icon='ARMATURE_DATA')
        box.label(text="Author: TheRatmir")
        box.operator("wm.url_open", text="Portfolio", icon='URL').url = "https://theratmir.github.io/TheRatmir-Portfolio/"


class THERIG_PT_SkinPanel(bpy.types.Panel):
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
        layout = self.layout
        bone = get_face_color_bone(context)
        
        if bone and "01_Face Off" in bone:
            layout.prop(bone, '["01_Face Off"]', text="Face Off", toggle=True)


class THERIG_PT_FaceEye(bpy.types.Panel):
    bl_label = "Eye"
    bl_idname = "THERIG_PT_face_eye"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        row = layout.row()
        if "17_Right Eye" in bone:
            row.prop(bone, '["17_Right Eye"]', text="On/Off")
        if "20_Left Eye" in bone:
            row.prop(bone, '["20_Left Eye"]', text="On/Off")
        
        row = layout.row()
        if "18_Right Eye Color1" in bone:
            row.prop(bone, '["18_Right Eye Color1"]', text="")
        if "21_Left Eye Color1" in bone:
            row.prop(bone, '["21_Left Eye Color1"]', text="")
        
        row = layout.row()
        if "19_Right Eye Color2" in bone:
            row.prop(bone, '["19_Right Eye Color2"]', text="")
        if "22_Left Eye Color2" in bone:
            row.prop(bone, '["22_Left Eye Color2"]', text="")


class THERIG_PT_FacePupil(bpy.types.Panel):
    bl_label = "Pupil"
    bl_idname = "THERIG_PT_face_pupil"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        row = layout.row()
        if "24_Right Pupil" in bone:
            row.prop(bone, '["24_Right Pupil"]', text="On/Off")
        if "30_Left Pupil" in bone:
            row.prop(bone, '["30_Left Pupil"]', text="On/Off")
        
        layout.separator()
        layout.label(text="Iris")
        
        row = layout.row()
        if "25_Right Pupil Color1" in bone:
            row.prop(bone, '["25_Right Pupil Color1"]', text="")
        if "31_Left Pupil Color1" in bone:
            row.prop(bone, '["31_Left Pupil Color1"]', text="")
        
        row = layout.row()
        if "26_Right Pupil Color2" in bone:
            row.prop(bone, '["26_Right Pupil Color2"]', text="")
        if "32_Left Pupil Color2" in bone:
            row.prop(bone, '["32_Left Pupil Color2"]', text="")
        
        layout.separator()
        layout.label(text="Pupil")
        
        row = layout.row()
        if "27_Right Pupil2 Color1" in bone:
            row.prop(bone, '["27_Right Pupil2 Color1"]', text="")
        if "33_Left Pupil2 Color1" in bone:
            row.prop(bone, '["33_Left Pupil2 Color1"]', text="")
        
        row = layout.row()
        if "28_Right Pupil2 Color2" in bone:
            row.prop(bone, '["28_Right Pupil2 Color2"]', text="")
        if "34_Left Pupil2 Color2" in bone:
            row.prop(bone, '["34_Left Pupil2 Color2"]', text="")
        
        layout.separator()
        layout.label(text="Spark")
        
        row = layout.row()
        if "29_Right Spark Color" in bone:
            row.prop(bone, '["29_Right Spark Color"]', text="")
        if "35_Left Spark Color" in bone:
            row.prop(bone, '["35_Left Spark Color"]', text="")
        
        layout.separator()
        layout.label(text="Glow")
        
        if "43_Pupil Glow" in bone:
            layout.prop(bone, '["43_Pupil Glow"]', text="Pupil Glow")
        
        row = layout.row()
        if "44_Right Pupil Glow Strength" in bone:
            row.prop(bone, '["44_Right Pupil Glow Strength"]', text="Right")
        if "45_Left Pupil Glow Strength" in bone:
            row.prop(bone, '["45_Left Pupil Glow Strength"]', text="Left")


class THERIG_PT_FaceBrows(bpy.types.Panel):
    bl_label = "Brows"
    bl_idname = "THERIG_PT_face_brows"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        row = layout.row()
        if "03_Right Eyebrow" in bone:
            row.prop(bone, '["03_Right Eyebrow"]', text="On/Off")
        if "06_Left Eyebrow" in bone:
            row.prop(bone, '["06_Left Eyebrow"]', text="On/Off")
        
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


class THERIG_PT_FaceEyelashes(bpy.types.Panel):
    bl_label = "Eyelashes"
    bl_idname = "THERIG_PT_face_eyelashes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not is_this_rig(context) or not get_face_color_bone(context) or not is_face_enabled(context):
            return False
        head_bone = get_head_settings_bone(context)
        if head_bone and "Eyelashes" in head_bone:
            return head_bone["Eyelashes"] == 1
        return False

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        row = layout.row()
        if "10_Right Eyelash" in bone:
            row.prop(bone, '["10_Right Eyelash"]', text="On/Off")
        if "13_Left Eyelash" in bone:
            row.prop(bone, '["13_Left Eyelash"]', text="On/Off")
        
        row = layout.row()
        if "12_Right Eyelash Color1" in bone:
            row.prop(bone, '["12_Right Eyelash Color1"]', text="")
        if "11_Right Eyelash Color2" in bone:
            row.prop(bone, '["11_Right Eyelash Color2"]', text="")
        row.separator()
        if "14_Left Eyelash Color1" in bone:
            row.prop(bone, '["14_Left Eyelash Color1"]', text="")
        if "15_Left Eyelash Color2" in bone:
            row.prop(bone, '["15_Left Eyelash Color2"]', text="")


class THERIG_PT_FaceMouth(bpy.types.Panel):
    bl_label = "Mouth"
    bl_idname = "THERIG_PT_face_mouth"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        if "36_Mouth" in bone:
            layout.prop(bone, '["36_Mouth"]', text="Mouth")
        
        layout.separator()
        
        layout.label(text="Teeth")
        row = layout.row()
        if "37_Teeth Color1" in bone:
            row.prop(bone, '["37_Teeth Color1"]', text="")
        if "38_Teeth Color2" in bone:
            row.prop(bone, '["38_Teeth Color2"]', text="")
        
        layout.separator()
        
        if "40_Mouth Color" in bone:
            layout.prop(bone, '["40_Mouth Color"]', text="Mouth Color")
        if "39_Tongue Color" in bone:
            layout.prop(bone, '["39_Tongue Color"]', text="Tongue Color")
        
        layout.separator()
        
        if "41_Lips" in bone:
            layout.prop(bone, '["41_Lips"]', text="Lips")
        if "42_Lips Color" in bone:
            layout.prop(bone, '["42_Lips Color"]', text="Lips Color")


class THERIG_PT_FaceSettings(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "THERIG_PT_face_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_head_settings_bone(context) and is_face_enabled(context)

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


class THERIG_PT_BodyPanel(bpy.types.Panel):
    bl_label = "Body"
    bl_idname = "THERIG_PT_body"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_body_settings_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_body_settings_bone(context)
        
        if "Breast" in bone:
            layout.prop(bone, '["Breast"]', text="Breast")
        if "Breast Size" in bone:
            layout.prop(bone, '["Breast Size"]', text="Breast Size")
        if "Hip" in bone:
            layout.prop(bone, '["Hip"]', text="Hip")


class THERIG_PT_ArmsPanel(bpy.types.Panel):
    bl_label = "Arms"
    bl_idname = "THERIG_PT_arms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_main"
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
        
        row = layout.row(align=True)
        if r_bone and "Fingers" in r_bone:
            row.prop(r_bone, '["Fingers"]', text="Fingers")
        if l_bone and "Fingers" in l_bone:
            row.prop(l_bone, '["Fingers"]', text="Fingers")
        
        row = layout.row(align=True)
        if r_bone and "Parent bone" in r_bone:
            row.prop(r_bone, '["Parent bone"]', text="Parent")
        if l_bone and "Parent bone" in l_bone:
            row.prop(l_bone, '["Parent bone"]', text="Parent")
        
        row = layout.row(align=True)
        if r_bone and "Tweak" in r_bone:
            row.prop(r_bone, '["Tweak"]', text="Tweak")
        if l_bone and "Tweak" in l_bone:
            row.prop(l_bone, '["Tweak"]', text="Tweak")


class THERIG_PT_LegsPanel(bpy.types.Panel):
    bl_label = "Legs"
    bl_idname = "THERIG_PT_legs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_main"
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
        
        row = layout.row(align=True)
        if r_bone and "Tweak" in r_bone:
            row.prop(r_bone, '["Tweak"]', text="Tweak")
        if l_bone and "Tweak" in l_bone:
            row.prop(l_bone, '["Tweak"]', text="Tweak")


class THERIG_PT_TaperPanel(bpy.types.Panel):
    bl_label = "Taper"
    bl_idname = "THERIG_PT_taper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_settings"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_taper_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_taper_bone(context)
        
        if not bone:
            return
        
        layout.label(text="Body")
        if " 1.Body Taper Top" in bone:
            layout.prop(bone, '[" 1.Body Taper Top"]', text="Top")
        if " 2.Body Taper Bottom" in bone:
            layout.prop(bone, '[" 2.Body Taper Bottom"]', text="Bottom")
        
        layout.separator()
        layout.label(text="Arms")
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        row = layout.row()
        if " 3.Right Arm Taper Top" in bone:
            row.prop(bone, '[" 3.Right Arm Taper Top"]', text="Top")
        if " 5.Left Arm Taper Top" in bone:
            row.prop(bone, '[" 5.Left Arm Taper Top"]', text="Top")
        
        row = layout.row()
        if " 4.Right Arm Taper Bottom" in bone:
            row.prop(bone, '[" 4.Right Arm Taper Bottom"]', text="Bottom")
        if " 6.Left Arm Taper Bottom" in bone:
            row.prop(bone, '[" 6.Left Arm Taper Bottom"]', text="Bottom")
        
        layout.separator()
        layout.label(text="Legs")
        row = layout.row()
        row.label(text="Right")
        row.label(text="Left")
        
        row = layout.row()
        if " 9.Right Leg Taper Up" in bone:
            row.prop(bone, '[" 9.Right Leg Taper Up"]', text="Top")
        if " 7.Left Leg Taper Top" in bone:
            row.prop(bone, '[" 7.Left Leg Taper Top"]', text="Top")
        
        row = layout.row()
        if "10.Right Leg Taper Bottom" in bone:
            row.prop(bone, '["10.Right Leg Taper Bottom"]', text="Bottom")
        if " 8.Left Leg Taper Bottom" in bone:
            row.prop(bone, '[" 8.Left Leg Taper Bottom"]', text="Bottom")


class THERIG_PT_ArmorPanel(bpy.types.Panel):
    bl_label = "Armor"
    bl_idname = "THERIG_PT_armor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheRig"
    bl_parent_id = "THERIG_PT_settings"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_armor_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_armor_bone(context)
        
        if not bone:
            return
        
        layout.label(text="Helmet")
        row = layout.row()
        if "01_Helmet" in bone:
            row.prop(bone, '["01_Helmet"]', text="On/Off")
        if "02_H_Type" in bone:
            row.prop(bone, '["02_H_Type"]', text="Type")
        if "03_H_Color" in bone:
            layout.prop(bone, '["03_H_Color"]', text="Leather Color")
        
        layout.separator()
        layout.label(text="ChestPlate")
        row = layout.row()
        if "04_ChestPlate" in bone:
            row.prop(bone, '["04_ChestPlate"]', text="On/Off")
        if "05_C_Type" in bone:
            row.prop(bone, '["05_C_Type"]', text="Type")
        if "06_C_Color" in bone:
            layout.prop(bone, '["06_C_Color"]', text="Leather Color")
        
        layout.separator()
        layout.label(text="Leggings")
        row = layout.row()
        if "07_Leggings" in bone:
            row.prop(bone, '["07_Leggings"]', text="On/Off")
        if "08_L_Type" in bone:
            row.prop(bone, '["08_L_Type"]', text="Type")
        if "09_L_Color" in bone:
            layout.prop(bone, '["09_L_Color"]', text="Leather Color")
        
        layout.separator()
        layout.label(text="Boots")
        row = layout.row()
        if "10_Boots" in bone:
            row.prop(bone, '["10_Boots"]', text="On/Off")
        if "11_B_Type" in bone:
            row.prop(bone, '["11_B_Type"]', text="Type")
        if "12_B_Color" in bone:
            layout.prop(bone, '["12_B_Color"]', text="Leather Color")
        
        layout.separator()
        if "13_Elytra/Cape" in bone:
            layout.prop(bone, '["13_Elytra/Cape"]', text="Elytra/Cape")


class THERIG_PT_SettingsPanel(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "THERIG_PT_settings"
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
        rig_bone = get_therig_bone(context)
        
        if rig_bone:
            if "Arm Type" in rig_bone:
                layout.prop(rig_bone, '["Arm Type"]', text="Arm Type")
            if "Bevel" in rig_bone:
                layout.prop(rig_bone, '["Bevel"]', text="Bevel")
            if "Bevel Amount" in rig_bone:
                layout.prop(rig_bone, '["Bevel Amount"]', text="Bevel Amount")


classes = [
    THERIG_OT_DownloadSkin,
    THERIG_OT_ChangeSkin,
    THERIG_PT_MainPanel,
    THERIG_PT_SkinPanel,
    THERIG_PT_FacePanel,
    THERIG_PT_FaceEye,
    THERIG_PT_FacePupil,
    THERIG_PT_FaceBrows,
    THERIG_PT_FaceEyelashes,
    THERIG_PT_FaceMouth,
    THERIG_PT_FaceSettings,
    THERIG_PT_BodyPanel,
    THERIG_PT_ArmsPanel,
    THERIG_PT_LegsPanel,
    THERIG_PT_SettingsPanel,
    THERIG_PT_TaperPanel,
    THERIG_PT_ArmorPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
