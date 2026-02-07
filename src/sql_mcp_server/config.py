from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ServerConfig:
    instance_id: str
    provider: str
    host: str | None
    port: int | None
    user: str | None
    password: str | None
    database: str | None
    sqlite_path: str
    read_only: bool
    max_rows: int
    query_timeout: int
    statement_timeout_ms: int
    allowed_tables: set[str]
    server_name: str
    mssql_odbc_driver: str | None
    mssql_trust_server_certificate: bool

    @property
    def statement_timeout_seconds(self) -> int | None:
        if self.statement_timeout_ms <= 0:
            return None
        return max((self.statement_timeout_ms + 999) // 1000, 1)


def load_config(
    *,
    prefix: str | None = None,
    env: Mapping[str, str] | None = None,
    instance_id: str | None = None,
) -> ServerConfig:
    """Load a server configuration from environment variables.

    Args:
        prefix: Optional prefix applied to every environment key. This allows
            loading multiple logical instances from the same environment
            (e.g. `CRM_DB_PROVIDER`).
        env: Optional mapping overriding the OS environment. Provide a plain
            dict here to programmatically instantiate multiple instances with
            distinct settings inside the same process.
    """

    source = dict(os.environ)
    if env:
        # Explicit overrides take precedence.
        source.update(env)

    def _key(name: str) -> str:
        return f"{prefix}{name}" if prefix else name

    def _get(name: str, default: str | None = None) -> str | None:
        return source.get(_key(name), default)

    def _get_int(name: str, default: int) -> int:
        raw = _get(name)
        if raw is None or raw == "":
            return default
        return int(raw)

    def _get_bool(name: str, default: bool) -> bool:
        raw = _get(name)
        if raw is None or raw == "":
            return default
        return raw.lower() == "true"

    provider = (_get("DB_PROVIDER", "sqlite") or "sqlite").lower()
    resolved_instance_id = instance_id or (
        prefix[:-1].lower() if prefix and prefix.endswith("_") else prefix or "default"
    )
    if not resolved_instance_id:
        resolved_instance_id = "default"
    allowed_tables = {
        t.strip().lower()
        for t in (_get("DB_ALLOWED_TABLES", "") or "").split(",")
        if t.strip()
    }
    query_timeout = _get_int("DB_QUERY_TIMEOUT", 10)
    statement_timeout_ms = _get_int("DB_STATEMENT_TIMEOUT_MS", query_timeout * 1000)

    return ServerConfig(
        instance_id=resolved_instance_id,
        provider=provider,
        host=_get("DB_HOST"),
        port=_get_int("DB_PORT", 0) or None,
        user=_get("DB_USER"),
        password=_get("DB_PASSWORD"),
        database=_get("DB_DATABASE"),
        sqlite_path=_get("SQLITE_PATH", "./database.db") or "./database.db",
        read_only=_get_bool("DB_READ_ONLY", True),
        max_rows=_get_int("DB_MAX_ROWS", 100),
        query_timeout=query_timeout,
        statement_timeout_ms=statement_timeout_ms,
        allowed_tables=allowed_tables,
        server_name=_get("MCP_SERVER_NAME", "sql-mcp-server") or "sql-mcp-server",
        mssql_odbc_driver=_get("DB_MSSQL_ODBC_DRIVER"),
        mssql_trust_server_certificate=_get_bool(
            "DB_MSSQL_TRUST_SERVER_CERTIFICATE", False
        ),
    )


# Backwards compatibility for code that still imports module-level constants.
# New code should call `load_config()` directly.
DEFAULT_CONFIG = load_config()


def load_instance_configs() -> dict[str, ServerConfig]:
    """Return all configured instances.

    The optional `MCP_INSTANCES` environment variable accepts a comma-separated
    list of prefixes. For example, `MCP_INSTANCES=CRM,ERP` will look for
    `CRM_DB_PROVIDER`, `ERP_DB_PROVIDER`, etc. When not provided, this function
    returns a single `default` instance built from the un-prefixed environment.
    """

    raw_instances = os.getenv("MCP_INSTANCES", "")
    if not raw_instances.strip():
        cfg = load_config()
        return {cfg.instance_id: cfg}

    configs: dict[str, ServerConfig] = {}
    for chunk in raw_instances.split(","):
        slug = chunk.strip()
        if not slug:
            continue
        prefix = f"{slug.upper()}_"
        cfg = load_config(prefix=prefix, instance_id=slug.lower() or slug)
        configs[cfg.instance_id] = cfg

    if not configs:
        cfg = load_config()
        configs[cfg.instance_id] = cfg

    return configs
