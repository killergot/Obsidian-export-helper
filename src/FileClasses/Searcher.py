import logging
import os
import re
from pathlib import Path
from urllib.parse import unquote

from src.FileClasses.decor import except_catch

log = logging.getLogger(__name__)


class SearcherAllFiles:
    """Класс для поиска всех подфайлов"""

    file_extensions: tuple[str, ...] = (
        ".txt",  # Текстовые файлы
        ".md",  # md-файлы
        ".pdf",  # PDF-файлы
        ".doc",  # Microsoft Word документы
        ".docx",  # Microsoft Word документы (новый формат)
        ".xls",  # Microsoft Excel файлы
        ".xlsx",  # Microsoft Excel файлы (новый формат)
        ".ppt",  # Microsoft PowerPoint файлы
        ".pptx",  # Microsoft PowerPoint файлы (новый формат)
        ".csv",  # CSV (Comma Separated Values) файлы
        ".jpg",  # JPEG изображения
        ".jpeg",  # JPEG изображения
        ".png",  # PNG изображения
        ".gif",  # GIF изображения
        ".bmp",  # BMP изображения
        ".zip",  # ZIP архивы
        ".7z",
        ".tar",
        ".tar.gz",
        ".rar",  # RAR архивы
        ".exe",  # Исполняемые файлы
        ".bat",  # Пакетные файлы
        ".html",  # HTML файлы
        ".css",  # CSS файлы
        ".js",  # JavaScript файлы
        ".json",  # JSON файлы
        ".xml",  # XML файлы
        ".mp3",  # MP3 аудиофайлы
        ".wav",  # WAV аудиофайлы
        ".mp4",  # MP4 видеофайлы
        ".avi",  # AVI видеофайлы
        ".mkv",  # MKV видеофайлы
        ".dll",  # Библиотеки динамической компоновки
    )

    def search_in(
        self, file_path: Path, vault_path: Path | None = None
    ) -> set[str]:
        """
        Главная функция для поиска всех подфайлов
        :param file_path: пусть к главному файлу
        :param vault_path: Путь к корневой папке Obsidian vault
        :return:
        """
        res: set[str] = set()
        if vault_path is None:
            self.main_file_path = file_path.parent
        else:
            self.main_file_path = vault_path
        log.debug(f"Главный путь для поиска: {self.main_file_path}")
        self.rec_find_links(file_path, res)
        log.debug(f"{file_path = }")
        res.add(str(file_path))
        return res


    def read_file(self, path: str) -> str | None:
        """Функция для чтение информации из файла"""
        with open(path, encoding="utf-8") as file:
            content: str = file.read()
            return content

    def refactor_path_files(self, links: list[str]) -> list[str]:
        """
        Меняет все названия файлов на полные с расширением
        Также удаляет из списка несуществующие файлы
        :param links: Список файлов с неполными путями
        :return: Список файлов с полными путями
        """
        return list(filter(None, [self.set_exist_file(i) for i in links]))

    @staticmethod
    def normalize_link(link: str) -> str:
        decoded_link = unquote(link).strip()
        return decoded_link.split("#", 1)[0]

    def set_exist_file(self, test: str) -> str | None:
        """Проверка того, существует ли файл"""
        if not test.endswith(self.file_extensions):
            test += ".md"
        if os.path.exists(test):
            return test
        for root, _, _ in os.walk(self.main_file_path):
            if (
                root.rfind(".git") == -1 and root.rfind(".obsidian") == -1
            ):  # убираем проверку технических папок
                temp = Path(root).joinpath(test)
                if temp.exists():
                    log.debug(temp.relative_to(self.main_file_path))
                    return str(temp.relative_to(self.main_file_path))
        return None

    def find_all_links(self, file: str) -> list[str]:
        """
        Функция для нахождения всех ссылок в файле Obsidian.

        Поддерживаемые форматы:
        - [[link]]
        - [[link|display name]]
        - [[link#section]]
        - [[link#section|display name]]
        - [text](link)
        - [text](link#section)
        - [text](<link with spaces>)
        - [text](file%20name%20with%20spaces)
        """

        patterns: dict[str, re.Pattern] = {
            # [[filename]] или [[filename|display]] или [[filename#section|display]]
            "wikilink [[...]]": re.compile(
                r"""
                \[\[
                    (?P<link>[^\]\|#\n]+)   # имя файла (без |, #, ], переноса)
                    (?:\#[^\]\|\n]*)?       # опциональная секция #section
                    (?:\|[^\]\n]*)?         # опциональное отображаемое имя |display
                \]\]
                """,
                re.VERBOSE | re.IGNORECASE,
            ),
            # [text](<link with spaces>)
            "markdown link <...>": re.compile(
                r"""
                \[
                    [^\]\n]*                # текст ссылки
                \]
                \(
                    <(?P<link>[^>\n]+)>     # ссылка в угловых скобках
                \)
                """,
                re.VERBOSE | re.IGNORECASE,
            ),
            # [text](link#section) - стандартная markdown ссылка
            "markdown link (...)": re.compile(
                r"""
                \[
                    [^\]\n]*                # текст ссылки  
                \]
                \(
                    (?P<link>
                        [^()\n<>\s]+        # путь к файлу (без пробелов)
                        (?:\#[^\s()]*)?     # опциональный якорь #section
                    )
                \)
                """,
                re.VERBOSE | re.IGNORECASE,
            ),
            # [text](file%20name.md) - URL-encoded пробелы
            "markdown link with %20": re.compile(
                r"""
                \[
                    [^\]\n]*                # текст ссылки
                \]
                \(
                    (?P<link>
                        [^()\n<>]*          # начало пути
                        %20                 # минимум один encoded пробел
                        [^()\n<>]*          # остаток пути
                    )
                \)
                """,
                re.VERBOSE | re.IGNORECASE,
            ),
        }

        results: list[str] = []

        for description, pattern in patterns.items():
            for match in pattern.finditer(file):
                link = match.group("link")
                if link and link not in results:
                    # Декодируем %20 в пробелы если нужно
                    decoded_link = self.normalize_link(link)
                    if not decoded_link:
                        continue
                    if decoded_link not in results:
                        results.append(decoded_link)

        # Обработка найденных ссылок в файле
        log.debug(f"Все найденные ссылки: {results}")
        refactor_results = self.refactor_path_files(results)
        if refactor_results:
            log.info(f"Обработанные найденные ссылки: {refactor_results}")

        return refactor_results

    @except_catch
    def rec_find_links(self, file_path: str, links: set[str]) -> None:
        """
        Recursive search linsks in files
        - MB we need add 1 more param for bloc deep recursion
        :param file_path:
        :param links:
        :return:
        """
        content: str | None = self.read_file(file_path)
        if content is None:
            log.error(file_path + " wrong in name file")
            exit(1)
        old_links = set(
            links
        )  # костыль для пересечения в цикл, чтб не попасть в рекурсию
        new_links = set(self.find_all_links(content))
        links |= new_links
        for i in new_links.difference(old_links):
            if i.endswith(".md"):
                self.rec_find_links(i, links)
