from __future__ import annotations
import logging
from typing import cast

from colorama import Fore, Style

DISPLAY = logging.INFO + 1
logging.addLevelName(DISPLAY, "DISPLAY")


class CustomLogger(logging.Logger):
    def display(self, message, *args, **kwargs):
        if self.isEnabledFor(DISPLAY):
            self._log(DISPLAY, message, args, **kwargs)


def get_display_logger(name: str | None) -> CustomLogger:
    """
    Get a logger that can display messages at the DISPLAY level.
    """
    logging.setLoggerClass(CustomLogger)
    return cast(CustomLogger, logging.getLogger(name))


class ColorFormatter(logging.Formatter):
    """
    A logging formatter that adds colors to log messages based on their level.
    """

    LEVEL_COLORS = {
        logging.CRITICAL: Fore.MAGENTA,
        logging.ERROR: Fore.RED,
        logging.WARNING: Fore.YELLOW,
        DISPLAY: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.DEBUG: Fore.BLUE,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        reset = Style.RESET_ALL
        record.msg = f"{color}{record.msg}{reset}"
        record.name = f"{Fore.WHITE}{record.name}{reset}"  # Add color to logger name
        return super().format(record)


def setup_logging(verbosity: int):
    """
    Configure logging based on verbosity level.
    - Default: WARNING
    - -v: INFO
    - -vv: DEBUG
    """

    level = DISPLAY
    if verbosity == 1:
        level = logging.INFO
    elif verbosity > 1:
        level = logging.DEBUG

    formatter = ColorFormatter("%(levelname)s:%(name)s: %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=level, handlers=[handler])
