import bpy
import os
from bpy_extras.io_utils import ImportHelper

RIG_ID = "TheSimpleA"
SKIN_TEXTURE_NAME = "Skin"


def is_this_rig(context):
    obj = context.active_object
    if obj and obj.type == 'ARMATURE':
        return obj.data.get("RigId") == RIG_ID
    return False


def get_face_color_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("Face_Color")
    return None


def is_face_enabled(context):
    bone = get_face_color_bone(context)
    if bone:
        face_off = bone.get("01_Face_Off", 0)
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


def get_r_arm_smooth_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("R_Arm_Smooth")
    return None


def get_l_arm_smooth_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("L_Arm_Smooth")
    return None


def get_r_leg_smooth_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("R_Leg_Smooth")
    return None


def get_l_leg_smooth_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("L_Leg_Smooth")
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


def get_thesimple_bone(context):
    rig = context.active_object
    if rig and rig.type == 'ARMATURE':
        return rig.pose.bones.get("TheSimple")
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


class THESIMPLE_OT_DownloadSkin(bpy.types.Operator):
    bl_idname = "thesimple.download_skin"
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


class THESIMPLE_OT_ChangeSkin(bpy.types.Operator, ImportHelper):
    bl_idname = "thesimple.change_skin"
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


class THESIMPLE_PT_MainPanel(bpy.types.Panel):
    bl_label = "TheSimple"
    bl_idname = "THESIMPLE_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"

    @classmethod
    def poll(cls, context):
        return is_this_rig(context)

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        icon_id = get_icon('thesimpleicon')
        if icon_id:
            box.label(text="TheSimple", icon_value=icon_id)
        else:
            box.label(text="TheSimple", icon='ARMATURE_DATA')
        box.label(text="Author: TheRatmir")
        box.operator("wm.url_open", text="Portfolio", icon='URL').url = "https://theratmir.github.io/TheRatmir-Portfolio/"


class THESIMPLE_PT_SkinPanel(bpy.types.Panel):
    bl_label = "Skin"
    bl_idname = "THESIMPLE_PT_skin"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_main"
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
            layout.operator("thesimple.change_skin", text="Change Skin", icon='FILE_IMAGE')
            layout.operator("thesimple.download_skin", text="Download by Username", icon='URL')
        else:
            layout.label(text="No skin texture found", icon='ERROR')


class THESIMPLE_PT_FacePanel(bpy.types.Panel):
    bl_label = "Face"
    bl_idname = "THESIMPLE_PT_face"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        if bone and "01_Face_Off" in bone:
            layout.prop(bone, '["01_Face_Off"]', text="Face Off")


class THESIMPLE_PT_FaceBrows(bpy.types.Panel):
    bl_label = "Brows"
    bl_idname = "THESIMPLE_PT_face_brows"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        if "02_Eyebrows" in bone:
            layout.prop(bone, '["02_Eyebrows"]', text="Eyebrows")
        
        layout.separator()
        
        split = layout.split(factor=0.5)
        split.label(text="Right")
        split.label(text="Left")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "03_Right_Eyebrow" in bone:
            col_r.prop(bone, '["03_Right_Eyebrow"]', text="")
        if "06_Left_Eyebrow" in bone:
            col_l.prop(bone, '["06_Left_Eyebrow"]', text="")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "04_Right_Eyebrow1_Color" in bone:
            col_r.prop(bone, '["04_Right_Eyebrow1_Color"]', text="")
        if "07_Left_Eyebrow1_Color" in bone:
            col_l.prop(bone, '["07_Left_Eyebrow1_Color"]', text="")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "05_Right_Eyebrow2_Color" in bone:
            col_r.prop(bone, '["05_Right_Eyebrow2_Color"]', text="")
        if "08_Left_Eyebrow2_Color" in bone:
            col_l.prop(bone, '["08_Left_Eyebrow2_Color"]', text="")


class THESIMPLE_PT_FaceEyelashes(bpy.types.Panel):
    bl_label = "Eyelashes"
    bl_idname = "THESIMPLE_PT_face_eyelashes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        split = layout.split(factor=0.5)
        split.label(text="Right")
        split.label(text="Left")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "09_Right_Eyelash" in bone:
            col_r.prop(bone, '["09_Right_Eyelash"]', text="")
        if "11_Left_Eyelash" in bone:
            col_l.prop(bone, '["11_Left_Eyelash"]', text="")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "10_Right_Eyelash_Color" in bone:
            col_r.prop(bone, '["10_Right_Eyelash_Color"]', text="")
        if "12_Left_Eyelash_Color" in bone:
            col_l.prop(bone, '["12_Left_Eyelash_Color"]', text="")


class THESIMPLE_PT_FaceEye(bpy.types.Panel):
    bl_label = "Eye"
    bl_idname = "THESIMPLE_PT_face_eye"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        if "13_Eyes" in bone:
            layout.prop(bone, '["13_Eyes"]', text="Eyes")
        
        layout.separator()
        
        split = layout.split(factor=0.5)
        split.label(text="Right")
        split.label(text="Left")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "14_Right_Eye" in bone:
            col_r.prop(bone, '["14_Right_Eye"]', text="")
        if "17_Left_Eye" in bone:
            col_l.prop(bone, '["17_Left_Eye"]', text="")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "15_Right_Eye_Color1" in bone:
            col_r.prop(bone, '["15_Right_Eye_Color1"]', text="")
        if "18_Left_Eye_Color1" in bone:
            col_l.prop(bone, '["18_Left_Eye_Color1"]', text="")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "16_Right_Eye_Color2" in bone:
            col_r.prop(bone, '["16_Right_Eye_Color2"]', text="")
        if "18_Left_Eye_Color2" in bone:
            col_l.prop(bone, '["18_Left_Eye_Color2"]', text="")


class THESIMPLE_PT_FacePupil(bpy.types.Panel):
    bl_label = "Pupil"
    bl_idname = "THESIMPLE_PT_face_pupil"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        if "19_Pupils" in bone:
            layout.prop(bone, '["19_Pupils"]', text="Pupils")
        
        layout.separator()
        
        split = layout.split(factor=0.5)
        split.label(text="Right")
        split.label(text="Left")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "20_Right_Pupil" in bone:
            col_r.prop(bone, '["20_Right_Pupil"]', text="")
        if "23_Left_Pupil" in bone:
            col_l.prop(bone, '["23_Left_Pupil"]', text="")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "21_Right_Pupil1_Color" in bone:
            col_r.prop(bone, '["21_Right_Pupil1_Color"]', text="")
        if "24_Left_Pupil1_Color" in bone:
            col_l.prop(bone, '["24_Left_Pupil1_Color"]', text="")
        
        split = layout.split(factor=0.5)
        col_r = split.column()
        col_l = split.column()
        if "22_Right_Pupil2_Color" in bone:
            col_r.prop(bone, '["22_Right_Pupil2_Color"]', text="")
        if "25_Left_Pupil2_Color" in bone:
            col_l.prop(bone, '["25_Left_Pupil2_Color"]', text="")
        
        layout.separator()
        
        if "26_Pupil_Glow" in bone:
            layout.prop(bone, '["26_Pupil_Glow"]', text="Pupil Glow")
        
        split = layout.split(factor=0.5)
        if "27_Right_Pupil_Glow_Strength" in bone:
            split.prop(bone, '["27_Right_Pupil_Glow_Strength"]', text="Right")
        if "28_Left_Pupil_Glow_Strength" in bone:
            split.prop(bone, '["28_Left_Pupil_Glow_Strength"]', text="Left")


class THESIMPLE_PT_FaceMouth(bpy.types.Panel):
    bl_label = "Mouth"
    bl_idname = "THESIMPLE_PT_face_mouth"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_face"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context) and get_face_color_bone(context) and is_face_enabled(context)

    def draw(self, context):
        layout = self.layout
        bone = get_face_color_bone(context)
        
        if "29_Mouth/Lips" in bone:
            layout.prop(bone, '["29_Mouth/Lips"]', text="Mouth/Lips")
        
        layout.separator()
        
        if "30_Teeth_Up_Color" in bone:
            layout.prop(bone, '["30_Teeth_Up_Color"]', text="Teeth Up")
        if "31_Teeth_Down_Color" in bone:
            layout.prop(bone, '["31_Teeth_Down_Color"]', text="Teeth Down")
        
        layout.separator()
        
        if "32_Tongue_Color" in bone:
            layout.prop(bone, '["32_Tongue_Color"]', text="Tongue")
        if "33_Mouth_Color" in bone:
            layout.prop(bone, '["33_Mouth_Color"]', text="Mouth")
        if "34_Lips_Color" in bone:
            layout.prop(bone, '["34_Lips_Color"]', text="Lips")


class THESIMPLE_PT_ArmsPanel(bpy.types.Panel):
    bl_label = "Arms"
    bl_idname = "THESIMPLE_PT_arms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_main"
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
        
        row = layout.row(align=True)
        if r_bone and "Bend Type" in r_bone:
            row.prop(r_bone, '["Bend Type"]', text="Bend Type")
        if l_bone and "Bend Type" in l_bone:
            row.prop(l_bone, '["Bend Type"]', text="Bend Type")
        
        # Smooth Bend - показывается только если Bend Type == 0
        r_smooth = get_r_arm_smooth_bone(context)
        l_smooth = get_l_arm_smooth_bone(context)
        r_show_smooth = r_bone and r_bone.get("Bend Type", 1) == 0
        l_show_smooth = l_bone and l_bone.get("Bend Type", 1) == 0
        
        if r_show_smooth or l_show_smooth:
            row = layout.row(align=True)
            if r_show_smooth and r_smooth and "Smooth Bend" in r_smooth:
                row.prop(r_smooth, '["Smooth Bend"]', text="Smooth")
            else:
                row.label(text="")
            if l_show_smooth and l_smooth and "Smooth Bend" in l_smooth:
                row.prop(l_smooth, '["Smooth Bend"]', text="Smooth")
            else:
                row.label(text="")


class THESIMPLE_PT_LegsPanel(bpy.types.Panel):
    bl_label = "Legs"
    bl_idname = "THESIMPLE_PT_legs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_main"
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
        
        row = layout.row(align=True)
        if r_bone and "Bend Type" in r_bone:
            row.prop(r_bone, '["Bend Type"]', text="Bend Type")
        if l_bone and "Bend Type" in l_bone:
            row.prop(l_bone, '["Bend Type"]', text="Bend Type")
        
        # Smooth Bend - показывается только если Bend Type == 0
        r_smooth = get_r_leg_smooth_bone(context)
        l_smooth = get_l_leg_smooth_bone(context)
        r_show_smooth = r_bone and r_bone.get("Bend Type", 1) == 0
        l_show_smooth = l_bone and l_bone.get("Bend Type", 1) == 0
        
        if r_show_smooth or l_show_smooth:
            row = layout.row(align=True)
            if r_show_smooth and r_smooth and "Smooth Bend" in r_smooth:
                row.prop(r_smooth, '["Smooth Bend"]', text="Smooth")
            else:
                row.label(text="")
            if l_show_smooth and l_smooth and "Smooth Bend" in l_smooth:
                row.prop(l_smooth, '["Smooth Bend"]', text="Smooth")
            else:
                row.label(text="")


class THESIMPLE_PT_TaperPanel(bpy.types.Panel):
    bl_label = "Taper"
    bl_idname = "THESIMPLE_PT_taper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_settings"
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


class THESIMPLE_PT_ArmorPanel(bpy.types.Panel):
    bl_label = "Armor"
    bl_idname = "THESIMPLE_PT_armor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_settings"
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


class THESIMPLE_PT_SettingsPanel(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "THESIMPLE_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TheSimple"
    bl_parent_id = "THESIMPLE_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return is_this_rig(context)

    def draw(self, context):
        layout = self.layout
        rig_bone = get_thesimple_bone(context)
        
        if rig_bone:
            if "Arm Type" in rig_bone:
                layout.prop(rig_bone, '["Arm Type"]', text="Arm Type")
            if "Bevel" in rig_bone:
                layout.prop(rig_bone, '["Bevel"]', text="Bevel")
            if "Bevel Amount" in rig_bone:
                layout.prop(rig_bone, '["Bevel Amount"]', text="Bevel Amount")


classes = [
    THESIMPLE_OT_DownloadSkin,
    THESIMPLE_OT_ChangeSkin,
    THESIMPLE_PT_MainPanel,
    THESIMPLE_PT_SkinPanel,
    THESIMPLE_PT_FacePanel,
    THESIMPLE_PT_FaceBrows,
    THESIMPLE_PT_FaceEyelashes,
    THESIMPLE_PT_FaceEye,
    THESIMPLE_PT_FacePupil,
    THESIMPLE_PT_FaceMouth,
    THESIMPLE_PT_ArmsPanel,
    THESIMPLE_PT_LegsPanel,
    THESIMPLE_PT_SettingsPanel,
    THESIMPLE_PT_TaperPanel,
    THESIMPLE_PT_ArmorPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
