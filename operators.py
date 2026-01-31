import os
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
import bpy.utils.previews

preview_collections = {}

def get_asset_path(filename):
    """Возвращает путь к файлу в папке assets."""
    return os.path.join(os.path.dirname(__file__), "assets", filename)

def get_icon(icon_name):
    """Получает иконку из коллекции превью."""
    pcoll = preview_collections.get("main")
    if pcoll and icon_name in pcoll:
        return pcoll[icon_name].icon_id
    return 0

def get_skin_texture_name(rig_name):
    """Определяет правильное имя текстуры скина на основе названия рига."""
    base_name = "Skin_plush.png" if "ThePlush" in rig_name else "Skin.png"
    
    # Проверяет, есть ли у рига числовой суффикс типа .001, .002 и т.д.
    if '.' in rig_name:
        parts = rig_name.rsplit('.', 1)
        if parts[1].isdigit():
            base_name = f"{base_name}.{parts[1]}"
    
    return base_name

def find_rig_mesh(rig):
    """Находит дочерний меш у рига."""
    return next((c for c in rig.children if c.type == 'MESH'), None)

def find_existing_skin_texture(base_name):
    """Ищет существующую текстуру скина, включая дубликаты типа .001, .002 и т.д."""
    # Сначала проверяет, существует ли текстура с точным именем
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

class THRIG_OT_AppendModify(bpy.types.Operator):
    bl_idname = "thrig.append_modify"
    bl_label = "TheRig(modify)"
    bl_description = "Add THE RIG (Zealum Edit) character to the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            bpy.ops.wm.append(
                filepath=os.path.join(get_asset_path("TheRigZealumEdit.blend"), "Collection", "TheRigZealumEdit(Append)"),
                directory=os.path.join(get_asset_path("TheRigZealumEdit.blend"), "Collection"),
                filename="TheRigZealumEdit(Append)"
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
            
            # Находит и удаляет существующую текстуру
            existing_img = find_existing_skin_texture(correct_texture_name)
            if existing_img:
                bpy.data.images.remove(existing_img)
            
            # Загружает новую текстуру
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

# NEW: Face Toggle Operators from Beta
class THRIG_OT_ShowFace(bpy.types.Operator):
    bl_idname = "thrig.show_face"
    bl_label = "Face"
    bl_description = "Show face controls"

    def execute(self, context):
        rig = context.active_object
        if rig and rig.type == 'ARMATURE':
            bone = rig.pose.bones.get("Face Color")
            if bone and "01_Face Off" in bone:
                bone["01_Face Off"] = 0

                rig.update_tag()
                bpy.context.view_layer.update()

                bpy.context.view_layer.objects.active = None
                bpy.context.view_layer.objects.active = rig

                self.report({'INFO'}, "Face ON")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Property not found on bone")
        return {'CANCELLED'}


class THRIG_OT_HideFace(bpy.types.Operator):
    bl_idname = "thrig.hide_face"
    bl_label = "No Face"
    bl_description = "Hide face controls"

    def execute(self, context):
        rig = context.active_object
        if rig and rig.type == 'ARMATURE':
            bone = rig.pose.bones.get("Face Color")
            if bone and "01_Face Off" in bone:
                bone["01_Face Off"] = 1

                rig.update_tag()
                bpy.context.view_layer.update()

                bpy.context.view_layer.objects.active = None
                bpy.context.view_layer.objects.active = rig

                self.report({'INFO'}, "Face OFF")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Property not found on bone")
        return {'CANCELLED'}


# NEW: Eye Color System
class THRIG_OT_SetEyeColor(bpy.types.Operator):
    bl_idname = "thrig.set_eye_color"
    bl_label = "Apply Eye Color"
    bl_description = "Apply eye colors to the rig"
    
    def execute(self, context):
        rig = context.active_object
        if not rig or rig.type != 'ARMATURE':
            return {'CANCELLED'}
        
        bone = rig.pose.bones.get("Face Color")
        if not bone:
            return {'CANCELLED'}
        
        props = context.scene.thrig_eye_props
        
        # Apply colors based on sync mode
        if props.sync_eyes:
            # Sync mode - same colors for both eyes
            # Iris
            bone["25_Right Pupil Color1"] = props.iris_color1[:]
            bone["26_Right Pupil Color2"] = props.iris_color2[:]
            bone["31_Left Pupil Color1"] = props.iris_color1[:]
            bone["32_Left Pupil Color2"] = props.iris_color2[:]
            
            # Pupil
            bone["27_Right Pupil2 Color1"] = props.pupil_color1[:]
            bone["28_Right Pupil2 Color2"] = props.pupil_color2[:]
            bone["33_Left Pupil2 Color1"] = props.pupil_color1[:]
            bone["34_Left Pupil2 Color2"] = props.pupil_color2[:]
        else:
            # Individual mode - separate colors for each eye
            # Right Iris
            bone["25_Right Pupil Color1"] = props.right_iris_color1[:]
            bone["26_Right Pupil Color2"] = props.right_iris_color2[:]
            
            # Left Iris
            bone["31_Left Pupil Color1"] = props.left_iris_color1[:]
            bone["32_Left Pupil Color2"] = props.left_iris_color2[:]
            
            # Right Pupil
            bone["27_Right Pupil2 Color1"] = props.right_pupil_color1[:]
            bone["28_Right Pupil2 Color2"] = props.right_pupil_color2[:]
            
            # Left Pupil
            bone["33_Left Pupil2 Color1"] = props.left_pupil_color1[:]
            bone["34_Left Pupil2 Color2"] = props.left_pupil_color2[:]
        
        # Force update viewport
        rig.update_tag()
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        context.view_layer.update()
        
        return {'FINISHED'}


# Property Group for Eye Colors - now stored per rig, not globally
class THRIG_EyeColorProperties(bpy.types.PropertyGroup):
    was_synced: BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    
    sync_eyes: BoolProperty(
        name="Sync Eyes",
        description="Apply same colors to both eyes",
        default=True,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Synced colors (when sync_eyes is True)
    iris_color1: bpy.props.FloatVectorProperty(
        name="Iris Color 1",
        subtype='COLOR',
        default=(0.023, 0.004, 0.003, 1.0),  # #2A0C0AFF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    iris_color2: bpy.props.FloatVectorProperty(
        name="Iris Color 2",
        subtype='COLOR',
        default=(0.093, 0.009, 0.008, 1.0),  # #561816FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    pupil_color1: bpy.props.FloatVectorProperty(
        name="Pupil Color 1",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0, 1.0),  # #000000FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    pupil_color2: bpy.props.FloatVectorProperty(
        name="Pupil Color 2",
        subtype='COLOR',
        default=(0.014, 0.014, 0.014, 1.0),  # #202020FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Белок глаз
    sclera_color1: bpy.props.FloatVectorProperty(
        name="Sclera Color 1",
        subtype='COLOR',
        default=(0.827, 0.859, 0.910, 1.0),  # #D3DBE8FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    sclera_color2: bpy.props.FloatVectorProperty(
        name="Sclera Color 2",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0, 1.0),  # #FFFFFFFF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Индивидуальные цвета (когда sync_eyes выключен)
    # Правая бровь
    right_eyebrow_color1: bpy.props.FloatVectorProperty(
        name="Right Eyebrow Color 1",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0, 1.0),  # #000000FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    right_eyebrow_color2: bpy.props.FloatVectorProperty(
        name="Right Eyebrow Color 2",
        subtype='COLOR',
        default=(0.014, 0.014, 0.014, 1.0),  # #202020FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Левая бровь
    left_eyebrow_color1: bpy.props.FloatVectorProperty(
        name="Left Eyebrow Color 1",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0, 1.0),  # #000000FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    left_eyebrow_color2: bpy.props.FloatVectorProperty(
        name="Left Eyebrow Color 2",
        subtype='COLOR',
        default=(0.014, 0.014, 0.014, 1.0),  # #202020FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Индивидуальные цвета (когда sync_eyes выключен)
    # Правый глаз - радужка
    right_iris_color1: bpy.props.FloatVectorProperty(
        name="Right Iris Color 1",
        subtype='COLOR',
        default=(0.023, 0.004, 0.003, 1.0),  # #2A0C0AFF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    right_iris_color2: bpy.props.FloatVectorProperty(
        name="Right Iris Color 2",
        subtype='COLOR',
        default=(0.093, 0.009, 0.008, 1.0),  # #561816FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Правый глаз - зрачок
    right_pupil_color1: bpy.props.FloatVectorProperty(
        name="Right Pupil Color 1",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0, 1.0),  # #000000FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    right_pupil_color2: bpy.props.FloatVectorProperty(
        name="Right Pupil Color 2",
        subtype='COLOR',
        default=(0.014, 0.014, 0.014, 1.0),  # #202020FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Левый глаз - радужка
    left_iris_color1: bpy.props.FloatVectorProperty(
        name="Left Iris Color 1",
        subtype='COLOR',
        default=(0.023, 0.004, 0.003, 1.0),  # #2A0C0AFF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    left_iris_color2: bpy.props.FloatVectorProperty(
        name="Left Iris Color 2",
        subtype='COLOR',
        default=(0.093, 0.009, 0.008, 1.0),  # #561816FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Левый глаз - зрачок
    left_pupil_color1: bpy.props.FloatVectorProperty(
        name="Left Pupil Color 1",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0, 1.0),  # #000000FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    left_pupil_color2: bpy.props.FloatVectorProperty(
        name="Left Pupil Color 2",
        subtype='COLOR',
        default=(0.014, 0.014, 0.014, 1.0),  # #202020FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Правый белок
    right_sclera_color1: bpy.props.FloatVectorProperty(
        name="Right Sclera Color 1",
        subtype='COLOR',
        default=(0.827, 0.859, 0.910, 1.0),  # #D3DBE8FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    right_sclera_color2: bpy.props.FloatVectorProperty(
        name="Right Sclera Color 2",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0, 1.0),  # #FFFFFFFF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    
    # Левый белок
    left_sclera_color1: bpy.props.FloatVectorProperty(
        name="Left Sclera Color 1",
        subtype='COLOR',
        default=(0.827, 0.859, 0.910, 1.0),  # #D3DBE8FF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )
    left_sclera_color2: bpy.props.FloatVectorProperty(
        name="Left Sclera Color 2",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0, 1.0),  # #FFFFFFFF
        min=0.0, max=1.0,
        size=4,
        update=lambda self, context: update_eye_color_for_rig(context.active_object)
    )


def update_eye_color_for_rig(rig):
    """Apply eye colors to a specific rig"""
    if not rig or rig.type != 'ARMATURE':
        return
    
    bone = rig.pose.bones.get("Face Color")
    if not bone:
        return
    
    # Get properties for THIS specific rig
    if not hasattr(rig, "thrig_eye_props"):
        return
    
    props = rig.thrig_eye_props
    
    # When turning OFF sync mode - copy synced colors to RIGHT eye only
    if not props.sync_eyes and props.was_synced:
        props.was_synced = False
        props.right_iris_color1 = props.iris_color1[:]
        props.right_iris_color2 = props.iris_color2[:]
        props.right_pupil_color1 = props.pupil_color1[:]
        props.right_pupil_color2 = props.pupil_color2[:]
    
    # When turning ON sync mode - keep current colors
    elif props.sync_eyes and not props.was_synced:
        props.was_synced = True
    
    # Apply colors directly
    try:
        if props.sync_eyes:
            # Sync mode
            bone["25_Right Pupil Color1"] = props.iris_color1[:3]
            bone["26_Right Pupil Color2"] = props.iris_color2[:3]
            bone["31_Left Pupil Color1"] = props.iris_color1[:3]
            bone["32_Left Pupil Color2"] = props.iris_color2[:3]
            
            bone["27_Right Pupil2 Color1"] = props.pupil_color1[:3]
            bone["28_Right Pupil2 Color2"] = props.pupil_color2[:3]
            bone["33_Left Pupil2 Color1"] = props.pupil_color1[:3]
            bone["34_Left Pupil2 Color2"] = props.pupil_color2[:3]
        else:
            # Individual mode
            bone["25_Right Pupil Color1"] = props.right_iris_color1[:3]
            bone["26_Right Pupil Color2"] = props.right_iris_color2[:3]
            bone["31_Left Pupil Color1"] = props.left_iris_color1[:3]
            bone["32_Left Pupil Color2"] = props.left_iris_color2[:3]
            
            bone["27_Right Pupil2 Color1"] = props.right_pupil_color1[:3]
            bone["28_Right Pupil2 Color2"] = props.right_pupil_color2[:3]
            bone["33_Left Pupil2 Color1"] = props.left_pupil_color1[:3]
            bone["34_Left Pupil2 Color2"] = props.left_pupil_color2[:3]
        
        # Force viewport update
        rig.update_tag()
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        bpy.context.view_layer.update()
    except:
        pass


def menu_func_root(self, context):
    self.layout.separator()
    self.layout.operator(THRIG_OT_AppendMain.bl_idname, text="THE RIG", icon_value=get_icon('therigicon'))
    self.layout.operator(THRIG_OT_AppendModify.bl_idname, text="TheRig(modify)", icon_value=get_icon('therigicon'))
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
    
    bpy.utils.register_class(THRIG_EyeColorProperties)
    bpy.utils.register_class(THRIG_OT_AppendMain)
    bpy.utils.register_class(THRIG_OT_AppendModify)
    bpy.utils.register_class(THPLUSH_OT_AppendPlush)
    bpy.utils.register_class(THSIMPLE_OT_AppendSimple)
    bpy.utils.register_class(THCAMERA_OT_AppendCamera)
    bpy.utils.register_class(THBUFF_OT_AppendBuff)
    bpy.utils.register_class(THRIG_OT_ChangeSkin)
    bpy.utils.register_class(THRIG_OT_LoadCustomSkin)
    bpy.utils.register_class(THRIG_OT_ShowFace)
    bpy.utils.register_class(THRIG_OT_HideFace)
    bpy.utils.register_class(THRIG_OT_SetEyeColor)
    bpy.types.VIEW3D_MT_add.append(menu_func_root)
    
    # Store eye color properties on each Object (rig), not globally
    bpy.types.Object.thrig_eye_props = bpy.props.PointerProperty(type=THRIG_EyeColorProperties)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func_root)
    
    del bpy.types.Object.thrig_eye_props
    
    bpy.utils.unregister_class(THRIG_OT_SetEyeColor)
    bpy.utils.unregister_class(THRIG_OT_HideFace)
    bpy.utils.unregister_class(THRIG_OT_ShowFace)
    bpy.utils.unregister_class(THRIG_OT_LoadCustomSkin)
    bpy.utils.unregister_class(THRIG_OT_ChangeSkin)
    bpy.utils.unregister_class(THBUFF_OT_AppendBuff)
    bpy.utils.unregister_class(THCAMERA_OT_AppendCamera)
    bpy.utils.unregister_class(THSIMPLE_OT_AppendSimple)
    bpy.utils.unregister_class(THPLUSH_OT_AppendPlush)
    bpy.utils.unregister_class(THRIG_OT_AppendModify)
    bpy.utils.unregister_class(THRIG_OT_AppendMain)
    bpy.utils.unregister_class(THRIG_EyeColorProperties)
    
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()