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
- Без `--vault_path` корнем vault считается папка, в которой лежит `source_file`.

## Дополнительные флаги

```powershell
.\obsidian-export-helper.exe <source_file> [--output <path>] [--delete] [--folder] [--verbose] [--vault_path <path>]
```

- `--output`, `-o` - путь назначения для файлов. Если папки нет, она будет создана.
- `--delete` - перемещать файлы, то есть удалять их из исходного места после переноса.
- `--folder` - сохранять структуру папок относительно корня Obsidian vault.
- `--verbose` - подробные логи.
- `--vault_path` - корневая папка Obsidian vault. Если не задана, используется папка `source_file`.

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

