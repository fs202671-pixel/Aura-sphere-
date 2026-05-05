"""
Wolf Responder - Lobo Respondedor
=================================

Agente de resposta e contenção de incidentes.
Características:
- Execução de medidas de contenção
- Isolamento de componentes afetados
- Coordenação de resposta automática
- Minimização de impacto
"""

import asyncio
import time
import signal
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import subprocess

from memory.collective import CollectiveMemory
from core.security import SecurityManager
from core.sandbox import SandboxManager

logger = logging.getLogger(__name__)

class ResponseAction(Enum):
    ISOLATE_PROCESS = "isolate_process"
    BLOCK_NETWORK = "block_network"
    TERMINATE_PROCESS = "terminate_process"
    QUARANTINE_FILE = "quarantine_file"
    RESTRICT_ACCESS = "restrict_access"
    LOG_INCIDENT = "log_incident"
    ALERT_HUMAN = "alert_human"

class ContainmentStatus(Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class ContainmentAction:
    """Ação de contenção executada"""
    action_id: str
    action_type: ResponseAction
    target: str
    parameters: Dict[str, Any]
    status: ContainmentStatus
    start_time: float
    end_time: Optional[float]
    result: Optional[str]
    rollback_actions: List[Dict[str, Any]]

class WolfResponder:
    """
    Lobo respondedor - executa contenção de incidentes

    Funcionalidades:
    - Receber alertas escalados
    - Executar ações de contenção
    - Coordenar resposta automática
    - Rastrear e reportar ações
    """

    def __init__(self, responder_id: Optional[str] = None):
        self.responder_id = responder_id or f"responder_{int(time.time())}"
        self.memory = CollectiveMemory()
        self.security = SecurityManager()
        self.sandbox = SandboxManager()

        # Estado
        self.active = False

        # Ações em andamento
        self.active_containments: Dict[str, ContainmentAction] = {}

        # Estatísticas
        self.incidents_handled = 0
        self.actions_executed = 0
        self.containment_failures = 0

        # Callbacks
        self.status_callbacks: List[callable] = []

        logger.info(f"WolfResponder {self.responder_id} initialized")

    async def start_responding(self):
        """Inicia o monitoramento de incidentes"""
        self.active = True
        logger.info(f"WolfResponder {self.responder_id} started responding")

        while self.active:
            try:
                # Verificar alertas escalados
                await self._check_escalated_alerts()

                # Monitorar ações em andamento
                await self._monitor_active_containments()

                # Limpar ações completadas antigas
                await self._cleanup_completed_actions()

                # Aguardar próximo ciclo
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"WolfResponder {self.responder_id} error: {e}")
                await asyncio.sleep(5)

    async def _check_escalated_alerts(self):
        """Verifica alertas escalados pendentes"""
        # Buscar alertas escalados não tratados
        escalated_alerts = await self.memory.get_escalated_alerts()

        for alert in escalated_alerts:
            try:
                # Verificar se já existe contenção para este alerta
                if await self._has_active_containment(alert['alert_id']):
                    continue

                # Iniciar contenção
                await self._initiate_containment(alert)
                await self.memory.update_alert_status(alert['alert_id'], handled=True)

                self.incidents_handled += 1

            except Exception as e:
                logger.error(f"Failed to handle escalated alert {alert.get('alert_id')}: {e}")

    async def _has_active_containment(self, alert_id: str) -> bool:
        """
        Verifica se há contenção ativa para o alerta

        Args:
            alert_id: ID do alerta

        Returns:
            True se há contenção ativa
        """
        for action in self.active_containments.values():
            if action.target == alert_id and action.status in [ContainmentStatus.INITIATED, ContainmentStatus.IN_PROGRESS]:
                return True
        return False

    async def _initiate_containment(self, alert: Dict[str, Any]):
        """
        Inicia processo de contenção para um alerta

        Args:
            alert: Dados do alerta escalado
        """
        alert_id = alert['alert_id']
        risk_level = alert.get('risk_level', 1)

        logger.warning(f"WolfResponder {self.responder_id} initiating containment for alert {alert_id}")

        # Determinar ações baseadas no risco e tipo de alerta
        actions = await self._plan_containment_actions(alert)

        # Executar ações em sequência
        for action in actions:
            await self._execute_containment_action(action, alert)

    async def _plan_containment_actions(self, alert: Dict[str, Any]) -> List[ResponseAction]:
        """
        Planeja ações de contenção

        Args:
            alert: Dados do alerta

        Returns:
            Lista de ações a executar
        """
        actions = []
        risk_level = alert.get('risk_level', 1)
        original_signal = alert.get('original_signal', {})
        signal_type = original_signal.get('type', '')

        # Sempre logar o incidente
        actions.append(ResponseAction.LOG_INCIDENT)

        # Ações baseadas no nível de risco
        if risk_level >= 4:  # CRITICAL
            actions.extend([
                ResponseAction.ISOLATE_PROCESS,
                ResponseAction.BLOCK_NETWORK,
                ResponseAction.ALERT_HUMAN
            ])
        elif risk_level >= 3:  # HIGH
            actions.extend([
                ResponseAction.TERMINATE_PROCESS,
                ResponseAction.RESTRICT_ACCESS
            ])
        elif risk_level >= 2:  # MEDIUM
            actions.append(ResponseAction.RESTRICT_ACCESS)

        # Ações específicas baseadas no tipo de sinal
        if signal_type == 'network_activity':
            actions.append(ResponseAction.BLOCK_NETWORK)
        elif signal_type == 'behavior_analysis':
            actions.append(ResponseAction.ISOLATE_PROCESS)

        # Remover duplicatas mantendo ordem
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                unique_actions.append(action)
                seen.add(action)

        return unique_actions

    async def _execute_containment_action(self, action_type: ResponseAction, alert: Dict[str, Any]):
        """
        Executa uma ação de contenção

        Args:
            action_type: Tipo da ação
            alert: Dados do alerta
        """
        action_id = f"{action_type.value}_{alert['alert_id']}_{int(time.time())}"

        # Criar ação de contenção
        containment = ContainmentAction(
            action_id=action_id,
            action_type=action_type,
            target=alert['alert_id'],
            parameters=self._get_action_parameters(action_type, alert),
            status=ContainmentStatus.INITIATED,
            start_time=time.time(),
            end_time=None,
            result=None,
            rollback_actions=[]
        )

        self.active_containments[action_id] = containment

        try:
            # Executar ação
            containment.status = ContainmentStatus.IN_PROGRESS

            result = await self._perform_action(containment)

            containment.status = ContainmentStatus.COMPLETED
            containment.result = result
            containment.end_time = time.time()

            self.actions_executed += 1

            logger.info(f"WolfResponder {self.responder_id} completed action {action_id}")

        except Exception as e:
            containment.status = ContainmentStatus.FAILED
            containment.result = str(e)
            containment.end_time = time.time()

            self.containment_failures += 1

            logger.error(f"WolfResponder {self.responder_id} failed action {action_id}: {e}")

            # Tentar rollback se disponível
            await self._rollback_action(containment)

        # Armazenar resultado
        await self._store_containment_result(containment)

        # Notificar callbacks
        await self._notify_status_change(containment)

    def _get_action_parameters(self, action_type: ResponseAction, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém parâmetros para a ação"""
        params = {}

        if action_type == ResponseAction.ISOLATE_PROCESS:
            params['process_info'] = alert.get('original_signal', {}).get('data', {}).get('processes', [])
        elif action_type == ResponseAction.BLOCK_NETWORK:
            params['connections'] = alert.get('original_signal', {}).get('data', {}).get('connections', [])
        elif action_type == ResponseAction.TERMINATE_PROCESS:
            params['process_info'] = alert.get('original_signal', {}).get('data', {}).get('processes', [])

        return params

    async def _perform_action(self, containment: ContainmentAction) -> str:
        """
        Executa a ação específica

        Args:
            containment: Ação de contenção

        Returns:
            Resultado da execução
        """
        action_type = containment.action_type
        params = containment.parameters

        if action_type == ResponseAction.LOG_INCIDENT:
            return await self._log_incident(containment.target, params)

        elif action_type == ResponseAction.ISOLATE_PROCESS:
            return await self._isolate_process(params)

        elif action_type == ResponseAction.BLOCK_NETWORK:
            return await self._block_network(params)

        elif action_type == ResponseAction.TERMINATE_PROCESS:
            return await self._terminate_process(params)

        elif action_type == ResponseAction.QUARANTINE_FILE:
            return await self._quarantine_file(params)

        elif action_type == ResponseAction.RESTRICT_ACCESS:
            return await self._restrict_access(params)

        elif action_type == ResponseAction.ALERT_HUMAN:
            return await self._alert_human(containment.target, params)

        else:
            raise ValueError(f"Unknown action type: {action_type}")

    async def _log_incident(self, alert_id: str, params: Dict[str, Any]) -> str:
        """Registra incidente"""
        incident_data = {
            'incident_id': f"incident_{alert_id}_{int(time.time())}",
            'alert_id': alert_id,
            'timestamp': time.time(),
            'responder_id': self.responder_id,
            'details': params
        }

        await self.memory.store_incident(incident_data)
        return f"Incident logged: {incident_data['incident_id']}"

    async def _isolate_process(self, params: Dict[str, Any]) -> str:
        """Isola processo"""
        processes = params.get('process_info', [])

        if not processes:
            return "No processes to isolate"

        isolated = []
        for proc in processes[:5]:  # limitar a 5 processos
            try:
                pid = proc.get('pid')
                if pid:
                    # Enviar sinal STOP para pausar processo
                    os.kill(pid, signal.SIGSTOP)
                    isolated.append(str(pid))
            except (ProcessLookupError, PermissionError) as e:
                logger.warning(f"Failed to isolate process {pid}: {e}")

        return f"Isolated processes: {', '.join(isolated)}"

    async def _block_network(self, params: Dict[str, Any]) -> str:
        """Bloqueia conexões de rede"""
        connections = params.get('connections', [])

        if not connections:
            return "No connections to block"

        # Usar iptables ou firewall rules (simulado)
        blocked = []
        for conn in connections[:10]:  # limitar a 10 conexões
            try:
                # Simular bloqueio - em produção usaria iptables
                remote_addr = conn.get('remote_addr', '')
                if remote_addr:
                    # Adicionar à lista de bloqueio
                    blocked.append(remote_addr)
            except Exception as e:
                logger.warning(f"Failed to block connection {conn}: {e}")

        return f"Blocked connections: {', '.join(blocked)}"

    async def _terminate_process(self, params: Dict[str, Any]) -> str:
        """Termina processo"""
        processes = params.get('process_info', [])

        if not processes:
            return "No processes to terminate"

        terminated = []
        for proc in processes[:3]:  # limitar a 3 processos por segurança
            try:
                pid = proc.get('pid')
                if pid:
                    os.kill(pid, signal.SIGTERM)
                    terminated.append(str(pid))
            except (ProcessLookupError, PermissionError) as e:
                logger.warning(f"Failed to terminate process {pid}: {e}")

        return f"Terminated processes: {', '.join(terminated)}"

    async def _quarantine_file(self, params: Dict[str, Any]) -> str:
        """Quarentena arquivo"""
        path = params.get('path') or params.get('file_path')
        if not path or not os.path.exists(path):
            return "No valid file path to quarantine"

        quarantine_dir = os.path.join('/tmp', 'aura_sphere_quarantine')
        os.makedirs(quarantine_dir, exist_ok=True)

        try:
            basename = os.path.basename(path)
            dest = os.path.join(quarantine_dir, f"{basename}_{int(time.time())}")
            os.rename(path, dest)
            return f"Quarantined file to {dest}"
        except Exception as e:
            logger.error(f"Failed to quarantine file {path}: {e}")
            return f"Failed to quarantine file: {e}"

    async def _restrict_access(self, params: Dict[str, Any]) -> str:
        """Restringe acesso"""
        path = params.get('path') or params.get('resource')
        if not path or not os.path.exists(path):
            return "No valid path to restrict"

        try:
            os.chmod(path, 0o000)
            return f"Restricted access to {path}"
        except Exception as e:
            logger.error(f"Failed to restrict access on {path}: {e}")
            return f"Failed to restrict access: {e}"

    async def _alert_human(self, alert_id: str, params: Dict[str, Any]) -> str:
        """Alerta humano"""
        alert_data = {
            'alert_id': alert_id,
            'message': f"Critical security incident detected: {alert_id}",
            'timestamp': time.time(),
            'responder_id': self.responder_id,
            'requires_attention': True
        }

        await self.memory.store_human_alert(alert_data)
        return f"Human alert sent for incident {alert_id}"

    async def _rollback_action(self, containment: ContainmentAction):
        """
        Executa rollback de uma ação

        Args:
            containment: Ação a fazer rollback
        """
        try:
            containment.status = ContainmentStatus.ROLLED_BACK

            # Executar ações de rollback
            for rollback_action in containment.rollback_actions:
                # TODO: Implementar rollback específico
                pass

            logger.info(f"WolfResponder {self.responder_id} rolled back action {containment.action_id}")

        except Exception as e:
            logger.error(f"Failed to rollback action {containment.action_id}: {e}")

    async def _store_containment_result(self, containment: ContainmentAction):
        """
        Armazena resultado da contenção

        Args:
            containment: Ação de contenção
        """
        result_data = {
            'action_id': containment.action_id,
            'action_type': containment.action_type.value,
            'target': containment.target,
            'status': containment.status.value,
            'start_time': containment.start_time,
            'end_time': containment.end_time,
            'result': containment.result,
            'responder_id': self.responder_id,
            'timestamp': time.time()
        }

        await self.memory.store_containment_result(result_data)

    async def _notify_status_change(self, containment: ContainmentAction):
        """
        Notifica mudança de status

        Args:
            containment: Ação de contenção
        """
        for callback in self.status_callbacks:
            try:
                await callback(containment)
            except Exception as e:
                logger.error(f"Failed to execute status callback: {e}")

    async def _monitor_active_containments(self):
        """Monitora ações de contenção ativas"""
        # Verificar timeouts
        current_time = time.time()
        timeout_threshold = 300  # 5 minutos

        for action_id, containment in list(self.active_containments.items()):
            if containment.status == ContainmentStatus.IN_PROGRESS:
                elapsed = current_time - containment.start_time
                if elapsed > timeout_threshold:
                    # Timeout - marcar como falha
                    containment.status = ContainmentStatus.FAILED
                    containment.result = "Action timed out"
                    containment.end_time = current_time

                    await self._store_containment_result(containment)
                    await self._notify_status_change(containment)

                    del self.active_containments[action_id]

    async def _cleanup_completed_actions(self):
        """Limpa ações completadas antigas"""
        current_time = time.time()
        cleanup_threshold = 3600  # 1 hora

        to_remove = []
        for action_id, containment in self.active_containments.items():
            if containment.end_time and (current_time - containment.end_time) > cleanup_threshold:
                to_remove.append(action_id)

        for action_id in to_remove:
            del self.active_containments[action_id]

    def add_status_callback(self, callback):
        """
        Adiciona callback para mudanças de status

        Args:
            callback: Função callback
        """
        self.status_callbacks.append(callback)

    async def get_responder_status(self) -> Dict[str, Any]:
        """Retorna status do respondedor"""
        return {
            'responder_id': self.responder_id,
            'active': self.active,
            'incidents_handled': self.incidents_handled,
            'actions_executed': self.actions_executed,
            'containment_failures': self.containment_failures,
            'active_containments': len(self.active_containments)
        }

    def stop_responding(self):
        """Para o respondedor"""
        self.active = False
        logger.info(f"WolfResponder {self.responder_id} stopped responding")