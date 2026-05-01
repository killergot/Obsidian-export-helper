# Obsidian export helper

Export one Obsidian note with all linked notes and assets into a portable folder.  
Утилита для экспорта заметки Obsidian вместе со связанными файлами: вложенными заметками, markdown-ссылками, wikilink-ссылками и изображениями. Подходит, когда нужно быстро собрать отдельный кусок vault в переносимую папку.

## Демонстрация

![Демонстрация экспорта Obsidian vault](assets/demo.gif)

На демонстрации показан типичный сценарий:

- открывается исходный файл в оригинальном Obsidian vault;
- видны подссылки и изображение, на которые ссылается заметка;
- запускается `obsidian-export-helper`;
- открывается экспортированный vault, где собраны исходная заметка и связанные файлы.

### Дополнительные флаги
```powershell
.\obsidian-export-helper.exe <source_file> [--output <path>] [--delete] [--folder] [--verbose] [--vault_path <path>]
```

- `--output`, `-o` — путь назначения для файлов. Если папки нет, она будет создана.
- `--delete` — перемещать файлы (удалять из исходного места) вместо копирования.
- `--folder` — сохранять структуру папок относительно корня Obsidian.
- `--verbose` — подробные логи.
- `--vault_path` — корневая папка Obsidian vault. Если не задана, используется папка `source_file`.

### Примеры
Скопировать все связанные файлы в папку `output` рядом с бинарником:
```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md"
```

Сохранить структуру папок в пользовательский каталог:
```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md" --folder -o "D:\Export"
```

Переместить файлы (удалить из исходника):
```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md" --delete -o "D:\Export"
```

Указать корень Obsidian vault явно:
```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md" --vault_path "D:\Vault"
```

## Разработка

### Требования
- Python 3.10+

### Запуск из исходников
```powershell
python main.py <source_file>
```

По умолчанию файлы копируются в `output/` рядом с `main.py`.

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

