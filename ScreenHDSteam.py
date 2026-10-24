import os
import glob
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

CONFIG_FILE = "config.txt"
def load_paths():
    """Загрузка путей с надежным извлечением чистых строк из массива"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if len(lines) >= 2:
                    # ИСПРАВЛЕНО: Извлекаем элементы из списка по индексам передnormpath
                    path_hd = os.path.normpath(lines[0])
                    path_steam = os.path.normpath(lines[1])
                    return path_hd, path_steam
        except Exception:
            pass
    return "", ""

def save_paths(hd_path, steam_path):
    """Принудительная перезапись и сохранение конфигурации на диск в UTF-8"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"{os.path.normpath(hd_path)}\n{os.path.normpath(steam_path)}")
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось записать конфиг: {e}")
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Конфигурация среды")
        self.geometry("600x320")
        self.resizable(False, False)
        
        # Надежное исправление фокуса и модальности окон в Windows
        self.after(100, self.lift)
        self.focus_set()
        
        self.configure(fg_color="#0d0f12")
        
        lbl_title = ctk.CTkLabel(self, text="НАСТРОЙКИ СИНХРОНИЗАЦИИ", font=("Segoe UI", 15, "bold"), text_color="#00f0ff")
        lbl_title.pack(pady=20)
        
        # Папка HD
        frame_hd = ctk.CTkFrame(self, fg_color="transparent")
        frame_hd.pack(fill="x", padx=30, pady=8)
        lbl_hd = ctk.CTkLabel(frame_hd, text="Источник (Папка HD):", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        lbl_hd.pack(anchor="w")
        self.entry_hd = ctk.CTkEntry(frame_hd, fg_color="#1e293b", border_color="#334155", text_color="#f8fafc", placeholder_text="Путь к четким копиям...")
        self.entry_hd.insert(0, parent.hd_path)
        self.entry_hd.pack(side="left", fill="x", expand=True, pady=5, padx=(0, 10), ipady=2)
        btn_hd = ctk.CTkButton(frame_hd, text="Обзор", fg_color="#00f0ff", hover_color="#00b8cc", text_color="#0f172a", font=("Segoe UI", 11, "bold"), width=70, command=self.browse_hd)
        btn_hd.pack(side="right", pady=5)
        # Папка Steam
        frame_steam = ctk.CTkFrame(self, fg_color="transparent")
        frame_steam.pack(fill="x", padx=30, pady=8)
        lbl_steam = ctk.CTkLabel(frame_steam, text="Приемник (Папка Steam\\userdata):", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        lbl_steam.pack(anchor="w")
        self.entry_steam = ctk.CTkEntry(frame_steam, fg_color="#1e293b", border_color="#334155", text_color="#f8fafc", placeholder_text="Путь к userdata или скриншотам игры...")
        self.entry_steam.insert(0, parent.steam_path)
        self.entry_steam.pack(side="left", fill="x", expand=True, pady=5, padx=(0, 10), ipady=2)
        btn_steam = ctk.CTkButton(frame_steam, text="Обзор", fg_color="#00f0ff", hover_color="#00b8cc", text_color="#0f172a", font=("Segoe UI", 11, "bold"), width=70, command=self.browse_steam)
        btn_steam.pack(side="right", pady=5)
        
        btn_close = ctk.CTkButton(self, text="СОХРАНИТЬ КОНФИГУРАЦИЮ", fg_color="#00f0ff", hover_color="#00b8cc", text_color="#07080a", font=("Segoe UI", 12, "bold"), height=40, corner_radius=8, command=self.save_and_close)
        btn_close.pack(pady=25)

        self.entry_hd.bind("<Control-v>", lambda e: self.custom_paste(self.entry_hd))
        self.entry_steam.bind("<Control-v>", lambda e: self.custom_paste(self.entry_steam))
        self.entry_hd.bind("<Control-c>", lambda e: self.custom_copy(self.entry_hd))
        self.entry_steam.bind("<Control-c>", lambda e: self.custom_copy(self.entry_steam))

    def custom_paste(self, widget):
        try:
            text = self.clipboard_get()
            widget.delete(0, tk.END)
            widget.insert(tk.INSERT, text)
        except Exception:
            pass
        return "break"

    def custom_copy(self, widget):
        try:
            text = widget.get()
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception:
            pass
        return "break"
    def browse_hd(self):
        self.grab_release()
        folder = filedialog.askdirectory(title="Выберите папку с HD-скриншотами")
        if folder:
            self.entry_hd.delete(0, tk.END)
            self.entry_hd.insert(0, os.path.normpath(folder))
        self.grab_set()
        self.focus_set()

    def browse_steam(self):
        self.grab_release()
        folder = filedialog.askdirectory(title="Выберите папку Steam\\userdata")
        if folder:
            self.entry_steam.delete(0, tk.END)
            self.entry_steam.insert(0, os.path.normpath(folder))
        self.grab_set()
        self.focus_set()

    def save_and_close(self):
        hd = os.path.normpath(self.entry_hd.get()) if self.entry_hd.get() else ""
        steam = os.path.normpath(self.entry_steam.get()) if self.entry_steam.get() else ""
        save_paths(hd, steam)
        self.parent.hd_path = hd
        self.parent.steam_path = steam
        self.destroy()
        self.parent.scan_screenshots()
class ScreenshotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.configure(fg_color="#07080a") 
        self.title("ScreenHDSteam Studio")
        self.geometry("1000x720")
        self.minsize(800, 580)

        self.hd_path, self.steam_path = load_paths()
        self.matched_screenshots = []
        self.selected_items = set()
        self.thumbnail_images = {}

        self.bind("<Configure>", self.on_window_resize)
        self.current_width = 1000

        # --- ВЕРХНЯЯ НАВИГАЦИОННАЯ ПАНЕЛЬ ---
        self.header_frame = ctk.CTkFrame(self, fg_color="#0d0f12", height=65, corner_radius=0, border_width=1, border_color="#1e293b")
        self.header_frame.pack(fill="x", side="top")
        
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="ScreenHDSteam", font=("Segoe UI", 22, "bold"), text_color="#ffffff")
        self.lbl_title.pack(side="left", padx=30, pady=15)
        
        self.badge = ctk.CTkLabel(self.header_frame, text="v2.6 NEON", font=("Segoe UI Semibold", 10), 
                                   text_color="#00f0ff", fg_color=("#1e293b", "#142129"), 
                                   width=70, height=20, corner_radius=10)
        self.badge.pack(side="left", padx=(0, 20), pady=22)

        self.btn_settings = ctk.CTkButton(self.header_frame, text="⚙ Настройки", width=110, height=34, corner_radius=6,
                                           fg_color="#1e293b", hover_color="#334155", text_color="#94a3b8",
                                           font=("Segoe UI Semibold", 12), command=self.open_settings)
        self.btn_settings.pack(side="right", padx=30, pady=15)

        # --- ОСНОВНАЯ ЗОНА ГАЛЕРЕИ ---
        self.scroll_gallery = ctk.CTkScrollableFrame(self, fg_color="#090a0d", corner_radius=0, border_width=0)
        self.scroll_gallery.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.grid_container = ctk.CTkFrame(self.scroll_gallery, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True)

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

        # 1. Сканируем папку Steam и собираем пути для основных файлов
        steam_names_to_paths = {}
        for ext in ["*.jpg", "*.jpeg"]:
            for p in glob.glob(os.path.join(self.steam_path, ext)):
                if "thumbnails" not in os.path.normpath(p).split(os.sep):
                    steam_names_to_paths[os.path.basename(p)] = p
            for p in glob.glob(os.path.join(self.steam_path, "**", ext), recursive=True):
                if "thumbnails" not in os.path.normpath(p).split(os.sep):
                    steam_names_to_paths[os.path.basename(p)] = p

        self.matched_screenshots.clear()
        self.selected_items.clear()
        self.thumbnail_images.clear()

        added_steam_files = set()

        # 2. Глубокое сканирование папки HD (решает проблему скрытых файлов в Документах Windows)
        hd_patterns = ["*.jpg", "*.jpeg", "*.png", "*.avif"]
        hd_all_files = []
        
        # Собираем файлы в корне папки HD
        for pattern in hd_patterns:
            hd_all_files.extend(glob.glob(os.path.join(self.hd_path, pattern)))
        # На случай багов локализации Windows, проверяем и вложенные файлы
        for pattern in hd_patterns:
            hd_all_files.extend(glob.glob(os.path.join(self.hd_path, "**", pattern), recursive=True))

        # Сопоставляем файлы
        for hd_file_path in hd_all_files:
            hd_filename = os.path.basename(hd_file_path)
            hd_name_base, _ = os.path.splitext(hd_filename)
            
            # Убираем префикс ID игры (например, 1091500_), если он прикрепился к имени PNG
            if "_" in hd_name_base:
                parts = hd_name_base.split("_")
                if parts[0].isdigit() and len(parts) > 1:
                    hd_name_base = "_".join(parts[1:])
            
            for steam_filename, corresponding_steam_path in steam_names_to_paths.items():
                steam_name_base, _ = os.path.splitext(steam_filename)
                
                # Точное сравнение базовых имен без учета расширений и ID игры
                if steam_name_base == hd_name_base or steam_name_base in hd_name_base:
                    if steam_filename not in added_steam_files:
                        self.matched_screenshots.append((steam_filename, hd_file_path, corresponding_steam_path))
                        added_steam_files.add(steam_filename)
                    break 

        # ИСПРАВЛЕНО: Сортируем строго по пути к файлу Steam (индекс 2 в кортеже)
        self.matched_screenshots.sort(key=lambda x: os.path.getmtime(x[2]), reverse=True)
        self.render_gallery()
    def render_gallery(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        if not self.matched_screenshots:
            lbl_empty = ctk.CTkLabel(self.grid_container, 
                                     text="Синхронизированные кадры не найдены.\n\nПрограмма отображает только те файлы из HD папки,\nимена которых совпадают со скриншотами в Steam.", 
                                     font=("Segoe UI", 13), text_color="#64748b")
            lbl_empty.pack(pady=100)
            return

        columns = max(2, self.current_width // 230)
        for i in range(columns):
            self.grid_container.grid_columnconfigure(i, weight=1, pad=12)

        for index, (filename, hd_path, steam_path) in enumerate(self.matched_screenshots):
            row = index // columns
            col = index % columns

            item_frame = ctk.CTkFrame(self.grid_container, corner_radius=10, border_width=1, border_color="#1e293b", fg_color="#0d0f12")
            item_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

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
                btn_img.pack(padx=8, pady=8, fill="both")
            else:
                btn_img = ctk.CTkButton(item_frame, text="Ошибка чтения файла", command=lambda fn=filename: self.toggle_select(fn))
                btn_img.pack(padx=8, pady=8, fill="both")

            btn_zoom = ctk.CTkButton(item_frame, text="🔍 ПРОСМОТР", font=("Segoe UI", 10, "bold"), height=26, corner_radius=6,
                                     fg_color="#1e293b", hover_color="#334155", text_color="#00f0ff",
                                     command=lambda hp=hd_path: self.open_full_screen(hp))
            btn_zoom.pack(padx=8, pady=(0, 8), fill="x")

            item_frame.filename = filename
            if filename in self.selected_items:
                item_frame.configure(border_color="#ffee00", fg_color="#1a1c13")
    def toggle_select(self, filename):
        if filename in self.selected_items:
            self.selected_items.remove(filename)
        else:
            self.selected_items.add(filename)
        
        for widget in self.grid_container.winfo_children():
            if hasattr(widget, 'filename'):
                if widget.filename in self.selected_items:
                    widget.configure(border_color="#ffee00", fg_color="#1a1c13")
                else:
                    widget.configure(border_color="#1e293b", fg_color="#0d0f12")

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
                    # 1. Открываем оригинальный HD кадр
                    img = Image.open(hd_path)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # 2. Перезаписываем строго ТЯЖЕЛЫЙ основной файл скриншота в корне
                    if os.path.exists(steam_path):
                        os.remove(steam_path)
                    img.save(steam_path, "JPEG", quality=100, subsampling=0)
                    
                    # 3. Перезаписываем ЛЕГКУЮ превьюшку в подпапке thumbnails
                    steam_dir = os.path.dirname(steam_path)
                    thumb_path = os.path.join(steam_dir, "thumbnails", filename)
                    
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)
                    else:
                        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                        
                    thumb_img = img.copy()
                    thumb_img.thumbnail((400, 250))
                    thumb_img.save(thumb_path, "JPEG", quality=90)
                    
                    # Сброс кэша файла
                    os.utime(steam_path, None)
                    
                    # Удаляем оригинал из Моих Документов
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
