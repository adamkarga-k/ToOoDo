import ctypes
from ctypes import wintypes
import threading
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

WM_HOTKEY = 0x0312
WM_USER = 0x0400
WM_TRAY = WM_USER + 20
MOD_ALT = 0x0001
MOD_SHIFT = 0x0004
VK_T = 0x54

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HICON),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", wintypes.HICON),
    ]

hotkey_received = False

def wnd_proc(hwnd, msg, wparam, lparam):
    global hotkey_received
    if msg == WM_HOTKEY:
        print("WM_HOTKEY RECEIVED!")
        hotkey_received = True
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

c_wndproc = WNDPROC(wnd_proc)

def run_loop():
    hinst = kernel32.GetModuleHandleW(None)
    wc = WNDCLASSEXW()
    wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
    wc.lpfnWndProc = c_wndproc
    wc.hInstance = hinst
    wc.lpszClassName = "ToOoDo_MsgClass"
    user32.RegisterClassExW(ctypes.byref(wc))

    # Message-only window
    HWND_MESSAGE = -3
    hwnd = user32.CreateWindowExW(0, "ToOoDo_MsgClass", "ToOoDo_MsgWindow", 0, 0, 0, 0, 0, HWND_MESSAGE, 0, hinst, 0)
    print("Created hidden window:", hwnd)
    
    res = user32.RegisterHotKey(hwnd, 101, MOD_ALT | MOD_SHIFT, VK_T)
    print("HotKey registered:", res)

    # Let's post a synthetic WM_HOTKEY to test
    user32.PostMessageW(hwnd, WM_HOTKEY, 101, 0)

    msg = wintypes.MSG()
    start = time.time()
    while time.time() - start < 1.0:
        if user32.PeekMessageW(ctypes.byref(msg), hwnd, 0, 0, 1): # PM_REMOVE = 1
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.05)

    user32.UnregisterHotKey(hwnd, 101)
    user32.DestroyWindow(hwnd)

run_loop()
print("Test completed successfully, hotkey_received =", hotkey_received)
