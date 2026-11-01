# <img src="iconShdS.png" width="400" height="400" align="center">ScreenHDSteam Studio - RU


### ⚡ ScreenHDSteam Studio v4.1 - Перерождение на PyQt6 и Загрузка своих скриншотов

Рад представить масштабное обновление ScreenHDSteam Studio v4.1! В этом релизе полностью переписал графическое ядро программы. Отказался от старого фреймворка CustomTkinter в пользу профессионального и производительного PyQt6. Приложение стало значительно быстрее, стабильнее и обзавелось функциями, которые сделают работу со скриншотами Steam максимально комфортной.

Все необходимые графические ресурсы и новые иконки теперь полностью зашиты внутрь исполняемого файла. Приложение поставляется в виде одного монолитного файла формата EXE и готово к работе сразу после запуска.

---

### 🌟 Ключевые изменения и новые возможности

🔷 Полный переход на PyQt6
Графический каркас приложения полностью заменен. Это позволило внедрить глубокую темную тему, плавную анимацию загрузки, идеальное сглаживание миниатюр. Мы смогли полностью избавиться от скрытых багов отображения окон, свойственных старой библиотеке.

🌐 Автоматическая локализация (RU / EN)
Программа получила полноценную двуязычную поддержку. При запуске скрипт самостоятельно определяет язык вашей операционной системы. Он мгновенно переводит весь интерфейс, системные уведомления и диалоговые окна на русский или английский язык.

🔄 Умная система проверки обновлений
Внедрен асинхронный сетевой воркер, который в фоновом режиме бережно проверяет появление новых версий в репозитории GitHub. Процесс абсолютно автономен, не вызывает зависаний интерфейса и работает даже при нестабильном интернет-соединении.

🎨 Динамический инфо-индикатор в шапке
Если на сервере появится новая версия, номер сборки в верхнем меню мгновенно окрасится в ярко-желтый цвет. Под ним активируется аккуратный статус-текст «Требуется обновление», а рядом загорится кликабельная иконка со стрелочкой. Она в один клик перенаправит вас на страницу загрузки релиза.

📸 Новый режим: Кастомная замена
В дополнение к автоматическому умному сопоставлению добавлен полностью ручной режим. Теперь вы можете кликнуть на любой скриншот Steam в галерее и принудительно заменить его абсолютно любым графическим файлом с вашего компьютера. Поддерживаются форматы JPG, PNG, WEBP, AVIF.

🖼 Премиальный пак встроенных графических иконок
Текстовые эмодзи на кнопках остались в прошлом. Все элементы управления (Настройки, Обновить, Просмотр, Переключение режимов) получили собственные минималистичные PNG-иконки высокого разрешения. Они теперь вшиты напрямую в тело программы и идеально сочетаются с неоновым стилем интерфейса.

---

### 🛠 Исправления дефектов и оптимизация стабильности

* Фиксация выпадающего списка игр: Исправлен критический баг позиционирования меню выбора игр в настройках. Теперь при перемещении окна настроек по экрану выпадающий список больше не улетает и остается намертво привязанным к своему полю.
* Ликвидация серых рамок фокуса: Устранен визуальный дефект операционной системы Windows, при котором вокруг кликнутых кнопок появились серые пунктирные контуры фокуса ввода. Элементам прописано принудительное зануление контуров.
* Защита от сбоев при чтении конфигурации: Переписана логика парсинга строк файла config.txt с жестким контролем индексов данных. Это полностью исключает падение программы при повреждении конфигурационного файла.
* Улучшенный парсинг цифровых префиксов: Изменена логика сопоставления названий файлов в асинхронном сканере. Карточки скриншотов Steam, чьи имена начинаются со сложных числовых ID, теперь обрабатываются без сбоев.
* Монолитная EXE-сборка: Все пути к графическим ассетам и иконкам оптимизированы для компиляции через PyInstaller. Ресурсы запечатаны внутри исполняемого файла и автоматически извлекаются в систему при старте.

---

### 📦 Инструкция по установке и обновлению

1. Скачайте свежий исполнительный файл ScreenHDSteam.exe из вложений ниже.
2. Запустите приложение и наслаждайтесь качественными HD-кадрами в вашем профиле Steam!

---

### 💻 Развертывание и компиляция для разработчиков

Если вы хотите запустить проект из исходного кода или самостоятельно скомпилировать монолитный исполняемый файл, используйте следующую инструкцию.

Установка необходимых зависимостей:
```bash
pip install PyQt6 pillow pyinstaller
```

Инструкция по компиляции монолитного EXE-файла:
Чтобы все графические иконки интерфейса, логотипы и файлы ресурсов корректно упаковались внутрь одного исполняемого файла и не требовали внешних папок, сборка должна выполняться строго из корневой директории проекта через PyInstaller с флагами принудительного включения данных:

```bash
# 1. Перейдите в корневую папку вашего проекта
cd C:\Users\Ivan\Desktop\ScreenHDSteam

# 2. Выполните команду сборки (все ассеты из папки Debug будут вшиты в корень временной директории _MEIPASS)
python -m PyInstaller --noconsole --onefile --icon="Debug/iconShdS.ico" --add-data "Debug/btn_settings.png;." --add-data "Debug/btn_refresh.png;." --add-data "Debug/btn_view.png;." --add-data "Debug/btn_mode_auto.png;." --add-data "Debug/btn_mode_custom.png;." --add-data "Debug/btn_update_git.png;." --add-data "Debug/iconShdS.png;." Debug/ScreenHDSteam.py
```

Готовый автономный файл ScreenHDSteam.exe появится в автоматически созданной папке dist в корне вашего проекта.

## 📜 Лицензия и Статус проекта
* Проект распространяется под открытой лицензией **MIT License**. Вы можете свободно модифицировать и распространять этот код.
* **Текущий статус:** Проект успешно завершен и доведен до стабильного состояния. Глобальное обновление версии 3.0 принесло стопроцентную автоматизацию поиска путей Steam и исправило все известные баги интерфейса. 
Утилита полностью решает поставленные задачи, поэтому активное расширение функционала не планируется, однако автор оставляет за собой возможность выпускать технические исправления и патчи в будущем при необходимости.
* *Built with ❤️ and AI assistance.* Логика, архитектура глубокого поиска и графический интерфейс спроектированы в соавторстве с ИИ по техническому заданию автора.


# <img src="iconShdS.png" width="400" height="400" align="center">ScreenHDSteam Studio - ENG


# ⚡ ScreenHDSteam Studio v4.1 — Reborn on PyQt6 & Custom Screenshot Uploads

I am excited to present a major update: **ScreenHDSteam Studio v4.1**! In this release, the application's graphical core has been completely rewritten. I migrated from the old CustomTkinter framework to the professional and high-performance **PyQt6**. 

The application is now significantly faster and more stable, packed with new features to make managing your Steam screenshots as seamless as possible.

### 🌟 What's New
* **PyQt6 Transition:** Complete core rewrite for better UI rendering, snappier animations, and lower resource consumption.
* **Custom Backgrounds:** Added support for custom replacements and custom screenshot uploads.
* **Embedded Assets:** All required graphical assets and new icons are now fully embedded directly into the executable.
* **Portable EXE:** The application is distributed as a single, standalone EXE file and is ready to use right out of the box.


---

### 🌟 Key Changes and New Features

🔷 Complete Shift to PyQt6
The graphical backbone of the application has been completely replaced. This transition brings a deep dark theme, fluid scanning animations, flawless thumbnail smoothing. It eliminates hidden rendering bugs common to the legacy library.

🌐 Automatic Localization (RU / EN)
The program now features native bilingual support. Upon startup, the script automatically detects your operating system language. It instantly localizes the interface, system alerts, and dialog boxes to Russian or English.

🔄 Smart Update Verification System
An asynchronous network worker now runs quietly in the background to seamlessly check for new releases in the GitHub repository. This process is fully autonomous, does not freeze the interface, and remains robust even on unstable internet connections.

🎨 Dynamic Header Status Indicator
When a new version drops on the server, the build number in the top menu instantly highlights in bright neon yellow. An elegant status line reading “Update Required” activates underneath, and a clickable icon appears to redirect you to the release download page in a single click.

📸 New Feature: Custom Replacement
In addition to the automatic smart matching algorithm, we have added a fully manual replacement mode. You can now click on any Steam screenshot in your gallery and force-replace it with absolutely any image file from your computer. JPG, PNG, WEBP, and AVIF formats are supported.

🖼 Premium Embedded Icon Pack
Text emojis on buttons are a thing of the past. All interface controls (Settings, Refresh, View, Mode Toggles) received their own high-resolution minimalist PNG icons. They are compiled directly into the binary file and match the neon layout style flawlessly.

---

### 🛠 Bug Fixes and Stability Optimizations

* Locked Game Selection Dropdown: Fixed a critical positioning bug with the game choice menu in settings. Moving the configuration window across the screen no longer causes the dropdown list to fly out of bounds, keeping it perfectly pinned to its field.
* Eliminated Gray Focus Outlines: Resolved a visual glitch in Windows where clicking on buttons would generate a dotted gray focus border around them. Elements now enforce a strict non-focus outline rule.
* Corrupted Configuration Protection: Rewrote the file parsing logic for config.txt with strict array bounds checks. This prevents application crashes even if the underlying text settings become malformed.
* Enhanced Numerical Prefix Parsing: Improved the image comparison architecture within the asynchronous scanner. Steam screenshot assets starting with complex numerical AppID prefixes are now cross-referenced seamlessly.
* Monolithic EXE Deployment: All asset and asset tree lookup variables have been optimized for PyInstaller. Resources are encapsulated entirely within the binary and extract on the fly upon initialization.

---

### 📦 Installation & Upgrade Instructions

1. Download the latest executable file ScreenHDSteam.exe from the assets section below.
2. Run the application and enjoy pristine uncompressed HD captures right in your Steam profile!

---

### 💻 Developer Guide: Compilation & Deployment

Follow these instructions if you wish to run the application from source code or compile the standalone executable with all embedded assets manually.

Prerequisite Installation:
```bash
pip install PyQt6 pillow pyinstaller
```

Monolithic EXE Compilation Instructions:
To guarantee that all interface graphics, brand assets, and resource paths pack correctly inside a single binary without requiring external folders, execution must occur directly from your project's root folder utilizing PyInstaller with active data mapping flags:

```bash
# 1. Switch to your active project directory
cd C:\Users\Ivan\Desktop\ScreenHDSteam

# 2. Run the PyInstaller compilation command (all Debug assets will map to the root of the temporary _MEIPASS folder)
python -m PyInstaller --noconsole --onefile --icon="Debug/iconShdS.ico" --add-data "Debug/btn_settings.png;." --add-data "Debug/btn_refresh.png;." --add-data "Debug/btn_view.png;." --add-data "Debug/btn_mode_auto.png;." --add-data "Debug/btn_mode_custom.png;." --add-data "Debug/btn_update_git.png;." --add-data "Debug/iconShdS.png;." Debug/ScreenHDSteam.py
```

Your compiled, standalone binary file ScreenHDSteam.exe will be ready inside the freshly generated dist folder located in your root project directory.

## 📜 License and Project Status
* The project is distributed under the open **MIT License**. You are free to modify and distribute this source code.
* **Current Status:** The project is successfully completed and brought to a stable release state. The global version 3.0 update brought one hundred percent automation to Steam path discovery and resolved all known interface bugs. The utility resolves the designated tasks fully, meaning active feature expansion is not planned, though the author retains the option to release technical fixes and maintenance patches in the future if necessary.
* *Built with ❤️ and AI assistance.* The logic, deep intersection NTFS cache search architecture, and graphical interface were designed in collaboration with AI based on the technical specifications of the author.

