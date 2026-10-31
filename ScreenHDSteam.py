import os
import glob
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import winreg
import json

CONFIG_FILE = "config.txt"

def get_steam_main_path():
    """Находит основную директорию установки Steam через реестр Windows"""
    try:
        hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path = winreg.QueryValueEx(hkey, "SteamPath")
        return os.path.normpath(steam_path)
    except Exception:
        for p in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam", r"S:\Steam"]:
            if os.path.exists(p):
                return os.path.normpath(p)
    return ""

def auto_detect_hd_screenshot_folder():
    """Автоматически считывает путь к несжатым HD-скриншотам из всех возможных конфигов Steam"""
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
                            detected_path = os.path.normpath(parts[-2].strip())
                            if os.path.exists(detected_path):
                                return detected_path
        except Exception:
            pass

    userdata_path = os.path.join(steam_path, "userdata")
    if os.path.exists(userdata_path):
        for user_id in os.listdir(userdata_path):
            vdf_path = os.path.join(userdata_path, user_id, "config", "localconfig.vdf")
            if os.path.exists(vdf_path):
                try:
                    with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if "ingameuncompressedscreenshotfolder" in line.lower():
                                parts = line.split('"')
                                if len(parts) >= 4:
                                    detected_path = os.path.normpath(parts[-2].strip())
                                    if os.path.exists(detected_path):
                                        return detected_path
                except Exception:
                    pass
    return ""

def get_steam_lib_paths():
    """Находит все подключенные библиотеки Steam на ПК"""
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
                            p = os.path.normpath(parts[-2].strip())
                            if os.path.exists(p) and p not in libs:
                                libs.append(p)
    return list(set(libs))

def get_game_name_local(appid):
    """Ищет манифест установленной игры локально и выдергивает ее имя"""
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
    if str(appid) in common_apps:
        return common_apps[str(appid)]
        
    return f"Игра (AppID {appid})"

def scan_games_with_screenshots():
    """Сканирует библиотеки и выводит список всех доступных игр со скриншотами"""
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
                    files = glob.glob(os.path.join(screenshots_dir, "*.jpg")) + glob.glob(os.path.join(screenshots_dir, "*.jpeg"))
                    if files:
                        game_name = get_game_name_local(app_id)
                        found_games[game_name] = os.path.normpath(screenshots_dir)
    return found_games

def load_paths():
    """Загрузка путей из конфига с умной проверкой существования папки HD"""
    hd_path, steam_path = "", ""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if len(lines) >= 1:
                    hd_path = os.path.normpath(lines[0])
                if len(lines) >= 2:
                    steam_path = os.path.normpath(lines[1])
        except Exception:
            pass
            
    if not hd_path or hd_path == "." or not os.path.exists(hd_path) or "remote" in hd_path:
        detected_hd = auto_detect_hd_screenshot_folder()
        if detected_hd:
            hd_path = detected_hd
        else:
            hd_path = os.path.normpath(os.path.expanduser("~/Documents"))
        
    return hd_path, steam_path

def save_paths(hd_path, steam_path):
    """Сохранение путей в конфигурационный файл"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"{os.path.normpath(hd_path)}\n{os.path.normpath(steam_path)}")
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось записать конфиг: {e}")

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # ИСПРАВЛЕНО: Убран эмодзи, оставлен чистый текст для заголовка окна
        self.title("Конфигурация среды")
        self.geometry("600x320")
        self.resizable(False, False)
        
        # Надежный расчет абсолютного пути к .ico файлу
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ico_path = os.path.join(current_dir, "iconShdS.ico")
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
        except Exception as e:
            print(f"Ошибка загрузки иконки окна настроек: {e}")
        
        self.after(100, self.lift)
        self.focus_set()
        self.configure(fg_color="#0d0f12")
        
        # --- ВЕРХНИЙ РЯД С ИКОНКОЙ И НАЗВАНИЕМ НАСТРОЕК ---
        frame_title = ctk.CTkFrame(self, fg_color="transparent")
        frame_title.pack(pady=20)
        
        # ИСПРАВЛЕНО: Добавляем PNG-иконку перед заголовком настроек
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            png_icon_path = os.path.join(current_dir, "iconShdS.png")
            raw_icon = Image.open(png_icon_path)
            # Размер 22x22 идеально сочетается с высотой шрифта заголовка настроек
            settings_icon = ctk.CTkImage(light_image=raw_icon, dark_image=raw_icon, size=(22, 22))
            
            lbl_title_icon = ctk.CTkLabel(frame_title, image=settings_icon, text="")
            lbl_title_icon.pack(side="left", padx=(0, 8))
            
            lbl_title = ctk.CTkLabel(frame_title, text="НАСТРОЙКИ СИНХРОНИЗАЦИИ", font=("Segoe UI", 15, "bold"), text_color="#00f0ff")
            lbl_title.pack(side="left")
        except Exception:
            # Резервный текстовый вариант, если картинка не загрузилась
            lbl_title = ctk.CTkLabel(frame_title, text="НАСТРОЙКИ СИНХРОНИЗАЦИИ", font=("Segoe UI", 15, "bold"), text_color="#00f0ff")
            lbl_title.pack(side="left")
        
        # --- ПАПКА HD ---
        frame_hd = ctk.CTkFrame(self, fg_color="transparent")
        frame_hd.pack(fill="x", padx=30, pady=8)
        lbl_hd = ctk.CTkLabel(frame_hd, text="Источник (Папка HD с четкими копиями):", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        lbl_hd.pack(anchor="w")
        self.entry_hd = ctk.CTkEntry(frame_hd, fg_color="#1e293b", border_color="#334155", text_color="#f8fafc", placeholder_text="Выберите папку с HD-скриншотами...")
        self.entry_hd.insert(0, parent.hd_path)
        self.entry_hd.pack(side="left", fill="x", expand=True, pady=5, padx=(0, 10), ipady=2)
        btn_hd = ctk.CTkButton(frame_hd, text="Обзор", fg_color="#00f0ff", hover_color="#00b8cc", text_color="#0f172a", font=("Segoe UI", 11, "bold"), width=70, command=self.browse_hd)
        btn_hd.pack(side="right", pady=5)
        
        # --- АВТОМАТИЧЕСКИЙ ВЫБОР ИГРЫ STEAM ---
        frame_steam = ctk.CTkFrame(self, fg_color="transparent")
        frame_steam.pack(fill="x", padx=30, pady=8)
        lbl_steam = ctk.CTkLabel(frame_steam, text="Выберите игру из найденных в Steam:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        lbl_steam.pack(anchor="w", pady=(0, 5))
        
        # Сканируем ПК
        self.games_dict = scan_games_with_screenshots()
        games_list = list(self.games_dict.keys())
        
        # Если игр нет или конфиг чистый, даем выбрать
        if not games_list:
            games_list = ["Игры со скриншотами не найдены"]
            current_value = games_list[0]
        else:
            current_value = "Выберите игру..."
            for name, path in self.games_dict.items():
                if parent.steam_path and os.path.normpath(path) == os.path.normpath(parent.steam_path):
                    current_value = name
                    break
            if current_value == "Выберите игру..." and games_list:
                current_value = "Выберите игру..."
        
        # Добавляем дефолтный пункт в начало списка, если игры найдены
        if games_list and games_list[0] != "Игры со скриншотами не найдены" and "Выберите игру..." not in games_list:
            games_list.insert(0, "Выберите игру...")

        self.option_menu = ctk.CTkOptionMenu(
            frame_steam, 
            values=games_list,
            fg_color="#1e293b",
            button_color="#00f0ff",
            button_hover_color="#00b8cc",
            text_color="#f8fafc",
            dropdown_fg_color="#1e293b",
            dropdown_text_color="#f8fafc",
            dropdown_hover_color="#334155",
            font=("Segoe UI Semibold", 11),
            height=35
        )
        self.option_menu.set(current_value)
        self.option_menu.pack(fill="x", pady=2)
        
        btn_close = ctk.CTkButton(self, text="СОХРАНИТЬ НАСТРОЙКИ", fg_color="#00f0ff", hover_color="#00b8cc", text_color="#07080a", font=("Segoe UI", 12, "bold"), height=40, corner_radius=8, command=self.save_and_close)
        btn_close.pack(pady=25)


    def browse_hd(self):
        self.grab_release()
        folder = filedialog.askdirectory(title="Выберите папку с HD-скриншотами")
        if folder:
            self.entry_hd.delete(0, tk.END)
            self.entry_hd.insert(0, os.path.normpath(folder))
        self.grab_set()
        self.focus_set()

    def save_and_close(self):
        hd = os.path.normpath(self.entry_hd.get()) if self.entry_hd.get() else ""
        selected_game = self.option_menu.get()
        
        if selected_game in ["Выберите игру...", "Игры со скриншотами не найдены"]:
            steam = ""
        else:
            steam = self.games_dict.get(selected_game, "")

        save_paths(hd, steam)
        self.parent.hd_path = hd
        self.parent.steam_path = steam
        self.destroy()
        self.parent.scan_screenshots()

class ScreenshotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.configure(fg_color="#07080a") 
        # ИСПРАВЛЕНО: Убран эмодзи, оставлен чистый текст для системного заголовка
        self.title("ScreenHDSteam Studio")
        self.geometry("1000x720")
        self.minsize(800, 580)

        # Пуленепробиваемый расчет абсолютного пути к .ico файлу
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ico_path = os.path.join(current_dir, "iconShdS.ico")
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
        except Exception as e:
            print(f"Ошибка загрузки иконки главного окна: {e}")

        self.hd_path, self.steam_path = load_paths()
        self.matched_screenshots = []
        self.selected_items = set()
        self.thumbnail_images = {}

        self.bind("<Configure>", self.on_window_resize)
        self.current_width = 1000

        # --- ВЕРХНЯЯ НАВИГАЦИОННАЯ ПАНЕЛЬ ---
        self.header_frame = ctk.CTkFrame(self, fg_color="#0d0f12", height=65, corner_radius=0, border_width=1, border_color="#1e293b")
        self.header_frame.pack(fill="x", side="top")
        
        # ИСПРАВЛЕНО: Загружаем оригинальный PNG и добавляем виджетом строго ПЕРЕД названием
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            png_icon_path = os.path.join(current_dir, "iconShdS.png")
            raw_icon = Image.open(png_icon_path)
            # Высота 28 пикселей идеально подходит под шрифт размером 22
            header_icon = ctk.CTkImage(light_image=raw_icon, dark_image=raw_icon, size=(28, 28))
            
            # Виджет картинки иконки
            self.lbl_header_icon = ctk.CTkLabel(self.header_frame, image=header_icon, text="")
            self.lbl_header_icon.pack(side="left", padx=(30, 8), pady=15)
            
            # Текст идет следом за иконкой (padx слева равен 0, так как отступ сделан у иконки)
            self.lbl_title = ctk.CTkLabel(self.header_frame, text="ScreenHDSteam", font=("Segoe UI", 22, "bold"), text_color="#ffffff")
            self.lbl_title.pack(side="left", padx=(0, 20), pady=15)
        except Exception as e:
            # Резервный вариант, если PNG-файл удален или переименован (чтобы программа не падала)
            self.lbl_title = ctk.CTkLabel(self.header_frame, text="ScreenHDSteam", font=("Segoe UI", 22, "bold"), text_color="#ffffff")
            self.lbl_title.pack(side="left", padx=30, pady=15)
            print(f"Не удалось отрисовать иконку в шапке: {e}")
        
        self.badge = ctk.CTkLabel(self.header_frame, text="v3.0 AUTO", font=("Segoe UI Semibold", 10), 
                                   text_color="#00f0ff", fg_color=("#1e293b", "#142129"), 
                                   width=70, height=20, corner_radius=10)
        self.badge.pack(side="left", padx=(0, 20), pady=22)

        self.btn_settings = ctk.CTkButton(self.header_frame, text="⚙ Настройки", width=110, height=34, corner_radius=6,
                                           fg_color="#1e293b", hover_color="#334155", text_color="#94a3b8",
                                           font=("Segoe UI Semibold", 12), command=self.open_settings)
        self.btn_settings.pack(side="right", padx=30, pady=15)

        # --- ОСНОВНАЯ ЗОНА ГАЛЕРЕИ ---
        # Создаем стандартный скролл-фрейм
        self.scroll_gallery = ctk.CTkScrollableFrame(self, fg_color="#090a0d", corner_radius=0, border_width=0)
        self.scroll_gallery.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Контейнером является сам скролл-фрейм (ОСТАВЛЯЕМ ТОЛЬКО ЭТУ СТРОКУ)
        self.grid_container = self.scroll_gallery


        # --- НИЖНЯЯ ПАНЕЛЬ ДЕЙСТВИЙ ---
        self.frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bottom.pack(fill="x", padx=30, pady=(0, 30))

        self.btn_replace = ctk.CTkButton(self.frame_bottom, text="АПГРЕЙД В HD И ОЧИСТКА ПАМЯТИ", 
                                         fg_color="#00f0ff", hover_color="#00cc99", text_color="#07080a",
                                         font=("Segoe UI", 13, "bold"), height=48, corner_radius=8,
                                         command=self.replace_selected)
        self.btn_replace.pack(side="left", fill="x", expand=True, padx=(0, 15))

        self.btn_refresh = ctk.CTkButton(self.frame_bottom, text="🔄 ОБНОВИТЬ", width=140, height=48, corner_radius=8,
                                         fg_color="#ffee00", hover_color="#cccc00", text_color="#07080a", 
                                         font=("Segoe UI", 12, "bold"), command=self.scan_screenshots)
        self.btn_refresh.pack(side="right")

        if self.hd_path and self.steam_path:
            self.after(300, self.scan_screenshots)


    def open_settings(self):
        SettingsWindow(self)

    def on_window_resize(self, event):
        if event.widget == self and abs(self.current_width - event.width) > 40:
            self.current_width = event.width
            self.render_gallery()
    def scan_screenshots(self):
        if not self.hd_path or not self.steam_path or not os.path.exists(self.hd_path) or not os.path.exists(self.steam_path):
            return

        # 1. Читаем скриншоты Steam (кэш thumbnails игнорируется)
        steam_names_to_paths = {}
        for ext in ["*.jpg", "*.jpeg"]:
            for p in glob.glob(os.path.join(self.steam_path, ext)):
                steam_names_to_paths[os.path.basename(p)] = p

        self.matched_screenshots.clear()
        self.selected_items.clear()
        self.thumbnail_images.clear()
        added_steam_files = set()

        # 2. Сканируем папку HD
        hd_patterns = ["*.jpg", "*.jpeg", "*.png", "*.avif"]
        hd_all_files = []
        for pattern in hd_patterns:
            hd_all_files.extend(glob.glob(os.path.join(self.hd_path, pattern)))
        for pattern in hd_patterns:
            hd_all_files.extend(glob.glob(os.path.join(self.hd_path, "**", pattern), recursive=True))

        # Надежное сопоставление по вхождению базового имени файла
        for hd_file_path in hd_all_files:
            hd_filename = os.path.basename(hd_file_path)
            hd_name_base, _ = os.path.splitext(hd_filename)
            
            for steam_filename, corresponding_steam_path in steam_names_to_paths.items():
                steam_name_base, _ = os.path.splitext(steam_filename)
                
                if steam_name_base == hd_name_base or hd_name_base.endswith(steam_name_base):
                    if steam_filename not in added_steam_files:
                        self.matched_screenshots.append((steam_filename, hd_file_path, corresponding_steam_path))
                        added_steam_files.add(steam_filename)
                    break 

        try:
            self.matched_screenshots.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        except Exception as e:
            print(f"Ошибка сортировки: {e}")

        self.render_gallery()

    def render_gallery(self):
        # 1. Надежная и полная очистка перед перерисовкой
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        if not self.matched_screenshots:
            if not self.steam_path or self.steam_path == ".":
                msg = "Игра не выбрана.\n\nПожалуйста, перейдите в Настройки и выберите игру\nиз выпадающего списка найденных в Steam."
            else:
                msg = "Синхронизированные кадры не найдены.\n\nПрограмма отображает только те файлы из HD папки,\nимена которых совпадают со скриншотами в выбранной игре."
                
            lbl_empty = ctk.CTkLabel(self.grid_container, text=msg, font=("Segoe UI", 13), text_color="#64748b")
            lbl_empty.pack(pady=100)
            return

        # Расчет количества колонок в ряду на основе ширины окна
        columns = max(2, self.current_width // 230)
        current_row_frame = None

        # 2. Отрисовка карточек через строки-контейнеры
        for index, (filename, hd_path, steam_path) in enumerate(self.matched_screenshots):
            # Каждые N элементов создаем новый горизонтальный ряд
            if index % columns == 0:
                current_row_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
                current_row_frame.pack(fill="x", pady=6, anchor="n")

            # ИСПРАВЛЕНО: Жестко фиксируем размеры и убираем expand=True, чтобы элементы не растягивались
            item_frame = ctk.CTkFrame(current_row_frame, corner_radius=10, border_width=1, border_color="#1e293b", fg_color="#0d0f12", width=220, height=175)
            item_frame.pack(side="left", padx=8, expand=False, anchor="w")
            item_frame.pack_propagate(False) # Запрещаем содержимому менять размеры карточки


            # Загрузка миниатюры
            try:
                img = Image.open(hd_path)
                img.thumbnail((200, 120))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 120))
                self.thumbnail_images[filename] = ctk_img
            except Exception:
                ctk_img = None

            if ctk_img:
                btn_img = ctk.CTkButton(item_frame, image=ctk_img, text="", fg_color="transparent", 
                                        hover_color="#00f0ff", height=120, corner_radius=8,
                                        command=lambda fn=filename: self.toggle_select(fn))
                btn_img.pack(padx=8, pady=8, fill="both", expand=True)
            else:
                btn_img = ctk.CTkButton(item_frame, text="Ошибка чтения файла", command=lambda fn=filename: self.toggle_select(fn))
                btn_img.pack(padx=8, pady=8, fill="both", expand=True)

            btn_zoom = ctk.CTkButton(item_frame, text="🔍 ПРОСМОТР", font=("Segoe UI", 10, "bold"), height=26, corner_radius=6,
                                     fg_color="#1e293b", hover_color="#334155", text_color="#00f0ff",
                                     command=lambda hp=hd_path: self.open_full_screen(hp))
            btn_zoom.pack(padx=8, pady=(0, 8), fill="x")

            item_frame.filename = filename
            if filename in self.selected_items:
                item_frame.configure(border_color="#ffee00", fg_color="#1a1c13")



    def toggle_select(self, filename):
        """Метод выделения скриншотов с глубоким обновлением рамок внутри рядов"""
        if filename in self.selected_items:
            self.selected_items.remove(filename)
        else:
            self.selected_items.add(filename)
        
        # Проходим по всем горизонтальным рядам в галерее
        for row_frame in self.grid_container.winfo_children():
            if row_frame.__class__.__name__ == "CTkFrame":
                # Внутри каждого ряда ищем карточки скриншотов
                for widget in row_frame.winfo_children():
                    if hasattr(widget, 'filename') and widget.filename == filename:
                        # Меняем цвет рамки и фона в зависимости от статуса выделения
                        if filename in self.selected_items:
                            widget.configure(border_color="#ffee00", fg_color="#1a1c13")
                        else:
                            widget.configure(border_color="#1e293b", fg_color="#0d0f12")
                        return  # Нашли нужный кадр — выходим из функции


    def open_full_screen(self, path):
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {e}")

    def replace_selected(self):
        if not self.selected_items:
            messagebox.showwarning("Внимание", "Выберите кадры для апгрейда!")
            return

        success_count = 0
        for filename, hd_path, steam_path in self.matched_screenshots:
            if filename in self.selected_items:
                try:
                    img = Image.open(hd_path)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    if os.path.exists(steam_path):
                        os.remove(steam_path)
                    img.save(steam_path, "JPEG", quality=100, subsampling=0)
                    
                    steam_dir = os.path.dirname(steam_path)
                    thumb_path = os.path.join(steam_dir, "thumbnails", filename)
                    
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)
                    else:
                        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                        
                    thumb_img = img.copy()
                    thumb_img.thumbnail((400, 250))
                    thumb_img.save(thumb_path, "JPEG", quality=90)
                    
                    os.utime(steam_path, None)
                    os.remove(hd_path)
                    success_count += 1
                except Exception as e:
                    print(f"Ошибка жесткой перезаписи Steam: {e}")

        if success_count > 0:
            messagebox.showinfo("Успешно", f"Скриншоты заменены на HD, миниатюры обновлены: {success_count} шт.")
            self.scan_screenshots()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ScreenshotApp()
    app.mainloop()
