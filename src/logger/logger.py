import logging
import sys


class ColorFormatter(logging.Formatter):
    RESET = "\x1b[0m"

    COLORS = {
        logging.DEBUG: "\x1b[38;5;245m",  # серый
        logging.INFO: "\x1b[38;5;39m",  # синий
        logging.WARNING: "\x1b[38;5;214m",  # оранжевый
        logging.ERROR: "\x1b[38;5;196m",  # красный
        logging.CRITICAL: "\x1b[1;38;5;196m",  # жирный красный
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        record.name = f"\x1b[38;5;81m{record.name}{self.RESET}"
        record.filename = f"\x1b[38;5;110m{record.filename}{self.RESET}"

        return super().format(record)


def init_log(level: int):
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()

    # === СТАРЫЙ ФОРМАТ (как у тебя) ===
    file_format = (
        "[%(asctime)s] #%(levelname)-8s "
        "%(filename)s:%(lineno)d - %(name)s - %(message)s"
    )

    # === КОНСОЛЬ (тот же формат, но с цветами) ===
    console_format = (
        "[%(asctime)s] #%(levelname)-8s "
        "%(filename)s:%(lineno)s - %(name)s - %(message)s"
    )

    # ===== FILE =====
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(file_format))

    # ===== CONSOLE =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColorFormatter(console_format))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
