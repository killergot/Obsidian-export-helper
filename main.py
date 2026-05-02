import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.FileClasses.DirectoryWorker import DirectoryWorker
from src.FileClasses.FileSetter import FileSetter, TransferResult
from src.FileClasses.IgnoreMatcher import DEFAULT_IGNORE_FILE, IgnoreMatcher
from src.FileClasses.Searcher import SearcherAllFiles
from src.lexicon.lexicon import LEXICON_RU
from src.logger.logger import init_log


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}


def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def source_candidates(source_arg: str) -> list[Path]:
    source_path = Path(source_arg)
    if source_path.suffix == "":
        return [source_path.with_suffix(".md")]
    if source_path.suffix.lower() != ".md":
        raise ValueError(
            f"source_file must be a Markdown file (.md): {source_arg}. "
            "If you omit the suffix, the exporter will try '<name>.md'."
        )
    return [source_path]


def resolve_source_file(source_arg: str, vault_path: Path | None) -> Path:
    candidates = source_candidates(source_arg)
    checked_paths: list[Path] = []

    for candidate in candidates:
        if candidate.is_absolute():
            candidate_path = candidate.resolve()
        elif vault_path is not None:
            candidate_path = (vault_path / candidate).resolve()
        else:
            candidate_path = candidate.resolve()

        checked_paths.append(candidate_path)
        if candidate_path.is_file():
            return candidate_path

    checked = ", ".join(str(path) for path in checked_paths)
    raise FileNotFoundError(f"source file not found: {source_arg}. Checked: {checked}")


def relative_to_vault(source_file: Path, vault_path: Path) -> Path:
    try:
        return source_file.relative_to(vault_path)
    except ValueError as exc:
        raise ValueError(
            f"--vault_path does not contain source_file. "
            f"source_file: {source_file}; vault_path: {vault_path}"
        ) from exc


def resolve_ignore_file(launch_dir: Path, ignore_file_arg: str | None) -> Path | None:
    if ignore_file_arg is None:
        ignore_file = launch_dir / DEFAULT_IGNORE_FILE
        return ignore_file if ignore_file.is_file() else None

    ignore_file = Path(ignore_file_arg)
    if not ignore_file.is_absolute():
        ignore_file = launch_dir / ignore_file
    ignore_file = ignore_file.resolve()
    if not ignore_file.is_file():
        raise FileNotFoundError(f"ignore file not found: {ignore_file}")
    return ignore_file


def build_ignore_matcher(
    vault_path: Path, launch_dir: Path, ignore_file_arg: str | None
) -> tuple[IgnoreMatcher, Path | None]:
    ignore_file = resolve_ignore_file(launch_dir, ignore_file_arg)
    if ignore_file is None:
        return IgnoreMatcher.empty(vault_path), None
    return IgnoreMatcher.from_file(vault_path, ignore_file), ignore_file


def print_summary(
    transfer_result: TransferResult,
    missing_links: list[str],
    ignored_files: list[str],
    output_path: Path,
) -> None:
    transferred_files = transfer_result.transferred_files
    notes = sum(1 for file_name in transferred_files if Path(file_name).suffix == ".md")
    images = sum(
        1 for file_name in transferred_files if Path(file_name).suffix.lower() in IMAGE_EXTENSIONS
    )

    print("Export complete:")
    print(f"- notes: {notes}")
    print(f"- images: {images}")
    print(f"- missing links: {len(missing_links)}")
    print(f"- ignored files: {len(ignored_files)}")
    print(f"- output: {output_path}")


def report_path_for(app_dir: Path, source_file: Path) -> Path:
    return app_dir / f"export-report-{source_file.stem}.md"


def write_report(
    *,
    app_dir: Path,
    output_path: Path,
    source_file: Path,
    source_file_for_search: Path,
    vault_path: Path,
    transfer_result: TransferResult,
    missing_links: list[str],
    ignored_files: list[str],
    resolved_links: dict[str, str],
    delete: bool,
    folder: bool,
    ignore_file: Path | None,
) -> Path:
    report_path = report_path_for(app_dir, source_file)
    transferred_files = transfer_result.transferred_files
    notes = sum(1 for file_name in transferred_files if Path(file_name).suffix == ".md")
    images = sum(
        1 for file_name in transferred_files if Path(file_name).suffix.lower() in IMAGE_EXTENSIONS
    )

    lines = [
        f"# Export report: {source_file.name}",
        "",
        "## Parameters",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Source file: `{source_file}`",
        f"- Source file inside vault: `{source_file_for_search}`",
        f"- Vault path: `{vault_path}`",
        f"- Output: `{output_path}`",
        f"- Delete source files: `{delete}`",
        f"- Preserve folders: `{folder}`",
        f"- Ignore file: `{ignore_file or 'None'}`",
        "",
        "## Summary",
        "",
        f"- Notes: {notes}",
        f"- Images: {images}",
        f"- Missing links: {len(missing_links)}",
        f"- Ignored files: {len(ignored_files)}",
        f"- Copied files: {len(transfer_result.copied_files)}",
        f"- Moved files: {len(transfer_result.moved_files)}",
        f"- Skipped files: {len(transfer_result.skipped_files)}",
        "",
        "## Copied files",
        "",
    ]

    copied_or_moved = transferred_files
    if copied_or_moved:
        lines.extend(f"- `{file_name}`" for file_name in copied_or_moved)
    else:
        lines.append("- None")

    lines.extend(["", "## Skipped files", ""])
    skipped_files = (
        transfer_result.skipped_files
        + [f"{file_name} (ignored by ignore file)" for file_name in ignored_files]
        + [f"{link} (linked target is missing)" for link in missing_links]
    )
    if skipped_files:
        lines.extend(f"- `{file_name}`" for file_name in skipped_files)
    else:
        lines.append("- None")

    lines.extend(["", "## Resolved links", ""])
    if resolved_links:
        lines.extend(
            f"- `{source_link}` -> `{resolved_file}`"
            for source_link, resolved_file in sorted(resolved_links.items())
        )
    else:
        lines.append("- None")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    configure_stdio()

    parser = argparse.ArgumentParser(description=LEXICON_RU["/help"])
    parser.add_argument("source_file", help=LEXICON_RU["source_file"])

    default_output = get_app_dir().joinpath("output")
    default_output.mkdir(parents=True, exist_ok=True)

    parser.add_argument(
        "-o", "--output", help=LEXICON_RU["--output"], default=default_output
    )
    parser.add_argument("--delete", help=LEXICON_RU["--delete"], action="store_true")
    parser.add_argument("--folder", help=LEXICON_RU["--folder"], action="store_true")
    parser.add_argument("--verbose", help=LEXICON_RU["--verbose"], action="store_true")
    parser.add_argument("--vault_path", help=LEXICON_RU["--vault_path"], default=None)
    parser.add_argument(
        "--ignore-file",
        help=(
            "Path to a gitignore-style ignore file. "
            f"Defaults to {DEFAULT_IGNORE_FILE} in the launch directory when present."
        ),
        default=None,
    )
    parser.add_argument(
        "--report",
        help="Generate export-report-{filename}.md next to the binary or main.py.",
        action="store_true",
    )
    args = parser.parse_args()

    if args.verbose:
        init_log(logging.DEBUG)
    else:
        init_log(logging.INFO)

    try:
        launch_dir = Path.cwd().resolve()
        explicit_vault_path = Path(args.vault_path).resolve() if args.vault_path else None
        if explicit_vault_path is not None and not explicit_vault_path.is_dir():
            raise NotADirectoryError(LEXICON_RU["vault_path_not_dir"])

        source_file = resolve_source_file(args.source_file, explicit_vault_path)
        vault_path = explicit_vault_path or source_file.parent
        source_file_for_search = relative_to_vault(source_file, vault_path)
        ignore_matcher, ignore_file = build_ignore_matcher(
            vault_path, launch_dir, args.ignore_file
        )
        if ignore_matcher.is_ignored(source_file_for_search):
            raise ValueError(
                f"source_file занесен в список исключений: {source_file_for_search}. "
                f"Ignore file: {ignore_file or DEFAULT_IGNORE_FILE}"
            )
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        parser.error(str(exc))

    output_path = Path(args.output).resolve()
    searcher = SearcherAllFiles(ignore_matcher=ignore_matcher)

    DirectoryWorker.pushd(vault_path)

    try:
        if Path.cwd() != vault_path:
            raise RuntimeError(LEXICON_RU["not_set_vault_path"])

        links = searcher.search_in(source_file_for_search, vault_path=vault_path)

        log = logging.getLogger(__name__)

        log.debug(default_output)
        log.debug(links)
        transfer_result = FileSetter.file_transfer(
            links,
            str(output_path),
            del_flag=args.delete,
            folder_flag=args.folder,
            ignore_matcher=ignore_matcher,
        )
    finally:
        DirectoryWorker.popd()

    if args.report:
        report_path = write_report(
            app_dir=get_app_dir(),
            output_path=output_path,
            source_file=source_file,
            source_file_for_search=source_file_for_search,
            vault_path=vault_path,
            transfer_result=transfer_result,
            missing_links=searcher.missing_links,
            ignored_files=searcher.ignored_files,
            resolved_links=searcher.resolved_links,
            delete=args.delete,
            folder=args.folder,
            ignore_file=ignore_file,
        )
        logging.getLogger(__name__).info("Report written: %s", report_path)

    print_summary(
        transfer_result,
        searcher.missing_links,
        searcher.ignored_files,
        output_path,
    )


if __name__ == "__main__":
    main()
