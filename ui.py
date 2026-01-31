import os
import bpy

def get_rig_icon(rig_name):
    """Возвращает иконку для конкретного рига."""
    from . import operators
    
    if 'TheRig' in rig_name:
        return operators.get_icon('therigicon')
    elif 'ThePlush' in rig_name:
        return operators.get_icon('theplushicon')
    elif 'TheSimple' in rig_name:
        return operators.get_icon('thesimpleicon')
    elif 'TheBuff' in rig_name:
        return operators.get_icon('thebufficon')
    else:
        return 0  # Дефолтная иконка


class THRIG_PT_MainPanel(bpy.types.Panel):
    bl_label = "THE RIG Tools"
    bl_idname = "THRIG_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rig Tools"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and any(x in obj.name for x in ['TheRig', 'ThePlush'])

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # Показывает название рига с его иконкой
        rig_icon = get_rig_icon(obj.name)
        if rig_icon:
            layout.label(text=f"Active: {obj.name}", icon_value=rig_icon)
        else:
            layout.label(text=f"Active: {obj.name}", icon='ARMATURE_DATA')
        
        box = layout.box()
        box.label(text="Skin System", icon='MATERIAL')
        
        skin_dir = os.path.join(os.path.dirname(__file__), "skins")
        if os.path.exists(skin_dir):
            for skin in sorted(os.listdir(skin_dir)):
                if skin.lower().endswith(('.png', '.jpg', '.jpeg')):
                    op = box.operator("thrig.change_skin", text=os.path.splitext(skin)[0])
                    op.skin_name = skin
        else:
            box.label(text="No skins folder found!", icon='ERROR')
        
        box.operator("thrig.load_custom_skin", icon='FILE_FOLDER')


class THRIG_PT_FaceTogglePanel(bpy.types.Panel):
    bl_label = "Face Toggle"
    bl_idname = "THRIG_PT_face_toggle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rig Tools"

    @classmethod
    def poll(cls, context):
        rig = context.active_object
        # Показывается только для TheRig и его копий (TheRig.001, TheRig.002 и т.д.)
        if not rig or rig.type != 'ARMATURE':
            return False
        return rig.name.startswith('TheRig')

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("thrig.show_face", text="Face", depress=self.is_face_on(context))
        row.operator("thrig.hide_face", text="No Face", depress=not self.is_face_on(context))

    def is_face_on(self, context):
        rig = context.active_object
        if rig and rig.type == 'ARMATURE':
            bone = rig.pose.bones.get("Face Color")
            if bone and "01_Face Off" in bone:
                return bone["01_Face Off"] == 0
        return False


# НОВОЕ: Панель системы цвета глаз
class THRIG_PT_EyeColorPanel(bpy.types.Panel):
    bl_label = "Eye Color System"
    bl_idname = "THRIG_PT_eye_color"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rig Tools"

    @classmethod
    def poll(cls, context):
        rig = context.active_object
        return rig and rig.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        rig = context.active_object
        props = rig.thrig_eye_props  # Получает свойства из самого рига, а не из сцены
        
        # Чекбокс синхронизации
        layout.prop(props, "sync_eyes", text="Sync Both Eyes")
        layout.separator()
        
        if props.sync_eyes:
            # Режим синхронизации - всего 8 цветов
            box = layout.box()
            box.label(text="Eyebrow", icon='CURVE_BEZCURVE')
            box.prop(props, "eyebrow_color1", text="")
            box.prop(props, "eyebrow_color2", text="")
            
            box = layout.box()
            box.label(text="Iris", icon='MATSPHERE')
            box.prop(props, "iris_color1", text="")
            box.prop(props, "iris_color2", text="")
            
            box = layout.box()
            box.label(text="Pupil", icon='MATCUBE')
            box.prop(props, "pupil_color1", text="")
            box.prop(props, "pupil_color2", text="")
            
            box = layout.box()
            box.label(text="Sclera", icon='LIGHT_SUN')
            box.prop(props, "sclera_color1", text="")
            box.prop(props, "sclera_color2", text="")
        else:
            # Индивидуальный режим - цвета в строках (правый | левый)
            box = layout.box()
            box.label(text="Eyebrow", icon='CURVE_BEZCURVE')
            
            # Цвет бровей 1 - правый и левый в одну строку
            row = box.row(align=True)
            row.prop(props, "right_eyebrow_color1", text="")
            row.prop(props, "left_eyebrow_color1", text="")
            
            # Цвет бровей 2 - правый и левый в одну строку
            row = box.row(align=True)
            row.prop(props, "right_eyebrow_color2", text="")
            row.prop(props, "left_eyebrow_color2", text="")
            
            box = layout.box()
            box.label(text="Iris", icon='MATSPHERE')
            
            # Цвет радужки 1 - правый и левый в одну строку
            row = box.row(align=True)
            row.prop(props, "right_iris_color1", text="")
            row.prop(props, "left_iris_color1", text="")
            
            # Цвет радужки 2 - правый и левый в одну строку
            row = box.row(align=True)
            row.prop(props, "right_iris_color2", text="")
            row.prop(props, "left_iris_color2", text="")
            
            box = layout.box()
            box.label(text="Pupil", icon='MATCUBE')
            
            # Цвет зрачка 1 - правый и левый в одну строку
            row = box.row(align=True)
            row.prop(props, "right_pupil_color1", text="")
            row.prop(props, "left_pupil_color1", text="")
            
            # Цвет зрачка 2 - правый и левый в одну строку
            row = box.row(align=True)
            row.prop(props, "right_pupil_color2", text="")
            row.prop(props, "left_pupil_color2", text="")
            
            box = layout.box()
            box.label(text="Sclera", icon='LIGHT_SUN')
            
            # Цвет белка 1 - правый и левый в одну строку
            row = box.row(align=True)
            row.prop(props, "right_sclera_color1", text="")
            row.prop(props, "left_sclera_color1", text="")
            
            # Цвет белка 2 - правый и левый в одну строку
            row = box.row(align=True)
            row.prop(props, "right_sclera_color2", text="")
            row.prop(props, "left_sclera_color2", text="")


def register():
    bpy.utils.register_class(THRIG_PT_MainPanel)
    bpy.utils.register_class(THRIG_PT_FaceTogglePanel)
    bpy.utils.register_class(THRIG_PT_EyeColorPanel)

def unregister():
    bpy.utils.unregister_class(THRIG_PT_EyeColorPanel)
    bpy.utils.unregister_class(THRIG_PT_FaceTogglePanel)
    bpy.utils.unregister_class(THRIG_PT_MainPanel)