from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DBClient(ABC):
    @abstractmethod
    def execute(self, query: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def list_tables(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def describe_table(self, table: str) -> list[dict[str, Any]]:
        raise NotImplementedError
