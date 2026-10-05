import os
import sys
import winreg
import shutil

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "TaskbarTodoBar"

def get_pythonw_path():
    # pythonw.exe yolunu bul
    which_path = shutil.which("pythonw.exe")
    if which_path and os.path.exists(which_path):
        return which_path
    
    cand = sys.executable.replace("python.exe", "pythonw.exe")
    if os.path.exists(cand):
        return cand
        
    return "pythonw.exe"

def get_launch_command():
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'
    main_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    pythonw = get_pythonw_path()
    return f'"{pythonw}" "{main_py}"'

def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True if val else False
    except FileNotFoundError:
        return False
    except Exception:
        return False

def set_autostart(enable=True):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_ALL_ACCESS)
        if enable:
            cmd = get_launch_command()
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print("Autostart update error:", e)
        return False
