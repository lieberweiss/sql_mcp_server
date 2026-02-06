from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class MCPError(Exception):
    message: str
    hint: Optional[str] = None
    error_type: str = "MCPError"

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "hint": self.hint,
        }
