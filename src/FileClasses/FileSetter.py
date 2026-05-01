import logging
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


class FileSetter:
    """Copy or move collected files from the current vault directory."""

    @staticmethod
    def new_make_dirs(src_path: str, dst_path: str) -> str:
        path = Path(src_path)
        if path.parent != Path("."):
            log.debug("Creating %s", path.parent)
            (Path(dst_path) / path.parent).mkdir(parents=True, exist_ok=True)
        return str(Path(dst_path) / path)

    @classmethod
    def file_transfer(
        cls,
        file_list: set[str],
        dst_path: str,
        *,
        del_flag: bool = False,
        folder_flag: bool = False,
    ) -> None:
        dst = Path(dst_path)
        dst.mkdir(parents=True, exist_ok=True)

        for file_name in file_list:
            new_dst_path: str | Path = dst
            if folder_flag:
                new_dst_path = cls.new_make_dirs(file_name, str(dst))

            if not del_flag:
                shutil.copy2(file_name, new_dst_path)
            else:
                shutil.move(file_name, new_dst_path)

        log.info("Complete")
