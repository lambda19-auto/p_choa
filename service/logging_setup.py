"""
Centralized logging configuration for the project.
"""
from __future__ import annotations

import logging
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
ALL_LOGS_PATH = LOG_DIR / "all.log"
ERROR_LOGS_PATH = LOG_DIR / "errors.log"


def setup_logging() -> None:
    """
    Configure root logger file handlers:
    - INFO+ records -> logs/all.log
    - ERROR+ records -> logs/errors.log

    By default, Python root logger starts at WARNING. When no handlers are
    configured yet and the level is still default WARNING, raise it to INFO so
    logs/all.log receives INFO records. Explicitly configured stricter levels
    (e.g. ERROR) are preserved.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    if root_logger.level == logging.WARNING and not root_logger.handlers:
        root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    existing_file_targets = {
        Path(getattr(handler, "baseFilename")).resolve()
        for handler in root_logger.handlers
        if hasattr(handler, "baseFilename")
    }

    if ALL_LOGS_PATH.resolve() not in existing_file_targets:
        all_handler = logging.FileHandler(ALL_LOGS_PATH, encoding="utf-8")
        all_handler.setLevel(logging.INFO)
        all_handler.setFormatter(formatter)
        root_logger.addHandler(all_handler)

    if ERROR_LOGS_PATH.resolve() not in existing_file_targets:
        error_handler = logging.FileHandler(ERROR_LOGS_PATH, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
