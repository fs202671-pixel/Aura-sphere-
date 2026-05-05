"""
Permission System - Sistema de Permissões Hierárquicas

Implementa controle de acesso baseado em níveis de confiança e responsabilidade.
"""

from typing import Dict, List, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

class PermissionLevel(Enum):
    """Níveis de permissão do sistema"""
    LEVEL_0_READ_ONLY = 0        # Apenas leitura e análise
    LEVEL_1_SUGGEST = 1          # Pode sugerir ações
    LEVEL_2_EXECUTE_CONFIRMED = 2  # Executa com confirmação do usuário
    LEVEL_3_SANDBOX_EVOLUTION = 3  # Auto-evolução em sandbox
    LEVEL_4_PRODUCTION_EVOLUTION = 4  # Auto-evolução em produção (MÁXIMO - NUNCA USAR)

@dataclass
class PermissionGrant:
    """Concessão de permissão temporária"""
    level: PermissionLevel
    granted_by: str  # Quem concedeu
    granted_at: datetime
    expires_at: Optional[datetime]
    reason: str
    scope: List[str]  # Áreas permitidas

@dataclass
class UserSession:
    """Sessão do usuário com permissões"""
    user_id: str
    current_level: PermissionLevel
    permissions: List[PermissionGrant]
    session_start: datetime
    last_activity: datetime

class PermissionManager:
    """Gerenciador central de permissões"""

    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def create_session(self, user_id: str) -> UserSession:
        """Cria uma nova sessão com nível mínimo de permissão"""
        session = UserSession(
            user_id=user_id,
            current_level=PermissionLevel.LEVEL_0_READ_ONLY,
            permissions=[],
            session_start=datetime.now(),
            last_activity=datetime.now()
        )
        self.sessions[user_id] = session
        self._audit("session_created", {"user_id": user_id})
        return session

    def grant_permission(self, user_id: str, level: PermissionLevel,
                        granted_by: str, reason: str,
                        duration_minutes: Optional[int] = None,
                        scope: Optional[List[str]] = None) -> bool:
        """
        Concede permissão temporária a um usuário

        Args:
            user_id: ID do usuário
            level: Nível de permissão a conceder
            granted_by: Quem está concedendo
            reason: Motivo da concessão
            duration_minutes: Duração em minutos (None = permanente na sessão)
            scope: Escopo das permissões (None = todas as áreas)
        """

        if user_id not in self.sessions:
            return False

        expires_at = None
        if duration_minutes:
            expires_at = datetime.now() + timedelta(minutes=duration_minutes)

        grant = PermissionGrant(
            level=level,
            granted_by=granted_by,
            granted_at=datetime.now(),
            expires_at=expires_at,
            reason=reason,
            scope=scope or ["*"]  # * = todas as áreas
        )

        session = self.sessions[user_id]
        session.permissions.append(grant)

        # Atualizar nível atual se for maior
        if level.value > session.current_level.value:
            session.current_level = level

        self._audit("permission_granted", {
            "user_id": user_id,
            "level": level.value,
            "granted_by": granted_by,
            "reason": reason,
            "expires": expires_at.isoformat() if expires_at else None
        })

        return True

    def check_permission(self, user_id: str, required_level: PermissionLevel,
                        action: str, scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Verifica se um usuário tem permissão para uma ação

        Returns:
            Dict com resultado da verificação
        """

        if user_id not in self.sessions:
            return {
                "allowed": False,
                "reason": "Sessão não encontrada",
                "current_level": None
            }

        session = self.sessions[user_id]

        # Atualizar atividade
        session.last_activity = datetime.now()

        # Verificar expiração de permissões
        self._cleanup_expired_permissions(user_id)

        # Verificar nível
        current_level = session.current_level.value
        required = required_level.value

        if current_level < required:
            return {
                "allowed": False,
                "reason": f"Nível insuficiente: {current_level} < {required}",
                "current_level": current_level,
                "required_level": required
            }

        # Verificar escopo se especificado
        if scope:
            allowed_scopes = []
            for grant in session.permissions:
                if grant.level.value >= required_level.value:
                    allowed_scopes.extend(grant.scope)

            if "*" not in allowed_scopes and scope not in allowed_scopes:
                return {
                    "allowed": False,
                    "reason": f"Escopo não permitido: {scope}",
                    "current_level": current_level,
                    "allowed_scopes": list(set(allowed_scopes))
                }

        self._audit("permission_check", {
            "user_id": user_id,
            "action": action,
            "level": current_level,
            "result": "allowed"
        })

        return {
            "allowed": True,
            "current_level": current_level,
            "granted_permissions": len(session.permissions)
        }

    def revoke_permission(self, user_id: str, level: PermissionLevel,
                         revoked_by: str, reason: str) -> bool:
        """Revoga uma permissão específica"""

        if user_id not in self.sessions:
            return False

        session = self.sessions[user_id]

        # Remover permissões do nível especificado
        original_count = len(session.permissions)
        session.permissions = [
            p for p in session.permissions
            if p.level != level
        ]

        # Recalcular nível atual
        if session.permissions:
            max_level = max(p.level.value for p in session.permissions)
            session.current_level = PermissionLevel(max_level)
        else:
            session.current_level = PermissionLevel.LEVEL_0_READ_ONLY

        removed = original_count - len(session.permissions)

        self._audit("permission_revoked", {
            "user_id": user_id,
            "level": level.value,
            "revoked_by": revoked_by,
            "reason": reason,
            "permissions_removed": removed
        })

        return removed > 0

    def get_user_level(self, user_id: str) -> PermissionLevel:
        """Retorna o nível de permissão atual do usuário."""
        if user_id not in self.sessions:
            return PermissionLevel.LEVEL_0_READ_ONLY
        return self.sessions[user_id].current_level

    def _cleanup_expired_permissions(self, user_id: str) -> None:
        """Remove permissões expiradas"""
        if user_id not in self.sessions:
            return

        session = self.sessions[user_id]
        now = datetime.now()

        original_count = len(session.permissions)
        session.permissions = [
            p for p in session.permissions
            if p.expires_at is None or p.expires_at > now
        ]

        removed = original_count - len(session.permissions)
        if removed > 0:
            # Recalcular nível se permissões expiraram
            if session.permissions:
                max_level = max(p.level.value for p in session.permissions)
                session.current_level = PermissionLevel(max_level)
            else:
                session.current_level = PermissionLevel.LEVEL_0_READ_ONLY

            self._audit("expired_permissions_cleaned", {
                "user_id": user_id,
                "removed": removed
            })

    def _audit(self, event: str, details: Dict[str, Any]) -> None:
        """Registra evento no audit log"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "details": details
        }
        self.audit_log.append(audit_entry)

        # Manter apenas últimas 1000 entradas
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def get_audit_log(self, user_id: Optional[str] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna log de auditoria"""
        log = self.audit_log
        if user_id:
            log = [entry for entry in log if entry["details"].get("user_id") == user_id]

        return log[-limit:]

    def get_session_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retorna informações da sessão"""
        if user_id not in self.sessions:
            return None

        session = self.sessions[user_id]
        return {
            "user_id": session.user_id,
            "current_level": session.current_level.value,
            "level_description": session.current_level.name,
            "permissions_count": len(session.permissions),
            "session_start": session.session_start.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "active_permissions": [
                {
                    "level": p.level.value,
                    "granted_by": p.granted_by,
                    "granted_at": p.granted_at.isoformat(),
                    "expires_at": p.expires_at.isoformat() if p.expires_at else None,
                    "reason": p.reason,
                    "scope": p.scope
                }
                for p in session.permissions
            ]
        }

# ========== INSTÂNCIA GLOBAL ==========

permission_manager = PermissionManager()

# ========== FUNÇÕES DE CONVENIÊNCIA ==========

def require_permission(user_id: str, level: PermissionLevel, action: str,
                      scope: Optional[str] = None) -> bool:
    """Decorator para verificar permissão antes de executar ação"""
    result = permission_manager.check_permission(user_id, level, action, scope)
    return result["allowed"]

def grant_user_permission(user_id: str, level: PermissionLevel,
                         reason: str, duration_minutes: Optional[int] = None) -> bool:
    """Concede permissão ao usuário (apenas para testes/simulação)"""
    return permission_manager.grant_permission(
        user_id=user_id,
        level=level,
        granted_by="system",
        reason=reason,
        duration_minutes=duration_minutes
    )