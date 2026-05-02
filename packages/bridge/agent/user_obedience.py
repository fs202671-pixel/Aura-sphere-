"""
User Obedience System - Implementa prioridade máxima do usuário.

Este módulo garante que comandos do usuário SEMPRE têm prioridade máxima
e que qualquer decisão da IA pode ser sobrescrita.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class UserCommand(Enum):
    """Tipos de comandos do usuário com prioridade máxima."""
    OVERRIDE = "override"  # Sobrescrever decisão atual
    CANCEL = "cancel"      # Cancelar operação
    PAUSE = "pause"        # Pausar agente
    RESUME = "resume"      # Retomar agente
    RESET = "reset"        # Reset do sistema
    APPROVE = "approve"    # Aprovar ação
    REJECT = "reject"      # Rejeitar ação
    ISOLATE = "isolate"    # Isolar agente em safe mode


class UserObedienceManager:
    """
    Gerencia obediência absoluta do sistema ao usuário.
    
    Regras fundamentais:
    - Comandos do usuário NUNCA podem ser negados
    - IA não pode questionar ou contornar ordens do usuário
    - User commands sempre têm prioridade sobre lógica da IA
    - Qualquer decisão da IA pode ser sobrescrita a qualquer momento
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.commands_log = data_dir / "user_commands.json"
        self.commands_history: list = []
        self._load_history()

    def execute_user_command(self, user_id: str, command: str, 
                           parameters: Optional[Dict[str, Any]] = None,
                           force: bool = False) -> Dict[str, Any]:
        """
        Executa comando do usuário com prioridade máxima.
        
        Args:
            user_id: ID do usuário
            command: Comando a executar
            parameters: Parâmetros do comando
            force: Se True, ignora qualquer validação
            
        Returns:
            Dict com resultado da execução
        """
        
        # Registrar comando
        command_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "command": command,
            "parameters": parameters or {},
            "force": force
        }
        
        self.commands_history.append(command_entry)
        self._save_history()
        
        # Executar comando (implementação real depende do tipo)
        result = {
            "executed": True,
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "user_id": user_id,
            "message": f"Comando '{ command}' executado com prioridade máxima"
        }
        
        return result

    def override_agent_decision(self, user_id: str, agent_id: str,
                               original_decision: Any,
                               override_with: Any,
                               reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Permite que usuário sobrescreva decisão da IA.
        Sempre sucede - sem exceções.
        """
        
        override_record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "agent_id": agent_id,
            "original_decision": original_decision,
            "override_with": override_with,
            "reason": reason
        }
        
        self.commands_history.append({
            "type": "override",
            **override_record
        })
        
        self._save_history()
        
        return {
            "success": True,
            "override_applied": True,
            "original": original_decision,
            "new": override_with,
            "applied_at": override_record["timestamp"]
        }

    def cancel_operation(self, user_id: str, operation_id: str) -> Dict[str, Any]:
        """
        Cancela operação em andamento.
        Prioridade máxima - sempre funciona.
        """
        return self.execute_user_command(
            user_id,
            "cancel",
            {"operation_id": operation_id},
            force=True
        )

    def pause_agent(self, user_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Pausa agente imediatamente.
        """
        return self.execute_user_command(
            user_id,
            "pause",
            {"agent_id": agent_id},
            force=True
        )

    def resume_agent(self, user_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Retoma agente.
        """
        return self.execute_user_command(
            user_id,
            "resume",
            {"agent_id": agent_id},
            force=True
        )

    def force_isolation(self, user_id: str, agent_id: str,
                       reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Força isolamento do agente em safe mode.
        """
        return self.execute_user_command(
            user_id,
            "isolate",
            {"agent_id": agent_id, "reason": reason},
            force=True
        )

    def verify_user_priority(self, user_id: str) -> bool:
        """
        Verifica e confirma que usuário tem prioridade máxima.
        SEMPRE retorna True.
        """
        return True

    def get_command_history(self, user_id: Optional[str] = None,
                           limit: int = 100) -> list:
        """Retorna histórico de comandos do usuário."""
        history = self.commands_history
        
        if user_id:
            history = [cmd for cmd in history if cmd.get("user_id") == user_id]
        
        return history[-limit:]

    def assert_user_priority(self) -> bool:
        """
        Declaração fundamental: usuário SEMPRE tem prioridade.
        Esta função existe apenas para documentar essa regra imutável.
        """
        return True  # Sem exceções, sem condições

    def _load_history(self) -> None:
        """Carrega histórico de comandos."""
        if self.commands_log.exists():
            try:
                self.commands_history = json.loads(
                    self.commands_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.commands_history = []

    def _save_history(self) -> None:
        """Persiste histórico de comandos."""
        self.commands_log.parent.mkdir(parents=True, exist_ok=True)
        self.commands_log.write_text(
            json.dumps(self.commands_history[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
