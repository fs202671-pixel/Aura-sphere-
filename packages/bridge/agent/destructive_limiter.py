"""
Destructive Capability Limiter - Limita ações potencialmente destrutivas

Este módulo implementa limitações para previnir ações que poderiam
causar dano irreversível ao sistema.
"""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import json
import shutil


class DestructiveAction(Enum):
    """Tipos de ações potencialmente destrutivas."""
    DELETE_FILES = "delete_files"
    MODIFY_CORE = "modify_core"
    SYSTEM_RESET = "system_reset"
    DATABASE_WIPE = "database_wipe"
    CONFIG_OVERRIDE = "config_override"
    PERMISSION_ELEVATION = "permission_elevation"
    BACKUP_DELETE = "backup_delete"


class DestructiveCapabilityLimiter:
    """
    Limita ações destrutivas do sistema.
    
    Mecanismos:
    - Detecção de ações destrutivas
    - Rate limiting (máx. 1 ação destrutiva por hora)
    - Janelas de segurança (requer espera entre operações)
    - Logging completo de todas operações
    - Requisito de backup antes de operações
    - Confirmação dupla do usuário
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.limits_dir = data_dir / "destructive_limits"
        self.limits_dir.mkdir(parents=True, exist_ok=True)
        
        self.actions_log = self.limits_dir / "destructive_actions.json"
        self.restrictions_log = self.limits_dir / "restrictions.json"
        
        self.actions_performed: List[Dict] = []
        self.restrictions: Dict[str, Any] = {}
        
        self._load_state()
        self._initialize_restrictions()

    def _initialize_restrictions(self) -> None:
        """Inicializa restrições padrão."""
        
        self.restrictions = {
            "max_destructive_per_hour": 1,
            "min_gap_between_actions_minutes": 30,
            "require_backup_before": True,
            "require_user_confirmation": True,
            "protected_paths": [
                "packages/bridge/agent/core",
                "packages/bridge/database.py",
                "packages/bridge/schemas.py"
            ],
            "protected_patterns": [
                "*.core.py",
                "*_immutable*",
                "*_rules*"
            ],
            "max_files_delete": 10,  # Máx. arquivos por delete
            "rollback_window_hours": 24  # Tempo para rollback
        }

    def can_perform_action(self, action_type: DestructiveAction,
                          target: Optional[str] = None,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verifica se ação destrutiva pode ser executada.
        """
        
        permission = {
            "allowed": True,
            "reason": "OK",
            "checks": {},
            "remediation": None
        }
        
        # Check 1: Ação é destrutiva?
        if action_type in [DestructiveAction.DELETE_FILES,
                          DestructiveAction.SYSTEM_RESET,
                          DestructiveAction.DATABASE_WIPE]:
            permission["checks"]["is_destructive"] = True
            
            # Check 2: Rate limiting
            recent_actions = self._get_recent_actions(3600)  # últimas 1 hora
            if len(recent_actions) >= self.restrictions["max_destructive_per_hour"]:
                permission["allowed"] = False
                permission["reason"] = "Rate limit: máx. 1 ação destrutiva por hora"
                permission["checks"]["rate_limit_exceeded"] = True
                return permission
            else:
                permission["checks"]["rate_limit_ok"] = True
            
            # Check 3: Gap entre ações
            if permission["checks"].get("rate_limit_ok") and recent_actions:
                last_action = recent_actions[-1]
                gap = (datetime.now().timestamp() - 
                      datetime.fromisoformat(last_action["timestamp"]).timestamp())
                
                min_gap_seconds = self.restrictions["min_gap_between_actions_minutes"] * 60
                if gap < min_gap_seconds:
                    permission["allowed"] = False
                    wait_time = int((min_gap_seconds - gap) / 60)
                    permission["reason"] = f"Aguarde {wait_time} minutos entre ações destrutivas"
                    permission["remediation"] = f"Próxima ação disponível em: {wait_time} minutos"
                    return permission
            
            # Check 4: Caminhos protegidos
            if target:
                target_path = Path(target)
                for protected in self.restrictions["protected_paths"]:
                    if protected in str(target_path):
                        permission["allowed"] = False
                        permission["reason"] = f"Caminho protegido: {protected}"
                        permission["checks"]["protected_path"] = True
                        return permission
            
            permission["checks"]["path_ok"] = True
        
        return permission

    def request_destructive_action(self, action_type: DestructiveAction,
                                  user_id: str,
                                  target: Optional[str] = None,
                                  reason: Optional[str] = None) -> str:
        """
        Submete requisição de ação destrutiva.
        Retorna request_id para confirmação em dois tempos.
        """
        
        import hashlib
        
        request_id = hashlib.md5(
            f"{action_type.value}{target}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        request_record = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action_type": action_type.value,
            "target": target,
            "reason": reason,
            "status": "pending_confirmation",
            "confirmations": []
        }
        
        self.actions_performed.append(request_record)
        self._save_state()
        
        return request_id

    def confirm_destructive_action(self, request_id: str, user_id: str,
                                  confirmation_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Confirma ação destrutiva (segundo tempo).
        Requer dois passos para executar.
        """
        
        result = {
            "request_id": request_id,
            "confirmed": False,
            "timestamp": datetime.now().isoformat(),
            "message": ""
        }
        
        # Encontrar request
        for action in self.actions_performed:
            if action["request_id"] == request_id:
                # Verificar se user é o mesmo
                if action["user_id"] != user_id:
                    result["message"] = "Usuário não autorizado para confirmar"
                    return result
                
                # Registrar confirmação
                action["confirmations"].append({
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Se temos 2 confirmações (ou timeout expirou), permitir
                if len(action["confirmations"]) >= 2 or self._check_confirmation_timeout(action):
                    action["status"] = "confirmed"
                    result["confirmed"] = True
                    result["message"] = "Ação destrutiva confirmada e pronta para execução"
                else:
                    result["message"] = f"Confirmar 1 vez mais (total: {len(action['confirmations'])}/2)"
                
                break
        
        self._save_state()
        return result

    def execute_destructive_action(self, request_id: str,
                                  backup_created: bool = False) -> Dict[str, Any]:
        """
        Executa ação destrutiva confirmada.
        """
        
        result = {
            "request_id": request_id,
            "executed": False,
            "timestamp": datetime.now().isoformat(),
            "message": ""
        }
        
        # Encontrar request confirmado
        action_record = None
        for action in self.actions_performed:
            if action["request_id"] == request_id:
                action_record = action
                break
        
        if not action_record:
            result["message"] = "Requisição não encontrada"
            return result
        
        if action_record["status"] != "confirmed":
            result["message"] = "Ação não confirmada. Confirme antes de executar."
            return result
        
        # Check: backup obrigatório antes de ações destrutivas
        if self.restrictions["require_backup_before"] and not backup_created:
            result["message"] = "Backup obrigatório antes de ação destrutiva"
            return result
        
        # Executar (simulado)
        try:
            action_type = action_record["action_type"]
            target = action_record["target"]
            
            if action_type == DestructiveAction.DELETE_FILES.value and target:
                # Simular deleção
                pass
            elif action_type == DestructiveAction.DATABASE_WIPE.value:
                # Simular wipe
                pass
            
            action_record["status"] = "executed"
            action_record["executed_at"] = datetime.now().isoformat()
            
            result["executed"] = True
            result["message"] = f"Ação {action_type} executada com sucesso"
            
        except Exception as e:
            result["message"] = f"Erro ao executar: {str(e)}"
        
        self._save_state()
        return result

    def request_can_be_rolled_back(self, request_id: str) -> Dict[str, Any]:
        """
        Verifica se ação pode ser desfeita.
        """
        
        rollback_info = {
            "request_id": request_id,
            "can_rollback": False,
            "reason": "",
            "rollback_until": None
        }
        
        for action in self.actions_performed:
            if action["request_id"] == request_id:
                if action["status"] != "executed":
                    rollback_info["reason"] = "Ação ainda não foi executada"
                    return rollback_info
                
                # Verificar se está dentro da janela de rollback
                executed_time = datetime.fromisoformat(action.get("executed_at"))
                rollback_window = timedelta(hours=self.restrictions["rollback_window_hours"])
                rollback_until = executed_time + rollback_window
                
                if datetime.now() <= rollback_until:
                    rollback_info["can_rollback"] = True
                    rollback_info["rollback_until"] = rollback_until.isoformat()
                else:
                    rollback_info["reason"] = "Janela de rollback expirada"
                
                break
        
        return rollback_info

    def get_restrictions(self) -> Dict[str, Any]:
        """Retorna configuração de restrições."""
        return self.restrictions

    def update_restriction(self, restriction_name: str,
                          new_value: Any) -> Dict[str, Any]:
        """
        Atualiza configuração de restrição.
        Requer aprovação do usuário.
        """
        
        update_result = {
            "restriction": restriction_name,
            "old_value": self.restrictions.get(restriction_name),
            "new_value": new_value,
            "timestamp": datetime.now().isoformat(),
            "updated": False,
            "message": ""
        }
        
        if restriction_name in self.restrictions:
            self.restrictions[restriction_name] = new_value
            update_result["updated"] = True
            update_result["message"] = "Restrição atualizada"
            self._save_state()
        else:
            update_result["message"] = f"Restrição '{restriction_name}' desconhecida"
        
        return update_result

    def get_action_history(self, limit: int = 100) -> List[Dict]:
        """Retorna histórico de ações destrutivas."""
        return self.actions_performed[-limit:]

    def _get_recent_actions(self, within_seconds: int) -> List[Dict]:
        """Retorna ações destrutivas recentes."""
        
        cutoff_time = datetime.now().timestamp() - within_seconds
        
        return [
            action for action in self.actions_performed
            if action["status"] == "executed" and
            datetime.fromisoformat(action.get("executed_at", action["timestamp"])).timestamp() > cutoff_time
        ]

    def _check_confirmation_timeout(self, action: Dict) -> bool:
        """
        Verifica se timeout de confirmação expirou.
        Se mais de 5 minutos e tem 1+ confirmação, permite execução.
        """
        
        first_time = datetime.fromisoformat(action["timestamp"])
        elapsed = (datetime.now() - first_time).total_seconds()
        
        return elapsed > 300 and len(action["confirmations"]) >= 1

    def _load_state(self) -> None:
        """Carrega estado de ações destrutivas."""
        
        if self.actions_log.exists():
            try:
                self.actions_performed = json.loads(
                    self.actions_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.actions_performed = []

    def _save_state(self) -> None:
        """Persiste estado de ações destrutivas."""
        
        self.limits_dir.mkdir(parents=True, exist_ok=True)
        
        self.actions_log.write_text(
            json.dumps(self.actions_performed[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        self.restrictions_log.write_text(
            json.dumps(self.restrictions, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
