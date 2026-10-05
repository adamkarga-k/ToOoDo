import ctypes
from ctypes import wintypes
import os
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

LRESULT = wintypes.LPARAM
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT

user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID
]
user32.CreateWindowExW.restype = wintypes.HWND

WM_HOTKEY = 0x0312
WM_USER = 0x0400
WM_TRAY = WM_USER + 42
WM_LBUTTONUP = 0x0202
WM_RBUTTONUP = 0x0205
WM_LBUTTONDBLCLK = 0x0203

MOD_ALT = 0x0001
MOD_SHIFT = 0x0004
VK_T = 0x54 # 'T'

NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002

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

class TrayAndHotkeyManager:
    """
    Win32 Sistem Tepsisi (Tray Icon) ve Global Kısayol Tuşu (Alt+Shift+T) Yöneticisi.
    Arka planda hafif bir mesaj döngüsü çalıştırır ve Tkinter ana iş parçacığına çağrı yapar.
    """
    def __init__(self, root, on_hotkey=None, on_tray_click=None, on_tray_right_click=None):
        self.root = root
        self.on_hotkey = on_hotkey
        self.on_tray_click = on_tray_click
        self.on_tray_right_click = on_tray_right_click
        
        self.hwnd = None
        self.hicon = None
        self.nid = None
        self.running = True
        self.thread = None

        # İkon dosyasını hazırla
        from paths import get_resource_path
        self.ico_path = get_resource_path(os.path.join("assets", "cat_tray.ico"))
        self.setup_tray_icon()

        # Arka plan mesaj döngüsünü başlat
        self.thread = threading.Thread(target=self._msg_loop, daemon=True)
        self.thread.start()

    def setup_tray_icon(self):
        from paths import get_resource_path
        if not os.path.exists(self.ico_path):
            try:
                from PIL import Image
                src_png = get_resource_path(os.path.join("assets", "cat_gray.png"))
                if os.path.exists(src_png):
                    im = Image.open(src_png)
                    crop = im.crop((0, 0, 32, 32))
                    crop.save(self.ico_path, format="ICO", sizes=[(16, 16), (32, 32)])
            except Exception:
                pass

        if os.path.exists(self.ico_path):
            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x00000010
            self.hicon = user32.LoadImageW(None, self.ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_HOTKEY:
            if self.on_hotkey:
                self.root.after(0, self.on_hotkey)
            return 0

        elif msg == WM_TRAY:
            low_msg = lparam & 0xFFFF
            if low_msg in (WM_LBUTTONUP, WM_LBUTTONDBLCLK):
                if self.on_tray_click:
                    self.root.after(0, self.on_tray_click)
                return 0
            elif low_msg == WM_RBUTTONUP:
                if self.on_tray_right_click:
                    self.root.after(0, self.on_tray_right_click)
                return 0

        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def _msg_loop(self):
        hinst = kernel32.GetModuleHandleW(None)
        class_name = f"ToOoDo_TrayClass_{os.getpid()}"

        c_proc = WNDPROC(self._wnd_proc)
        wc = WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wc.lpfnWndProc = c_proc
        wc.hInstance = hinst
        wc.lpszClassName = class_name
        user32.RegisterClassExW(ctypes.byref(wc))

        self.hwnd = user32.CreateWindowExW(
            0, class_name, "ToOoDo_TrayHelper",
            0, 0, 0, 0, 0,
            None, None, hinst, None
        )

        # 1. Global Kısayol Tuşunu Kaydet (Alt + Shift + T)
        HOTKEY_ID = 2024
        user32.RegisterHotKey(self.hwnd, HOTKEY_ID, MOD_ALT | MOD_SHIFT, VK_T)

        # 2. Sistem Tepsisine İkon Ekle
        if self.hicon and self.hwnd:
            self.nid = NOTIFYICONDATAW()
            self.nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
            self.nid.hWnd = self.hwnd
            self.nid.uID = 1
            self.nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
            self.nid.uCallbackMessage = WM_TRAY
            self.nid.hIcon = self.hicon
            self.nid.szTip = "ToOoDo - Mini Görev Şeridi (Alt+Shift+T)"
            shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(self.nid))

        # Standart Win32 Mesaj Döngüsü
        msg = wintypes.MSG()
        while self.running:
            b_ret = user32.GetMessageW(ctypes.byref(msg), self.hwnd, 0, 0)
            if b_ret == 0 or b_ret == -1:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        # Temizlik
        user32.UnregisterHotKey(self.hwnd, HOTKEY_ID)
        if self.nid:
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(self.nid))
        user32.DestroyWindow(self.hwnd)

    def destroy(self):
        self.running = False
        if self.hwnd:
            user32.PostMessageW(self.hwnd, 0x0010, 0, 0) # WM_CLOSE
