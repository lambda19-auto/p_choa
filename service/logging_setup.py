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
    Configure root logger:
    - all records -> logs/all.log
    - errors only -> logs/errors.log
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    if root_logger.level > logging.INFO:
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
    setup_logging()
    return logging.getLogger(name)
