import json
import os
import sys
import shutil
import uuid
from datetime import datetime, timedelta
from paths import get_data_dir

DATA_FILE = os.path.join(get_data_dir(), "tasks.json")

class Task:
    def __init__(self, title, due_time, task_id=None, completed=False, created_at=None, completed_at=None):
        self.id = task_id or str(uuid.uuid4())
        self.title = title.strip()
        if isinstance(due_time, str):
            try:
                self.due_time = datetime.fromisoformat(due_time)
            except ValueError:
                self.due_time = datetime.now() + timedelta(hours=1)
        else:
            self.due_time = due_time
            
        self.completed = completed
        
        if created_at is None:
            self.created_at = datetime.now()
        elif isinstance(created_at, str):
            self.created_at = datetime.fromisoformat(created_at)
        else:
            self.created_at = created_at

        if completed_at is None:
            self.completed_at = None
        elif isinstance(completed_at, str):
            self.completed_at = datetime.fromisoformat(completed_at)
        else:
            self.completed_at = completed_at

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return None
        return cls(
            title=data.get("title", ""),
            due_time=data.get("due_time", datetime.now() + timedelta(hours=1)),
            task_id=data.get("id"),
            completed=data.get("completed", False),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "due_time": self.due_time.isoformat(),
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    @property
    def remaining_seconds(self):
        return (self.due_time - datetime.now()).total_seconds()

    @property
    def urgency_level(self):
        rem = self.remaining_seconds
        if rem <= 0:
            return "expired"
        elif rem <= 30 * 60:
            return "critical"
        elif rem <= 2 * 3600:
            return "warning"
        elif rem <= 8 * 3600:
            return "moderate"
        else:
            return "normal"

    @property
    def formatted_remaining(self):
        from i18n import t
        rem = self.remaining_seconds
        if rem <= 0:
            past = abs(int(rem))
            if past < 60:
                return t("due_now")
            elif past < 3600:
                return t("min_overdue", m=past // 60)
            else:
                return t("hour_overdue", h=past // 3600)
        
        rem_int = int(rem)
        hours = rem_int // 3600
        minutes = (rem_int % 3600) // 60
        
        if hours > 24:
            days = hours // 24
            return t("days_left", d=days)
        elif hours > 0:
            return t("hours_min_left", h=hours, m=minutes)
        else:
            return t("min_left", m=max(1, minutes))

    @property
    def formatted_status(self):
        if not self.completed:
            return self.formatted_remaining

        from i18n import t
        if not self.completed_at:
            return "✓"

        now = datetime.now()
        diff = now - self.completed_at

        # Bugün mü tamamlandı?
        if self.completed_at.date() == now.date():
            return f"✓ {self.completed_at.strftime('%H:%M')}"
        elif diff.days == 1 or (diff.days == 0 and self.completed_at.day != now.day):
            return t("status_yesterday")
        else:
            days = max(1, diff.days)
            return t("status_days_ago", d=days)


class TaskManager:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.tasks = []
        self.load_tasks()

    def _read_tasks_from_file(self, filepath):
        if not filepath or not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    tasks = []
                    for item in data:
                        t = Task.from_dict(item)
                        if t:
                            tasks.append(t)
                    return tasks if tasks else None
        except Exception:
            pass
        return None

    def load_tasks(self):
        # 1. Öncelikle merkezi AppData veritabanını oku
        tasks = self._read_tasks_from_file(self.data_file)

        # 2. Eğer dosya bozulmuşsa veya boşsa otomatik .bak yedeğini kontrol et
        if not tasks:
            tasks = self._read_tasks_from_file(self.data_file + ".bak")

        # 3. Eğer AppData'da henüz görev yoksa diğer olası konumlardan ara ve otomatik kurtar:
        if not tasks:
            exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else ""
            script_dir = os.path.dirname(os.path.abspath(__file__))
            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

            candidates = [
                os.path.join(script_dir, "tasks.json"),
                os.path.join(exe_dir, "tasks.json") if exe_dir else "",
                os.path.join(desktop_dir, "Yeni Metin Belgesi.txt"),
                os.path.join(script_dir, "tasks.json.bak"),
            ]
            for candidate in candidates:
                if candidate:
                    recovered = self._read_tasks_from_file(candidate)
                    if recovered:
                        tasks = recovered
                        break

        # 4. Hiçbir yerde hiçbir görev bulunamazsa (ilk sıfır kurulum)
        if not tasks:
            now = datetime.now()
            self.tasks = [
                Task("Kahve eşliğinde planlama", now + timedelta(minutes=25)),
                Task("E-postaları yanıtla", now + timedelta(hours=1, minutes=30)),
                Task("Akşam yürüyüşü", now + timedelta(hours=4)),
            ]
            self.save_tasks()
            return

        self.tasks = tasks
        # Verileri hem AppData'ya hem de yerel yedeklere güvenle sabitle
        self.save_tasks()

    def save_tasks(self):
        try:
            # 1. Mevcut sağlam dosyayı önce .bak olarak yedekle
            if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 10:
                try:
                    shutil.copy2(self.data_file, self.data_file + ".bak")
                except Exception:
                    pass

            # 2. Atomik yazım: Önce .tmp dosyasına yazıp ardından replace et (dosya bozulmasını engeller)
            tmp_file = self.data_file + ".tmp"
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in self.tasks], f, ensure_ascii=False, indent=2)

            os.replace(tmp_file, self.data_file)

            # 3. Çift Güvenlik: Proje klasörüne de ayna kopyasını al (yerel yedek)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            local_tasks = os.path.join(script_dir, "tasks.json")
            if os.path.abspath(local_tasks) != os.path.abspath(self.data_file):
                try:
                    shutil.copy2(self.data_file, local_tasks)
                except Exception:
                    pass
        except Exception as e:
            print("save_tasks error:", e)

    def add_task(self, title, due_time):
        task = Task(title=title, due_time=due_time)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def complete_task(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                t.completed = True
                t.completed_at = datetime.now()
                break
        self.save_tasks()

    def restore_task(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                t.completed = False
                t.completed_at = None
                # Eğer süresi geçmişse 1 saat sonraya ayarla
                if t.due_time <= datetime.now():
                    t.due_time = datetime.now() + timedelta(hours=1)
                break
        self.save_tasks()

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save_tasks()

    def clear_completed(self):
        self.tasks = [t for t in self.tasks if not t.completed]
        self.save_tasks()

    def snooze_task(self, task_id, minutes):
        for t in self.tasks:
            if t.id == task_id:
                t.due_time = max(datetime.now(), t.due_time) + timedelta(minutes=minutes)
                break
        self.save_tasks()

    def get_active_tasks_sorted(self):
        return sorted([t for t in self.tasks if not t.completed], key=lambda t: t.due_time)

    def get_completed_tasks_sorted(self):
        completed = [t for t in self.tasks if t.completed]
        # En son tamamlanan en üstte
        return sorted(completed, key=lambda t: t.completed_at or t.created_at, reverse=True)

    def get_bar_tasks(self):
        """
        Çubuk üzerinde gösterilecek görevleri döndürür:
        1. Aktif (yapılmamış) görevler: Vadesine göre sıralı en önde yer alır.
        2. Son 3 gün içinde tamamlanmış görevler: Sona atılır, üstü çizili kalır.
        3 günden eski olanlar çubuktan otomatik kalkar (arşiv/geçmişte kalır).
        """
        now = datetime.now()
        three_days_ago = now - timedelta(days=3)

        # 1. Aktif görevler (vadesi en yakın olan en başta)
        active = sorted([t for t in self.tasks if not t.completed], key=lambda t: t.due_time)

        # 2. Son 3 gün içinde tamamlananlar (kullanıcı kaldırana kadar çubukta sona atılmış kalır)
        recent_completed = []
        for t in self.tasks:
            if t.completed:
                if t.completed_at is None:
                    t.completed_at = t.created_at or now
                if t.completed_at >= three_days_ago:
                    recent_completed.append(t)

        # En son tamamlanan aktiflerin hemen ardında görünsün
        recent_completed = sorted(recent_completed, key=lambda t: t.completed_at, reverse=True)

        return active + recent_completed
