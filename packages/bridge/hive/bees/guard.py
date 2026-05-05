"""
Bee Guard - Abelha Guarda
========================

Agente de segurança e proteção.
Características:
- Detecção de ameaças
- Validação de segurança
- Proteção contra ataques
- Monitoramento de anomalias
"""

import asyncio
import time
import hashlib
import json
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

from memory.collective import CollectiveMemory
from core.security import SecurityManager

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class SecurityEvent:
    """Evento de segurança detectado"""
    event_id: str
    event_type: str
    severity: ThreatLevel
    description: str
    source: str
    data: Dict[str, Any]
    timestamp: float
    handled: bool = False

@dataclass
class SecurityRule:
    """Regra de segurança"""
    rule_id: str
    name: str
    pattern: str
    severity: ThreatLevel
    action: str
    enabled: bool = True

class BeeGuard:
    """
    Abelha guarda - protege o sistema

    Funcionalidades:
    - Monitorar atividades suspeitas
    - Validar segurança de dados
    - Detectar ataques e anomalias
    - Implementar medidas de proteção
    """

    def __init__(self, guard_id: Optional[str] = None):
        self.guard_id = guard_id or f"guard_{int(time.time())}"
        self.memory = CollectiveMemory()
        self.security = SecurityManager()

        # Regras de segurança
        self.security_rules: Dict[str, SecurityRule] = {}
        self.active = False

        # Estatísticas
        self.events_detected = 0
        self.threats_blocked = 0
        self.false_positives = 0

        # Padrões suspeitos
        self.suspicious_patterns = self._load_suspicious_patterns()

        # Whitelist de hashes seguros
        self.safe_hashes: Set[str] = set()

        logger.info(f"BeeGuard {self.guard_id} initialized")

    def _load_suspicious_patterns(self) -> List[str]:
        """Carrega padrões suspeitos"""
        return [
            r"(?i)(password|secret|key|token)\s*[:=]\s*['\"][^'\"]*['\"]",
            r"(?i)(eval|exec|system|shell_exec)\s*\(",
            r"(?i)(import\s+(os|subprocess|sys))",
            r"(?i)(rm\s+-rf\s+/|del\s+/s\s+/q)",
            r"(?i)(SELECT\s+.*\s+FROM\s+.*--)",
            r"(?i)(<script[^>]*>.*?</script>)",
            r"(?i)(javascript:|data:|vbscript:)",
            r"(?i)(\.\./|\.\.\\)",
        ]

    async def start_guarding(self):
        """Inicia o monitoramento de segurança"""
        self.active = True
        logger.info(f"BeeGuard {self.guard_id} started guarding")

        # Carregar regras de segurança
        await self._load_security_rules()

        while self.active:
            try:
                # Monitorar atividades
                await self._monitor_activities()

                # Verificar tarefas pendentes
                await self._check_pending_tasks()

                # Limpar eventos antigos
                await self._cleanup_old_events()

                # Aguardar antes do próximo ciclo
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"BeeGuard {self.guard_id} error: {e}")
                await asyncio.sleep(5)

    async def _load_security_rules(self):
        """Carrega regras de segurança da memória coletiva"""
        # TODO: Implementar carregamento real das regras
        self.security_rules = {
            "sql_injection": SecurityRule(
                rule_id="sql_injection",
                name="SQL Injection Detection",
                pattern=r"(?i)(SELECT|INSERT|UPDATE|DELETE).*['\"];",
                severity=ThreatLevel.HIGH,
                action="block"
            ),
            "xss_attempt": SecurityRule(
                rule_id="xss_attempt",
                name="XSS Attempt Detection",
                pattern=r"(?i)<script[^>]*>.*?</script>",
                severity=ThreatLevel.HIGH,
                action="block"
            ),
            "path_traversal": SecurityRule(
                rule_id="path_traversal",
                name="Path Traversal Detection",
                pattern=r"(?i)(\.\./|\.\.\\)",
                severity=ThreatLevel.MEDIUM,
                action="block"
            )
        }

    async def _monitor_activities(self):
        """Monitora atividades do sistema"""
        # Verificar tarefas recentes
        recent_tasks = await self.memory.get_recent_tasks(limit=10)

        for task in recent_tasks:
            # Verificar segurança da tarefa
            threat = await self._analyze_task_security(task)

            if threat:
                await self._handle_security_event(threat)

        # Verificar dados na memória coletiva
        memory_data = await self.memory.get_recent_data(limit=50)

        for data in memory_data:
            # Verificar conteúdo suspeito
            threat = await self._analyze_data_security(data)

            if threat:
                await self._handle_security_event(threat)

    async def _check_pending_tasks(self):
        """Verifica tarefas pendentes por muito tempo"""
        pending_tasks = await self.memory.get_pending_tasks()

        current_time = time.time()
        max_pending_time = 3600  # 1 hora

        for task in pending_tasks:
            task_time = task.get('timestamp', 0)
            if current_time - task_time > max_pending_time:
                # Tarefa pendente há muito tempo - possível anomalia
                event = SecurityEvent(
                    event_id=f"stale_task_{task['id']}",
                    event_type="stale_task",
                    severity=ThreatLevel.LOW,
                    description=f"Task {task['id']} has been pending for too long",
                    source="task_monitor",
                    data={'task': task},
                    timestamp=current_time
                )

                await self._handle_security_event(event)

    async def _cleanup_old_events(self):
        """Limpa eventos de segurança antigos"""
        if hasattr(self.memory, 'cleanup_security_events'):
            await self.memory.cleanup_security_events()

    async def _analyze_task_security(self, task: Dict[str, Any]) -> Optional[SecurityEvent]:
        """
        Analisa segurança de uma tarefa

        Args:
            task: Dados da tarefa

        Returns:
            Evento de segurança se detectado
        """
        task_data = task.get('data', {})
        task_type = task.get('type', '')

        # Verificar dados da tarefa
        for key, value in task_data.items():
            if isinstance(value, str):
                threat = self._check_content_against_rules(value)
                if threat:
                    return SecurityEvent(
                        event_id=f"task_threat_{task['id']}_{key}",
                        event_type="task_data_threat",
                        severity=threat['severity'],
                        description=f"Threat detected in task {task['id']} data: {threat['rule']}",
                        source=f"task_{task['id']}",
                        data={'task': task, 'threat': threat},
                        timestamp=time.time()
                    )

        # Verificar tipo de tarefa suspeito
        if task_type in ['system_exec', 'file_delete', 'network_access']:
            return SecurityEvent(
                event_id=f"suspicious_task_{task['id']}",
                event_type="suspicious_task_type",
                severity=ThreatLevel.MEDIUM,
                description=f"Suspicious task type: {task_type}",
                source=f"task_{task['id']}",
                data={'task': task},
                timestamp=time.time()
            )

        return None

    async def _analyze_data_security(self, data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """
        Analisa segurança de dados

        Args:
            data: Dados a analisar

        Returns:
            Evento de segurança se detectado
        """
        # Verificar conteúdo dos dados
        data_str = json.dumps(data, default=str)

        threat = self._check_content_against_rules(data_str)
        if threat:
            return SecurityEvent(
                event_id=f"data_threat_{hash(data_str) % 10000}",
                event_type="data_content_threat",
                severity=threat['severity'],
                description=f"Threat detected in data content: {threat['rule']}",
                source="memory_data",
                data={'data': data, 'threat': threat},
                timestamp=time.time()
            )

        return None

    def _check_content_against_rules(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Verifica conteúdo contra regras de segurança

        Args:
            content: Conteúdo a verificar

        Returns:
            Detalhes da ameaça se encontrada
        """
        for rule_id, rule in self.security_rules.items():
            if not rule.enabled:
                continue

            if re.search(rule.pattern, content, re.IGNORECASE):
                return {
                    'rule': rule_id,
                    'severity': rule.severity,
                    'action': rule.action
                }

        # Verificar padrões suspeitos
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    'rule': 'suspicious_pattern',
                    'severity': ThreatLevel.MEDIUM,
                    'action': 'flag'
                }

        return None

    async def _handle_security_event(self, event: SecurityEvent):
        """
        Trata um evento de segurança

        Args:
            event: Evento a tratar
        """
        self.events_detected += 1

        logger.warning(f"BeeGuard {self.guard_id} detected security event: {event.description}")

        # Armazenar evento na memória coletiva
        event_data = {
            'event_id': event.event_id,
            'type': event.event_type,
            'severity': event.severity.value,
            'description': event.description,
            'source': event.source,
            'data': event.data,
            'timestamp': event.timestamp,
            'handled': event.handled
        }

        await self.memory.store_security_event(event_data)

        # Executar ação baseada na severidade
        if event.severity == ThreatLevel.CRITICAL:
            await self._execute_critical_action(event)
        elif event.severity == ThreatLevel.HIGH:
            await self._execute_high_action(event)
        elif event.severity == ThreatLevel.MEDIUM:
            await self._execute_medium_action(event)
        else:
            await self._execute_low_action(event)

        # Marcar evento como tratado quando apropriado
        await self.memory.update_security_event(event.event_id, {'handled': True})

    async def _execute_critical_action(self, event: SecurityEvent):
        """Executa ação para ameaça crítica"""
        # Bloquear imediatamente
        await self._block_threat(event)
        self.threats_blocked += 1

        # Alertar sistema
        await self._alert_system(event)

    async def _execute_high_action(self, event: SecurityEvent):
        """Executa ação para ameaça alta"""
        # Bloquear e registrar
        await self._block_threat(event)
        self.threats_blocked += 1

    async def _execute_medium_action(self, event: SecurityEvent):
        """Executa ação para ameaça média"""
        # Apenas registrar e monitorar
        pass

    async def _execute_low_action(self, event: SecurityEvent):
        """Executa ação para ameaça baixa"""
        # Apenas registrar
        pass

    async def _block_threat(self, event: SecurityEvent):
        """
        Bloqueia uma ameaça

        Args:
            event: Evento da ameaça
        """
        # Marcar como tratado
        event.handled = True

        # Dependendo do tipo, tomar ação específica
        if event.event_type == "task_data_threat":
            # Cancelar tarefa suspeita
            task_id = event.data.get('task', {}).get('id')
            if task_id:
                await self.memory.update_task_status(task_id, 'blocked')

        elif event.event_type == "data_content_threat":
            # Remover dados suspeitos
            # TODO: Implementar remoção segura
            pass

    async def _alert_system(self, event: SecurityEvent):
        """
        Alerta o sistema sobre ameaça crítica

        Args:
            event: Evento crítico
        """
        alert_data = {
            'alert_type': 'critical_security_threat',
            'event': {
                'id': event.event_id,
                'type': event.event_type,
                'description': event.description,
                'severity': event.severity.value
            },
            'timestamp': time.time(),
            'guard_id': self.guard_id
        }

        await self.memory.store_alert(alert_data)

        logger.critical(f"BeeGuard {self.guard_id} issued critical alert: {event.description}")

    def add_security_rule(self, rule: SecurityRule):
        """
        Adiciona uma nova regra de segurança

        Args:
            rule: Regra a adicionar
        """
        self.security_rules[rule.rule_id] = rule
        logger.info(f"BeeGuard {self.guard_id} added security rule: {rule.name}")

    def remove_security_rule(self, rule_id: str):
        """Remove uma regra de segurança"""
        if rule_id in self.security_rules:
            del self.security_rules[rule_id]
            logger.info(f"BeeGuard {self.guard_id} removed security rule: {rule_id}")

    def add_safe_hash(self, hash_value: str):
        """
        Adiciona hash à whitelist de seguros

        Args:
            hash_value: Hash seguro
        """
        self.safe_hashes.add(hash_value)

    def remove_safe_hash(self, hash_value: str):
        """Remove hash da whitelist"""
        self.safe_hashes.discard(hash_value)

    async def validate_data_integrity(self, data: Any, expected_hash: Optional[str] = None) -> bool:
        """
        Valida integridade de dados

        Args:
            data: Dados a validar
            expected_hash: Hash esperado (opcional)

        Returns:
            True se válido
        """
        data_str = json.dumps(data, sort_keys=True, default=str)
        actual_hash = hashlib.sha256(data_str.encode()).hexdigest()

        if expected_hash:
            return actual_hash == expected_hash

        # Verificar se está na whitelist
        return actual_hash in self.safe_hashes

    async def get_guard_status(self) -> Dict[str, Any]:
        """Retorna status do guard"""
        return {
            'guard_id': self.guard_id,
            'active': self.active,
            'events_detected': self.events_detected,
            'threats_blocked': self.threats_blocked,
            'false_positives': self.false_positives,
            'rules_count': len(self.security_rules),
            'safe_hashes_count': len(self.safe_hashes)
        }

    def stop_guarding(self):
        """Para o monitoramento"""
        self.active = False
        logger.info(f"BeeGuard {self.guard_id} stopped guarding")