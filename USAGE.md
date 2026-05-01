# Obsidian export helper: использование

## Базовый запуск

Скачайте архив для своей ОС из GitHub Releases, распакуйте и запустите бинарник:

```powershell
.\obsidian-export-helper.exe <source_file>
```

```cmd
obsidian-export-helper.exe <source_file>
```

Для Linux/macOS:

```bash
chmod +x ./obsidian-export-helper
./obsidian-export-helper <source_file>
```

По умолчанию файлы копируются в папку `output/` рядом с бинарником.

- `<source_file>` - путь к исходной заметке Obsidian (`.md`), из которой будут найдены и собраны связанные файлы.
- Если указать `<source_file>` без расширения, например `учеба`, утилита попробует найти `учеба.md`.
- Без `--vault_path` корнем vault считается папка, в которой лежит `source_file`.

## Дополнительные флаги

```powershell
.\obsidian-export-helper.exe <source_file> [--vault_path <path>] [--output <path>] [--delete] [--folder] [--report] [--verbose]
```

- `--vault_path` - корневая папка Obsidian vault. Если не задана, используется папка `source_file`. Если задана, `source_file` должен находиться внутри этой папки.
- `--output`, `-o` - путь назначения для файлов. Если папки нет, она будет создана.
- `--delete` - перемещать файлы, то есть удалять их из исходного места после переноса.
- `--folder` - сохранять структуру папок относительно корня Obsidian vault.
- `--report` - создать markdown-отчёт `export-report-{filename}.md` рядом с бинарником, а при запуске из исходников - рядом с `main.py`.
- `--verbose` - подробные логи.

После успешного экспорта в консоль выводится summary:

```text
Export complete:
- notes: 12
- images: 4
- missing links: 2
- output: D:\Export
```

## Примеры

Скопировать все связанные файлы в папку `output` рядом с бинарником:

```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md"
```

Сохранить структуру папок в пользовательский каталог:

```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md" --folder -o "D:\Export"
```

Переместить файлы с удалением из исходного vault:

```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md" --delete -o "D:\Export"
```

Указать корень Obsidian vault явно:

```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md" --vault_path "D:\Vault"
```

Создать отчёт по экспорту:

```powershell
.\obsidian-export-helper.exe "D:\Vault\Notes\index.md" --vault_path "D:\Vault" -o "D:\Export" --report
```

Отчёт `export-report-index.md` создаётся рядом с бинарником или `main.py` и содержит:

- основные параметры запуска;
- статистику по заметкам, изображениям и отсутствующим ссылкам;
- список скопированных или перемещённых файлов;
- список пропущенных файлов и missing links;
- соответствия найденных ссылок реальным файлам.

## Что экспортируется

Утилита рекурсивно собирает файлы, найденные через поддерживаемые ссылки:

- `[[link]]`
- `[[link|display]]`
- `[[link#section]]`
- `[[link#section|display]]`
- `[text](link)`
- `[text](link#section)`
- `[text](<link with spaces>)`
- `[text](file%20name.md)`

