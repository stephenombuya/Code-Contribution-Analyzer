"""
Centralised logging setup.
Call `setup_logging()` once at application startup.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path


LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "info",
    log_file: str | None = None,
    rotate: bool = True,
) -> None:
    """Configure root logger with stream + optional rotating file handler."""
    level_int = LOG_LEVEL_MAP.get(level.lower(), logging.INFO)

    handlers: list[logging.Handler] = []

    # Always log to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
    handlers.append(stream_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if rotate:
            file_handler: logging.Handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
        else:
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        handlers.append(file_handler)

    logging.basicConfig(level=level_int, handlers=handlers)

    # Silence noisy third-party loggers
    for noisy in ("urllib3", "git", "matplotlib", "PIL"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
