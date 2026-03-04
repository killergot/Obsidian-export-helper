import argparse
import logging
import os
from pathlib import Path

from src.FileClasses.DirectoryWorker import DirectoryWorker
from src.FileClasses.FileSetter import FileSetter
from src.FileClasses.Searcher import SearcherAllFiles
from src.lexicon.lexicon import LEXICON_RU
from src.logger.logger import init_log

if __name__ == "__main__":
    os.makedirs("./output", exist_ok=True)
    parser = argparse.ArgumentParser(description=LEXICON_RU["/help"])
    parser.add_argument("source_file", help=LEXICON_RU["source_file"])

    # folder in this project
    default_output = Path(__file__).resolve().parent.joinpath("output")

    parser.add_argument(
        "-o", "--output", help=LEXICON_RU["--output"], default=default_output
    )
    parser.add_argument("--delete", help=LEXICON_RU["--delete"], action="store_true")
    parser.add_argument("--folder", help=LEXICON_RU["--folder"], action="store_true")
    parser.add_argument("--verbose", help=LEXICON_RU["--verbose"], action="store_true")
    parser.add_argument("--main_path", help=LEXICON_RU["--main_path"], default=None)
    args = parser.parse_args()

    if args.verbose:
        init_log(logging.DEBUG)
    else:
        init_log(logging.INFO)

    searcher = SearcherAllFiles()

    if args.main_path is None:
        main_path = Path(args.source_file).resolve().parent
    else:
        main_path = Path(args.main_path)

    assert main_path.is_dir(), LEXICON_RU["main_path_not_dir"]
    DirectoryWorker.pushd(main_path)
    assert Path.cwd() == main_path, LEXICON_RU["not_set_main_path"]

    links = searcher.searchIn(Path(args.source_file))

    log = logging.getLogger(__name__)

    log.debug(default_output)
    log.debug(links)
    FileSetter.file_transfer(
        links, args.output, del_flag=args.delete, folder_flag=args.folder
    )
    DirectoryWorker.popd()
    print(LEXICON_RU["OK"])
