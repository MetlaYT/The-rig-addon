import bpy
import os
import json
import shutil
import zipfile
from bpy.props import StringProperty, EnumProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup, Operator, AddonPreferences
from bpy_extras.io_utils import ImportHelper, ExportHelper

# Путь к файлу с данными о кастомных ригах
def get_custom_rigs_file():
    return os.path.join(os.path.dirname(__file__), "assets", "custom_rigs.json")

def get_custom_rigs_folder():
    return os.path.join(os.path.dirname(__file__), "assets", "custom")

def load_custom_rigs():
    """Загрузить список кастомных ригов из JSON"""
    filepath = get_custom_rigs_file()
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_custom_rigs(rigs_data):
    """Сохранить список кастомных ригов в JSON"""
    filepath = get_custom_rigs_file()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(rigs_data, f, indent=2, ensure_ascii=False)

def get_base_rig_collection_name(base_type):
    """Получить имя коллекции для аппенда в зависимости от базового типа"""
    mapping = {
        'THERIG': 'TheRig(Append)',
        'THERIGMOD': 'TheRig[Modify](Append)',
        'THESIMPLE': 'TheSimple(Append)',
        'THEPLUSH': 'ThePlush(Append)',
        'THEBUFF': 'TheBufff(Append)',
    }
    return mapping.get(base_type, 'TheRig(Append)')

def get_base_rig_id(base_type):
    """Получить RigId для базового типа"""
    mapping = {
        'THERIG': 'TheRigA',
        'THERIGMOD': 'TheRigMA',
        'THESIMPLE': 'TheSimpleA',
        'THEPLUSH': 'ThePlushA',
        'THEBUFF': 'TheBuffA',
    }
    return mapping.get(base_type, 'TheRigA')


class THRIG_OT_AddCustomRig(Operator):
    bl_idname = "thrig.add_custom_rig"
    bl_label = "Add Custom Rig"
    bl_description = "Add a custom rig from the currently open file"
    bl_options = {'REGISTER', 'UNDO'}
    
    rig_name: StringProperty(
        name="Rig Name",
        description="Name for your custom rig (English only)",
        default=""
    )
    
    author_name: StringProperty(
        name="Author",
        description="Author of this rig",
        default=""
    )
    
    website: StringProperty(
        name="Website",
        description="Author's website or portfolio URL",
        default=""
    )
    
    base_type: EnumProperty(
        name="Base Rig",
        description="Which rig was this based on",
        items=[
            ('THERIG', "TheRig", "Based on TheRig"),
            ('THERIGMOD', "TheRig Modify", "Based on TheRig Modify (Zealum Edit)"),
            ('THESIMPLE', "TheSimple", "Based on TheSimple"),
            ('THEPLUSH', "ThePlush", "Based on ThePlush"),
            ('THEBUFF', "TheBuff", "Based on TheBuff"),
        ],
        default='THERIG'
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "rig_name")
        layout.prop(self, "base_type")
        layout.separator()
        layout.prop(self, "author_name")
        layout.prop(self, "website")
    
    def execute(self, context):
        if not self.rig_name:
            self.report({'ERROR'}, "Please enter a rig name!")
            return {'CANCELLED'}
        
        # Проверяем что имя на английском (базовая проверка)
        if not self.rig_name.isascii():
            self.report({'ERROR'}, "Rig name must be in English (ASCII characters only)!")
            return {'CANCELLED'}
        
        # Проверяем что файл открыт и сохранён
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Please save your .blend file first!")
            return {'CANCELLED'}
        
        source_filepath = bpy.data.filepath
        
        # Ищем коллекцию для аппенда
        base_collection_name = get_base_rig_collection_name(self.base_type)
        append_collection = None
        original_collection_name = None
        
        for coll in bpy.data.collections:
            if "(Append)" in coll.name:
                append_collection = coll
                original_collection_name = coll.name
                break
        
        if not append_collection:
            self.report({'ERROR'}, f"No (Append) collection found in current file! Expected something like '{base_collection_name}'")
            return {'CANCELLED'}
        
        # Создаём папку для кастомных ригов если её нет
        custom_folder = get_custom_rigs_folder()
        if not os.path.exists(custom_folder):
            os.makedirs(custom_folder)
        
        # Новое имя для файла и коллекции
        new_collection_name = f"{self.rig_name}(Append)"
        new_filename = f"{self.rig_name}.blend"
        dest_filepath = os.path.join(custom_folder, new_filename)
        
        # Проверяем что такого рига ещё нет
        existing_rigs = load_custom_rigs()
        for rig in existing_rigs:
            if rig['name'].lower() == self.rig_name.lower():
                self.report({'ERROR'}, f"Rig '{self.rig_name}' already exists!")
                return {'CANCELLED'}
        
        try:
            # Переименовываем коллекцию в текущем файле
            old_name = append_collection.name
            append_collection.name = new_collection_name
            
            # Сохраняем как новый файл
            bpy.ops.wm.save_as_mainfile(filepath=dest_filepath, copy=True)
            
            # Возвращаем старое имя коллекции
            append_collection.name = old_name
            
            # Сохраняем информацию о риге
            rig_data = {
                'name': self.rig_name,
                'filename': new_filename,
                'collection_name': new_collection_name,
                'base_type': self.base_type,
                'rig_id': get_base_rig_id(self.base_type),
                'author': self.author_name,
                'website': self.website
            }
            
            existing_rigs.append(rig_data)
            save_custom_rigs(existing_rigs)
            
            self.report({'INFO'}, f"Custom rig '{self.rig_name}' added successfully!")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add rig: {str(e)}")
            return {'CANCELLED'}


class THRIG_OT_RemoveCustomRig(Operator):
    bl_idname = "thrig.remove_custom_rig"
    bl_label = "Remove Custom Rig"
    bl_description = "Remove a custom rig"
    bl_options = {'REGISTER', 'UNDO'}
    
    rig_name: StringProperty()
    
    def execute(self, context):
        rigs = load_custom_rigs()
        
        # Ищем риг для удаления
        rig_to_remove = None
        for rig in rigs:
            if rig['name'] == self.rig_name:
                rig_to_remove = rig
                break
        
        if not rig_to_remove:
            self.report({'ERROR'}, f"Rig '{self.rig_name}' not found!")
            return {'CANCELLED'}
        
        # Удаляем файл
        custom_folder = get_custom_rigs_folder()
        filepath = os.path.join(custom_folder, rig_to_remove['filename'])
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            self.report({'WARNING'}, f"Could not delete file: {str(e)}")
        
        # Удаляем из списка
        rigs.remove(rig_to_remove)
        save_custom_rigs(rigs)
        
        self.report({'INFO'}, f"Rig '{self.rig_name}' removed!")
        return {'FINISHED'}


class THRIG_OT_EditCustomRig(Operator):
    bl_idname = "thrig.edit_custom_rig"
    bl_label = "Edit Custom Rig"
    bl_description = "Edit custom rig settings"
    bl_options = {'REGISTER', 'UNDO'}
    
    rig_name: StringProperty()
    
    new_author: StringProperty(name="Author", default="")
    new_website: StringProperty(name="Website", default="")
    
    def invoke(self, context, event):
        rigs = load_custom_rigs()
        for rig in rigs:
            if rig['name'] == self.rig_name:
                self.new_author = rig.get('author', '')
                self.new_website = rig.get('website', '')
                break
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Editing: {self.rig_name}")
        layout.prop(self, "new_author")
        layout.prop(self, "new_website")
    
    def execute(self, context):
        rigs = load_custom_rigs()
        
        for rig in rigs:
            if rig['name'] == self.rig_name:
                rig['author'] = self.new_author
                rig['website'] = self.new_website
                break
        
        save_custom_rigs(rigs)
        self.report({'INFO'}, f"Rig '{self.rig_name}' updated!")
        return {'FINISHED'}


class THRIG_OT_AppendCustomRig(Operator):
    bl_idname = "thrig.append_custom_rig"
    bl_label = "Append Custom Rig"
    bl_description = "Add custom rig to the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    rig_name: StringProperty()
    
    def execute(self, context):
        rigs = load_custom_rigs()
        
        rig_data = None
        for rig in rigs:
            if rig['name'] == self.rig_name:
                rig_data = rig
                break
        
        if not rig_data:
            self.report({'ERROR'}, f"Rig '{self.rig_name}' not found!")
            return {'CANCELLED'}
        
        custom_folder = get_custom_rigs_folder()
        filepath = os.path.join(custom_folder, rig_data['filename'])
        
        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Rig file not found: {filepath}")
            return {'CANCELLED'}
        
        try:
            # Используем оригинальное имя коллекции из файла
            collection_name = rig_data['collection_name']
            
            bpy.ops.wm.append(
                filepath=os.path.join(filepath, "Collection", collection_name),
                directory=os.path.join(filepath, "Collection"),
                filename=collection_name
            )
            
            self.report({'INFO'}, f"Added {self.rig_name}!")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to append rig: {str(e)}")
            return {'CANCELLED'}


# Список кастомных ригов для UI
class THRIG_UL_CustomRigsList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='ARMATURE_DATA')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='ARMATURE_DATA')


class CustomRigItem(PropertyGroup):
    name: StringProperty()
    base_type: StringProperty()
    author: StringProperty()
    website: StringProperty()


class THRIG_OT_ExportCustomRig(Operator, ExportHelper):
    bl_idname = "thrig.export_custom_rig"
    bl_label = "Export Custom Rig"
    bl_description = "Export a custom rig as a shareable .zip file"
    
    filename_ext = ".zip"
    filter_glob: StringProperty(default="*.zip", options={'HIDDEN'})
    
    rig_name: StringProperty()
    
    def execute(self, context):
        rigs = load_custom_rigs()
        
        rig_data = None
        for rig in rigs:
            if rig['name'] == self.rig_name:
                rig_data = rig
                break
        
        if not rig_data:
            self.report({'ERROR'}, f"Rig '{self.rig_name}' not found!")
            return {'CANCELLED'}
        
        custom_folder = get_custom_rigs_folder()
        blend_filepath = os.path.join(custom_folder, rig_data['filename'])
        
        if not os.path.exists(blend_filepath):
            self.report({'ERROR'}, f"Rig file not found!")
            return {'CANCELLED'}
        
        try:
            # Создаём zip архив
            with zipfile.ZipFile(self.filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Добавляем .blend файл
                zipf.write(blend_filepath, rig_data['filename'])
                
                # Создаём и добавляем info.json с метаданными
                info = {
                    'name': rig_data['name'],
                    'collection_name': rig_data['collection_name'],
                    'base_type': rig_data['base_type'],
                    'rig_id': rig_data['rig_id'],
                    'author': rig_data.get('author', ''),
                    'website': rig_data.get('website', ''),
                    'version': '1.0'
                }
                info_json = json.dumps(info, indent=2, ensure_ascii=False)
                zipf.writestr('info.json', info_json)
            
            self.report({'INFO'}, f"Exported '{self.rig_name}' to {self.filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export: {str(e)}")
            return {'CANCELLED'}


class THRIG_OT_ImportCustomRig(Operator, ImportHelper):
    bl_idname = "thrig.import_custom_rig"
    bl_label = "Import Custom Rig"
    bl_description = "Import a custom rig from a .zip file"
    
    filename_ext = ".zip"
    filter_glob: StringProperty(default="*.zip", options={'HIDDEN'})
    
    def execute(self, context):
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "File not found!")
            return {'CANCELLED'}
        
        custom_folder = get_custom_rigs_folder()
        if not os.path.exists(custom_folder):
            os.makedirs(custom_folder)
        
        try:
            with zipfile.ZipFile(self.filepath, 'r') as zipf:
                # Читаем info.json
                if 'info.json' not in zipf.namelist():
                    self.report({'ERROR'}, "Invalid rig package: info.json not found!")
                    return {'CANCELLED'}
                
                info_data = zipf.read('info.json')
                info = json.loads(info_data.decode('utf-8'))
                
                rig_name = info['name']
                
                # Проверяем что такого рига ещё нет
                existing_rigs = load_custom_rigs()
                for rig in existing_rigs:
                    if rig['name'].lower() == rig_name.lower():
                        self.report({'ERROR'}, f"Rig '{rig_name}' already exists!")
                        return {'CANCELLED'}
                
                # Извлекаем .blend файл
                blend_filename = f"{rig_name}.blend"
                for name in zipf.namelist():
                    if name.endswith('.blend'):
                        # Извлекаем с новым именем
                        blend_data = zipf.read(name)
                        dest_path = os.path.join(custom_folder, blend_filename)
                        with open(dest_path, 'wb') as f:
                            f.write(blend_data)
                        break
                else:
                    self.report({'ERROR'}, "Invalid rig package: .blend file not found!")
                    return {'CANCELLED'}
                
                # Добавляем в список ригов
                rig_data = {
                    'name': rig_name,
                    'filename': blend_filename,
                    'collection_name': info['collection_name'],
                    'base_type': info['base_type'],
                    'rig_id': info['rig_id'],
                    'author': info.get('author', ''),
                    'website': info.get('website', '')
                }
                
                existing_rigs.append(rig_data)
                save_custom_rigs(existing_rigs)
                
                self.report({'INFO'}, f"Imported '{rig_name}' successfully!")
                return {'FINISHED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import: {str(e)}")
            return {'CANCELLED'}


def draw_custom_rigs_panel(self, context):
    """Рисует секцию кастомных ригов в настройках аддона"""
    layout = self.layout
    
    box = layout.box()
    box.label(text="Custom Rigs", icon='ARMATURE_DATA')
    
    # Кнопки добавления и импорта
    row = box.row(align=True)
    row.operator("thrig.add_custom_rig", text="Add Custom Rig", icon='ADD')
    row.operator("thrig.import_custom_rig", text="Import .zip", icon='IMPORT')
    
    box.separator()
    
    # Список существующих кастомных ригов
    rigs = load_custom_rigs()
    
    if not rigs:
        box.label(text="No custom rigs added yet", icon='INFO')
    else:
        # Группируем по base_type
        base_types = {}
        for rig in rigs:
            bt = rig.get('base_type', 'THERIG')
            if bt not in base_types:
                base_types[bt] = []
            base_types[bt].append(rig)
        
        for base_type, rig_list in base_types.items():
            # Заголовок группы
            group_box = box.box()
            group_box.label(text=f"Based on {base_type}", icon='FILE_FOLDER')
            
            for rig in rig_list:
                rig_box = group_box.box()
                
                row = rig_box.row()
                row.label(text=rig['name'], icon='ARMATURE_DATA')
                
                if rig.get('author'):
                    rig_box.label(text=f"Author: {rig['author']}")
                if rig.get('website'):
                    rig_box.label(text=f"Website: {rig['website']}")
                
                row = rig_box.row(align=True)
                op = row.operator("thrig.edit_custom_rig", text="Edit", icon='GREASEPENCIL')
                op.rig_name = rig['name']
                op = row.operator("thrig.export_custom_rig", text="Export", icon='EXPORT')
                op.rig_name = rig['name']
                op = row.operator("thrig.remove_custom_rig", text="Remove", icon='TRASH')
                op.rig_name = rig['name']


def menu_func_custom_rigs(self, context):
    """Добавляет подменю кастомных ригов в меню Add"""
    rigs = load_custom_rigs()
    
    if rigs:
        self.layout.menu("THRIG_MT_custom_rigs", icon='ARMATURE_DATA')


class THRIG_MT_CustomRigsMenu(bpy.types.Menu):
    bl_idname = "THRIG_MT_custom_rigs"
    bl_label = "Custom Rigs"
    
    def draw(self, context):
        layout = self.layout
        rigs = load_custom_rigs()
        
        if not rigs:
            layout.label(text="No custom rigs", icon='INFO')
        else:
            for rig in rigs:
                op = layout.operator(
                    "thrig.append_custom_rig",
                    text=rig['name'],
                    icon='ARMATURE_DATA'
                )
                op.rig_name = rig['name']


classes = [
    CustomRigItem,
    THRIG_OT_AddCustomRig,
    THRIG_OT_RemoveCustomRig,
    THRIG_OT_EditCustomRig,
    THRIG_OT_AppendCustomRig,
    THRIG_OT_ExportCustomRig,
    THRIG_OT_ImportCustomRig,
    THRIG_UL_CustomRigsList,
    THRIG_MT_CustomRigsMenu,
]


def menu_func_custom_rigs(self, context):
    """Добавляет подменю Community Rigs в меню Add"""
    rigs = load_custom_rigs()
    if rigs:  # Показываем только если есть кастомные риги
        self.layout.separator()
        self.layout.menu("THRIG_MT_custom_rigs", text="Community Rigs", icon='COMMUNITY')


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Добавляем подменю в Shift+A
    bpy.types.VIEW3D_MT_add.append(menu_func_custom_rigs)


def unregister():
    # Убираем подменю из Shift+A
    bpy.types.VIEW3D_MT_add.remove(menu_func_custom_rigs)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
