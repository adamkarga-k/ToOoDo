import tkinter as tk
from tkinter import messagebox
import ctypes
from ctypes import wintypes
import json
import os
from datetime import datetime

from task_manager import TaskManager
from task_manager import TaskManager
from add_task_dialog import AddTaskDialog
from history_dialog import HistoryDialog
from appbar_manager import AppBarManager
from cat_companion import CatCompanion
from tray_hotkey_manager import TrayAndHotkeyManager
from task_tooltip import TaskTooltip
import autostart
from paths import get_data_dir, get_resource_path
from i18n import (
    t, set_lang, get_current_lang, get_selected_lang,
    get_system_lang, LANGUAGES
)

CONFIG_FILE = os.path.join(get_data_dir(), "config.json")

# DPI Awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

THEMES = {
    "paper": {
        "paper_bg": "#FAF9F6",
        "border_color": "#EAE6DE",
        "pencil_color": "#8A8277",
        "pencil_hover": "#2E2A27",
        "pencil_hover_bg": "#F2EFEA",
        "empty_text_fg": "#948D82",
        "card_ticking_bg": "#DCFCE7",
        "card_ticking_border": "#16A34A",
        "card_strike_fg": "#8C857B",
        "menu_bg": "#FAF8F5",
        "menu_fg": "#3C3836",
        "menu_active_bg": "#EAE4D9",
        "menu_active_fg": "#2D2A28",
        "task_styles": {
            "expired":  {"bg": "#FDF2F0", "border": "#F4C4BA", "chk": "#D9534F", "title": "#8A2A25", "rem": "#B84842"},
            "critical": {"bg": "#FEF7EE", "border": "#F8DCB3", "chk": "#E27B1E", "title": "#8C4708", "rem": "#B86518"},
            "warning":  {"bg": "#FCF9EC", "border": "#EBE2A8", "chk": "#B89617", "title": "#665008", "rem": "#8C7115"},
            "moderate": {"bg": "#F3F7F4", "border": "#D1E2D8", "chk": "#528464", "title": "#2E4F39", "rem": "#4F785E"},
            "normal":   {"bg": "#FFFFFF", "border": "#E5E1D8", "chk": "#B0A89C", "title": "#3C3835", "rem": "#8A837A"},
            "completed":{"bg": "#F5F3EF", "border": "#E5E1D8", "chk": "#16A34A", "title": "#9C9488", "rem": "#B5AEA3"},
        }
    },
    "dark_kraft": {
        "paper_bg": "#1C1B19",
        "border_color": "#2C2A26",
        "pencil_color": "#9E9689",
        "pencil_hover": "#F0EBE1",
        "pencil_hover_bg": "#2A2824",
        "empty_text_fg": "#827B70",
        "card_ticking_bg": "#142E1F",
        "card_ticking_border": "#22C55E",
        "card_strike_fg": "#756F64",
        "menu_bg": "#22201D",
        "menu_fg": "#E2DCD2",
        "menu_active_bg": "#33302B",
        "menu_active_fg": "#FFFFFF",
        "task_styles": {
            "expired":  {"bg": "#2B1A19", "border": "#542724", "chk": "#E0645C", "title": "#FCA5A5", "rem": "#F87171"},
            "critical": {"bg": "#291E12", "border": "#573815", "chk": "#E58E26", "title": "#FDBA74", "rem": "#FB923C"},
            "warning":  {"bg": "#262413", "border": "#4D4817", "chk": "#D4B127", "title": "#FDE047", "rem": "#EAB308"},
            "moderate": {"bg": "#16241C", "border": "#254230", "chk": "#4E9968", "title": "#86EFAC", "rem": "#4ADE80"},
            "normal":   {"bg": "#23221F", "border": "#36332E", "chk": "#787268", "title": "#DDD8CE", "rem": "#968F83"},
            "completed":{"bg": "#1E1D1B", "border": "#2B2925", "chk": "#22C55E", "title": "#756F64", "rem": "#5E584E"},
        }
    }
}

class TaskbarTodoApp:
    def __init__(self):
        self.root = tk.Tk()
        
        # Model & Config
        self.task_manager = TaskManager()
        self.config = self.load_config()
        
        # Dil Seçimini Başlat
        saved_lang = self.config.get("language", "auto")
        set_lang(saved_lang)
        self.root.title(t("app_title"))
        
        # Win32 ayarları
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Tema Ayarlarını Uygula
        self.apply_theme()

        self.bar_height = 30           # Daha ince, zarif ve minimalist yükseklik
        self.scroll_offset = 0
        self.max_scroll = 0
        self.auto_scroll = False
        self.is_hovered = False
        self.is_bar_visible = True
        
        # Tıklanabilir alan kayıtları
        self.task_rects = []       # [(card_x1, card_x2, task), ...]
        self.checkbox_rects = []   # [(chk_x1, chk_y1, chk_x2, chk_y2, task), ...]
        self.ticking_tasks = set() # Tiklenip kaybolma animasyonundaki görevler

        self.tooltip = TaskTooltip(self.root)
        self.appbar_manager = AppBarManager(self.root)

        # Ekran boyutları ve pencere konumu
        self.setup_window_position()
        self.set_toolwindow_style()

        # Ana Arayüz Bileşenleri
        self.create_widgets()

        # Sevimli Kedi Arkadaşı
        self.cat = CatCompanion(self.root, self.canvas, self.config, on_redraw_needed=self.refresh_ui)

        # Sistem Tepsisi ve Global Kısayol Tuşu (Alt+Shift+T)
        self.tray_manager = TrayAndHotkeyManager(
            self.root,
            on_hotkey=self.on_global_hotkey,
            on_tray_click=self.toggle_bar_visibility,
            on_tray_right_click=self.show_tray_menu
        )

        # Olay Dinleyicileri
        self.root.bind("<MouseWheel>", self.on_mouse_wheel)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # İlk çizim
        self.refresh_ui()

        # 5 saniyede bir süreleri güncelle (Sıfır CPU tüketimi)
        self.schedule_timer_update()

    def apply_theme(self):
        theme_key = self.config.get("theme", "paper")
        self.theme = THEMES.get(theme_key, THEMES["paper"])
        self.paper_bg = self.theme["paper_bg"]
        self.border_color = self.theme["border_color"]
        self.pencil_color = self.theme["pencil_color"]

        self.root.configure(bg=self.paper_bg)
        if hasattr(self, 'top_line'):
            self.top_line.configure(bg=self.border_color)
        if hasattr(self, 'control_frame'):
            self.control_frame.configure(bg=self.paper_bg)
        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=self.paper_bg)
        if hasattr(self, 'menu_btn'):
            self.menu_btn.configure(bg=self.paper_bg, fg=self.pencil_color)
        if hasattr(self, 'history_btn'):
            self.history_btn.configure(bg=self.paper_bg, fg=self.pencil_color)
        if hasattr(self, 'add_btn'):
            self.add_btn.configure(bg=self.paper_bg, fg=self.pencil_color)

    def load_config(self):
        default_cfg = {
            "position": "screen_top",
            "auto_scroll": False,
            "language": "auto",
            "theme": "paper",
            "cat_enabled": True,
            "cat_variant": "gray"
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default_cfg, **json.load(f)}
            except Exception:
                pass
        return default_cfg

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def get_screen_and_workarea(self):
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)

        SPI_GETWORKAREA = 0x0030
        class RECT(ctypes.Structure):
            _fields_ = [('left', wintypes.LONG), ('top', wintypes.LONG), ('right', wintypes.LONG), ('bottom', wintypes.LONG)]
        rc = RECT()
        user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rc), 0)
        
        return screen_w, screen_h, rc.left, rc.top, rc.right, rc.bottom

    def setup_window_position(self):
        screen_w, screen_h, wa_left, wa_top, wa_right, wa_bottom = self.get_screen_and_workarea()
        self.screen_width = screen_w

        pos = self.config.get("position", "above_taskbar")

        if pos == "screen_bottom":
            self.appbar_manager.unregister()
            top_y = screen_h - self.bar_height
        elif pos == "screen_top":
            top_y = 0
            # Ekranın en üstüne alındığında Windows Çalışma Alanını rezerve et
            # Böylece tam ekran pencereler bu çubuğun altından başlar!
            self.appbar_manager.register_appbar_top(self.bar_height)
        else:  # "above_taskbar"
            self.appbar_manager.unregister()
            top_y = wa_bottom - self.bar_height

        self.root.geometry(f"{screen_w}x{self.bar_height}+0+{top_y}")

    def reposition(self):
        self.setup_window_position()

    def set_toolwindow_style(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if not hwnd:
                hwnd = self.root.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW = 0x00040000
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception:
            pass

    def create_widgets(self):
        # Üst minimal sınır çizgisi
        self.top_line = tk.Frame(self.root, bg=self.border_color, height=1)
        self.top_line.pack(side="top", fill="x")

        # Sağ kontrol alanı
        self.control_frame = tk.Frame(self.root, bg=self.paper_bg, width=80, height=self.bar_height - 1)
        self.control_frame.pack(side="right", fill="y")
        self.control_frame.pack_propagate(False)

        # 1. Menü Simgesi (⋮)
        self.menu_btn = tk.Label(
            self.control_frame,
            text="⋮",
            font=("Segoe UI", 10),
            bg=self.paper_bg,
            fg=self.pencil_color,
            width=2,
            cursor="hand2"
        )
        self.menu_btn.pack(side="right", padx=(0, 6), fill="y")
        self.menu_btn.bind("<Button-1>", self.show_context_menu)
        self.menu_btn.bind("<Enter>", lambda e: self.menu_btn.configure(fg=self.theme["pencil_hover"], bg=self.theme["pencil_hover_bg"]))
        self.menu_btn.bind("<Leave>", lambda e: self.menu_btn.configure(fg=self.pencil_color, bg=self.paper_bg))

        # 2. Tamamlananlar Simgesi (✓) - Butonsuz, sade kurşun kalem tonu
        self.history_btn = tk.Label(
            self.control_frame,
            text="✓",
            font=("Segoe UI", 10),
            bg=self.paper_bg,
            fg=self.pencil_color,
            width=2,
            cursor="hand2"
        )
        self.history_btn.pack(side="right", padx=1, fill="y")
        self.history_btn.bind("<Button-1>", self.open_history_dialog)
        self.history_btn.bind("<Enter>", lambda e: self.history_btn.configure(fg=self.theme["pencil_hover"], bg=self.theme["pencil_hover_bg"]))
        self.history_btn.bind("<Leave>", lambda e: self.history_btn.configure(fg=self.pencil_color, bg=self.paper_bg))

        # 3. + Yeni Not Ekle Simgesi - Butonsuz, sade kurşun kalem tonu
        self.add_btn = tk.Label(
            self.control_frame,
            text="+",
            font=("Segoe UI", 11),
            bg=self.paper_bg,
            fg=self.pencil_color,
            width=2,
            cursor="hand2"
        )
        self.add_btn.pack(side="right", padx=1, fill="y")
        self.add_btn.bind("<Button-1>", self.open_add_dialog)
        self.add_btn.bind("<Enter>", lambda e: self.add_btn.configure(fg=self.theme["pencil_hover"], bg=self.theme["pencil_hover_bg"]))
        self.add_btn.bind("<Leave>", lambda e: self.add_btn.configure(fg=self.pencil_color, bg=self.paper_bg))

        # Sol Kaydırılabilir Canvas (Not Şeridi)
        self.canvas = tk.Canvas(
            self.root,
            bg=self.paper_bg,
            bd=0,
            highlightthickness=0,
            height=self.bar_height - 1
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        # Olay Bağlamaları
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<Enter>", self.on_canvas_enter)
        self.canvas.bind("<Leave>", self.on_canvas_leave)
        self.canvas.bind("<Motion>", self.on_canvas_motion, add="+")

        self.drag_start_x = 0
        self.is_dragging = False

    def on_canvas_enter(self, event):
        self.is_hovered = True

    def on_canvas_leave(self, event):
        self.is_hovered = False
        self.tooltip.hide()

    def on_canvas_motion(self, event):
        if self.is_dragging:
            self.tooltip.hide()
            return

        task = self.get_task_at(event.x)
        if task:
            card_mid_x = event.x_root
            for x1, x2, t in self.task_rects:
                if t.id == task.id:
                    card_mid_x = self.canvas.winfo_rootx() + ((x1 + x2) // 2)
                    break

            bar_y = self.root.winfo_rooty()
            place_above = (self.config.get("position") != "screen_top")
            theme_name = self.config.get("theme", "paper")
            self.tooltip.schedule_show(task, card_mid_x, bar_y, place_above, theme_name)
        else:
            self.tooltip.hide()

    def on_canvas_press(self, event):
        self.tooltip.hide()
        self.drag_start_x = event.x
        self.is_dragging = False

    def on_canvas_drag(self, event):
        self.tooltip.hide()
        dx = event.x - self.drag_start_x
        if abs(dx) > 5:
            self.is_dragging = True
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - dx))
            self.drag_start_x = event.x
            self.redraw_tasks()

    def on_canvas_release(self, event):
        if not self.is_dragging:
            self.on_canvas_click(event)

    def on_mouse_wheel(self, event):
        self.tooltip.hide()
        delta = -1 if event.delta < 0 else 1
        self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset + (delta * 40)))
        self.redraw_tasks()

    def refresh_ui(self):
        self.redraw_tasks()

    def redraw_tasks(self):
        self.canvas.delete("all")
        self.task_rects.clear()
        self.checkbox_rects.clear()

        tasks = self.task_manager.get_bar_tasks()
        canvas_w = self.canvas.winfo_width()
        if canvas_w <= 1:
            canvas_w = self.screen_width - 105

        cat_offset = 46 if (hasattr(self, 'cat') and self.cat.enabled) else 10
        curr_x = cat_offset - self.scroll_offset
        y1 = 3
        y2 = self.bar_height - 4
        mid_y = (self.bar_height - 1) // 2

        styles = self.theme["task_styles"]
        active_tasks = [t for t in tasks if not t.completed]

        if not tasks:
            self.canvas.create_text(
                cat_offset + 4, mid_y,
                text=t("empty_tasks"),
                anchor="w",
                fill=self.theme["empty_text_fg"],
                font=("Segoe UI", 9, "italic")
            )
            self.max_scroll = 0
            if hasattr(self, 'cat'):
                self.cat.update_tasks_state(has_tasks=False, overdue_task_x=None)
                if self.cat.enabled:
                    self.cat.render()
            return

        for task in tasks:
            is_done = task.completed
            is_ticking = (task.id in self.ticking_tasks)
            is_checked = is_done or is_ticking

            if is_done:
                style = styles.get("completed", styles["normal"])
                rem_text = task.formatted_status
            else:
                urg = task.urgency_level
                style = styles.get(urg, styles["normal"])
                rem_text = task.formatted_remaining

            # Görünen karakter sayısını belirgin şekilde artır (48 karaktere kadar rahat görünür)
            display_title = task.title if len(task.title) <= 48 else task.title[:45] + ".."
            
            # Kart genişliği (Kutucuk + Metin + Kalan Süre)
            item_width = max(110, int((len(display_title) + len(rem_text)) * 6.8) + 48)

            card_x1 = curr_x
            card_x2 = curr_x + item_width

            # 1. Kart Zemin ve Zarif Kenarlık
            self.canvas.create_rectangle(
                card_x1, y1, card_x2, y2,
                fill=style["bg"],
                outline=style["border"],
                width=1,
                tags=(f"task_{task.id}", "task_pill")
            )

            # 2. Görünür Checkbox Kutucuğu [ ] / [✓]
            chk_size = 14
            chk_x1 = card_x1 + 7
            chk_y1 = mid_y - (chk_size // 2)
            chk_x2 = chk_x1 + chk_size
            chk_y2 = chk_y1 + chk_size

            # Checkbox arka plan ve çerçeve
            box_bg = self.theme["card_ticking_bg"] if is_checked else style["bg"]
            box_border = self.theme["card_ticking_border"] if is_checked else style["chk"]
            self.canvas.create_rectangle(
                chk_x1, chk_y1, chk_x2, chk_y2,
                fill=box_bg,
                outline=box_border,
                width=1.4,
                tags=(f"chk_{task.id}", "checkbox")
            )

            if is_checked:
                # Canlı ve net yeşil vektör tik işareti
                chk_color = "#22C55E" if self.config.get("theme") == "dark_kraft" else "#16A34A"
                self.canvas.create_line(
                    chk_x1 + 3, mid_y, chk_x1 + 6, mid_y + 3,
                    fill=chk_color, width=2, capstyle="round",
                    tags=(f"chk_{task.id}", "checkbox")
                )
                self.canvas.create_line(
                    chk_x1 + 6, mid_y + 3, chk_x1 + 11, mid_y - 3,
                    fill=chk_color, width=2, capstyle="round",
                    tags=(f"chk_{task.id}", "checkbox")
                )

            # Tıklama alanı (Kolay tıklanması için genişletilmiş alan)
            self.checkbox_rects.append((chk_x1 - 6, chk_y1 - 6, chk_x2 + 8, chk_y2 + 6, task))

            # 3. Görev Metni
            title_color = self.theme["card_strike_fg"] if is_checked else style["title"]
            title_font = ("Calibri", 10, "bold" if not is_checked and not is_done and urg in ("expired", "critical") else "normal")
            title_text_id = self.canvas.create_text(
                chk_x2 + 7, mid_y,
                text=display_title,
                anchor="w",
                fill=title_color,
                font=title_font,
                tags=(f"task_{task.id}", "task_pill")
            )

            # Tiklendiğinde veya tamamlandığında metnin üstüne kurşun kalemle çizgi çek (Strikethrough)
            if is_checked:
                bbox = self.canvas.bbox(title_text_id)
                if bbox:
                    self.canvas.create_line(
                        bbox[0], mid_y, bbox[2], mid_y,
                        fill=self.theme["card_strike_fg"],
                        width=1.4,
                        tags=(f"task_{task.id}", "task_pill")
                    )

            # 4. Kalan Süre / Tamamlanma Zamanı
            rem_fg = style["rem"] if not is_checked else self.theme["card_strike_fg"]
            self.canvas.create_text(
                card_x2 - 8, mid_y,
                text=rem_text,
                anchor="e",
                fill=rem_fg,
                font=("Segoe UI", 8),
                tags=(f"task_{task.id}", "task_pill")
            )

            self.task_rects.append((card_x1, card_x2, task))
            curr_x = card_x2 + 6

        total_content_w = curr_x + self.scroll_offset
        self.max_scroll = max(0, total_content_w - canvas_w + 20)

        # En yakın gecikmiş aktif görevin X koordinatını kediye bildir
        first_overdue_x = None
        for card_x1, card_x2, task in self.task_rects:
            if not task.completed and task.urgency_level in ("expired", "critical"):
                first_overdue_x = card_x1
                break

        if hasattr(self, 'cat'):
            # Aktif görev bittiyse (sadece üstü çizililer kaldıysa) kedi huzurla uyur
            self.cat.update_tasks_state(has_tasks=bool(active_tasks), overdue_task_x=first_overdue_x)
            if self.cat.enabled:
                self.cat.render()

    def on_canvas_click(self, event):
        # Kediye tıklandıysa miyavlasın / pati atsın
        if hasattr(self, 'cat') and self.cat.is_point_on_cat(event.x, event.y):
            self.cat.trigger_meow()
            return

        # Önce checkbox tıklaması mı kontrol et
        for x1, y1, x2, y2, task in self.checkbox_rects:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                if task.completed:
                    # Tamamlanmış görevin kutusuna tıklandı: Geri Al (Aktif Yap)
                    self.task_manager.restore_task(task.id)
                    self.redraw_tasks()
                else:
                    self.check_and_complete_task(task)
                return

        # Görev kartına tıklandıysa menü/detay
        task = self.get_task_at(event.x)
        if task:
            self.show_task_menu(event, task)

    def check_and_complete_task(self, task):
        if task.id in self.ticking_tasks:
            return
        # 1. Tiklendi durumuna al ve hemen yeniden çiz (Yeşil tik ve çizilen çizgi belirir)
        self.ticking_tasks.add(task.id)
        if hasattr(self, 'cat'):
            self.cat.trigger_meow()
        self.redraw_tasks()

        # 2. 450 milisaniye sonra görev sona atılır (tamamlanmış olarak kalır)
        self.root.after(450, lambda tid=task.id: self.finalize_complete_task(tid))

    def finalize_complete_task(self, task_id):
        self.ticking_tasks.discard(task_id)
        self.task_manager.complete_task(task_id)
        self.redraw_tasks()

    def on_canvas_right_click(self, event):
        task = self.get_task_at(event.x)
        if task:
            self.show_task_menu(event, task)

    def get_task_at(self, click_x):
        for x1, x2, task in self.task_rects:
            if x1 <= click_x <= x2:
                return task
        return None

    def show_task_menu(self, event, task):
        self.tooltip.hide()
        menu = tk.Menu(self.root, tearoff=0, bg=self.theme["menu_bg"], fg=self.theme["menu_fg"],
                       activebackground=self.theme["menu_active_bg"], activeforeground=self.theme["menu_active_fg"])
        
        if task.completed:
            menu.add_command(label=f"✓  {task.title}", state="disabled")
            menu.add_separator()
            menu.add_command(label=t("card_restore"), command=lambda: (self.task_manager.restore_task(task.id), self.redraw_tasks()))
            menu.add_separator()
            menu.add_command(label=t("card_delete"), command=lambda: (self.task_manager.delete_task(task.id), self.redraw_tasks()))
        else:
            menu.add_command(label=f"✎  {task.title}", state="disabled")
            menu.add_separator()
            menu.add_command(label=t("card_complete"), command=lambda: self.check_and_complete_task(task))
            menu.add_command(label=t("card_snooze_15m"), command=lambda: (self.task_manager.snooze_task(task.id, 15), self.redraw_tasks()))
            menu.add_command(label=t("card_snooze_1h"), command=lambda: (self.task_manager.snooze_task(task.id, 60), self.redraw_tasks()))
            menu.add_command(label=t("card_snooze_1d"), command=lambda: (self.task_manager.snooze_task(task.id, 1440), self.redraw_tasks()))
            menu.add_separator()
            menu.add_command(label=t("card_delete"), command=lambda: (self.task_manager.delete_task(task.id), self.redraw_tasks()))

        menu.tk_popup(event.x_root, event.y_root)

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg=self.theme["menu_bg"], fg=self.theme["menu_fg"],
                       activebackground=self.theme["menu_active_bg"], activeforeground=self.theme["menu_active_fg"])
        menu.add_command(label=t("menu_add_note"), command=self.open_add_dialog)
        menu.add_command(label=t("menu_history"), command=self.open_history_dialog)
        menu.add_separator()

        curr_pos = self.config.get("position", "screen_top")
        
        pos_menu = tk.Menu(menu, tearoff=0, bg=self.theme["menu_bg"], fg=self.theme["menu_fg"],
                           activebackground=self.theme["menu_active_bg"], activeforeground=self.theme["menu_active_fg"])
        pos_menu.add_command(
            label=f"✓ {t('pos_top')}" if curr_pos == "screen_top" else f"  {t('pos_top')}",
            command=lambda: self.change_position("screen_top")
        )
        pos_menu.add_command(
            label=f"✓ {t('pos_above_taskbar')}" if curr_pos == "above_taskbar" else f"  {t('pos_above_taskbar')}",
            command=lambda: self.change_position("above_taskbar")
        )
        pos_menu.add_command(
            label=f"✓ {t('pos_bottom')}" if curr_pos == "screen_bottom" else f"  {t('pos_bottom')}",
            command=lambda: self.change_position("screen_bottom")
        )
        menu.add_cascade(label=t("menu_position"), menu=pos_menu)

        # 🎨 Defter Teması Alt Menüsü
        theme_menu = tk.Menu(menu, tearoff=0, bg=self.theme["menu_bg"], fg=self.theme["menu_fg"],
                             activebackground=self.theme["menu_active_bg"], activeforeground=self.theme["menu_active_fg"])
        curr_theme = self.config.get("theme", "paper")
        theme_menu.add_command(
            label=f"✓ {t('theme_light')}" if curr_theme == "paper" else f"  {t('theme_light')}",
            command=lambda: self.change_theme("paper")
        )
        theme_menu.add_command(
            label=f"✓ {t('theme_dark')}" if curr_theme == "dark_kraft" else f"  {t('theme_dark')}",
            command=lambda: self.change_theme("dark_kraft")
        )
        menu.add_cascade(label=t("menu_theme"), menu=theme_menu)

        # 🌐 Dil / Language Alt Menüsü
        lang_menu = tk.Menu(menu, tearoff=0, bg=self.theme["menu_bg"], fg=self.theme["menu_fg"],
                            activebackground=self.theme["menu_active_bg"], activeforeground=self.theme["menu_active_fg"])
        sel_lang = get_selected_lang()
        sys_lang_name = LANGUAGES.get(get_system_lang(), get_system_lang())
        auto_label = t("lang_auto", name=sys_lang_name)
        lang_menu.add_command(
            label=f"✓ {auto_label}" if sel_lang == "auto" else f"  {auto_label}",
            command=lambda: self.change_language("auto")
        )
        lang_menu.add_separator()
        for code, name in LANGUAGES.items():
            is_active = (sel_lang == code)
            lbl = f"✓ {name}" if is_active else f"  {name}"
            lang_menu.add_command(
                label=lbl,
                command=lambda c=code: self.change_language(c)
            )
        menu.add_cascade(label=t("menu_language"), menu=lang_menu)

        menu.add_separator()

        # 🐱 Sevimli Kedi Alt Menüsü
        cat_menu = tk.Menu(menu, tearoff=0, bg=self.theme["menu_bg"], fg=self.theme["menu_fg"],
                           activebackground=self.theme["menu_active_bg"], activeforeground=self.theme["menu_active_fg"])
        is_cat_enabled = self.config.get("cat_enabled", True)
        curr_cat_var = self.config.get("cat_variant", "gray")
        
        cat_toggle_lbl = f"✓ {t('cat_show')} ({t('state_on')})" if is_cat_enabled else f"  {t('cat_show')} ({t('state_off')})"
        cat_menu.add_command(label=cat_toggle_lbl, command=self.toggle_cat_enabled)
        cat_menu.add_separator()

        variants = [
            ("gray", t("cat_color_gray")),
            ("ginger", t("cat_color_ginger")),
            ("white", t("cat_color_white")),
        ]
        for v_code, v_name in variants:
            v_active = (curr_cat_var == v_code)
            lbl = f"✓ {v_name}" if v_active else f"  {v_name}"
            cat_menu.add_command(
                label=lbl,
                command=lambda vc=v_code: self.change_cat_variant(vc)
            )
        menu.add_cascade(label=t("menu_cat"), menu=cat_menu)

        menu.add_separator()

        # Windows Başlangıcında Otomatik Açma Seçeneği
        is_auto = autostart.is_autostart_enabled()
        st_auto = t("state_on") if is_auto else t("state_off")
        auto_start_label = f"✓ {t('menu_autostart')} ({st_auto})" if is_auto else f"  {t('menu_autostart')} ({st_auto})"
        menu.add_command(label=auto_start_label, command=self.toggle_autostart)

        # Otomatik Kayan Bant
        st_scroll = t("state_on") if self.auto_scroll else t("state_off")
        auto_text = f"✓ {t('menu_autoscroll')} ({st_scroll})" if self.auto_scroll else f"  {t('menu_autoscroll')} ({st_scroll})"
        menu.add_command(label=auto_text, command=self.toggle_auto_scroll)

        menu.add_separator()
        menu.add_command(label=t("hotkey_info"), state="disabled")
        menu.add_separator()
        menu.add_command(label=t("menu_exit"), command=self.quit_app)

        menu.tk_popup(event.x_root, event.y_root)

    def change_theme(self, theme_key):
        self.config["theme"] = theme_key
        self.save_config()
        self.apply_theme()
        self.redraw_tasks()

    def change_cat_variant(self, variant):
        self.config["cat_variant"] = variant
        self.save_config()
        if hasattr(self, 'cat'):
            self.cat.set_variant(variant)

    def toggle_cat_enabled(self):
        current = self.config.get("cat_enabled", True)
        new_state = not current
        self.config["cat_enabled"] = new_state
        self.save_config()
        if hasattr(self, 'cat'):
            self.cat.set_enabled(new_state)
        self.redraw_tasks()

    def change_language(self, lang_code):
        self.config["language"] = lang_code
        self.save_config()
        set_lang(lang_code)
        self.root.title(t("app_title"))
        self.redraw_tasks()

    def toggle_autostart(self):
        currently_enabled = autostart.is_autostart_enabled()
        autostart.set_autostart(not currently_enabled)

    def on_global_hotkey(self):
        if not self.is_bar_visible:
            self.toggle_bar_visibility()
        self.open_add_dialog()

    def toggle_bar_visibility(self):
        self.is_bar_visible = not self.is_bar_visible
        if self.is_bar_visible:
            self.root.deiconify()
            self.reposition()
        else:
            self.appbar_manager.restore_all()
            self.root.withdraw()

    def show_tray_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg=self.theme["menu_bg"], fg=self.theme["menu_fg"],
                       activebackground=self.theme["menu_active_bg"], activeforeground=self.theme["menu_active_fg"])
        toggle_txt = f"✓ {t('tray_toggle')}" if self.is_bar_visible else f"  {t('tray_toggle')}"
        menu.add_command(label=toggle_txt, command=self.toggle_bar_visibility)
        menu.add_command(label=t("menu_add_note"), command=self.open_add_dialog)
        menu.add_separator()
        menu.add_command(label=t("hotkey_info"), state="disabled")
        menu.add_separator()
        menu.add_command(label=t("menu_exit"), command=self.quit_app)

        x, y = self.root.winfo_pointerxy()
        menu.tk_popup(x, max(10, y - 90))

    def quit_app(self):
        if hasattr(self, 'tray_manager'):
            self.tray_manager.destroy()
        self.appbar_manager.restore_all()
        self.root.destroy()

    def change_position(self, new_pos):
        self.config["position"] = new_pos
        self.save_config()
        self.setup_window_position()

    def toggle_auto_scroll(self):
        self.auto_scroll = not self.auto_scroll
        self.config["auto_scroll"] = self.auto_scroll
        self.save_config()
        if self.auto_scroll:
            self.tick_auto_scroll()

    def tick_auto_scroll(self):
        if not self.auto_scroll:
            return

        if not self.is_hovered and self.max_scroll > 0:
            self.scroll_offset += 1
            if self.scroll_offset > self.max_scroll:
                self.scroll_offset = 0
            self.redraw_tasks()

        self.root.after(45, self.tick_auto_scroll)

    def open_add_dialog(self, event=None):
        if hasattr(self, 'current_dialog') and self.current_dialog and self.current_dialog.winfo_exists():
            self.current_dialog.destroy()
            self.current_dialog = None

        place_above = (self.config.get("position") != "screen_top")
        btn_x = self.root.winfo_rootx() + self.root.winfo_width()
        btn_y = self.root.winfo_rooty()
        
        self.current_dialog = AddTaskDialog(
            parent=self.root,
            on_save_callback=self.on_task_added,
            x=btn_x,
            y=btn_y,
            place_above=place_above,
            theme=self.config.get("theme", "paper")
        )

    def open_history_dialog(self, event=None):
        if hasattr(self, 'current_dialog') and self.current_dialog and self.current_dialog.winfo_exists():
            self.current_dialog.destroy()
            self.current_dialog = None

        place_above = (self.config.get("position") != "screen_top")
        btn_x = self.root.winfo_rootx() + self.root.winfo_width()
        btn_y = self.root.winfo_rooty()

        self.current_dialog = HistoryDialog(
            parent=self.root,
            task_manager=self.task_manager,
            on_update_callback=self.redraw_tasks,
            x=btn_x,
            y=btn_y,
            place_above=place_above,
            theme=self.config.get("theme", "paper")
        )

    def on_task_added(self, title, due_time):
        self.task_manager.add_task(title, due_time)
        self.scroll_offset = 0
        self.redraw_tasks()

    def schedule_timer_update(self):
        self.redraw_tasks()
        self.root.after(5000, self.schedule_timer_update)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TaskbarTodoApp()
    app.run()
