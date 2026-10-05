import ctypes

LANGUAGES = {
    "tr": "Türkçe",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
}

TRANSLATIONS = {
    "tr": {
        "app_title": "ToOoDo",
        "empty_tasks": "🌿  Tüm görevler tamamlandı. Yeni not için [+] simgesine dokunun.",
        "due_now": "vakti doldu",
        "min_overdue": "{m} dk gecikti",
        "hour_overdue": "{h} sa gecikti",
        "days_left": "{d} gün",
        "hours_min_left": "{h} sa {m} dk",
        "min_left": "{m} dk",
        # Ekleme Penceresi
        "dialog_title": "✎  Yeni Görev",
        "quick_15m": "+15 dk",
        "quick_30m": "+30 dk",
        "quick_1h": "+1 sa",
        "quick_3h": "+3 sa",
        "quick_today_18": "Bugün 18:00",
        "quick_tomorrow_9": "Yarın 09:00",
        "due_label": "Teslim:",
        "pin_button": "Notu İğnele  ↵",
        # Geçmiş Penceresi
        "history_title": "✓  Tamamlananlar ({count})",
        "empty_history": "Henüz tamamlanan not yok.",
        "clear_history": "Geçmişi Temizle",
        "close_esc": "Kapat (Esc)",
        # Menü
        "menu_add_note": "✎  Yeni Not Ekle",
        "menu_history": "✓  Tamamlananlar Geçmişi",
        "menu_position": "📍 Çubuk Konumu",
        "pos_top": "Ekranın En Üstü (Pencereler Altında Açar)",
        "pos_above_taskbar": "Görev Çubuğunun Hemen Üstü (Simgeleri Kapatmaz)",
        "pos_bottom": "Ekranın En Dibi (Yalnızca Görev Çubuğu Gizliyse)",
        "menu_autostart": "Windows Başlangıcında Aç",
        "menu_autoscroll": "Otomatik Yavaş Akış",
        "menu_language": "🌐 Dil / Language",
        "lang_auto": "Otomatik (Sistem Dili: {name})",
        "menu_cat": "🐱 Sevimli Kedi",
        "cat_show": "Kediyi Göster",
        "cat_color_gray": "Kül Grisi (Duman)",
        "cat_color_ginger": "Sarman Tekir (Garfield)",
        "cat_color_white": "Pamuk Beyazı (Gümüş)",
        "menu_theme": "🎨 Defter Teması",
        "theme_light": "Krem Parşömen (Gündüz)",
        "theme_dark": "Koyu Kraft (Gece)",
        "tray_toggle": "👁 Şeridi Göster / Gizle",
        "hotkey_info": "Hızlı Not: Alt + Shift + T",
        "menu_exit": "✕ Kapat",
        "state_on": "Açık",
        "state_off": "Kapalı",
        "status_yesterday": "✓ Dün",
        "status_days_ago": "✓ {d}g",
        # Görev Kart Menüsü
        "card_complete": "✓ Tamamla (Üstünü Çiz)",
        "card_restore": "↩ Geri Al (Aktif Yap)",
        "card_snooze_15m": "⏱ +15 Dakika Ertele",
        "card_snooze_1h": "⏱ +1 Saat Ertele",
        "card_snooze_1d": "⏱ +1 Gün Ertele",
        "card_delete": "🗑 Çubuktan Kaldır / Sil",
    },
    "en": {
        "app_title": "ToOoDo",
        "empty_tasks": "🌿  All tasks completed. Tap [+] to pin a new note.",
        "due_now": "due now",
        "min_overdue": "{m}m overdue",
        "hour_overdue": "{h}h overdue",
        "days_left": "{d}d",
        "hours_min_left": "{h}h {m}m",
        "min_left": "{m}m",
        # Add Dialog
        "dialog_title": "✎  New Task",
        "quick_15m": "+15m",
        "quick_30m": "+30m",
        "quick_1h": "+1h",
        "quick_3h": "+3h",
        "quick_today_18": "Today 18:00",
        "quick_tomorrow_9": "Tomorrow 09:00",
        "due_label": "Due:",
        "pin_button": "Pin Note  ↵",
        # History Dialog
        "history_title": "✓  Completed ({count})",
        "empty_history": "No completed notes yet.",
        "clear_history": "Clear History",
        "close_esc": "Close (Esc)",
        # Menu
        "menu_add_note": "✎  Add New Note",
        "menu_history": "✓  Completed History",
        "menu_position": "📍 Bar Position",
        "pos_top": "Top of Screen (Windows Dock Below)",
        "pos_above_taskbar": "Above Taskbar (Does not cover icons)",
        "pos_bottom": "Bottom of Screen (Only if taskbar auto-hidden)",
        "menu_autostart": "Start with Windows",
        "menu_autoscroll": "Auto Slow Scroll",
        "menu_language": "🌐 Language",
        "lang_auto": "Automatic (System: {name})",
        "menu_cat": "🐱 Cat Companion",
        "cat_show": "Show Cat",
        "cat_color_gray": "Ash Gray (Russian Blue)",
        "cat_color_ginger": "Ginger Tabby",
        "cat_color_white": "Cotton White",
        "menu_theme": "🎨 Notebook Theme",
        "theme_light": "Cream Parchment (Light)",
        "theme_dark": "Dark Kraft (Night)",
        "tray_toggle": "👁 Show / Hide Bar",
        "hotkey_info": "Quick Note: Alt + Shift + T",
        "menu_exit": "✕ Exit",
        "state_on": "On",
        "state_off": "Off",
        "status_yesterday": "✓ Yesterday",
        "status_days_ago": "✓ {d}d",
        # Task Card Menu
        "card_complete": "✓ Complete (Cross Out)",
        "card_restore": "↩ Restore (Make Active)",
        "card_snooze_15m": "⏱ Snooze 15 min",
        "card_snooze_1h": "⏱ Snooze 1 hour",
        "card_snooze_1d": "⏱ Snooze 1 day",
        "card_delete": "🗑 Remove / Delete Note",
    },
    "de": {
        "app_title": "ToOoDo",
        "empty_tasks": "🌿  Alle Aufgaben erledigt. Tippen Sie auf [+], um eine Notiz anzupinnen.",
        "due_now": "fällig",
        "min_overdue": "{m} Min überfällig",
        "hour_overdue": "{h} Std überfällig",
        "days_left": "{d} Tage",
        "hours_min_left": "{h} Std {m} Min",
        "min_left": "{m} Min",
        "dialog_title": "✎  Neue Aufgabe",
        "quick_15m": "+15 Min",
        "quick_30m": "+30 Min",
        "quick_1h": "+1 Std",
        "quick_3h": "+3 Std",
        "quick_today_18": "Heute 18:00",
        "quick_tomorrow_9": "Morgen 09:00",
        "due_label": "Fällig:",
        "pin_button": "Notiz anheften  ↵",
        "history_title": "✓  Erledigt ({count})",
        "empty_history": "Noch keine erledigten Notizen.",
        "clear_history": "Verlauf löschen",
        "close_esc": "Schließen (Esc)",
        "menu_add_note": "✎  Neue Notiz hinzufügen",
        "menu_history": "✓  Verlauf der erledigten Notizen",
        "menu_position": "📍 Leistenposition",
        "pos_top": "Oben am Bildschirm (Fenster docken unten)",
        "pos_above_taskbar": "Über der Taskleiste (Verdeckt nichts)",
        "pos_bottom": "Ganz unten (Nur bei ausgeblendeter Taskleiste)",
        "menu_autostart": "Mit Windows starten",
        "menu_autoscroll": "Automatischer Bildlauf",
        "menu_language": "🌐 Sprache / Language",
        "lang_auto": "Automatisch (System: {name})",
        "menu_cat": "🐱 Katzenbegleiter",
        "cat_show": "Katze anzeigen",
        "cat_color_gray": "Aschgrau",
        "cat_color_ginger": "Roter Tabby",
        "cat_color_white": "Baumwollweiß",
        "menu_theme": "🎨 Notizbuch-Thema",
        "theme_light": "Cremefarbenes Pergament (Hell)",
        "theme_dark": "Dunkles Kraftpapier (Nacht)",
        "tray_toggle": "👁 Leiste anzeigen / verbergen",
        "hotkey_info": "Schnellnotiz: Alt + Shift + T",
        "menu_exit": "✕ Beenden",
        "state_on": "Ein",
        "state_off": "Aus",
        "status_yesterday": "✓ Gestern",
        "status_days_ago": "✓ {d}T",
        "card_complete": "✓ Erledigen (Durchstreichen)",
        "card_restore": "↩ Wiederherstellen (Aktivieren)",
        "card_snooze_15m": "⏱ +15 Min verschieben",
        "card_snooze_1h": "⏱ +1 Std verschieben",
        "card_snooze_1d": "⏱ +1 Tag verschieben",
        "card_delete": "🗑 Entfernen / Löschen",
    },
    "es": {
        "app_title": "ToOoDo",
        "empty_tasks": "🌿  Todas las tareas completadas. Toca [+] para fijar una nota.",
        "due_now": "vencido",
        "min_overdue": "{m}m retrasado",
        "hour_overdue": "{h}h retrasado",
        "days_left": "{d}d",
        "hours_min_left": "{h}h {m}m",
        "min_left": "{m}m",
        "dialog_title": "✎  Nueva Tarea",
        "quick_15m": "+15m",
        "quick_30m": "+30m",
        "quick_1h": "+1h",
        "quick_3h": "+3h",
        "quick_today_18": "Hoy 18:00",
        "quick_tomorrow_9": "Mañana 09:00",
        "due_label": "Entrega:",
        "pin_button": "Fijar Nota  ↵",
        "history_title": "✓  Completadas ({count})",
        "empty_history": "Aún no hay notas completadas.",
        "clear_history": "Borrar Historial",
        "close_esc": "Cerrar (Esc)",
        "menu_add_note": "✎  Añadir Nueva Nota",
        "menu_history": "✓  Historial de Completadas",
        "menu_position": "📍 Posición de la Barra",
        "pos_top": "Parte Superior (Ventanas se acoplan abajo)",
        "pos_above_taskbar": "Sobre Barra de Tareas (No cubre iconos)",
        "pos_bottom": "Parte Inferior (Solo si barra está oculta)",
        "menu_autostart": "Iniciar con Windows",
        "menu_autoscroll": "Desplazamiento Automático",
        "menu_language": "🌐 Idioma / Language",
        "lang_auto": "Automático (Sistema: {name})",
        "menu_cat": "🐱 Compañero Felino",
        "cat_show": "Mostrar Gato",
        "cat_color_gray": "Gris Ceniza",
        "cat_color_ginger": "Tabby Naranja",
        "cat_color_white": "Blanco Algodón",
        "menu_theme": "🎨 Tema del Cuaderno",
        "theme_light": "Pergamino Crema (Claro)",
        "theme_dark": "Kraft Oscuro (Noche)",
        "tray_toggle": "👁 Mostrar / Ocultar Barra",
        "hotkey_info": "Nota Rápida: Alt + Shift + T",
        "menu_exit": "✕ Salir",
        "state_on": "Activado",
        "state_off": "Desactivado",
        "status_yesterday": "✓ Ayer",
        "status_days_ago": "✓ {d}d",
        "card_complete": "✓ Completar (Tachar)",
        "card_restore": "↩ Restaurar (Hacer activo)",
        "card_snooze_15m": "⏱ Posponer 15 min",
        "card_snooze_1h": "⏱ Posponer 1 hora",
        "card_snooze_1d": "⏱ Posponer 1 día",
        "card_delete": "🗑 Quitar / Eliminar",
    }
}

def detect_system_language():
    """
    Windows yerel UI dilini doğrudan Win32 API ile tespit eder.
    Örn: 31 -> tr, 9 -> en, 7 -> de, 10 -> es
    """
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        primary_id = lang_id & 0x3FF
        mapping = {
            0x1F: "tr",  # 31: Turkish
            0x09: "en",  # 9: English
            0x07: "de",  # 7: German
            0x0A: "es",  # 10: Spanish
        }
        if primary_id in mapping:
            return mapping[primary_id]
    except Exception:
        pass
    return "en"

class I18n:
    def __init__(self, selected_lang="auto"):
        self.selected_lang = selected_lang
        self.system_lang = detect_system_language()

    @property
    def current_lang(self):
        if self.selected_lang == "auto" or not self.selected_lang:
            return self.system_lang if self.system_lang in TRANSLATIONS else "en"
        return self.selected_lang if self.selected_lang in TRANSLATIONS else "en"

    def get(self, key, **kwargs):
        lang = self.current_lang
        text = TRANSLATIONS.get(lang, {}).get(key)
        if text is None:
            # Fallback to English
            text = TRANSLATIONS.get("en", {}).get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

    def set_language(self, lang_code):
        self.selected_lang = lang_code

# Global nesne
_i18n = I18n()

def t(key, **kwargs):
    return _i18n.get(key, **kwargs)

def set_lang(lang_code):
    _i18n.set_language(lang_code)

def get_current_lang():
    return _i18n.current_lang

def get_selected_lang():
    return _i18n.selected_lang

def get_system_lang():
    return _i18n.system_lang
