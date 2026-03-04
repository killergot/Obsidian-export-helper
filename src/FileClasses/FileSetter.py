import logging
import os
import shutil
from pathlib import Path

from src.FileClasses.decor import except_catch

log = logging.getLogger(__name__)


class FileSetter:
    """
    Класс для переноса или копирования файлов из списка текущей рабочей директории куда либо
    """

    @staticmethod
    def new_make_dirs(src_path: str, dst_path: str) -> str:
        """
        Функция для создания папок внутри папки назначения
        :param src_path: Начальный путь файла
        :param dst_path: Целевая папка
        """
        path = Path(src_path)
        if path.parent != Path("."):
            log.debug(f"Создается {path.parent}")
            (Path(dst_path) / path.parent).mkdir(parents=True, exist_ok=True)
        return str(Path(dst_path) / path)

    @classmethod
    @except_catch
    def file_transfer(
        cls,
        file_list: set[str],
        dst_path: str,
        *,
        del_flag: bool = False,
        folder_flag: bool = False,
    ) -> None:
        """
        Переносит все файлы из одного места в другое
        :param file_list: Список всех файлов
        :param dst_path: Целевая папка
        :param del_flag: Нужно ли удалять файлы из исходного места
        :param folder_flag: Нужно ли сохранять сами папки
        :return:
        """

        if not os.path.exists(dst_path) and not os.path.isfile(dst_path):
            log.info("Папки назначения не существует, создайте её\n")
            return

        for i in file_list:
            new_dst_path: str = dst_path
            if folder_flag:
                new_dst_path = cls.new_make_dirs(i, dst_path)

            if not del_flag:
                shutil.copy2(i, new_dst_path)
            else:
                shutil.move(i, new_dst_path)

        log.info("Complete")
