import os
import glob
import shutil
import sys
import winreg
import json
import locale
import threading
import time
import urllib.request

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    PIL_AVAILABLE = False

from PyQt6.QtCore import Qt, QSize, QPoint, QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QScrollArea, QGridLayout, 
    QFrame, QPushButton, QFileDialog, QComboBox, 
    QLineEdit, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QImage, QPainter, QPainterPath, 
    QColor, QPen, QDesktopServices, QCursor
)

CONFIG_FILE = "config.txt"
ICON_FILE_NAME = "iconShdS.ico"
ICON_PNG_NAME = "iconShdS.png"

ICON_SETTINGS = "btn_settings.png"
ICON_REFRESH = "btn_refresh.png"
ICON_VIEW = "btn_view.png"
ICON_MODE_AUTO = "btn_mode_auto.png"
ICON_MODE_CUSTOM = "btn_mode_custom.png"
ICON_UPDATE_GIT = "btn_update_git.png"

VERSION = "v4.2 Major Update FREE"
GITHUB_CHECK_TAG = "v4.2"
GITHUB_RELEASE_URL = "https://boosty.to/steriagame"


def resolve_resource_path(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    direct_path = os.path.join(base_dir, file_name)
    if os.path.exists(direct_path):
        return direct_path
    debug_path = os.path.join(base_dir, "Debug", file_name)
    if os.path.exists(debug_path):
        return debug_path
    return file_name


def get_system_language():
    try:
        lang, _ = locale.getlocale()
        if lang and lang.lower().startswith("ru"):
            return "RU"
    except Exception:
        for env_var in ["LANG", "LC_ALL", "LC_CTYPE"]:
            val = os.environ.get(env_var, "")
            if val.lower().startswith("ru"):
                return "RU"
    return "EN"


LANG = get_system_language()
TRANSLATIONS = {
    "RU": {
        "title": "ScreenHDSteam Studio",
        "settings_title": "НАСТРОЙКИ СИНХРОНИЗАЦИИ",
        "settings_btn": " Настройки",
        "hd_label": "Источник (Папка HD с четкими копиями):",
        "hd_placeholder": "Выберите папку с HD-скриншотами...",
        "steam_label": "Выберите игру из найденных в Steam:",
        "game_select": "Выберите игру...",
        "no_games": "Игры со скриншотами не найдены",
        "save_settings": "СОХРАНИТЬ НАСТРОЙКИ",
        "browse": "Обзор",
        "upgrade_btn": "АПГРЕЙД В HD И ОЧИСТКА ПАМЯТИ",
        "refresh_btn": " ОБНОВИТЬ",
        "custom_btn": "ЗАМЕНИТЬ КАСТОМНЫМ ФАЙЛОМ",
        "view_btn": " ПРОСМОТР",
        "mode_auto": " Авто-апгрейд HD",
        "mode_custom": " Кастомная замена",
        "msg_no_game": "Игра не выбрана.\n\nПожалуйста, перейдите в Настройки и выберите игру\nиз выпадающего списка найденных в Steam.",
        "msg_no_screenshots": "Синхронизированные кадры не найдены.\n\nПрограмма отображает только те файлы из HD папки,\nимена которых совпадают со скриншотами в выбранной игре.",
        "select_error": "Внимание",
        "select_warning": "Выберите кадры для апгрейда!",
        "success_title": "Успешно",
        "success_msg": "Скриншоты заменены на HD, миниатюры обновлены: {} шт.<br><br><span style='color: #ef4444; font-weight: bold;'>ВАЖНО!</span> Скриншоты могут не обновиться в самом Steam пока Steam будет не перезагружен.",
        "file_error": "Ошибка файла",
        "select_single_warn": "Пожалуйста, выберите ровно один скриншот Steam для кастомной замены.",
        "scanning_text": "Выполняется сканирование директорий...",
        "ok": "OK",
        "update_required": "Требуется обновление",
        "choose_custom_file": "Выберите файл для подмены",
        "image_files_filter": "Изображения (*.jpg *.jpeg *.png *.webp *.avif)",
        "pillow_missing": "Библиотека Pillow не установлена.<br>Выполните в терминале: <b>pip install Pillow</b>",
        "process_error": "Не удалось обработать изображение.<br>Для поддержки формата (например, AVIF) установите: <b>pip install pillow-heif</b>"
    },
    "EN": {
        "title": "ScreenHDSteam Studio",
        "settings_title": "SYNCHRONIZATION SETTINGS",
        "settings_btn": " Settings",
        "hd_label": "Source (HD Folder with clear copies):",
        "hd_placeholder": "Select folder with HD screenshots...",
        "steam_label": "Select a game found in Steam:",
        "game_select": "Select a game...",
        "no_games": "No games with screenshots found",
        "save_settings": "SAVE SETTINGS",
        "browse": "Browse",
        "upgrade_btn": "UPGRADE TO HD AND CLEAN MEMORY",
        "refresh_btn": " REFRESH",
        "custom_btn": "REPLACE WITH CUSTOM FILE",
        "view_btn": " VIEW",
        "mode_auto": " Auto-Upgrade HD",
        "mode_custom": " Custom Replace",
        "msg_no_game": "No game selected.\n\nPlease open Settings and select a game\nfrom the dropdown menu found in Steam.",
        "msg_no_screenshots": "No synchronized captures found.\n\nThe application displays only those files from the HD folder\nwhose names match the screenshots in the selected game.",
        "select_error": "Attention",
        "select_warning": "Select captures for upgrade!",
        "success_title": "Success",
        "success_msg": "Screenshots replaced with HD, thumbnails updated: {} pcs.<br><br><span style='color: #ef4444; font-weight: bold;'>IMPORTANT!</span> Screenshots may not update inside Steam until Steam is restarted.",
        "file_error": "File Error",
        "select_single_warn": "Please select exactly one Steam screenshot for custom replacement.",
        "scanning_text": "Scanning directories in progress...",
        "ok": "OK",
        "update_required": "Update required",
        "choose_custom_file": "Select replacement file",
        "image_files_filter": "Images (*.jpg *.jpeg *.png *.webp *.avif)",
        "pillow_missing": "Pillow library is not installed.<br>Run in terminal: <b>pip install Pillow</b>",
        "process_error": "Failed to process image.<br>For additional formats (like AVIF), install: <b>pip install pillow-heif</b>"
    }
}


def __(key):
    return TRANSLATIONS.get(LANG, TRANSLATIONS["EN"]).get(key, key)


def get_steam_main_path():
    try:
        hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(hkey, "SteamPath")
        return os.path.normpath(steam_path)
    except Exception:
        for p in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam", r"S:\Steam"]:
            if os.path.exists(p):
                return os.path.normpath(p)
    return ""


def auto_detect_hd_screenshot_folder():
    steam_path = get_steam_main_path()
    if not steam_path:
        return ""
    global_config = os.path.join(steam_path, "config", "config.vdf")
    if os.path.exists(global_config):
        try:
            with open(global_config, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "ingameuncompressedscreenshotfolder" in line.lower():
                        parts = line.split('"')
                        if len(parts) >= 4:
                            detected_path = os.path.normpath(parts[-2].strip().replace(r"\\", os.sep))
                            if os.path.exists(detected_path):
                                return detected_path
        except Exception:
            pass
    return ""


def get_steam_lib_paths():
    libs = []
    steam_path = get_steam_main_path()
    if steam_path:
        libs.append(steam_path)
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf_path):
            with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if '"path"' in line.lower():
                        parts = line.split('"')
                        if len(parts) >= 4:
                            p = os.path.normpath(parts[-2].strip().replace(r"\\", os.sep))
                            if os.path.exists(p) and p not in libs:
                                libs.append(p)
    return list(set(libs))


def get_game_name_local(appid):
    libs = get_steam_lib_paths()
    for lib in libs:
        acf_path = os.path.join(lib, "steamapps", f"appmanifest_{appid}.acf")
        if os.path.exists(acf_path):
            try:
                with open(acf_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if '"name"' in line.lower():
                            parts = line.split('"')
                            if len(parts) >= 4:
                                return parts[-2].strip()
            except Exception:
                pass

    common_apps = {
        "2406770": "Bodycam",
        "1091500": "Cyberpunk 2077",
        "108600": "Project Zomboid",
        "221100": "DayZ",
        "12210": "Grand Theft Auto IV",
        "1407200": "Alan Wake Remastered",
        "1517290": "Battlefield 2042"
    }
    return common_apps.get(str(appid), f"Игра (AppID {appid})")


def scan_games_with_screenshots():
    found_games = {}
    libs = get_steam_lib_paths()
    for lib in libs:
        userdata_path = os.path.join(lib, "userdata")
        if not os.path.exists(userdata_path):
            continue
        for user_id in os.listdir(userdata_path):
            user_folder = os.path.join(userdata_path, user_id, "760", "remote")
            if not os.path.exists(user_folder):
                continue
            for app_id in os.listdir(user_folder):
                if app_id == "0":
                    continue
                screenshots_dir = os.path.join(user_folder, app_id, "screenshots")
                if os.path.exists(screenshots_dir):
                    files = (
                        glob.glob(os.path.join(screenshots_dir, "*.jpg")) + 
                        glob.glob(os.path.join(screenshots_dir, "*.jpeg"))
                    )
                    if files:
                        game_name = get_game_name_local(app_id)
                        found_games[game_name] = os.path.normpath(screenshots_dir)
    return found_games


def load_paths():
    hd_path, steam_path = "", ""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.read().splitlines()]
                if len(lines) >= 1:
                    hd_path = os.path.normpath(lines[0])
                if len(lines) >= 2:
                    steam_path = os.path.normpath(lines[1])
        except Exception:
            pass
    if not hd_path or not os.path.exists(hd_path):
        detected_hd = auto_detect_hd_screenshot_folder()
        hd_path = detected_hd if detected_hd else os.path.normpath(os.path.expanduser("~/Documents"))
    return hd_path, steam_path


def save_paths(hd_path, steam_path):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"{os.path.normpath(hd_path.strip())}\n{os.path.normpath(steam_path.strip())}")
    except Exception:
        pass


class SteamComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox { 
                background-color: #1e293b; 
                color: #f8fafc; 
                border: 1px solid #334155; 
                padding: 6px 12px; 
                border-radius: 4px; 
                min-width: 100px;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 1px solid #00f0ff;
            }
            QComboBox::drop-down { 
                subcontrol-origin: padding; 
                subcontrol-position: top right; 
                width: 30px; 
                border-left: none;
            }
            QComboBox::down-arrow { 
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #94a3b8;
                width: 0;
                height: 0;
                margin-right: 2px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #00f0ff;
            }
            QComboBox QAbstractItemView {
                background-color: #0d0f12;
                color: #f8fafc;
                border: 1px solid #1e293b;
                selection-background-color: #1e293b;
                selection-color: #00f0ff;
                outline: 0px;
                padding: 4px;
            }
            QComboBox::item { 
                min-height: 28px; 
                padding-left: 8px; 
            }
            QComboBox QAbstractItemView QScrollBar:vertical {
                background-color: #0d0f12;
                width: 10px;
                margin: 6px 0;
                border: none;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical {
                background-color: #334155;
                min-height: 20px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {
                background-color: #00f0ff;
            }
            QComboBox QAbstractItemView QScrollBar::sub-line:vertical,
            QComboBox QAbstractItemView QScrollBar::add-line:vertical,
            QComboBox QAbstractItemView QScrollBar::up-arrow:vertical, 
            QComboBox QAbstractItemView QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QComboBox QAbstractItemView QScrollBar::add-page:vertical, 
            QComboBox QAbstractItemView QScrollBar::sub-page:vertical {
                background: none;
            }
        """)


class SettingsWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(550, 240)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setStyleSheet("""
            QWidget#SettingsBase { 
                background-color: #0d0f12; 
                border: 1px solid #1e293b; 
                border-radius: 8px; 
            }
        """)
        
        png_path = resolve_resource_path(ICON_PNG_NAME)
        ico_path = resolve_resource_path(ICON_FILE_NAME)
        if os.path.exists(png_path):
            self.setWindowIcon(QIcon(png_path))
        elif os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
            
        self._is_dragging = False
        self._drag_position = QPoint()
        px = parent.x() + (parent.width() // 2) - 275
        py = parent.y() + (parent.height() // 2) - 120
        self.move(px, py)
        
        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        
        base_widget = QWidget(self)
        base_widget.setObjectName("SettingsBase")
        base_layout.addWidget(base_widget)
        
        layout = QVBoxLayout(base_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QFrame(base_widget)
        header.setFixedHeight(45)
        header.setStyleSheet("""
            QFrame { 
                background-color: #090a0d; 
                border-bottom: 1px solid #1e293b; 
                border-top-left-radius: 7px; 
                border-top-right-radius: 7px; 
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        title_lbl = QLabel(__("settings_title"), header)
        title_lbl.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 12px; border: none; background: transparent;")
        header_layout.addWidget(title_lbl)
        
        close_btn = QPushButton("✕", header)
        close_btn.setFixedSize(24, 24)
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.setStyleSheet("""
            QPushButton { color: #94a3b8; border: none; font-weight: bold; background: transparent; outline: none; } 
            QPushButton:hover { color: #ef4444; }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(header)
        self.build_settings_ui(base_widget)

    def build_settings_ui(self, container):
        content = QWidget(container)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 12, 25, 12)
        content_layout.setSpacing(6)
        
        hd_lbl = QLabel(__("hd_label"), content)
        hd_lbl.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px;")
        content_layout.addWidget(hd_lbl)
        
        hd_row = QHBoxLayout()
        hd_row.setSpacing(8)
        self.entry_hd = QLineEdit(content)
        self.entry_hd.setText(self.parent.hd_path)
        self.entry_hd.setStyleSheet("background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; padding: 5px; border-radius: 4px;")
        hd_row.addWidget(self.entry_hd)
        
        browse_btn = QPushButton(__("browse"), content)
        browse_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        browse_btn.setStyleSheet("""
            QPushButton { background-color: #1e293b; color: #00f0ff; font-weight: bold; border: 1px solid #334155; padding: 5px 15px; border-radius: 4px; outline: none; } 
            QPushButton:hover { background-color: #334155; }
        """)
        browse_btn.clicked.connect(self.browse_hd)
        hd_row.addWidget(browse_btn)
        content_layout.addLayout(hd_row)
        
        steam_lbl = QLabel(__("steam_label"), content)
        steam_lbl.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px;")
        content_layout.addWidget(steam_lbl)
        
        self.games_dict = scan_games_with_screenshots()
        games_list = list(self.games_dict.keys())
        self.option_menu = SteamComboBox(content)
        self.option_menu.addItem(__("game_select"))
        
        current_value = __("game_select")
        for g_name in games_list:
            self.option_menu.addItem(g_name)
            if self.parent.steam_path and os.path.normpath(self.games_dict[g_name]) == os.path.normpath(self.parent.steam_path):
                current_value = g_name
                
        self.option_menu.setCurrentText(current_value)
        content_layout.addWidget(self.option_menu)
        
        save_btn = QPushButton(__("save_settings"), content)
        save_btn.setFixedHeight(38)
        save_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #00f0ff; color: #07080a; font-weight: bold; border-radius: 6px; border: none; margin-top: 4px; outline: none; } 
            QPushButton:hover { background-color: #00cc99; }
        """)
        save_btn.clicked.connect(self.save_and_close)
        content_layout.addWidget(save_btn)
        container.layout().addWidget(content)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= 45:
            self._is_dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            self._is_dragging = False

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            new_position = event.globalPosition().toPoint() - self._drag_position
            screen = QApplication.screenAt(QCursor.pos())
            if screen:
                screen_geometry = screen.geometry()
                new_x = max(screen_geometry.x(), min(new_position.x(), screen_geometry.width() - self.width()))
                new_y = max(screen_geometry.y(), min(new_position.y(), screen_geometry.height() - self.height()))
                self.move(new_x, new_y)
            else:
                self.move(new_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        event.accept()

    def browse_hd(self):
        folder = QFileDialog.getExistingDirectory(self, __("hd_placeholder"))
        if folder:
            self.entry_hd.setText(os.path.normpath(folder))

    def save_and_close(self):
        hd = os.path.normpath(self.entry_hd.text())
        sel = self.option_menu.currentText()
        steam = "" if sel == __("game_select") else self.games_dict.get(sel, "")
        save_paths(hd, steam)
        self.parent.hd_path = hd
        self.parent.steam_path = steam
        self.close()
        self.parent.parent_scan_trigger()


class CustomMessageBox(QWidget):
    def __init__(self, title, text, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(460, 210)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        if parent:
            px = parent.x() + (parent.width() // 2) - 230
            py = parent.y() + (parent.height() // 2) - 105
            self.move(px, py)
            
        body = QFrame(self)
        body.setGeometry(0, 0, 460, 210)
        body.setStyleSheet("QFrame { background-color: #0d0f12; border: 1px solid #1e293b; border-radius: 12px; }")
        
        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_lbl = QLabel(title, body)
        title_lbl.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 15px; border: none; background: transparent;")
        layout.addWidget(title_lbl)
        
        text_lbl = QLabel(body)
        text_lbl.setTextFormat(Qt.TextFormat.RichText)
        text_lbl.setText(text)
        text_lbl.setStyleSheet("color: #f8fafc; font-size: 13px; border: none; background: transparent; line-height: 18px;")
        text_lbl.setWordWrap(True)
        layout.addWidget(text_lbl, 1)
        
        ok_btn = QPushButton(__("ok"), body)
        ok_btn.setFixedSize(100, 36)
        ok_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        ok_btn.setStyleSheet("""
            QPushButton { background-color: #00f0ff; color: #07080a; font-weight: bold; border-radius: 5px; border: none; outline: none; } 
            QPushButton:hover { background-color: #00cc99; }
        """)
        ok_btn.clicked.connect(self.close)
        layout.addWidget(ok_btn, 0, Qt.AlignmentFlag.AlignRight)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.fillPath(path, Qt.GlobalColor.transparent)


class CircularSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def update_animation(self):
        self.angle = (self.angle + 4) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#1e293b"), 4)
        painter.setPen(pen)
        painter.drawEllipse(5, 5, 40, 40)
        pen.setColor(QColor("#00f0ff"))
        painter.setPen(pen)
        painter.drawArc(5, 5, 40, 40, -self.angle * 16, 100 * 16)


class GitHubUpdateWorker(QThread):
    update_available_signal = pyqtSignal(str)

    def run(self):
        try:
            raw_url = "https://raw.githubusercontent.com/STERIAGAME/ScreenHDSteam/refs/heads/main/version.txt"
            req = urllib.request.Request(raw_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            req.add_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            req.add_header('Pragma', 'no-cache')
            req.add_header('Expires', '0')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    raw_data = response.read().decode('utf-8-sig')
                    server_version_text = " ".join(raw_data.replace('\r', '').replace('\n', '').replace('\xa0', '').strip().lower().split())
                    local_version_text = " ".join(VERSION.replace('\r', '').replace('\n', '').replace('\xa0', '').strip().lower().split())
                    
                    if server_version_text and server_version_text != local_version_text:
                        self.update_available_signal.emit(GITHUB_RELEASE_URL)
        except Exception:
            pass


class AsyncScanWorker(QThread):
    finished_signal = pyqtSignal(list, dict)

    def __init__(self, hd_path, steam_path, mode):
        super().__init__()
        self.hd_path = hd_path
        self.steam_path = steam_path
        self.mode = mode
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        matched = []
        thumbnails = {}
        if not self.steam_path or not os.path.exists(self.steam_path):
            if not self._is_cancelled:
                self.finished_signal.emit(matched, thumbnails)
            return

        steam_files = {}
        for ext in ["*.jpg", "*.jpeg"]:
            for p in glob.glob(os.path.join(self.steam_path, ext)):
                if self._is_cancelled:
                    return
                if "thumbnails" not in os.path.normpath(p).split(os.sep):
                    steam_files[os.path.basename(p)] = p

        hd_files = []
        if self.hd_path and os.path.exists(self.hd_path):
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.avif"]:
                if self._is_cancelled:
                    return
                hd_files.extend(glob.glob(os.path.join(self.hd_path, ext)))
                hd_files.extend(glob.glob(os.path.join(self.hd_path, "**", ext), recursive=True))

        added = set()
        for h_path in hd_files:
            if self._is_cancelled:
                return
            h_filename = os.path.basename(h_path)
            h_name, _ = os.path.splitext(h_filename)
            
            clean_h_name = h_name
            if "_" in h_name:
                parts = h_name.split("_")
                if len(parts) > 1 and parts[0].isdigit():
                    clean_h_name = "_".join(parts[1:])
            
            for s_name, s_path in steam_files.items():
                s_base, _ = os.path.splitext(s_name)
                # Точное сопоставление имени или суффикса (без непредсказуемого 's_base in h_name')
                if s_base == h_name or s_base == clean_h_name or h_name.endswith(f"_{s_base}"):
                    if s_name not in added:
                        matched.append((s_name, h_path, s_path))
                        added.add(s_name)
                    break

        if self.mode == "custom":
            for s_name, s_path in steam_files.items():
                if s_name not in added:
                    matched.append((s_name, "", s_path))

        try:
            matched.sort(key=lambda x: os.path.getmtime(x[2]) if (x and len(x) > 2 and os.path.exists(x[2])) else 0, reverse=True)
        except Exception:
            pass

        # Безопасная загрузка через QImage в фоновом потоке
        for s_name, h_path, s_path in matched:
            if self._is_cancelled:
                return
            p_path = h_path if (self.mode == "auto" and h_path) else s_path
            if p_path and os.path.exists(p_path):
                img = QImage(p_path)
                if not img.isNull():
                    scaled = img.scaled(200, 115, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    thumbnails[s_name] = scaled

        if not self._is_cancelled:
            self.finished_signal.emit(matched, thumbnails)


class ScreenshotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.CustomizeWindowHint)
        self.setMinimumSize(850, 600)
        self.resize(990, 800)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.hd_path, self.steam_path = load_paths()
        self.matched_screenshots = []
        self.thumbnail_pixmaps = {}
        self.selected_items = set()
        self.card_widgets = {}
        self.current_mode = "auto"
        self._drag_position = QPoint()
        self._is_dragging = False
        self.scan_in_progress = False
        self.worker = None

        png_path = resolve_resource_path(ICON_PNG_NAME)
        ico_path = resolve_resource_path(ICON_FILE_NAME)
        if os.path.exists(png_path):
            self.setWindowIcon(QIcon(png_path))
        elif os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        central_widget = QWidget(self)
        central_widget.setStyleSheet("""
            QWidget#CentralBase { 
                background-color: #07080a; 
                border-radius: 12px; 
                border: 1px solid #1e293b;
            }
        """)
        central_widget.setObjectName("CentralBase")
        self.setCentralWidget(central_widget)
        
        container_layout = QVBoxLayout(central_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        header = QFrame(central_widget)
        header.setStyleSheet("""
            QFrame { 
                background-color: #0d0f12; 
                border-bottom: 1px solid #1e293b; 
                border-top-left-radius: 11px; 
                border-top-right-radius: 11px; 
            }
        """)
        header.setFixedHeight(65)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(10)
        
        self.icon_lbl = QLabel(header)
        self.icon_lbl.setFixedSize(45, 45)
        self.icon_lbl.setStyleSheet("border: none; background: transparent;")
        
        pixmap_loaded = False
        resolved_png = resolve_resource_path(ICON_PNG_NAME)
        resolved_ico = resolve_resource_path(ICON_FILE_NAME)
        if os.path.exists(resolved_png):
            px = QPixmap(resolved_png)
            if not px.isNull():
                self.icon_lbl.setPixmap(px.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                pixmap_loaded = True
        if not pixmap_loaded and os.path.exists(resolved_ico):
            ico = QIcon(resolved_ico)
            px = ico.pixmap(QSize(48, 48))
            if not px.isNull():
                self.icon_lbl.setPixmap(px.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        header_layout.addWidget(self.icon_lbl)
        title_lbl = QLabel("ScreenHDSteam Studio", header)
        title_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent; border: none; margin-left: 5px;")
        header_layout.addWidget(title_lbl)
        
        version_layout = QVBoxLayout()
        version_layout.setSpacing(0)
        version_layout.setContentsMargins(6, 0, 0, 0)

        self.version_lbl = QLabel(VERSION, header)
        self.version_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        version_layout.addWidget(self.version_lbl)

        self.update_status_lbl = QLabel(__("update_required"), header)
        self.update_status_lbl.setStyleSheet("color: #ffee00; font-size: 8px; font-weight: bold; background: transparent; border: none; margin-top: -1px;")
        self.update_status_lbl.setVisible(False)
        version_layout.addWidget(self.update_status_lbl)

        header_layout.addLayout(version_layout, 0)
        header_layout.setAlignment(version_layout, Qt.AlignmentFlag.AlignVCenter)
        
        self.update_git_btn = QPushButton(header)
        self.update_git_btn.setFixedSize(20, 20)
        self.update_git_btn.setVisible(False)
        self.update_git_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.update_git_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        resolved_git_ico = resolve_resource_path(ICON_UPDATE_GIT)
        if os.path.exists(resolved_git_ico):
            self.update_git_btn.setIcon(QIcon(resolved_git_ico))
            self.update_git_btn.setIconSize(QSize(18, 18))
        self.update_git_btn.setStyleSheet("QPushButton { border: none; background: transparent; margin-top: 4px; outline: none; }")
        header_layout.addWidget(self.update_git_btn)
        
        header_layout.addStretch()
        self.btn_auto_mode = QPushButton(__("mode_auto"), header)
        self.btn_auto_mode.setCheckable(True)
        self.btn_auto_mode.setChecked(True)
        self.btn_auto_mode.setFixedSize(160, 34)
        self.btn_auto_mode.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        resolved_auto_ico = resolve_resource_path(ICON_MODE_AUTO)
        if os.path.exists(resolved_auto_ico):
            self.btn_auto_mode.setIcon(QIcon(resolved_auto_ico))
            self.btn_auto_mode.setIconSize(QSize(16, 16))
        self.btn_auto_mode.setStyleSheet("""
            QPushButton { color: #94a3b8; font-weight: bold; font-size: 12px; border: 1px solid #1e293b; background-color: #0d0f12; border-radius: 6px; padding-left: 5px; outline: none; } 
            QPushButton:checked { color: #00f0ff; background-color: #1e293b; border: 1px solid #00f0ff; }
        """)
        self.btn_auto_mode.clicked.connect(lambda: self.change_mode("auto"))
        header_layout.addWidget(self.btn_auto_mode)

        self.btn_custom_mode = QPushButton(__("mode_custom"), header)
        self.btn_custom_mode.setCheckable(True)
        self.btn_custom_mode.setFixedSize(160, 34)
        self.btn_custom_mode.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        resolved_custom_ico = resolve_resource_path(ICON_MODE_CUSTOM)
        if os.path.exists(resolved_custom_ico):
            self.btn_custom_mode.setIcon(QIcon(resolved_custom_ico))
            self.btn_custom_mode.setIconSize(QSize(16, 16))
        self.btn_custom_mode.setStyleSheet("""
            QPushButton { color: #94a3b8; font-weight: bold; font-size: 12px; border: 1px solid #1e293b; background-color: #0d0f12; border-radius: 6px; padding-left: 5px; outline: none; } 
            QPushButton:checked { color: #ffee00; background-color: #1e293b; border: 1px solid #ffee00; }
        """)
        self.btn_custom_mode.clicked.connect(lambda: self.change_mode("custom"))
        header_layout.addWidget(self.btn_custom_mode)

        settings_btn = QPushButton(__("settings_btn"), header)
        settings_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        resolved_set_ico = resolve_resource_path(ICON_SETTINGS)
        if os.path.exists(resolved_set_ico):
            settings_btn.setIcon(QIcon(resolved_set_ico))
            settings_btn.setIconSize(QSize(14, 14))
        settings_btn.setStyleSheet("""
            QPushButton { background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 6px 15px; border-radius: 4px; border: 1px solid #334155; outline: none; } 
            QPushButton:hover { background-color: #334155; color: white; }
        """)
        settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(settings_btn)

        min_btn = QPushButton("⎯", header)
        min_btn.setFixedSize(28, 28)
        min_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        min_btn.setStyleSheet("""
            QPushButton { color: #94a3b8; font-weight: bold; border: none; background: transparent; outline: none; } 
            QPushButton:hover { background-color: #1e293b; border-radius: 4px; }
        """)
        min_btn.clicked.connect(self.showMinimized)
        header_layout.addWidget(min_btn)

        close_btn = QPushButton("✕", header)
        close_btn.setFixedSize(28, 28)
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.setStyleSheet("""
            QPushButton { color: #94a3b8; font-weight: bold; border: none; background: transparent; outline: none; } 
            QPushButton:hover { background-color: #ef4444; color: white; border-radius: 4px; }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        container_layout.addWidget(header)

        self.scroll_area = QScrollArea(central_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background-color: #07080a; }
            QScrollBar:vertical { border: none; background-color: #07080a; width: 10px; margin: 0px; }
            QScrollBar::handle:vertical { background-color: #1e293b; min-height: 30px; border-radius: 5px; }
            QScrollBar::handle:vertical:hover { background-color: #334155; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        
        self.gallery_widget = QWidget()
        self.gallery_widget.setStyleSheet("background-color: #07080a; border: none;")
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setSpacing(15)
        self.gallery_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_area.setWidget(self.gallery_widget)
        container_layout.addWidget(self.scroll_area)
        
        footer = QFrame(central_widget)
        footer.setFixedHeight(70)
        footer.setStyleSheet("""
            QFrame { 
                background-color: #07080a; 
                border-bottom-left-radius: 11px; 
                border-bottom-right-radius: 11px; 
            }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(25, 0, 25, 0)

        self.action_btn = QPushButton(__("upgrade_btn"), footer)
        self.action_btn.setFixedHeight(45)
        self.action_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.action_btn.setStyleSheet("""
            QPushButton { background-color: #00f0ff; color: #07080a; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; outline: none; } 
            QPushButton:hover { background-color: #00cc99; }
        """)
        self.action_btn.clicked.connect(self.execute_main_action)
        footer_layout.addWidget(self.action_btn, 1)

        self.refresh_btn = QPushButton(__("refresh_btn"), footer)
        self.refresh_btn.setFixedSize(130, 45)
        self.refresh_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        resolved_ref_ico = resolve_resource_path(ICON_REFRESH)
        if os.path.exists(resolved_ref_ico):
            self.refresh_btn.setIcon(QIcon(resolved_ref_ico))
            self.refresh_btn.setIconSize(QSize(14, 14))
        self.refresh_btn.setStyleSheet("""
            QPushButton { background-color: #ffee00; color: #07080a; font-weight: bold; border-radius: 6px; border: none; padding-left: 2px; outline: none; } 
            QPushButton:hover { background-color: #cccc00; }
        """)
        self.refresh_btn.clicked.connect(self.scan_screenshots)
        footer_layout.addWidget(self.refresh_btn)
        container_layout.addWidget(footer)
        
        self.check_github_updates()
        self.scan_screenshots()

    def check_github_updates(self):
        self.update_worker = GitHubUpdateWorker()
        self.update_worker.update_available_signal.connect(self.on_update_found)
        self.update_worker.start()

    def on_update_found(self, release_url):
        self.version_lbl.setStyleSheet("color: #ffee00; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        self.version_lbl.style().unpolish(self.version_lbl)
        self.version_lbl.style().polish(self.version_lbl)
        self.version_lbl.update()
        
        self.update_status_lbl.setVisible(True)
        self.update_git_btn.setVisible(True)
        self.update_git_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(release_url)))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.fillPath(path, Qt.GlobalColor.transparent)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 65:
            self._is_dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            self._is_dragging = False

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            new_position = event.globalPosition().toPoint() - self._drag_position
            screen = QApplication.screenAt(QCursor.pos())
            if screen:
                screen_geo = screen.geometry()
                new_x = max(screen_geo.x(), min(new_position.x(), screen_geo.right() - 100))
                new_y = max(screen_geo.y(), min(new_position.y(), screen_geo.bottom() - 100))
                self.move(new_x, new_y)
            else:
                self.move(new_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        event.accept()

    def parent_scan_trigger(self):
        self.scan_screenshots()

    def change_mode(self, mode):
        self.current_mode = mode
        self.selected_items.clear()
        if mode == "auto":
            self.btn_auto_mode.setChecked(True)
            self.btn_custom_mode.setChecked(False)
            self.action_btn.setText(__("upgrade_btn"))
            self.action_btn.setStyleSheet("""
                QPushButton { background-color: #00f0ff; color: #07080a; font-weight: bold; border-radius: 6px; border: none; outline: none; } 
                QPushButton:hover { background-color: #00cc99; }
            """)
        else:
            self.btn_auto_mode.setChecked(False)
            self.btn_custom_mode.setChecked(True)
            self.action_btn.setText(__("custom_btn"))
            self.action_btn.setStyleSheet("""
                QPushButton { background-color: #ffee00; color: #07080a; font-weight: bold; border-radius: 6px; border: none; outline: none; } 
                QPushButton:hover { background-color: #cccc00; }
            """)
        self.scan_screenshots()

    def open_settings(self):
        self.settings_win = SettingsWindow(self)
        self.settings_win.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.matched_screenshots and not self.scan_in_progress:
            new_columns = max(1, (self.width() - 40) // 235)
            if getattr(self, '_current_columns', 0) != new_columns:
                self.render_gallery()

    def scan_screenshots(self):
        # Безопасная неблокирующая отмена предыдущего потока
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            try:
                self.worker.finished_signal.disconnect()
            except Exception:
                pass

        self.scan_in_progress = True
        self.selected_items.clear()
        self.card_widgets.clear()
        
        for i in reversed(range(self.gallery_layout.count())): 
            item = self.gallery_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                self.gallery_layout.removeItem(item)
            
        loading_frame = QWidget()
        loading_frame.setStyleSheet("border: none; background-color: #07080a;")
        loading_layout = QVBoxLayout(loading_frame)
        loading_layout.setSpacing(15)
        
        spinner = CircularSpinner(loading_frame)
        loading_layout.addWidget(spinner, 0, Qt.AlignmentFlag.AlignCenter)
        
        status_lbl = QLabel(__("scanning_text"), loading_frame)
        status_lbl.setStyleSheet("color: #00f0ff; font-size: 13px; font-weight: bold; background-color: #07080a;")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(status_lbl)
        
        columns = max(1, (self.width() - 40) // 235)
        self.gallery_layout.addWidget(loading_frame, 0, 0, 1, columns, Qt.AlignmentFlag.AlignCenter)

        self.worker = AsyncScanWorker(self.hd_path, self.steam_path, self.current_mode)
        self.worker.finished_signal.connect(self.on_scan_finished)
        self.worker.start()

    def on_scan_finished(self, matched, thumbnail_images):
        self.scan_in_progress = False
        self.matched_screenshots = matched
        # Безопасная конвертация QImage в QPixmap на стороне основного потока GUI
        self.thumbnail_pixmaps = {fn: QPixmap.fromImage(img) for fn, img in thumbnail_images.items()}
        self.render_gallery()

    def render_gallery(self):
        self.card_widgets.clear()
        for i in reversed(range(self.gallery_layout.count())):
            item = self.gallery_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                self.gallery_layout.removeItem(item)

        if not self.matched_screenshots:
            msg = __("msg_no_game") if not self.steam_path else __("msg_no_screenshots")
            empty_lbl = QLabel(msg)
            empty_lbl.setStyleSheet("color: #64748b; font-size: 13px; border: none; background: transparent;")
            self.gallery_layout.addWidget(empty_lbl, 0, 0, Qt.AlignmentFlag.AlignCenter)
            return

        columns = max(1, (self.width() - 40) // 235)
        self._current_columns = columns
        total_rows = (len(self.matched_screenshots) + columns - 1) // columns

        for index, (filename, hd_path, steam_path) in enumerate(self.matched_screenshots):
            row = index // columns
            col = index % columns

            item_frame = QFrame()
            item_frame.setFixedSize(220, 175)
            self.card_widgets[filename] = item_frame
            self.apply_card_style(filename)
            
            frame_layout = QVBoxLayout(item_frame)
            frame_layout.setContentsMargins(8, 8, 8, 8)
            frame_layout.setSpacing(6)

            img_btn = QPushButton(item_frame)
            img_btn.setFixedSize(202, 115)
            img_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            img_btn.setStyleSheet("border: none; background: transparent; border-radius: 4px; outline: none;")
            if filename in self.thumbnail_pixmaps:
                img_btn.setIcon(QIcon(self.thumbnail_pixmaps[filename]))
                img_btn.setIconSize(QSize(200, 115))
            else:
                img_btn.setText(__("file_error"))
            img_btn.clicked.connect(lambda checked, fn=filename: self.toggle_select(fn))
            frame_layout.addWidget(img_btn)

            view_btn = QPushButton(__("view_btn"), item_frame)
            view_btn.setFixedHeight(24)
            view_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            resolved_vi_ico = resolve_resource_path(ICON_VIEW)
            if os.path.exists(resolved_vi_ico):
                view_btn.setIcon(QIcon(resolved_vi_ico))
                view_btn.setIconSize(QSize(12, 12))
            view_btn.setStyleSheet("""
                QPushButton { background-color: #1e293b; color: #00f0ff; font-weight: bold; font-size: 10px; border-radius: 4px; border: none; padding-left: 2px; outline: none; } 
                QPushButton:hover { background-color: #334155; }
            """)
            p_path = hd_path if (self.current_mode == "auto" and hd_path) else steam_path
            view_btn.clicked.connect(lambda checked, p=p_path: os.startfile(p) if (p and os.path.exists(p)) else None)
            frame_layout.addWidget(view_btn)

            self.gallery_layout.addWidget(item_frame, row, col, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.gallery_layout.addItem(spacer, total_rows, 0, 1, columns)

    def apply_card_style(self, filename):
        card = self.card_widgets.get(filename)
        if card:
            is_selected = filename in self.selected_items
            border_color = "#ffee00" if is_selected else "#1e293b"
            bg_color = "#1a1c13" if is_selected else "#0d0f12"
            card.setStyleSheet(f"QFrame {{ border: 1px solid {border_color}; background-color: {bg_color}; border-radius: 8px; }}")

    def toggle_select(self, filename):
        if self.current_mode == "custom":
            prev_items = list(self.selected_items)
            self.selected_items.clear()
            self.selected_items.add(filename)
            for prev_fn in prev_items:
                self.apply_card_style(prev_fn)
            self.apply_card_style(filename)
        else:
            if filename in self.selected_items:
                self.selected_items.remove(filename)
            else:
                self.selected_items.add(filename)
            self.apply_card_style(filename)

    def execute_main_action(self):
        if not self.selected_items: 
            msg_box = CustomMessageBox(__("select_error"), __("select_warning"), self)
            msg_box.show()
            return

        if self.current_mode == "auto":
            success = 0
            for filename, hd_path, steam_path in self.matched_screenshots:
                if filename in self.selected_items and hd_path:
                    if self.process_replacement(hd_path, steam_path, filename):
                        success += 1
                        try:
                            os.remove(hd_path)
                        except Exception:
                            pass
            if success:
                msg_box = CustomMessageBox(__("success_title"), __("success_msg").format(success), self)
                msg_box.show()
                self.scan_screenshots()
        else:
            if len(self.selected_items) != 1:
                msg_box = CustomMessageBox(__("select_error"), __("select_single_warn"), self)
                msg_box.show()
                return

            target_fn = next(iter(self.selected_items))
            steam_p = next((s for f, h, s in self.matched_screenshots if f == target_fn), "")
            if not steam_p:
                return

            custom_file, _ = QFileDialog.getOpenFileName(
                self, 
                __("choose_custom_file"), 
                "", 
                __("image_files_filter")
            )
            if custom_file and self.process_replacement(custom_file, steam_p, target_fn):
                msg_box = CustomMessageBox(__("success_title"), __("success_msg").format(1), self)
                msg_box.show()
                self.scan_screenshots()

    def process_replacement(self, src, dest, filename):
        if not PIL_AVAILABLE:
            msg_box = CustomMessageBox(__("file_error"), __("pillow_missing"), self)
            msg_box.show()
            return False

        try:
            img = Image.open(src)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            dest_dir = os.path.dirname(dest)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Атомарное сохранение основного файла через .tmp
            temp_dest = dest + ".tmp"
            img.save(temp_dest, "JPEG", quality=100, subsampling=0)
            if os.path.exists(temp_dest):
                if os.path.exists(dest):
                    try:
                        os.remove(dest)
                    except Exception:
                        pass
                os.replace(temp_dest, dest)

            # Атомарное сохранение миниатюры
            t_dir = os.path.join(dest_dir, "thumbnails")
            os.makedirs(t_dir, exist_ok=True)
            t_path = os.path.join(t_dir, filename)
            temp_t_path = t_path + ".tmp"

            t_img = img.copy()
            t_img.thumbnail((400, 250))
            t_img.save(temp_t_path, "JPEG", quality=90)
            if os.path.exists(temp_t_path):
                if os.path.exists(t_path):
                    try:
                        os.remove(t_path)
                    except Exception:
                        pass
                os.replace(temp_t_path, t_path)

            return True
        except Exception as e:
            msg_box = CustomMessageBox(__("file_error"), f"{__('process_error')}<br><br><small>{str(e)}</small>", self)
            msg_box.show()
            return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec())
