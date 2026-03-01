from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Sequence, Set

from sql_mcp_server.errors import MCPError

LOGGER = logging.getLogger("sql_mcp_server.auth")
ALL_SCOPES = frozenset({"r", "w", "a", "d"})
DEFAULT_KEYS_PATH = Path(__file__).resolve().parents[2] / "tokens.txt"


@dataclass(frozen=True)
class ApiPrincipal:
    username: str
    token: str
    scopes: Set[str]


class AuthManager:
    def __init__(self, raw_keys: str | None = None, keys_path: Path | None = None) -> None:
        self._keys_path = Path(keys_path or DEFAULT_KEYS_PATH)
        self._raw_keys = raw_keys
        self._last_mtime_ns: int | None = None
        entries = raw_keys if raw_keys is not None else self._read_keys_file()
        self._principals: Dict[str, ApiPrincipal] = self._parse_keys(entries)
        self._enabled = bool(self._principals)

    def _read_keys_file(self) -> str:
        try:
            return self._keys_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""

    def _maybe_reload_keys(self) -> None:
        if self._raw_keys is not None:
            return
        try:
            mtime_ns = self._keys_path.stat().st_mtime_ns
        except FileNotFoundError:
            mtime_ns = None
        if mtime_ns == self._last_mtime_ns:
            return
        self._last_mtime_ns = mtime_ns
        entries = self._read_keys_file()
        self._principals = self._parse_keys(entries)
        self._enabled = bool(self._principals)

    @staticmethod
    def _parse_keys(raw: str) -> Dict[str, ApiPrincipal]:
        principals: Dict[str, ApiPrincipal] = {}
        normalized = raw.replace(",", "\n")
        for chunk in normalized.splitlines():
            entry = chunk.strip()
            if not entry:
                continue
            parts = entry.split(":")
            if len(parts) != 3:
                LOGGER.warning("Invalid MCP_API_KEYS entry ignored: %s", entry)
                continue
            username, token, scopes_str = parts
            scope_set = {c.lower() for c in scopes_str if c.strip()}
            unknown = scope_set - ALL_SCOPES
            if unknown:
                LOGGER.warning(
                    "Ignoring unknown scopes for user %s: %s", username, "".join(sorted(unknown))
                )
                scope_set -= unknown
            principals[token] = ApiPrincipal(username=username, token=token, scopes=scope_set)
        return principals

    @property
    def enabled(self) -> bool:
        return self._enabled

    def authenticate(self, token: str | None) -> ApiPrincipal:
        self._maybe_reload_keys()
        if not self._enabled:
            return ApiPrincipal(username="anonymous", token="", scopes=set(ALL_SCOPES))
        if not token:
            raise MCPError(
                "Authentication required",
                hint="Provide api_key with a valid token",
                error_type="Unauthorized",
            )
        principal = self._principals.get(token)
        if not principal:
            raise MCPError(
                "Invalid API token",
                hint="Provide api_key with a valid token",
                error_type="Unauthorized",
            )
        return principal

    def require_scopes(self, principal: ApiPrincipal, required: Sequence[str]) -> None:
        if not self._enabled:
            return
        missing = {scope for scope in required if scope not in principal.scopes}
        if missing:
            raise MCPError(
                "Insufficient permissions",
                hint=f"Missing scopes: {''.join(sorted(missing))}",
                error_type="Forbidden",
            )


_auth_manager: AuthManager | None = None


def get_auth_manager() -> AuthManager:
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


def authorize(api_key: str | None, required_scopes: Sequence[str] | None = None) -> ApiPrincipal:
    manager = get_auth_manager()
    principal = manager.authenticate(api_key)
    if required_scopes:
        manager.require_scopes(principal, required_scopes)
    return principal


def ensure_scopes(principal: ApiPrincipal, scopes: Sequence[str]) -> None:
    if not scopes:
        return
    manager = get_auth_manager()
    manager.require_scopes(principal, scopes)
