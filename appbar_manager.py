import ctypes
from ctypes import wintypes
import atexit

user32 = ctypes.windll.user32

# Win32 Sabitleri
SPI_GETWORKAREA = 0x0030
SPI_SETWORKAREA = 0x002F

HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x001A

user32.SystemParametersInfoW.argtypes = [wintypes.UINT, wintypes.UINT, ctypes.c_void_p, wintypes.UINT]
user32.SystemParametersInfoW.restype = wintypes.BOOL

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', wintypes.LONG),
        ('top', wintypes.LONG),
        ('right', wintypes.LONG),
        ('bottom', wintypes.LONG)
    ]

class AppBarManager:
    """
    Windows Çalışma Alanı (WorkArea) Yöneticisi.
    Çubuk açıkken ekran tavanını 30 piksel rezerve eder (tam ekran pencereler çubuğun altından başlar).
    Çubuk kapandığında veya konumu değiştiğinde ekranı ANINDA 0 piksele sıfırlar.
    """
    def __init__(self, root):
        self.root = root
        self.is_top_docked = False

        # Program kapanırken her koşulda ekranı 0 piksele geri döndür
        atexit.register(self.restore_all)

    def get_current_workarea(self):
        rc = RECT()
        user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rc), 0)
        return rc.left, rc.top, rc.right, rc.bottom

    def register_appbar_top(self, bar_height):
        """
        Masaüstü çalışma alanının tavanını bar_height kadar aşağı çeker.
        Tüm tam ekran pencereler anında bu çubuğun alt sınırına kenetlenir.
        """
        try:
            left, current_top, right, bottom = self.get_current_workarea()
            new_rc = RECT(left, bar_height, right, bottom)
            
            # Anında ve bloke etmeden hafızada ayarla (fWinIni = 0)
            user32.SystemParametersInfoW(SPI_SETWORKAREA, 0, ctypes.byref(new_rc), 0)
            
            # Pencerelere asenkron olarak masaüstünün değiştiğini bildir
            user32.PostMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, SPI_SETWORKAREA, 0)
            self.is_top_docked = True
        except Exception as e:
            print("Register top error:", e)

    def unregister(self):
        """
        Çalışma alanını kesin olarak orijinal haline (top = 0) döndürür.
        """
        try:
            left, current_top, right, bottom = self.get_current_workarea()
            reset_rc = RECT(left, 0, right, bottom)
            
            # Tavanı kesinlikle 0 piksele sıfırla (fWinIni = 0)
            user32.SystemParametersInfoW(SPI_SETWORKAREA, 0, ctypes.byref(reset_rc), 0)
            
            # Pencerelere tam ekrana yayılmalarını bildir
            user32.PostMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, SPI_SETWORKAREA, 0)
            self.is_top_docked = False
        except Exception as e:
            print("Unregister error:", e)

    def restore_all(self):
        self.unregister()
