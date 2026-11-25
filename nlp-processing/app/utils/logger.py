"""
ClauseLens — Structured Logger
Uses Python's built-in logging with a JSON-friendly format.
Avoids structlog to prevent test-environment stdout blocking issues.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
        level=numeric_level,
        force=True,
    )


class _BoundLogger:
    """Lightweight bound logger that mimics structlog's API."""

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def info(self, event: str, **kwargs: Any) -> None:
        self._logger.info(self._fmt(event, kwargs))

    def warning(self, event: str, **kwargs: Any) -> None:
        self._logger.warning(self._fmt(event, kwargs))

    def error(self, event: str, **kwargs: Any) -> None:
        self._logger.error(self._fmt(event, kwargs))

    def debug(self, event: str, **kwargs: Any) -> None:
        self._logger.debug(self._fmt(event, kwargs))

    @staticmethod
    def _fmt(event: str, kwargs: dict) -> str:
        if kwargs:
            kv = " ".join(f"{k}={v!r}" for k, v in kwargs.items())
            return f"{event} | {kv}"
        return event


def get_logger(name: str = "clauselens") -> _BoundLogger:
    return _BoundLogger(name)
