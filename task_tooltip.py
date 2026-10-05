import tkinter as tk
from datetime import datetime
from i18n import t

class TaskTooltip:
    """
    ToOoDo Görev Kartı Hover Tooltip (Detay Baloncuğu).
    Mouse ile görev kartının üzerine gelindiğinde görevin tam başlığını,
    oluşturulma/vade/tamamlanma detaylarını estetik bir şekilde gösterir.
    """
    def __init__(self, root):
        self.root = root
        self.tip_window = None
        self.current_task_id = None
        self.after_id = None

    def schedule_show(self, task, x_root, y_root, place_above=True, theme="paper"):
        # Zaten aynı görevin balonu açıksa bir şey yapma
        if self.current_task_id == task.id and self.tip_window and self.tip_window.winfo_exists():
            return
        self.cancel()
        self.current_task_id = task.id
        self.after_id = self.root.after(
            160,
            lambda: self.show(task, x_root, y_root, place_above, theme)
        )

    def show(self, task, x_root, y_root, place_above, theme):
        self.hide()
        self.current_task_id = task.id

        is_dark = (theme == "dark_kraft")
        bg_card = "#22201D" if is_dark else "#FCFAF7"
        border_c = "#3E3B36" if is_dark else "#DDD6C9"
        title_fg = "#EFECE6" if is_dark else "#2E2A27"
        sub_fg = "#9E9689" if is_dark else "#8C857B"
        check_fg = "#22C55E" if is_dark else "#16A34A"

        self.tip_window = tw = tk.Toplevel(self.root)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)

        frame = tk.Frame(tw, bg=bg_card, highlightthickness=1, highlightbackground=border_c, padx=10, pady=7)
        frame.pack(fill="both", expand=True)

        # Başlık ve İkon
        header_frame = tk.Frame(frame, bg=bg_card)
        header_frame.pack(fill="x")

        status_icon = "✓ " if task.completed else "• "
        icon_color = check_fg if task.completed else sub_fg
        tk.Label(
            header_frame,
            text=status_icon,
            font=("Segoe UI", 9, "bold"),
            bg=bg_card,
            fg=icon_color
        ).pack(side="left", anchor="nw")

        title_lbl = tk.Label(
            header_frame,
            text=task.title,
            font=("Calibri", 10, "bold"),
            bg=bg_card,
            fg=title_fg,
            wraplength=340,
            justify="left",
            anchor="w"
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        # Alt Detay Bilgisi (Vade / Tamamlanma Durumu)
        if task.completed:
            time_info = task.formatted_status
            sub_text = f"Tamamlandı: {time_info}"
        else:
            due_str = task.due_time.strftime("%d.%m.%Y %H:%M")
            rem_str = task.formatted_remaining
            sub_text = f"Vade: {due_str} ({rem_str})"

        tk.Label(
            frame,
            text=sub_text,
            font=("Segoe UI", 8),
            bg=bg_card,
            fg=sub_fg,
            anchor="w"
        ).pack(fill="x", pady=(4, 0))

        # Konumlandırma & Ekran Taşmasını Önleme
        tw.update_idletasks()
        w = tw.winfo_reqwidth()
        h = tw.winfo_reqheight()

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        pos_x = min(max(10, x_root - (w // 2)), screen_w - w - 10)
        if place_above:
            pos_y = max(10, y_root - h - 6)
        else:
            pos_y = min(screen_h - h - 10, y_root + 34)

        tw.wm_geometry(f"{w}x{h}+{pos_x}+{pos_y}")

    def hide(self):
        self.cancel()
        self.current_task_id = None
        if self.tip_window and self.tip_window.winfo_exists():
            self.tip_window.destroy()
        self.tip_window = None

    def cancel(self):
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
