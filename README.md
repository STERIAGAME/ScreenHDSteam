# ⚡ ScreenHDSteam Studio (v2.6 NEON)

**ScreenHDSteam** - это современная минималистичная утилита на Python с интерфейсом, созданная специально для любителей виртуальной фотографии в играх. Программа решает проблему агрессивного сжатия скриншотов в клиенте Steam, автоматически заменяя "мыльные" облачные копии на несжатые оригиналы высокого качества.

---

## 🛑 Проблема (The Problem)
Когда вы нажимаете **F12** в игре, Steam делает два кадра: сжатый JPEG (около 600 КБ) для облака и качественный PNG/JPEG (от 4 МБ) во внешнюю папку. Однако загрузить в свой профиль Steam качественный кадр стандартными средствами невозможно - клиент принудительно синхронизирует только пережатую, "мыльную" картинку, уничтожая детализацию текстур и эффекты (особенно заметно в Cyberpunk 2077).

## 🚀 Решение и Возможности (Features)
* **Интеллектуальное сопоставление (Smart Matching):** Программа сканирует папки Steam и HD-оригиналов, автоматически связывая файлы `.png` и `.jpg` вместе по времени снимка, отсекая префиксы ID игр (например, `1091500_...`).
* **Интуитивный Multi-Select:** Больше не нужно зажимать Ctrl. Выделяйте нужные кадры обычными кликами мыши - выбранные элементы подсвечиваются яркой неоновой рамкой.
* **Обход блокировок файловой системы:** Скрипт принудительно обходит защиту дескрипторов Windows/Steam, на лету перекодируя PNG в идеальный JPEG (100% качество, без субсэмплинга), обновляя как основной файл, так и превью-миниатюру (`thumbnails`).
* **Эстетика:** Более менее приятный и удобный интерфейс на базе `customtkinter` с глубокими темными тонами, неоновыми акцентами и адаптивной сеткой под любые размеры экрана. 
(Можно и красивее , но делал чисто для себя на скорую руку ^_^  ).

* **Автоочистка памяти:** После успешного апгрейда программа автоматически удаляет оригиналы из папки источника, чтобы они не занимали лишнее место на диске.

---

## ⚙️ Настройка и Использование (How to Use)

1. Откройте **Steam** -> **Настройки** -> **В игре**. Включите тумблер *"Сохранять внешние копии моих скриншотов"* и выберите формат **PNG**.
2. Запустите **ScreenHDSteam**.
3. Нажмите кнопку **⚙ Настройки** в правом верхнем углу программы:
   * В поле **Источник** укажите папку, куда Steam сохраняет внешние копии (например, `C:\Users\USERNAME\Documents`).
   * В поле **Приемник** укажите путь к папку скриншотов игры в Steam (путь должен заканчиваться строго на слово `screenshots`, например: `D:\Steam\userdata\...\1091500\screenshots`).
4. Нажмите **Сохранить конфигурацию** (пути зафиксируются намертво).
5. Сделайте скриншот в игре (F12), перейдите в программу, нажмите **🔄 ОБНОВИТЬ**, выберите кадр и нажмите **АПГРЕЙД В HD**.
6. Перезапустите окно скриншотов в Steam - вес файла вырастет до нескольких мегабайт. Нажимайте **«Загрузить»**!

---

## 🛠️ Развертывание для разработчиков (Tech Stack)

Если вы хотите запустить проект из исходного кода:

```bash
# Установка необходимых зависимостей
pip install customtkinter pillow pyinstaller

# Запуск программы
python ScreenHDSteam.py

# Компиляция в автономный .exe файл Windows
python -m PyInstaller --noconsole --onefile --collect-all customtkinter ScreenHDSteam.py
```

---

## 📜 Лицензия и Статус проекта (License & Project Status)
* Проект распространяется под открытой лицензией **MIT License**. Вы можете свободно модифицировать и распространять этот код.
* **Текущий статус:** На данный момент основная функция умного сопоставления и принудительного апгрейда файлов протестирована и работает абсолютно исправно. Проект полностью завершен, решает все поставленные задачи, поэтому выпуск последующих обновлений, патчей или функциональных улучшений не планируется.
* *Built with ❤️ and AI assistance.* Логика, архитектура глубокого поиска пересечений кэша NTFS и графический интерфейс спроектированы в соавторстве с ИИ по техническому заданию автора.



_________________________________________________________


# ⚡ ScreenHDSteam Studio (v2.6 NEON)

**ScreenHDSteam** is a modern, minimalist Python GUI utility tailored specifically for virtual photography enthusiasts. The program solves the aggressive screenshot compression issue in the Steam client by automatically replacing "blurry" cloud copies with uncompressed, high-quality originals.

---

## 🛑 The Problem

When you press **F12** in-game, Steam captures two frames: a compressed JPEG (approx. 600 KB) for the cloud, and a high-quality PNG/JPEG (4 MB+) sent to an external folder. However, it is impossible to upload the high-quality shot to your Steam profile using standard methods—the client forces a sync of the re-compressed, "blurry" image, destroying texture details and effects (most noticeable in games like Cyberpunk 2077).

## 🚀 Features

* **Smart Matching:** The program scans both Steam and HD original folders, automatically linking `.png` and `.jpg` files together based on timestamps while filtering out game ID prefixes (e.g., `1091500_...`).
* **Intuitive Multi-Select:** No need to hold down Ctrl. Select the desired frames with regular mouse clicks—chosen items are highlighted with a vibrant neon border.
* **Bypassing File System Locks:** The script bypasses Windows/Steam handle protection on the fly, re-encoding PNGs into flawless JPEGs (100% quality, no subsampling) and updating both the main file and the preview thumbnail (`thumbnails`).
* **Aesthetics:** A clean and user-friendly interface built with `customtkinter`, featuring deep dark tones, neon accents, and an adaptive grid fitting any screen size. *(Could be fancier, but it was quickly put together for personal use ^_^).*
* **Auto Memory Cleanup:** Once the upgrade is successful, the program automatically deletes the originals from the source folder to save disk space.

---

## ⚙️ How to Use

1. Open **Steam** -> **Settings** -> **In-Game**. Toggle on *"Save an uncompressed copy of my screenshots"* and select the **PNG** format.
2. Launch **ScreenHDSteam**.
3. Click the **⚙ Settings** button in the top right corner of the program:
   * In the **Source** field, specify the folder where Steam saves your external copies (e.g., `C:\Users\USERNAME\Documents`).
   * In the **Destination** field, specify the path to the specific game's screenshot folder inside Steam (the path must end strictly with the word `screenshots`, e.g., `D:\Steam\userdata\...\1091500\screenshots`).
4. Click **Save Configuration** (the paths will be permanently saved).
5. Take a screenshot in-game (F12), switch to the program, click **🔄 REFRESH**, select your frame, and click **UPGRADE TO HD**.
6. Restart the Steam screenshot manager window—the file size will instantly jump to several megabytes. Hit **"Upload"**!

---

## 🛠️ Tech Stack (For Developers)

If you want to run the project from source code:

```bash
# Install required dependencies
pip install customtkinter pillow pyinstaller

# Run the application
python ScreenHDSteam.py

# Compile into a standalone Windows .exe file
python -m PyInstaller --noconsole --onefile --collect-all customtkinter ScreenHDSteam.py
```

---

## 📜 License & Project Status

* The project is distributed under the open **MIT License**. Feel free to modify and share this code.
* **Current Status:** The core smart matching and forced file upgrade features are fully tested and working flawlessly. The project is fully complete and achieves all its goals, so no future updates, patches, or functional improvements are planned.
* *Built with ❤️ and AI assistance.* The logic, deep NTFS cache intersection search architecture, and graphical user interface were co-designed with AI based on the author's technical specifications.

