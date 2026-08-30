import os
import sys
import json
import shutil
import threading
import time
import socket
import winreg
import ctypes
from datetime import datetime
import base64
import requests
import webview
import pystray
from PIL import Image
import psutil  # Lightweight process scanner

# Module-level references
window = None
tray_icon = None

# --- NATIVE WINDOW ICON OVERRIDE ---
try:
    myappid = 'bedrockcapsule.app.2.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# ==========================================
# 🌐 THE RESOURCE LOCATOR
# ==========================================
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

# ==========================================
# 🌐 PATHS & CONFIG 
# ==========================================
CLOUD_GATEWAY_URL = "https://bedrockcapsule-api.onrender.com/api/notify"
DEFAULT_BACKUP_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'BedrockCapsule_Backups')

local_app_data = os.environ.get('LOCALAPPDATA')
if not local_app_data:
    local_app_data = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')

CONFIG_DIR = os.path.join(local_app_data, "BedrockCapsule")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Legacy fallback for backups folder
legacy_backup_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'World_Backup')
if os.path.exists(legacy_backup_dir) and not os.path.exists(DEFAULT_BACKUP_DIR):
    DEFAULT_BACKUP_DIR = legacy_backup_dir

# --- ANTI-DUPLICATE & AUTOSTART SHIELD ---
PORT = 45555
def enforce_single_instance_and_autostart():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', PORT))
        s.listen(1)
        
        def listen_for_wakeup():
            while True:
                try:
                    conn, addr = s.accept()
                    data = conn.recv(1024)
                    if b"WAKEUP" in data:
                        try:
                            if window:
                                window.show()
                                window.restore()
                        except: pass
                    conn.close()
                except: pass
        threading.Thread(target=listen_for_wakeup, daemon=True).start()
    except socket.error:
        try:
            s_wake = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_wake.connect(('127.0.0.1', PORT))
            s_wake.sendall(b"WAKEUP")
            s_wake.close()
        except: pass
        sys.exit(0)

    try:
        if getattr(sys, 'frozen', False): 
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "BedrockCapsule"
            exe_path = sys.executable
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --autostart')
            winreg.CloseKey(key)
    except Exception as e:
        pass

def get_saved_theme():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("theme", "dark")
        except: pass
    return "dark"

def get_boot_html(theme):
    original_html_path = get_resource_path('index.html')
    original_logo_path = get_resource_path('logo.ico')
    
    try:
        with open(original_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception:
        html_content = "<!DOCTYPE html><html><body style='background:#121212;color:white;'><h2>Loading BedrockCapsule...</h2></body></html>"
        
    if theme == "light":
        html_content = html_content.replace('<html lang="en" data-theme="dark">', '<html lang="en" data-theme="light">')
    else:
        html_content = html_content.replace('<html lang="en" data-theme="light">', '<html lang="en" data-theme="dark">')
        
    try:
        if os.path.exists(original_logo_path):
            with open(original_logo_path, "rb") as f_logo:
                logo_b64 = base64.b64encode(f_logo.read()).decode("ascii")
                html_content = html_content.replace('src="logo.ico"', f'src="data:image/x-icon;base64,{logo_b64}"')
    except Exception:
        pass
        
    return html_content

def xor_crypt(file_path, key):
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)
    if key_len == 0: return
    chunk_size = 1024 * 512
    temp_path = file_path + ".tmp"
    try:
        with open(file_path, 'rb') as f_in, open(temp_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if not chunk: break
                expanded_key = (key_bytes * (len(chunk) // key_len + 1))[:len(chunk)]
                f_out.write(bytes(a ^ b for a, b in zip(chunk, expanded_key)))
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_path, file_path)
    except:
        if os.path.exists(temp_path):
            try: os.remove(temp_path)
            except: pass

class Api:
    def __init__(self):
        self.worlds_data = {}
        self.auto_pilot_running = False

    def minimize_window(self):
        try:
            if window: window.minimize()
        except: pass

    def close_window(self):
        try:
            if window: window.hide()
        except: pass

    def open_external_url(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except:
            return False

    def get_active_backup_dir(self, world_name=None):
        config = self.load_config()
        if world_name:
            routes = config.get("world_routes", {})
            if world_name in routes and routes[world_name] and os.path.exists(routes[world_name]):
                return routes[world_name]
        custom_path = config.get("custom_path", "")
        return custom_path if custom_path and os.path.exists(custom_path) else DEFAULT_BACKUP_DIR

    def open_backup_directory(self, world_name=None):
        try:
            target_dir = self.get_active_backup_dir(world_name)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            os.startfile(target_dir)
        except: pass

    def select_custom_path(self):
        try:
            if window:
                folder = window.create_file_dialog(webview.FOLDER_DIALOG)
                if folder and len(folder) > 0:
                    selected_path = folder[0]
                    config = self.load_config()
                    config["custom_path"] = selected_path
                    self.save_raw_config(config)
                    return selected_path
        except: pass
        return None

    def push_status(self, message, color_var="--text-muted"):
        try:
            if window:
                msg_json = json.dumps(str(message))
                col_json = json.dumps(str(color_var))
                window.evaluate_js(f"updateUIStatus({msg_json}, {col_json})")
        except: pass

    def load_config(self):
        config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: 
                    config = json.load(f)
            except: pass
        
        defaults = {
            "channel_id": "", 
            "auto_pilot": False, 
            "theme": "dark", 
            "ignore_launches": True, 
            "smart_storage": 5,
            "target_world": "",
            "custom_path": "",
            "analytics_playtime_sec": 0,
            "analytics_saves": 0,
            "session_logs": [],
            "desktop_notifications": True,
            "auto_compress": False,
            "world_routes": {},
            "auto_detect_world": False,
            "health_reminders": True,
            "backup_addons": False,
            "encryption_key": ""
        }
        for k, v in defaults.items():
            if k not in config: config[k] = v
        return config

    def get_session_logs(self):
        config = self.load_config()
        return config.get("session_logs", [])

    def _is_valid_archive(self, item_path, item_name):
        if item_name.endswith("_CRASH_RECOVERY") or item_name.startswith("_Addons_") or item_name.endswith(".tmp") or item_name.endswith(".decrypted.zip"):
            return False
        if item_name.endswith(".mcworld") or item_name.endswith(".locked"):
            return True
        if os.path.isdir(item_path):
            if os.path.exists(os.path.join(item_path, "levelname.txt")) or os.path.exists(os.path.join(item_path, "db")):
                return True
            try:
                datetime.strptime(item_name[-17:], "%Y_%m_%d_%H%M%S")
                return True
            except: pass
        return False

    def get_total_archives_count(self):
        config = self.load_config()
        paths_to_scan = set()
        
        paths_to_scan.add(DEFAULT_BACKUP_DIR)
        custom_path = config.get("custom_path", "").strip()
        if custom_path and os.path.exists(custom_path):
            paths_to_scan.add(custom_path)
            
        routes = config.get("world_routes", {})
        for w, p in routes.items():
            if p and os.path.exists(p):
                paths_to_scan.add(p)
                
        total = 0
        for path in paths_to_scan:
            if not os.path.exists(path): continue
            try:
                for item_name in os.listdir(path):
                    item_path = os.path.join(path, item_name)
                    if self._is_valid_archive(item_path, item_name):
                        total += 1
            except: pass
            
        return total

    def add_session_log(self, world_name, duration_sec, status):
        config = self.load_config()
        logs = config.get("session_logs", [])
        minutes = round(duration_sec / 60, 1)
        duration_str = f"{minutes} min"
        date_str = datetime.now().strftime("%b %d, %Y @ %I:%M %p")
        
        logs.insert(0, {
            "date": date_str,
            "world": world_name,
            "duration": duration_str,
            "status": status
        })
        
        if len(logs) > 30:
            logs = logs[:30]
            
        config["session_logs"] = logs
        self.save_raw_config(config)

    def save_raw_config(self, config_dict):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: 
                json.dump(config_dict, f, indent=4)
        except: pass

    def save_config(self, channel_id, auto_pilot, theme, ignore_launches, smart_storage, target_world, desktop_notifications=True, auto_compress=False, auto_detect_world=False, health_reminders=True, backup_addons=False, encryption_key=""):
        config = self.load_config()
        config.update({
            "channel_id": channel_id, 
            "auto_pilot": auto_pilot, 
            "theme": theme,
            "ignore_launches": ignore_launches, 
            "smart_storage": smart_storage,
            "target_world": target_world,
            "desktop_notifications": desktop_notifications,
            "auto_compress": auto_compress,
            "auto_detect_world": auto_detect_world,
            "health_reminders": health_reminders,
            "backup_addons": backup_addons,
            "encryption_key": encryption_key
        })
        self.save_raw_config(config)

    def save_world_route(self, world_name, custom_path):
        if not world_name: return False
        config = self.load_config()
        if "world_routes" not in config: config["world_routes"] = {}
        config["world_routes"][world_name] = custom_path
        self.save_raw_config(config)
        return True

    def get_world_route(self, world_name):
        config = self.load_config()
        routes = config.get("world_routes", {})
        return routes.get(world_name, "")

    def scan_worlds(self):
        self.worlds_data = {}
        search_paths = []
        appdata = os.environ.get('APPDATA')
        localappdata = os.environ.get('LOCALAPPDATA')
        
        if appdata:
            alt_bedrock_base = os.path.join(appdata, "Minecraft Bedrock", "Users")
            if os.path.exists(alt_bedrock_base):
                try:
                    for folder in os.listdir(alt_bedrock_base):
                        search_paths.append(os.path.join(alt_bedrock_base, folder, "games", "com.mojang", "minecraftWorlds"))
                except: pass

        if localappdata:
            search_paths.append(os.path.join(localappdata, "Packages", "Microsoft.MinecraftUWP_8wekyb3d8bbwe", "LocalState", "games", "com.mojang", "minecraftWorlds"))
            search_paths.append(os.path.join(localappdata, "Packages", "Microsoft.MinecraftWindowsBeta_8wekyb3d8bbwe", "LocalState", "games", "com.mojang", "minecraftWorlds"))
            
        for target_path in search_paths:
            if not os.path.exists(target_path): continue
            try:
                for folder_name in os.listdir(target_path):
                    folder_path = os.path.join(target_path, folder_name)
                    if not os.path.isdir(folder_path): continue
                    level_txt = os.path.join(folder_path, "levelname.txt")
                    if os.path.exists(level_txt):
                        try:
                            with open(level_txt, "r", encoding="utf-8", errors="ignore") as f:
                                clean_name = f.read().strip() or f"Unnamed World ({folder_name[:6]})"
                                if clean_name in self.worlds_data: clean_name = f"{clean_name} ({folder_name[:4]})"
                                self.worlds_data[clean_name] = folder_path
                        except: pass
            except: pass
        return list(self.worlds_data.keys())

    def get_archives_data(self, world_name=None):
        active_dir = self.get_active_backup_dir(world_name)
        if not os.path.exists(active_dir): return []
        
        safe_name = "".join(c for c in world_name if c.isalnum() or c in " _-").strip() if world_name else ""
        
        archive_list = []
        for item_name in os.listdir(active_dir):
            item_path = os.path.join(active_dir, item_name)
            
            # Filter archives to only show the ones for the selected world
            if safe_name:
                raw = item_name.replace(".mcworld", "").replace(".locked", "")
                if len(raw) >= 18 and raw[-18:].startswith("_20"):
                    if raw[:-18] != safe_name:
                        continue
                elif not item_name.startswith(safe_name + "_"):
                    continue
                
            if self._is_valid_archive(item_path, item_name):
                try:
                    if os.path.isdir(item_path):
                        size_bytes = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(item_path) for filename in filenames)
                    else:
                        size_bytes = os.path.getsize(item_path)
                    size_mb = round(size_bytes / (1024 * 1024), 1)
                    
                    try:
                        time_str = item_name.replace(".mcworld", "").replace(".locked", "")[-17:]  
                        dt_obj = datetime.strptime(time_str, "%Y_%m_%d_%H%M%S")
                        formatted_date = dt_obj.strftime("%b %d, %Y @ %I:%M %p")
                        sort_time = dt_obj.timestamp()
                    except:
                        sort_time = os.path.getmtime(item_path)
                        formatted_date = datetime.fromtimestamp(sort_time).strftime("%b %d, %Y @ %I:%M %p")

                    archive_list.append({
                        "name": item_name,
                        "size": f"{size_mb} MB",
                        "date": formatted_date,
                        "timestamp_raw": sort_time 
                    })
                except: pass
        archive_list.sort(key=lambda x: x["timestamp_raw"], reverse=True)
        return archive_list

    def rename_archive(self, old_name, new_name, world_name=None):
        if not old_name or not new_name: return False
        active_dir = self.get_active_backup_dir(world_name)
        old_path = os.path.join(active_dir, old_name)
        if not os.path.exists(old_path): return False

        is_zip = old_name.endswith(".mcworld")
        is_locked = old_name.endswith(".locked")
        
        raw_old_name = old_name.replace(".mcworld", "").replace(".locked", "")
        # Keep the timestamp intact when renaming to preserve order
        timestamp_part = raw_old_name[-18:] if len(raw_old_name) >= 18 and raw_old_name[-18:].startswith('_20') else ""
        safe_new_name = "".join(c for c in new_name if c.isalnum() or c in " _-").strip()
        if not safe_new_name: return False

        final_new_name = f"{safe_new_name}{timestamp_part}" if timestamp_part else safe_new_name
        if is_zip and not is_locked: final_new_name += ".mcworld"
        if is_locked: final_new_name += ".mcworld.locked"

        new_path = os.path.join(active_dir, final_new_name)
        if old_path == new_path: return True
        try:
            os.rename(old_path, new_path)
            return True
        except: return False

    def export_mcworld(self, folder_name, world_name=None):
        threading.Thread(target=self._export_mcworld_thread, args=(folder_name, world_name), daemon=True).start()

    def _export_mcworld_thread(self, folder_name, world_name=None):
        self.push_status("Exporting .mcworld file... Please wait.", "--warning")
        try:
            active_dir = self.get_active_backup_dir(world_name)
            source_dir = os.path.join(active_dir, folder_name)
            
            if folder_name.endswith(".locked"):
                self.push_status("Encrypted backup: Decrypt first before exporting!", "--warning")
                return

            if folder_name.endswith(".mcworld"):
                self.push_status("Archive is already a .mcworld file!", "--success")
                return
            
            if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
                self.push_status("Error: Directory not found.", "--danger")
                return

            output_base = os.path.join(active_dir, folder_name)
            
            # Zip the folder
            shutil.make_archive(output_base, 'zip', source_dir)
            
            # Rename to .mcworld
            zip_file = output_base + '.zip'
            mcworld_file = output_base + '.mcworld'
            if os.path.exists(zip_file):
                if os.path.exists(mcworld_file): os.remove(mcworld_file)
                os.replace(zip_file, mcworld_file)
            
            self.push_status(".mcworld exported to backup folder!", "--success")
        except Exception as e:
            self.push_status(f"Export Error: {str(e)[:40]}", "--danger")
        finally:
            try:
                if window: window.evaluate_js("resetActions()")
            except: pass

    def trigger_backup(self, world_name, channel_id, trigger_type="Manual Sync"):
        if not world_name or world_name not in self.worlds_data:
            self.scan_worlds()
        if not world_name or world_name not in self.worlds_data:
            self.push_status("Error: World not found. Reselect it.", "--danger")
            try:
                if window: window.evaluate_js("resetActions()")
            except: pass
            return
        threading.Thread(target=self._backup_thread, args=(world_name, channel_id, trigger_type), daemon=True).start()

    def _backup_thread(self, world_name, channel_id, trigger_type="Manual Sync"):
        self.push_status("Saving world snapshot...", "--warning")
        try:
            active_dir = self.get_active_backup_dir(world_name)
            os.makedirs(active_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
            safe_name = "".join(c for c in world_name if c.isalnum() or c in " _-").strip()
            
            backup_path = os.path.join(active_dir, f"{safe_name}_{timestamp}")
            world_path = self.worlds_data[world_name]
            
            config = self.load_config()
            auto_compress = config.get("auto_compress", False)
            enc_key = config.get("encryption_key", "").strip()
            if enc_key and not auto_compress: auto_compress = True # Encryption requires single file output
            
            success = False
            for attempt in range(5): 
                try:
                    if auto_compress:
                        zip_file = backup_path + '.zip'
                        mcworld_file = backup_path + '.mcworld'
                        if os.path.exists(zip_file): os.remove(zip_file)
                        shutil.make_archive(backup_path, 'zip', world_path)
                        
                        if os.path.exists(mcworld_file): os.remove(mcworld_file)
                        os.replace(zip_file, mcworld_file)
                        
                        if enc_key:
                            locked_file = mcworld_file + ".locked"
                            xor_crypt(mcworld_file, enc_key)
                            if os.path.exists(locked_file): os.remove(locked_file)
                            os.replace(mcworld_file, locked_file)
                            backup_path = locked_file
                        else:
                            backup_path = mcworld_file
                    else:
                        if os.path.exists(backup_path): shutil.rmtree(backup_path, ignore_errors=True)
                        shutil.copytree(world_path, backup_path, dirs_exist_ok=True)
                    success = True
                    break
                except Exception as e: 
                    time.sleep(2) 
            
            if not success: raise Exception("Minecraft world files locked by another process.")

            # Analytics Update
            config["analytics_saves"] = config.get("analytics_saves", 0) + 1
            self.save_raw_config(config)

            if auto_compress:
                size_bytes = os.path.getsize(backup_path)
            else:
                size_bytes = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(backup_path) for filename in filenames)
            size_mb = round(size_bytes / (1024 * 1024), 2)

            # Backup Addons if enabled
            if config.get("backup_addons", False):
                try:
                    mojang_dir = os.path.dirname(os.path.dirname(world_path))
                    dev_bp = os.path.join(mojang_dir, "development_behavior_packs")
                    dev_rp = os.path.join(mojang_dir, "development_resource_packs")
                    addons_dir = os.path.join(active_dir, f"_Addons_Archive_{timestamp}")
                    os.makedirs(addons_dir, exist_ok=True)
                    if os.path.exists(dev_bp) and os.listdir(dev_bp):
                        shutil.make_archive(os.path.join(addons_dir, "behavior_packs"), 'zip', dev_bp)
                    if os.path.exists(dev_rp) and os.listdir(dev_rp):
                        shutil.make_archive(os.path.join(addons_dir, "resource_packs"), 'zip', dev_rp)
                except: pass

            max_archives = max(1, min(5, int(config.get("smart_storage", 5))))
            
            # Filter archives to only the current target world
            world_archives = []
            for f in os.listdir(active_dir):
                item_full = os.path.join(active_dir, f)
                if not (os.path.isdir(item_full) or f.endswith(".mcworld") or f.endswith(".locked")):
                    continue
                raw_f = f.replace(".mcworld", "").replace(".locked", "")
                if len(raw_f) >= 18 and raw_f[-18:].startswith("_20"):
                    if raw_f[:-18] == safe_name:
                        world_archives.append(f)
                elif f.startswith(safe_name + "_"):
                    world_archives.append(f)
            
            if len(world_archives) > max_archives:
                def get_sort_time(folder_name):
                    try:
                        return datetime.strptime(folder_name.replace(".mcworld", "").replace(".locked", "")[-17:], "%Y_%m_%d_%H%M%S").timestamp()
                    except:
                        return os.path.getctime(os.path.join(active_dir, folder_name))
                world_archives.sort(key=get_sort_time, reverse=True)
                
                # Delete anything past the max_archives index
                for old_arch in world_archives[max_archives:]:
                    try: 
                        arch_path = os.path.join(active_dir, old_arch)
                        if os.path.isdir(arch_path): shutil.rmtree(arch_path, ignore_errors=True)
                        else: os.remove(arch_path)
                    except: pass

            fresh_channel = config.get("channel_id") or channel_id
            if fresh_channel:
                payload = {
                    "world_name": world_name, 
                    "size_mb": size_mb, 
                    "channel_id": fresh_channel,
                    "trigger_type": trigger_type
                }
                for attempt in range(3): 
                    try: 
                        res = requests.post(CLOUD_GATEWAY_URL, json=payload, timeout=10)
                        if res.status_code == 200: break 
                    except: pass
                    time.sleep(3) 

            self.push_status("Backup saved & synced!", "--success")
            if config.get("desktop_notifications", True):
                try:
                    if tray_icon: tray_icon.notify("Backup Saved Successfully!", "BedrockCapsule")
                except: pass
            try:
                if window: window.evaluate_js("refreshArchivesUI()") 
            except: pass
            try:
                if window: window.evaluate_js("loadAnalyticsUI()") 
            except: pass
        except Exception as e:
            self.push_status(f"Error: {str(e)[:40]}", "--danger")
        finally:
            try:
                if window: window.evaluate_js("resetActions()")
            except: pass

    def trigger_restore(self, folder_name, world_name=None):
        threading.Thread(target=self._restore_thread, args=(folder_name, world_name), daemon=True).start()

    def _restore_thread(self, folder_name, target_world_name=None):
        self.push_status("Restoring world backup... Please wait.", "--warning")
        try:
            if self._is_minecraft_running():
                self.push_status("Error: Close Minecraft entirely before restoring!", "--danger")
                try:
                    if window: window.evaluate_js("resetActions()")
                except: pass
                return

            if not self.worlds_data:
                self.scan_worlds()

            active_dir = self.get_active_backup_dir(target_world_name)
            source_backup_path = os.path.join(active_dir, folder_name)
            is_zip = folder_name.endswith(".mcworld")
            is_locked = folder_name.endswith(".locked")
            
            target_level_name = ""
            if not is_zip and not is_locked:
                level_txt_in_backup = os.path.join(source_backup_path, "levelname.txt")
                if os.path.exists(level_txt_in_backup):
                    try:
                        with open(level_txt_in_backup, "r", encoding="utf-8", errors="ignore") as f:
                            target_level_name = f.read().strip()
                    except: pass

            matched_world_dir = None
            if target_level_name and target_level_name in self.worlds_data:
                matched_world_dir = self.worlds_data[target_level_name]
            else:
                raw_name = folder_name.replace(".mcworld", "").replace(".locked", "")
                safe_world_name = raw_name[:-18] if (len(raw_name) >= 18 and raw_name[-18:].startswith('_20')) else raw_name
                for name, path in self.worlds_data.items():
                    if "".join(c for c in name if c.isalnum() or c in " _-").strip() == safe_world_name:
                        matched_world_dir = path
                        break
            
            if not matched_world_dir and target_world_name and target_world_name in self.worlds_data:
                matched_world_dir = self.worlds_data[target_world_name]
            
            if not matched_world_dir:
                self.push_status("Error: Cannot match backup to a world folder.", "--danger")
                try:
                    if window: window.evaluate_js("resetActions()")
                except: pass
                return

            backup_safety_fallback = matched_world_dir + "_CRASH_RECOVERY"
            if os.path.exists(backup_safety_fallback): shutil.rmtree(backup_safety_fallback, ignore_errors=True)
            if os.path.exists(matched_world_dir): shutil.move(matched_world_dir, backup_safety_fallback)

            os.makedirs(matched_world_dir, exist_ok=True)
            if is_locked:
                config = self.load_config()
                enc_key = config.get("encryption_key", "").strip()
                if not enc_key:
                    self.push_status("Error: Decryption Password required in settings!", "--danger")
                    if os.path.exists(backup_safety_fallback):
                        shutil.rmtree(matched_world_dir, ignore_errors=True)
                        shutil.move(backup_safety_fallback, matched_world_dir)
                    return
                temp_zip = source_backup_path + ".decrypted.zip"
                shutil.copy(source_backup_path, temp_zip)
                xor_crypt(temp_zip, enc_key) # Decrypt
                try:
                    shutil.unpack_archive(temp_zip, matched_world_dir, 'zip')
                except Exception as e:
                    self.push_status("Error: Incorrect password or corrupted backup!", "--danger")
                    if os.path.exists(temp_zip):
                        try: os.remove(temp_zip)
                        except: pass
                    if os.path.exists(backup_safety_fallback):
                        shutil.rmtree(matched_world_dir, ignore_errors=True)
                        shutil.move(backup_safety_fallback, matched_world_dir)
                    return
                if os.path.exists(temp_zip):
                    try: os.remove(temp_zip)
                    except: pass
            elif is_zip:
                try:
                    shutil.unpack_archive(source_backup_path, matched_world_dir, 'zip')
                except Exception as e:
                    if os.path.exists(backup_safety_fallback):
                        shutil.rmtree(matched_world_dir, ignore_errors=True)
                        shutil.move(backup_safety_fallback, matched_world_dir)
                    raise e
            else:
                try:
                    shutil.copytree(source_backup_path, matched_world_dir, dirs_exist_ok=True)
                except Exception as e:
                    if os.path.exists(backup_safety_fallback):
                        shutil.rmtree(matched_world_dir, ignore_errors=True)
                        shutil.move(backup_safety_fallback, matched_world_dir)
                    raise e
            
            if os.path.exists(backup_safety_fallback): shutil.rmtree(backup_safety_fallback, ignore_errors=True)
            self.push_status("World restored! You can launch Minecraft now.", "--success")
        except Exception as e:
            self.push_status(f"System Error: {str(e)[:40]}", "--danger")
        finally:
            try:
                if window: window.evaluate_js("resetActions()")
            except: pass

    def _is_minecraft_running(self):
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = (proc.info.get('name') or '').lower()
                    if proc_name in ('minecraft.windows.exe', 'minecraft.windowsbeta.exe', 'minecraft.exe'):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, KeyError, AttributeError):
                    pass
        except Exception:
            pass
        return False

    def toggle_auto_pilot(self, state, world_name, channel_id):
        self.auto_pilot_running = state
        if state:
            self.push_status("Auto-Pilot active • Monitoring Minecraft...", "--warning")
            threading.Thread(target=self._auto_pilot_loop, args=(world_name, channel_id), daemon=True).start()
        else:
            self.push_status("Auto-Pilot disabled. System ready.", "--text-muted")

    def _auto_pilot_loop(self, world_name, channel_id):
        was_running = False
        session_start = 0
        reminded = False
        
        while self.auto_pilot_running:
            is_running = self._is_minecraft_running()

            if is_running and not was_running:
                was_running = True
                session_start = time.time()
                reminded = False
                self.push_status("Minecraft detected • Session active...", "--accent-primary")
            elif is_running and was_running:
                config = self.load_config()
                if config.get("health_reminders", True) and not reminded:
                    if time.time() - session_start > 3 * 3600:
                        try:
                            if tray_icon: tray_icon.notify("You've been playing for 3 hours! Take a break & stretch.", "BedrockCapsule")
                        except: pass
                        reminded = True
            elif not is_running and was_running:
                time.sleep(2)
                if self._is_minecraft_running(): continue 
                    
                was_running = False
                play_time_sec = time.time() - session_start
                
                # Update total analytics
                config = self.load_config()
                config["analytics_playtime_sec"] = config.get("analytics_playtime_sec", 0) + play_time_sec
                self.save_raw_config(config)
                try:
                    if window: window.evaluate_js("loadAnalyticsUI()")
                except: pass

                # AUTO-DETECT WORLD LOGIC
                target_w = world_name
                if config.get("auto_detect_world", False):
                    self.scan_worlds()
                    newest_world = None
                    newest_time = 0
                    for w_name, w_path in self.worlds_data.items():
                        try:
                            # Check db folder and root for newest modification time
                            db_path = os.path.join(w_path, "db")
                            mtimes = []
                            if os.path.exists(db_path):
                                for f in os.listdir(db_path):
                                    try: mtimes.append(os.path.getmtime(os.path.join(db_path, f)))
                                    except: pass
                            level_txt = os.path.join(w_path, "levelname.txt")
                            if os.path.exists(level_txt):
                                try: mtimes.append(os.path.getmtime(level_txt))
                                except: pass
                            if mtimes:
                                w_mtime = max(mtimes)
                                if w_mtime > newest_time:
                                    newest_time = w_mtime
                                    newest_world = w_name
                        except: pass
                    
                    if newest_world and time.time() - newest_time < 300: 
                        target_w = newest_world
                        self.push_status(f"Detected played world: {target_w}", "--success")

                if not target_w:
                    target_w = config.get("target_world", "")
                if not target_w and self.worlds_data:
                    target_w = list(self.worlds_data.keys())[0]

                if config.get("ignore_launches", True) and play_time_sec < 300: 
                    self.push_status("Session under 5 mins. Backup skipped.", "--text-muted")
                    self.add_session_log(target_w, play_time_sec, "Skipped (<5m)")
                    if config.get("desktop_notifications", True):
                        try:
                            if tray_icon: tray_icon.notify("Session under 5 mins. Backup skipped.", "BedrockCapsule")
                        except: pass
                else:
                    self.push_status("Game closed! Saving world backup (5s)...", "--success")
                    self.add_session_log(target_w, play_time_sec, "Backup Saved")
                    time.sleep(5) 
                    fresh_channel = config.get("channel_id") or channel_id
                    self.trigger_backup(target_w, fresh_channel, trigger_type="Auto-Pilot")
            time.sleep(5)

# ==========================================
# 🌐 SYSTEM TRAY INTEGRATION
# ==========================================
def setup_system_tray():
    global tray_icon
    try:
        if sys.stdout is None: sys.stdout = open(os.devnull, 'w')
        if sys.stderr is None: sys.stderr = open(os.devnull, 'w')
        
        image = Image.open(icon_path)
        
        def show_app(icon, item): 
            try:
                if window:
                    window.show()
                    window.restore()
            except: pass
        def trigger_sync(icon, item): 
            try:
                if window: window.evaluate_js("startBackupUI()")
            except: pass
        def quit_app(icon, item):
            try:
                if icon: icon.stop()
            except: pass
            os._exit(0) 
            
        menu = pystray.Menu(
            pystray.MenuItem("BedrockCapsule 2.1", None, enabled=False),
            pystray.MenuItem("Open Dashboard", show_app, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quick Actions", pystray.Menu(
                pystray.MenuItem("Run Manual Backup", trigger_sync),
                pystray.MenuItem("Open Backups Folder", lambda: api.open_backup_directory())
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit BedrockCapsule", quit_app)
        )
        tray_icon = pystray.Icon("BedrockCapsule", image, "BedrockCapsule", menu)
        threading.Thread(target=tray_icon.run, daemon=True).start()
    except Exception as e: pass

def on_loaded():
    time.sleep(0.15)
    if "--autostart" not in sys.argv:
        try:
            if window: window.show()
        except: pass

def on_closing():
    try:
        if window: window.hide()
    except: pass
    return False

if __name__ == '__main__':
    enforce_single_instance_and_autostart()
    
    api = Api()
    icon_path = get_resource_path('logo.ico')
    
    initial_theme = get_saved_theme()
    bg_color = '#121212' if initial_theme == 'dark' else '#e5e7eb'
    boot_html = get_boot_html(initial_theme)
    
    setup_system_tray()
    
    is_hidden = "--autostart" in sys.argv
    
    # Window Dimensions
    window = webview.create_window(
        'BedrockCapsule 2.1', html=boot_html, js_api=api, width=750, height=600, 
        resizable=False, background_color=bg_color, frameless=True, hidden=is_hidden
    )
    
    window.events.loaded += on_loaded
    window.events.closing += on_closing
    
    webview.start(icon=icon_path)
