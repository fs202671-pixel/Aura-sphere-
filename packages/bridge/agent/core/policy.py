"""Gerenciamento de políticas internas do agente."""

from typing import Dict, Any

class PolicyManager:
    """Gerencia políticas de execução e bloqueios do agente."""

    def __init__(self) -> None:
        self.policies: Dict[str, Any] = {
            "max_pending_tasks": 20,
            "block_unsafe_actions": True,
            "safe_mode": True,
        }

    def get_policy(self, key: str, default: Any = None) -> Any:
        return self.policies.get(key, default)

    def set_policy(self, key: str, value: Any) -> None:
        self.policies[key] = value
