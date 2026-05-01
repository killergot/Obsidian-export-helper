
# Obsidian export helper
## Как использовать
### Готовый бинарник
Скачайте архив для своей ОС из GitHub Releases, распакуйте и запустите файл:

```powershell
.\obsidian-export-helper.exe <source_file>
```

Для Linux/macOS:

```bash
chmod +x ./obsidian-export-helper
./obsidian-export-helper <source_file>
```

Python пользователю не нужен. По умолчанию файлы копируются в папку `output/` рядом с бинарником.

### Требования
- Python 3.10+

Нужны только для запуска из исходников или локальной сборки.

### Базовый запуск
```powershell
python main.py <source_file>
```
- `<source_file>` — путь к исходной заметке Obsidian (`.md`), из которой будут найдены и собраны связанные файлы.
    - Данный способ стоит использовать, если source_file лежит в корне вашего obsidian репозитория
- По умолчанию файлы копируются в `output/` рядом с `main.py`.

### Дополнительные флаги
```powershell
python main.py <source_file> [--output <path>] [--delete] [--folder] [--verbose] [--main_path <path>]
```

- `--output`, `-o` — путь назначения для файлов.
- `--delete` — перемещать файлы (удалять из исходного места) вместо копирования.
- `--folder` — сохранять структуру папок относительно корня Obsidian.
- `--verbose` — подробные логи.
- `--main_path` — корневая папка Obsidian. Если не задана, берется папка относительно `source_file`.

### Возможные проблемы
- Не отлажена работа с якорями, если вы их много используете, могут не подтягиваться данные файлы

## Сборка бинарника

Локальная сборка для текущей ОС:

```bash
python -m pip install -r requirements-build.txt
pyinstaller --clean --noconfirm obsidian-export-helper.spec
```

Готовый файл появится в `dist/`.

## Релиз через GitHub Actions

Workflow `.github/workflows/release.yml` запускается при push тега `v*`, прогоняет тесты, собирает PyInstaller-бинарники и публикует архивы в GitHub Release:

- `obsidian-export-helper-windows-x64.zip`
- `obsidian-export-helper-linux-x64.zip`
- `obsidian-export-helper-macos-x64.zip`
- `obsidian-export-helper-macos-arm64.zip`

Пример релиза:

```bash
git tag v0.1.0
git push origin v0.1.0
```

### Примеры
Скопировать все связанные файлы в папку `output` рядом с проектом:
```powershell
python main.py "D:\Vault\Notes\index.md"
```

Сохранить структуру папок в пользовательский каталог:
```powershell
python main.py "D:\Vault\Notes\index.md" --folder -o "D:\Export"
```

Переместить файлы (удалить из исходника):
```powershell
python main.py "D:\Vault\Notes\index.md" --delete -o "D:\Export"
```

Указать корень Obsidian явно:
```powershell
python main.py "D:\Vault\Notes\index.md" --main_path "D:\Vault"
```

## Архитектура проекта

### Поток выполнения
1. `main.py` принимает аргументы CLI и настраивает логирование.
2. `SearcherAllFiles` ищет ссылки в `source_file` и рекурсивно собирает связанные файлы.
3. `FileSetter` копирует или перемещает найденные файлы в целевую директорию.

### Основные модули
- `main.py` — CLI входная точка.
- `src/FileClasses/Searcher.py` — поиск ссылок (wikilink и markdown) и сбор зависимых файлов.
- `src/FileClasses/FileSetter.py` — копирование/перемещение файлов, сохранение структуры.
- `src/FileClasses/DirectoryWorker.py` — временная смена рабочей директории.
- `src/logger/logger.py` — логирование в консоль и файл.
- `src/lexicon/lexicon.py` — текстовые сообщения/подсказки CLI.

### Форматы ссылок
Поддерживаются:
- `[[link]]`
- `[[link|display]]`
- `[[link#section]]`
- `[[link#section|display]]`
- `[text](link)`
- `[text](link#section)`
- `[text](<link with spaces>)`
- `[text](file%20name.md)`
