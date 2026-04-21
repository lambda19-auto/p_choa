"""
Centralized logging configuration for the project.
"""
from __future__ import annotations

import logging
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / "logi"
ALL_LOGS_PATH = LOG_DIR / "all.log"
ERROR_LOGS_PATH = LOG_DIR / "errors.log"


def setup_logging() -> None:
    """
    Configure root logger:
    - all records -> logi/all.log
    - errors only -> logi/errors.log
    """
    if logging.getLogger().handlers:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    all_handler = logging.FileHandler(ALL_LOGS_PATH, encoding="utf-8")
    all_handler.setLevel(logging.INFO)
    all_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(ERROR_LOGS_PATH, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    root_logger.addHandler(all_handler)
    root_logger.addHandler(error_handler)


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
