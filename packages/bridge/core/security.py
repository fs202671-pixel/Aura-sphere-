"""
Segurança do Core - Gerenciamento de permissões e acesso.

Este módulo expõe um SecurityManager leve que protege o acesso a
recursos do repositório e traduz regras do core para camadas de agentes.
"""

from typing import Any, Dict
from . import SecurityEnforcer, PermissionLevels


class SecurityManager:
    """Gerenciador de acesso e validação de permissões."""

    def __init__(self, user_id: str = "system"):
        self.user_id = user_id
        self.session_permissions: Dict[str, int] = {}

    async def validate_access(self, path: str, mode: str) -> bool:
        """Valida se o acesso ao caminho e modo solicitado é permitido."""
        normalized_path = path.replace("\\", "/")

        # Bloquear caminhos fora do repositório ou sensíveis
        forbidden_patterns = ["../", "/etc/", "/proc/", "/dev/", "~/"]
        if any(pattern in normalized_path for pattern in forbidden_patterns):
            SecurityEnforcer.log_security_event(
                "access_denied",
                {"user_id": self.user_id, "path": path, "mode": mode}
            )
            return False

        if mode not in {"read", "write", "execute"}:
            return False

        # Leitura básica é permitida, mas escrita/executação devem ser avaliadas
        if mode == "read":
            return True

        if mode in {"write", "execute"}:
            # Apenas permitir execução se o core não estiver protegido e se não houver ação proibida
            return SecurityEnforcer.check_action_allowed(
                f"{mode}_{normalized_path}",
                PermissionLevels.LEVEL_2_EXECUTE_CONFIRMED
            )

        return False

    def check_action_allowed(self, action: str, permission_level: int) -> bool:
        """Verifica se uma ação é permitida de acordo com o core."""
        return SecurityEnforcer.check_action_allowed(action, permission_level)

    def log_security_event(self, event: str, details: Dict[str, Any]) -> None:
        """Registra evento de segurança no core."""
        SecurityEnforcer.log_security_event(event, details)
