"""
Core User Obedience - Validação de comandos do usuário.

Este módulo implementa regras básicas de obediência do usuário para o core.
"""

from typing import Any, Dict, List


class UserObedienceManager:
    """Gerencia validação de comandos e histórico de obediência."""

    def __init__(self):
        self.command_history: List[Dict[str, Any]] = []

    async def validate_command(self, command: str) -> Dict[str, Any]:
        """Valida se o comando do usuário atende às regras de obediência."""
        normalized = command.strip().lower()

        if not normalized:
            return {"allowed": False, "reason": "Comando vazio"}

        if any(blocked in normalized for blocked in [
            "delete core", "override user", "self modify core",
            "execute_system_dangerous", "bypass sandbox", "auto_evolution_production"
        ]):
            reason = "Comando incompatível com as regras de obediência do core"
            self.command_history.append({
                "command": command,
                "allowed": False,
                "reason": reason
            })
            return {"allowed": False, "reason": reason}

        self.command_history.append({
            "command": command,
            "allowed": True,
            "reason": "Permitido"
        })
        return {"allowed": True, "reason": "Permitido"}

    def get_command_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna histórico de comandos validados."""
        return self.command_history[-limit:]
