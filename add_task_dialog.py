import tkinter as tk
from datetime import datetime, timedelta
from i18n import t

class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent, on_save_callback, x, y, place_above=True, theme="paper"):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        self.theme = theme
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        is_dark = (self.theme == "dark_kraft")
        bg_main = "#181715" if is_dark else "#F7F5F0"
        card_bg = "#22201D" if is_dark else "#FCFAF7"
        border_c = "#3A3733" if is_dark else "#DED8CE"
        text_fg = "#E2DCD2" if is_dark else "#443F3B"
        close_fg = "#827B70" if is_dark else "#A8A196"
        entry_bg = "#2C2A26" if is_dark else "#FFFFFF"
        entry_border = "#3D3933" if is_dark else "#E2DDD5"
        entry_fg = "#F0EBE1" if is_dark else "#2D2A28"
        label_fg = "#968F83" if is_dark else "#8C857A"
        btn_bg = "#36322D" if is_dark else "#EFECE5"
        btn_fg = "#E2DCD2" if is_dark else "#443F3B"
        btn_act_bg = "#45403A" if is_dark else "#E2DDD5"

        self.configure(bg=bg_main)
        self.target_time = datetime.now() + timedelta(hours=1)

        # Daha kompakt, minimalist boyutlar
        width = 280
        height = 195
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        pos_x = min(max(10, x - width + 30), screen_w - width - 10)
        if place_above:
            pos_y = max(10, y - height - 6)
        else:
            pos_y = min(screen_h - height - 10, y + 6)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        # Zarif Kağıt Kart Çerçevesi
        container = tk.Frame(self, bg=card_bg, highlightthickness=1, highlightbackground=border_c)
        container.pack(fill="both", expand=True)

        # 1. Başlık & Kapat Butonu (Daha küçük punto, zarif)
        header = tk.Frame(container, bg=card_bg)
        header.pack(fill="x", padx=12, pady=(10, 4))

        tk.Label(
            header,
            text=t("dialog_title"),
            font=("Segoe UI", 9, "bold"),
            bg=card_bg,
            fg=text_fg
        ).pack(side="left")

        close_btn = tk.Label(
            header,
            text="✕",
            font=("Segoe UI", 8),
            bg=card_bg,
            fg=close_fg,
            cursor="hand2"
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.destroy())

        # 2. Görev Başlığı Girişi (İnce, sade)
        entry_frame = tk.Frame(container, bg=entry_bg, highlightthickness=1, highlightbackground=entry_border)
        entry_frame.pack(fill="x", padx=12, pady=3)

        self.title_entry = tk.Entry(
            entry_frame,
            font=("Segoe UI", 9),
            bg=entry_bg,
            fg=entry_fg,
            insertbackground=entry_fg,
            relief="flat",
            bd=4
        )
        self.title_entry.pack(fill="x", padx=2, pady=1)
        self.title_entry.focus_set()

        # 3. Hızlı Seçim Butonları (Küçük, soft etiketler)
        quick_frame = tk.Frame(container, bg=card_bg)
        quick_frame.pack(fill="x", padx=12, pady=4)

        quick_buttons = [
            (t("quick_15m"), timedelta(minutes=15)),
            (t("quick_30m"), timedelta(minutes=30)),
            (t("quick_1h"), timedelta(hours=1)),
            (t("quick_3h"), timedelta(hours=3)),
            (t("quick_today_18"), "today_18"),
            (t("quick_tomorrow_9"), "tomorrow_9"),
        ]

        q_bg = "#2B2824" if is_dark else "#F2EFEA"
        q_fg = "#C2BCB2" if is_dark else "#5C554E"
        q_h_bg = "#38342E" if is_dark else "#E5DFD5"
        q_h_fg = "#FFFFFF" if is_dark else "#2D2A28"

        for i, (label, delta) in enumerate(quick_buttons):
            row = i // 3
            col = i % 3
            btn = tk.Label(
                quick_frame,
                text=label,
                font=("Segoe UI", 7),
                bg=q_bg,
                fg=q_fg,
                padx=4,
                pady=2,
                cursor="hand2",
                relief="flat"
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            quick_frame.columnconfigure(col, weight=1)
            btn.bind("<Button-1>", lambda e, d=delta: self.set_quick_time(d))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=q_h_bg, fg=q_h_fg))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=q_bg, fg=q_fg))

        # 4. Teslim Vakti Satırı
        time_info_frame = tk.Frame(container, bg=card_bg)
        time_info_frame.pack(fill="x", padx=12, pady=2)

        tk.Label(
            time_info_frame,
            text=t("due_label"),
            font=("Segoe UI", 8),
            bg=card_bg,
            fg=label_fg
        ).pack(side="left")

        self.time_var = tk.StringVar(value=self.target_time.strftime("%Y-%m-%d %H:%M"))
        self.time_entry = tk.Entry(
            time_info_frame,
            textvariable=self.time_var,
            font=("Segoe UI", 8),
            bg=entry_bg,
            fg=entry_fg,
            insertbackground=entry_fg,
            relief="flat",
            highlightthickness=1,
            highlightbackground=entry_border,
            width=16
        )
        self.time_entry.pack(side="right")

        # 5. İğnele Butonu (Minimal, sade, yumuşak ton)
        save_btn = tk.Button(
            container,
            text=t("pin_button"),
            font=("Segoe UI", 8),
            bg=btn_bg,
            fg=btn_fg,
            activebackground=btn_act_bg,
            activeforeground="#FFFFFF" if is_dark else "#2D2A28",
            relief="flat",
            bd=0,
            pady=4,
            cursor="hand2",
            command=self.save
        )
        save_btn.pack(fill="x", padx=12, pady=(6, 10))

        # Kısayollar
        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.destroy())

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

    def set_quick_time(self, delta):
        now = datetime.now()
        if delta == "tomorrow_9":
            tomorrow = now + timedelta(days=1)
            self.target_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        elif delta == "today_18":
            target = now.replace(hour=18, minute=0, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            self.target_time = target
        else:
            self.target_time = now + delta

        self.time_var.set(self.target_time.strftime("%Y-%m-%d %H:%M"))

    def save(self):
        title = self.title_entry.get().strip()
        if not title:
            return

        time_str = self.time_var.get().strip()
        try:
            due_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                due_time = datetime.strptime(time_str, "%H:%M")
                now = datetime.now()
                due_time = now.replace(hour=due_time.hour, minute=due_time.minute, second=0)
                if due_time <= now:
                    due_time += timedelta(days=1)
            except ValueError:
                due_time = datetime.now() + timedelta(hours=1)

        self.on_save_callback(title, due_time)
        self.destroy()
