import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from paths import get_resource_path

ASSETS_DIR = get_resource_path("assets")

class CatCompanion:
    """
    ToOoDo Sevimli Kedi Masaüstü Arkadaşı.
    16x32 (32x32 ızgara) animasyon karelerini Canvas üzerinde canlı olarak oynatır.
    """
    def __init__(self, root, canvas, config, on_redraw_needed=None):
        self.root = root
        self.canvas = canvas
        self.config = config
        self.on_redraw_needed = on_redraw_needed

        # Ayarlar
        self.enabled = self.config.get("cat_enabled", True)
        self.variant = self.config.get("cat_variant", "gray") # "gray", "ginger", "white"

        # Konumlar
        self.home_x = 22
        self.x = float(self.home_x)
        self.y = 15  # 30px çubuğun dikey merkezi
        self.target_x = float(self.home_x)

        # Durum Değişkenleri
        # "sleep", "yawn", "idle", "wander", "chase_mouse", "return_home", "meow", "alert_overdue", "peaceful_loaf"
        self.state = "sleep"
        self.current_anim = "sleep_l"
        self.frame_idx = 0
        self.anim_timer = None
        self.facing_right = True

        # Görev Durumları (Geciken Görevler ve Huzurlu Uyku)
        self.has_tasks = True
        self.overdue_task_x = None
        self.alert_timer = 0
        self.alert_action_ticks = 0

        # Fare Takip Bilgileri
        self.mouse_on_bar = False
        self.mouse_x = None
        self.mouse_last_seen = 0
        self.idle_ticks = 0

        # Sprite Karelerini Önbelleğe Al
        self.sprites = {} # {variant: {anim_name: [PhotoImage, ...]}}
        self.load_all_sprites()

        # Canvas Olaylarını Dinle
        self.canvas.bind("<Motion>", self.on_canvas_motion, add="+")
        self.canvas.bind("<Enter>", self.on_canvas_enter, add="+")
        self.canvas.bind("<Leave>", self.on_canvas_leave, add="+")

        # Döngüyü Başlat
        if self.enabled:
            self.tick()

    def load_all_sprites(self):
        variant_files = {
            "gray": "cat_gray.png",
            "ginger": "cat_ginger.png",
            "white": "cat_white.png",
        }

        # 32x32 ızgara satır indeksleri ve kare sayıları
        anim_rows = {
            "sit": (0, 6),
            "stand": (1, 8),
            "loaf": (3, 10),
            "walk_right": (6, 8),
            "walk_left": (7, 8),
            "sleep_l": (12, 2),
            "sleep_r": (13, 2),
            "stretch_l": (18, 4),
            "meow": (28, 3),
            "yawn": (32, 8),
            "wash": (36, 9),
            "scratch_r": (40, 11),
            "paw_left": (46, 7),
            "paw_right": (47, 7),
            "hind_legs": (52, 4),
        }

        for var_name, filename in variant_files.items():
            path = os.path.join(ASSETS_DIR, filename)
            if not os.path.exists(path):
                continue

            try:
                sheet = Image.open(path).convert("RGBA")
                self.sprites[var_name] = {}

                for anim_name, (row_idx, max_frames) in anim_rows.items():
                    frames = []
                    y = row_idx * 32
                    for col in range(max_frames):
                        x = col * 32
                        cell = sheet.crop((x, y, x + 32, y + 32))
                        frames.append(ImageTk.PhotoImage(cell))
                    self.sprites[var_name][anim_name] = frames
            except Exception as e:
                print(f"Error loading sprites for {var_name}: {e}")

    def set_variant(self, new_variant):
        if new_variant in self.sprites:
            self.variant = new_variant
            self.config["cat_variant"] = new_variant
            self.render()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.config["cat_enabled"] = enabled
        if not self.enabled:
            self.canvas.delete("cat_sprite")
            if self.anim_timer:
                self.root.after_cancel(self.anim_timer)
                self.anim_timer = None
        else:
            self.state = "sleep"
            self.current_anim = "sleep_l"
            self.x = float(self.home_x)
            self.tick()

    def on_canvas_enter(self, event):
        self.mouse_on_bar = True
        self.mouse_x = event.x
        self.mouse_last_seen = 0
        if self.enabled:
            self.wake_up_to_mouse()

    def on_canvas_leave(self, event):
        self.mouse_on_bar = False
        self.mouse_last_seen = 0

    def on_canvas_motion(self, event):
        self.mouse_on_bar = True
        self.mouse_x = event.x
        self.mouse_last_seen = 0
        if self.enabled:
            if self.state in ("sleep", "return_home"):
                self.wake_up_to_mouse()

    def wake_up_to_mouse(self):
        """Fare çubuğa geldiğinde kediyi anında uyandır ve fareye koştur"""
        if self.state not in ("chase_mouse", "meow"):
            self.state = "chase_mouse"
            self.current_anim = "walk_right"
            self.frame_idx = 0
            if self.anim_timer:
                self.root.after_cancel(self.anim_timer)
                self.anim_timer = None
            self.tick()

    def trigger_meow(self):
        """Kediye tıklandığında veya görev tamamlandığında miyavlama tetikle"""
        if not self.enabled:
            return
        self.state = "meow"
        self.current_anim = "meow"
        self.frame_idx = 0
        if self.anim_timer:
            self.root.after_cancel(self.anim_timer)
            self.anim_timer = None
        self.tick()

    def is_point_on_cat(self, px, py):
        """Tıklanan noktanın kedi üzerinde olup olmadığını kontrol et"""
        if not self.enabled:
            return False
        return (abs(px - self.x) <= 16 and 0 <= py <= 30)

    def update_tasks_state(self, has_tasks, overdue_task_x=None):
        """Görev listesi durumunu güncelle"""
        self.has_tasks = has_tasks
        self.overdue_task_x = overdue_task_x
        # Fare çubukta değilse ve kovalamıyorsa sol köşede uykuya devam etsin
        if not self.mouse_on_bar and self.state not in ("chase_mouse", "return_home", "meow", "alert_overdue"):
            self.state = "sleep"
            self.current_anim = "sleep_l"

    def tick(self):
        """Ana davranış ve animasyon zamanlayıcısı"""
        if not self.enabled:
            return

        interval = 90

        # Gerçek imleç konumunu Windows genelinde doğrula (hızlı çıkışları anında yakalamak için)
        try:
            x_root, y_root = self.root.winfo_pointerxy()
            cx = self.canvas.winfo_rootx()
            cy = self.canvas.winfo_rooty()
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            if not (cx <= x_root <= cx + cw and cy <= y_root <= cy + ch):
                self.mouse_on_bar = False
        except Exception:
            pass

        # 1. State Machine Güncellemesi
        if self.state == "alert_overdue":
            # Geciken Göreve Kedinin Tepkisi: Göreve doğru gidip patiyle işaret etsin
            interval = 75
            if self.overdue_task_x is not None:
                target = max(20.0, float(self.overdue_task_x) - 18.0)
                dx = target - self.x
                if abs(dx) > 4:
                    speed = 3.8
                    step = speed if dx > 0 else -speed
                    self.x += step
                    self.facing_right = (dx > 0)
                    self.current_anim = "walk_right" if self.facing_right else "walk_left"
                else:
                    # Göreve yetişti! Dikkat çekici pati veya alarm duruşu
                    self.alert_action_ticks += 1
                    self.current_anim = "paw_right" if self.facing_right else "paw_left"
                    if self.alert_action_ticks > 20: # ~1.5 saniye uyar
                        self.alert_action_ticks = 0
                        self.state = "return_home"
            else:
                self.state = "return_home"

        elif self.state == "sleep":
            self.current_anim = "sleep_l"
            self.x = float(self.home_x)
            
            # Geciken görev varsa ara ara gidip uyarsın (~40 saniyede bir)
            if self.overdue_task_x is not None:
                self.alert_timer += 1
                if self.alert_timer > 15:
                    self.alert_timer = 0
                    self.state = "alert_overdue"
                    self.alert_action_ticks = 0

            # Kedi sol köşesinde huzurla ve tamamen sabit uyur (kendi kendine ortalıkta gezinmez!)
            # Yavaş ve dinlendirici nefes alma ritmi:
            # 2.4 saniye tamamen sakin dinlenme (kare 0), 0.7 saniye hafif nefes (kare 1)
            if self.frame_idx == 0:
                interval = 2400
            else:
                interval = 700

        elif self.state == "chase_mouse":
            interval = 60 # Fareyi kovalarken akıcı ve hızlı hareket
            if self.mouse_on_bar and self.mouse_x is not None:
                max_w = max(100, self.canvas.winfo_width() - 110)
                target = min(float(self.mouse_x), max_w)
                dx = target - self.x

                if abs(dx) > 28:
                    speed = 5.2
                    step = speed if dx > 0 else -speed
                    self.x += step
                    self.facing_right = (dx > 0)
                    self.current_anim = "walk_right" if self.facing_right else "walk_left"
                else:
                    # Fareye yetişti! Etkileşim göster (pati at, iki ayağa kalk, bak)
                    self.idle_ticks += 1
                    if self.idle_ticks % 14 == 0:
                        pick = random.choice(["hind_legs", "paw_right" if self.facing_right else "paw_left", "sit"])
                        self.current_anim = pick
                        self.frame_idx = 0
            else:
                # Fare çubuktan ayrıldı, ~0.6 saniye sonra köşeye dön
                self.mouse_last_seen += 1
                if self.mouse_last_seen > 8:
                    self.mouse_last_seen = 0
                    self.state = "return_home"

        elif self.state == "return_home":
            interval = 65
            dx = self.home_x - self.x
            if abs(dx) > 3:
                step = -3.5 if dx < 0 else 3.5
                self.x += step
                self.facing_right = (dx > 0)
                self.current_anim = "walk_right" if self.facing_right else "walk_left"
            else:
                self.x = float(self.home_x)
                self.state = "sleep"
                self.current_anim = "sleep_l"
                self.frame_idx = 0
                interval = 2400

        elif self.state == "meow":
            interval = 110
            self.current_anim = "meow"
            frames = self.get_frames("meow")
            if self.frame_idx >= len(frames) - 1:
                # Miyavlama bitti, fare oradaysa kovalamaya devam et, yoksa yuvasında uyu
                if self.mouse_on_bar:
                    self.state = "chase_mouse"
                    self.current_anim = "sit"
                else:
                    self.state = "return_home" if abs(self.x - self.home_x) > 5 else "sleep"
                    self.current_anim = "sleep_l"
                self.frame_idx = 0

        # 2. Kare İlerlemesi & Çizim
        self.advance_frame()
        self.render()

        # Bir sonraki tick zamanlaması
        self.anim_timer = self.root.after(interval, self.tick)

    def get_frames(self, anim_name):
        var_dict = self.sprites.get(self.variant, {})
        return var_dict.get(anim_name, [])

    def advance_frame(self):
        frames = self.get_frames(self.current_anim)
        if not frames:
            return
        self.frame_idx = (self.frame_idx + 1) % len(frames)

    def render(self):
        if not self.enabled:
            self.canvas.delete("cat_sprite")
            return

        frames = self.get_frames(self.current_anim)
        if not frames:
            return

        idx = min(self.frame_idx, len(frames) - 1)
        img = frames[idx]

        # Canvas üzerinde kediyi çiz veya güncelle
        draw_x = int(self.x)
        draw_y = self.y

        # Eğer zaten varsa sadece koordinat ve görsel güncelle, yoksa oluştur
        existing = self.canvas.find_withtag("cat_sprite")
        if existing:
            self.canvas.coords(existing[0], draw_x, draw_y)
            self.canvas.itemconfig(existing[0], image=img)
            self.canvas.tag_raise(existing[0])
        else:
            self.canvas.create_image(draw_x, draw_y, image=img, tags=("cat_sprite",))
            self.canvas.tag_raise("cat_sprite")
