from __future__ import annotations

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class _ExtraAppendingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        extras = self._extract_extras(record)
        if not extras:
            return message
        rendered = " ".join(f"{k}={extras[k]!r}" for k in sorted(extras))
        return f"{message} | {rendered}"

    @staticmethod
    def _extract_extras(record: logging.LogRecord) -> dict[str, object]:
        reserved = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }
        return {k: v for k, v in record.__dict__.items() if k not in reserved}

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "server.log"
QUERIES_LOG_FILE = LOG_DIR / "queries.log"

QUERY_LOGGER_NAME = "sql_mcp_server.queries"
QUERY_LOG_ENV_VAR = "ENABLE_QUERY_LOGS"


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("sql_mcp_server")
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = _ExtraAppendingFormatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    file_handler = TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.propagate = False

    logger.debug("Logger initialized with file handler at %s", LOG_FILE)
    return logger


def get_logger() -> logging.Logger:
    return setup_logging()


def setup_query_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(QUERY_LOGGER_NAME)
    if logger.handlers:
        return logger

    enabled = _env_flag(QUERY_LOG_ENV_VAR, default=False)
    if not enabled:
        logger.addHandler(logging.NullHandler())
        logger.propagate = False
        return logger

    logger.setLevel(level)

    formatter = _ExtraAppendingFormatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    file_handler = TimedRotatingFileHandler(
        QUERIES_LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    logger.debug("Query logger initialized with file handler at %s", QUERIES_LOG_FILE)
    return logger


def get_query_logger() -> logging.Logger:
    return setup_query_logging()
