from __future__ import annotations

import hashlib
import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Dict


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

LOG_LEVEL_ENV_VAR = "SQL_MCP_LOG_LEVEL"
QUERY_LOGGER_NAME = "sql_mcp_server.queries"
QUERY_LOG_ENV_VAR = "ENABLE_QUERY_LOGS"
QUERY_BODY_ENV_VAR = "LOG_QUERY_BODIES"


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


def _log_level_from_env(default: int = logging.INFO) -> int:
    raw = os.getenv(LOG_LEVEL_ENV_VAR)
    if not raw:
        return default
    candidate = raw.strip().upper()
    return getattr(logging, candidate, default)


def _secure_file(path: Path) -> None:
    try:
        path.chmod(0o600)
    except PermissionError:
        pass
    except OSError:
        pass


class _SecureTimedRotatingFileHandler(TimedRotatingFileHandler):
    def _open(self):  # type: ignore[override]
        stream = super()._open()
        _secure_file(Path(self.baseFilename))
        return stream

    def rotate(self, source, dest):  # type: ignore[override]
        super().rotate(source, dest)
        _secure_file(Path(dest))


def setup_logging(level: int | None = None) -> logging.Logger:
    logger = logging.getLogger("sql_mcp_server")
    if logger.handlers:
        return logger

    logger.setLevel(level or _log_level_from_env())

    formatter = _ExtraAppendingFormatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    file_handler = _SecureTimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(stream=sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.propagate = False

    logger.debug("Logger initialized with file handler at %s", LOG_FILE)
    return logger


def get_logger() -> logging.Logger:
    return setup_logging()


def setup_query_logging(level: int | None = None) -> logging.Logger:
    logger = logging.getLogger(QUERY_LOGGER_NAME)
    if logger.handlers:
        return logger

    enabled = _env_flag(QUERY_LOG_ENV_VAR, default=False)
    if not enabled:
        logger.addHandler(logging.NullHandler())
        logger.propagate = False
        return logger

    logger.setLevel(level or _log_level_from_env())

    formatter = _ExtraAppendingFormatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    file_handler = _SecureTimedRotatingFileHandler(
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


_QUERY_BODY_LOGGING = _env_flag(QUERY_BODY_ENV_VAR, default=False)


def render_query_logging_metadata(query: str) -> Dict[str, object]:
    digest = hashlib.sha256(query.encode("utf-8", "ignore")).hexdigest()
    metadata: Dict[str, object] = {
        "query_hash": digest,
        "query_length": len(query),
    }
    if _QUERY_BODY_LOGGING:
        metadata["query"] = query
    return metadata
