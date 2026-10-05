import ctypes
from ctypes import wintypes
import os

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

LRESULT = wintypes.LPARAM
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT

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

def dummy_proc(hwnd, msg, wp, lp):
    return user32.DefWindowProcW(hwnd, msg, wp, lp)

c_proc = WNDPROC(dummy_proc)
wc = WNDCLASSEXW()
wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
wc.lpfnWndProc = c_proc
wc.hInstance = kernel32.GetModuleHandleW(None)
wc.lpszClassName = "ToOoDo_TestClass"

atom = user32.RegisterClassExW(ctypes.byref(wc))
print("RegisterClassExW atom:", atom)

user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID
]
user32.CreateWindowExW.restype = wintypes.HWND

hwnd = user32.CreateWindowExW(
    0, "ToOoDo_TestClass", "ToOoDo_TestWindow",
    0, 0, 0, 0, 0,
    None, None, wc.hInstance, None
)
print("CreateWindowExW hwnd:", hwnd)

# Test Tray Icon
class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uID', wintypes.UINT),
        ('uFlags', wintypes.UINT),
        ('uCallbackMessage', wintypes.UINT),
        ('hIcon', wintypes.HICON),
        ('szTip', wintypes.WCHAR * 128),
        ('dwState', wintypes.DWORD),
        ('dwStateMask', wintypes.DWORD),
        ('szInfo', wintypes.WCHAR * 256),
        ('uTimeoutOrVersion', wintypes.UINT),
        ('szInfoTitle', wintypes.WCHAR * 64),
        ('dwInfoFlags', wintypes.DWORD),
    ]

# Load cat_tray.ico
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
LR_DEFAULTSIZE = 0x00000040
ico_path = os.path.abspath(r"C:\Users\Ubeydullah\.gemini\antigravity\scratch\taskbar_todo\assets\cat_tray.ico")
hicon = user32.LoadImageW(None, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
print("Loaded hicon:", hicon)

NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NIM_ADD = 0x00000000
NIM_DELETE = 0x00000002

nid = NOTIFYICONDATAW()
nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
nid.hWnd = hwnd
nid.uID = 1001
nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
nid.uCallbackMessage = 0x0400 + 20
nid.hIcon = hicon
nid.szTip = "ToOoDo"

res = shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))
print("Shell_NotifyIconW add result:", res)

# Remove tray icon
shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
user32.DestroyWindow(hwnd)
print("Tray test passed!")
