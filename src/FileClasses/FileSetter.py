import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from src.FileClasses.IgnoreMatcher import IgnoreMatcher

log = logging.getLogger(__name__)


@dataclass
class TransferResult:
    copied_files: list[str] = field(default_factory=list)
    moved_files: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)

    @property
    def transferred_files(self) -> list[str]:
        return self.copied_files + self.moved_files


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
        ignore_matcher: IgnoreMatcher | None = None,
    ) -> TransferResult:
        result = TransferResult()
        dst = Path(dst_path)
        dst.mkdir(parents=True, exist_ok=True)

        for file_name in sorted(file_list):
            if ignore_matcher is not None and ignore_matcher.is_ignored(file_name):
                message = f"{file_name} (ignored by ignore file)"
                log.info("Skipping %s", message)
                result.skipped_files.append(message)
                continue

            if not Path(file_name).exists():
                message = f"{file_name} (source file is missing during transfer)"
                log.warning("Skipping %s", message)
                result.skipped_files.append(message)
                continue

            new_dst_path: str | Path = dst
            if folder_flag:
                new_dst_path = cls.new_make_dirs(file_name, str(dst))

            if not del_flag:
                shutil.copy2(file_name, new_dst_path)
                result.copied_files.append(file_name)
            else:
                shutil.move(file_name, new_dst_path)
                result.moved_files.append(file_name)

        log.info("Complete")
        return result
