"""Módulo de segurança do core do agente."""

from typing import Dict, Any

class SecurityManager:
    """Gerencia regras de segurança para componentes de agente."""

    def __init__(self) -> None:
        self.rules = {
            "allow_external_execution": False,
            "allow_data_exfiltration": False,
            "allow_remote_control": False,
        }

    def is_action_allowed(self, action: str, context: Dict[str, Any] | None = None) -> bool:
        if action == "read_only":
            return True
        return self.rules.get(action, False)

    def set_rule(self, action: str, allowed: bool) -> None:
        self.rules[action] = allowed
