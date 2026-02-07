from __future__ import annotations

from dataclasses import dataclass

from sql_mcp_server.config import ServerConfig, load_instance_configs
from sql_mcp_server.db.base import DBClient
from sql_mcp_server.db.factory import create_db_client
from sql_mcp_server.errors import MCPError
from sql_mcp_server.middleware.sql_validator import SQLValidator


@dataclass(slots=True)
class InstanceContext:
    config: ServerConfig
    db: DBClient
    validator: SQLValidator


class InstanceRegistry:
    def __init__(self) -> None:
        self._configs = load_instance_configs()
        self._instances: dict[str, InstanceContext] = {}

    def instance_ids(self) -> list[str]:
        return sorted(self._configs.keys())

    def describe_configs(self) -> list[ServerConfig]:
        return [self._configs[instance_id] for instance_id in self.instance_ids()]

    def get(self, instance_id: str | None = None) -> InstanceContext:
        key = (instance_id or "default").lower()
        config = self._configs.get(key)
        if config is None:
            raise MCPError(
                f"Unknown database instance: {key}",
                hint=(
                    "Provide a valid instance_id. Available instances: "
                    + ", ".join(self.instance_ids() or ["default"])
                ),
                error_type="UnknownInstance",
            )

        if key not in self._instances:
            self._instances[key] = InstanceContext(
                config=config,
                db=create_db_client(config),
                validator=SQLValidator(config),
            )
        return self._instances[key]


_registry: InstanceRegistry | None = None


def get_instance_registry() -> InstanceRegistry:
    global _registry
    if _registry is None:
        _registry = InstanceRegistry()
    return _registry
