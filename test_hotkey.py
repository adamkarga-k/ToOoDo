import ctypes
from ctypes import wintypes
import tkinter as tk

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

root = tk.Tk()
root.title("Test Tray & Hotkey")
hwnd = root.winfo_id()
# Ensure parent window hwnd if tk wraps it
parent_hwnd = user32.GetParent(hwnd)
target_hwnd = parent_hwnd if parent_hwnd else hwnd

print(f"Target HWND: {target_hwnd}")

# Test RegisterHotKey
MOD_ALT = 0x0001
MOD_SHIFT = 0x0004
VK_T = 0x54 # ord('T')
HOTKEY_ID = 9999

res = user32.RegisterHotKey(target_hwnd, HOTKEY_ID, MOD_ALT | MOD_SHIFT, VK_T)
print("RegisterHotKey result:", res)
user32.UnregisterHotKey(target_hwnd, HOTKEY_ID)
root.destroy()
