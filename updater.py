import bpy
import urllib.request
import json
import os
import zipfile
import shutil
import tempfile
import threading

GITHUB_REPO = "MetlaYT/The-rig-addon"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
ADDON_NAME = "The_rig_addon"

update_available = False
latest_version = None
download_url = None


def get_current_version():
    from . import bl_info
    return bl_info["version"]


def version_tuple_to_string(version_tuple):
    return ".".join(str(v) for v in version_tuple)


def string_to_version_tuple(version_string):
    version_string = version_string.lstrip("vV")
    parts = version_string.split(".")
    return tuple(int(p) for p in parts[:3])


def is_newer_version(remote_version, local_version):
    for r, l in zip(remote_version, local_version):
        if r > l:
            return True
        elif r < l:
            return False
    return False


def check_for_updates_thread():
    global update_available, latest_version, download_url
    
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={'User-Agent': 'Blender-TheRig-Addon'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        tag_name = data.get("tag_name", "0.0.0")
        remote_version = string_to_version_tuple(tag_name)
        local_version = get_current_version()
        
        if is_newer_version(remote_version, local_version):
            update_available = True
            latest_version = remote_version
            
            assets = data.get("assets", [])
            for asset in assets:
                if asset["name"].endswith(".zip"):
                    download_url = asset["browser_download_url"]
                    break
            
            if not download_url:
                download_url = data.get("zipball_url")
            
            def show_update_popup():
                bpy.ops.therig.update_popup('INVOKE_DEFAULT')
            
            bpy.app.timers.register(show_update_popup, first_interval=1.0)
            
    except Exception as e:
        print(f"[TheRig] Update check failed: {e}")


def check_for_updates():
    thread = threading.Thread(target=check_for_updates_thread, daemon=True)
    thread.start()


class THERIG_OT_UpdatePopup(bpy.types.Operator):
    bl_idname = "therig.update_popup"
    bl_label = "TheRig Update Available"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)
    
    def draw(self, context):
        layout = self.layout
        
        local_ver = version_tuple_to_string(get_current_version())
        remote_ver = version_tuple_to_string(latest_version) if latest_version else "?"
        
        layout.label(text="New version of TheRig addon available!", icon='INFO')
        layout.separator()
        
        row = layout.row()
        row.label(text=f"Current version: {local_ver}")
        row.label(text=f"New version: {remote_ver}")
        
        layout.separator()
        layout.operator("therig.download_update", text="Download Update", icon='IMPORT')
        layout.operator("therig.open_github", text="Open GitHub Page", icon='URL')


class THERIG_OT_OpenGitHub(bpy.types.Operator):
    bl_idname = "therig.open_github"
    bl_label = "Open GitHub"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        import webbrowser
        webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
        return {'FINISHED'}


class THERIG_OT_DownloadUpdate(bpy.types.Operator):
    bl_idname = "therig.download_update"
    bl_label = "Download Update"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        global download_url
        
        if not download_url:
            self.report({'ERROR'}, "Download URL not available")
            return {'CANCELLED'}
        
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "therig_update.zip")
            
            self.report({'INFO'}, "Downloading update...")
            
            req = urllib.request.Request(
                download_url,
                headers={'User-Agent': 'Blender-TheRig-Addon'}
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                with open(zip_path, 'wb') as f:
                    f.write(response.read())
            
            addon_path = os.path.dirname(os.path.realpath(__file__))
            parent_path = os.path.dirname(addon_path)
            
            extract_path = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            extracted_folders = os.listdir(extract_path)
            if len(extracted_folders) == 1:
                source_path = os.path.join(extract_path, extracted_folders[0])
            else:
                source_path = extract_path
            
            backup_path = addon_path + "_backup"
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.move(addon_path, backup_path)
            
            shutil.move(source_path, addon_path)
            
            shutil.rmtree(backup_path)
            shutil.rmtree(temp_dir)
            
            self.report({'INFO'}, "Update downloaded! Please restart Blender to apply.")
            
            bpy.ops.therig.restart_prompt('INVOKE_DEFAULT')
            
        except Exception as e:
            self.report({'ERROR'}, f"Update failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class THERIG_OT_RestartPrompt(bpy.types.Operator):
    bl_idname = "therig.restart_prompt"
    bl_label = "Restart Required"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Update installed successfully!", icon='CHECKMARK')
        layout.label(text="Please restart Blender to apply changes.")


class THERIG_OT_CheckUpdates(bpy.types.Operator):
    bl_idname = "therig.check_updates"
    bl_label = "Check for Updates"
    bl_description = "Check for TheRig addon updates"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        global update_available, latest_version, download_url
        update_available = False
        latest_version = None
        download_url = None
        
        check_for_updates()
        self.report({'INFO'}, "Checking for updates...")
        return {'FINISHED'}


@bpy.app.handlers.persistent
def check_updates_on_load(dummy):
    check_for_updates()


classes = [
    THERIG_OT_UpdatePopup,
    THERIG_OT_OpenGitHub,
    THERIG_OT_DownloadUpdate,
    THERIG_OT_RestartPrompt,
    THERIG_OT_CheckUpdates,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    if check_updates_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(check_updates_on_load)
    
    bpy.app.timers.register(check_for_updates, first_interval=3.0)


def unregister():
    if check_updates_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(check_updates_on_load)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
