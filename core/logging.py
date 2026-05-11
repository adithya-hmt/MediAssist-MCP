"""Central logging helpers for the project."""

from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    """Set up a clean, console-friendly logging format."""

    level_name = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module logger."""

    return logging.getLogger(name)

