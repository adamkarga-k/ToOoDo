import tkinter as tk
from datetime import datetime
from i18n import t

class HistoryDialog(tk.Toplevel):
    def __init__(self, parent, task_manager, on_update_callback, x, y, place_above=True, theme="paper"):
        super().__init__(parent)
        self.task_manager = task_manager
        self.on_update_callback = on_update_callback
        self.theme = theme

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.is_dark = (self.theme == "dark_kraft")
        self.bg_main = "#181715" if self.is_dark else "#F7F5F0"
        self.card_bg = "#22201D" if self.is_dark else "#FCFAF7"
        self.border_c = "#3A3733" if self.is_dark else "#DED8CE"
        self.header_fg = "#E2DCD2" if self.is_dark else "#443F3B"
        self.close_fg = "#827B70" if self.is_dark else "#A8A196"
        self.line_c = "#2C2A26" if self.is_dark else "#EFECE6"

        self.muted_fg = "#9E9689" if self.is_dark else "#8C857B"
        self.sub_fg = "#756F64" if self.is_dark else "#B5AEA3"
        self.del_fg = "#827B70" if self.is_dark else "#C5BDB2"
        self.empty_fg = "#827B70" if self.is_dark else "#A8A196"
        self.footer_fg = "#827B70" if self.is_dark else "#9C9488"
        self.hover_text = "#E2DCD2" if self.is_dark else "#2E2A27"

        self.configure(bg=self.bg_main)

        # Görev Ekle penceresiyle uyumlu, rahat okunabilir boyutlar
        width = 310
        height = 230
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        pos_x = min(max(10, x - width + 30), screen_w - width - 10)
        if place_above:
            pos_y = max(10, y - height - 6)
        else:
            pos_y = min(screen_h - height - 10, y + 6)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        # Ana Kart Çerçevesi (Görev Ekle ile birebir uyumlu)
        self.container = tk.Frame(self, bg=self.card_bg, highlightthickness=1, highlightbackground=self.border_c)
        self.container.pack(fill="both", expand=True)

        # 1. Başlık & Kapat Butonu
        header = tk.Frame(self.container, bg=self.card_bg)
        header.pack(fill="x", padx=12, pady=(10, 4))

        completed_count = len(self.task_manager.get_completed_tasks_sorted())
        self.header_label = tk.Label(
            header,
            text=t("history_title", count=completed_count),
            font=("Segoe UI", 9, "bold"),
            bg=self.card_bg,
            fg=self.header_fg
        )
        self.header_label.pack(side="left")

        close_btn = tk.Label(
            header,
            text="✕",
            font=("Segoe UI", 8),
            bg=self.card_bg,
            fg=self.close_fg,
            cursor="hand2"
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.destroy())

        # İnce Defter Çizgisi
        tk.Frame(self.container, bg=self.line_c, height=1).pack(fill="x", padx=12, pady=(2, 4))

        # 2. Kaydırılabilir Liste Alanı
        list_container = tk.Frame(self.container, bg=self.card_bg)
        list_container.pack(side="top", fill="both", expand=True, padx=12, pady=2)

        self.list_canvas = tk.Canvas(list_container, bg=self.card_bg, bd=0, highlightthickness=0)
        self.scroll_frame = tk.Frame(self.list_canvas, bg=self.card_bg)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        )

        self.canvas_window = self.list_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=284)
        self.list_canvas.pack(side="left", fill="both", expand=True)

        # Fare tekerleğiyle kaydırma
        self.list_canvas.bind("<MouseWheel>", lambda e: self.list_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.scroll_frame.bind("<MouseWheel>", lambda e: self.list_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # 3. Alt Araç Çubuğu (Geçmişi Temizle & Kapat)
        footer = tk.Frame(self.container, bg=self.card_bg)
        footer.pack(fill="x", padx=12, pady=(4, 8))

        self.clear_btn = tk.Label(
            footer,
            text=t("clear_history"),
            font=("Segoe UI", 7),
            bg=self.card_bg,
            fg=self.footer_fg,
            cursor="hand2"
        )
        self.clear_btn.pack(side="left")
        self.clear_btn.bind("<Button-1>", self.clear_history)
        self.clear_btn.bind("<Enter>", lambda e: self.clear_btn.configure(fg="#EF4444" if self.is_dark else "#C55244"))
        self.clear_btn.bind("<Leave>", lambda e: self.clear_btn.configure(fg=self.footer_fg))

        done_btn = tk.Label(
            footer,
            text=t("close_esc"),
            font=("Segoe UI", 7),
            bg=self.card_bg,
            fg=self.footer_fg,
            cursor="hand2"
        )
        done_btn.pack(side="right")
        done_btn.bind("<Button-1>", lambda e: self.destroy())

        self.bind("<Escape>", lambda e: self.destroy())

        self.render_items()
        self.start_click_outside_listener()

    def start_click_outside_listener(self):
        """Pencere dışına tıklandığında otomatik kapanması için dinleyici başlatır"""
        self.after(160, self._check_click_outside)

    def _check_click_outside(self):
        if not self.winfo_exists():
            return

        import ctypes
        user32 = ctypes.windll.user32

        # Sol veya sağ fare tuşu basıldı mı? (VK_LBUTTON = 0x01, VK_RBUTTON = 0x02)
        l_down = (user32.GetAsyncKeyState(0x01) & 0x8000) != 0
        r_down = (user32.GetAsyncKeyState(0x02) & 0x8000) != 0

        if l_down or r_down:
            px, py = self.winfo_pointerxy()
            rx1 = self.winfo_rootx()
            ry1 = self.winfo_rooty()
            rx2 = rx1 + self.winfo_width()
            ry2 = ry1 + self.winfo_height()

            # Eğer fare tıklaması bu pencerenin sınırları dışındaysa kapat
            if not (rx1 <= px <= rx2 and ry1 <= py <= ry2):
                self.destroy()
                return

        if self.winfo_exists():
            self.after(45, self._check_click_outside)

    def render_items(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        completed = self.task_manager.get_completed_tasks_sorted()
        self.header_label.configure(text=t("history_title", count=len(completed)))

        if not completed:
            empty_lbl = tk.Label(
                self.scroll_frame,
                text=t("empty_history"),
                font=("Segoe UI", 8, "italic"),
                bg=self.card_bg,
                fg=self.empty_fg,
                justify="center",
                pady=30
            )
            empty_lbl.pack(fill="x")
            return

        check_fg = "#22C55E" if self.is_dark else "#16A34A"

        for task in completed:
            row = tk.Frame(self.scroll_frame, bg=self.card_bg)
            row.pack(fill="x", pady=2)

            # Sol minik yeşil tik
            tk.Label(
                row,
                text="✓",
                font=("Segoe UI", 8, "bold"),
                bg=self.card_bg,
                fg=check_fg,
                padx=2
            ).pack(side="left")

            # Görev Başlığı ve Vakti
            text_frame = tk.Frame(row, bg=self.card_bg)
            text_frame.pack(side="left", fill="x", expand=True, padx=4)

            # Görevin TAMAMI kesilmeden, satır satır sarılmış (wraplength) olarak gösterilsin
            title_lbl = tk.Label(
                text_frame,
                text=task.title,
                font=("Segoe UI", 8),
                bg=self.card_bg,
                fg=self.muted_fg,
                wraplength=215,
                justify="left",
                anchor="w"
            )
            title_lbl.pack(fill="x")

            time_str = task.completed_at.strftime("%H:%M") if task.completed_at else ""
            if time_str:
                tk.Label(
                    text_frame,
                    text=time_str,
                    font=("Segoe UI", 6),
                    bg=self.card_bg,
                    fg=self.sub_fg,
                    anchor="w"
                ).pack(fill="x")

            # Sade Glif Butonlar: Geri Al (↩) ve Sil (✕) - Butonsuz
            btn_frame = tk.Frame(row, bg=self.card_bg)
            btn_frame.pack(side="right")

            restore_btn = tk.Label(
                btn_frame,
                text="↩",
                font=("Segoe UI", 8),
                bg=self.card_bg,
                fg=self.muted_fg,
                padx=3,
                cursor="hand2"
            )
            restore_btn.pack(side="left")
            restore_btn.bind("<Button-1>", lambda e, t=task: self.restore_item(t.id))
            restore_btn.bind("<Enter>", lambda e, b=restore_btn: b.configure(fg=self.hover_text))
            restore_btn.bind("<Leave>", lambda e, b=restore_btn: b.configure(fg=self.muted_fg))

            del_btn = tk.Label(
                btn_frame,
                text="✕",
                font=("Segoe UI", 8),
                bg=self.card_bg,
                fg=self.del_fg,
                padx=3,
                cursor="hand2"
            )
            del_btn.pack(side="left")
            del_btn.bind("<Button-1>", lambda e, t=task: self.delete_item(t.id))
            del_btn.bind("<Enter>", lambda e, b=del_btn: b.configure(fg="#EF4444" if self.is_dark else "#DC2626"))
            del_btn.bind("<Leave>", lambda e, b=del_btn: b.configure(fg=self.del_fg))

    def restore_item(self, task_id):
        self.task_manager.restore_task(task_id)
        self.render_items()
        self.on_update_callback()

    def delete_item(self, task_id):
        self.task_manager.delete_task(task_id)
        self.render_items()
        self.on_update_callback()

    def clear_history(self, event=None):
        self.task_manager.clear_completed()
        self.render_items()
        self.on_update_callback()
