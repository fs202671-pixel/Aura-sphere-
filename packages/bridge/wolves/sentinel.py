"""
Wolf Sentinel - Lobo Sentinela
==============================

Agente de validação e classificação de alertas.
Características:
- Validação de alertas recebidos
- Classificação de risco e severidade
- Correlação de eventos
- Decisão de escalação
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json

from memory.collective import CollectiveMemory
from core.security import SecurityManager

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class AlertStatus(Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    FALSE_POSITIVE = "false_positive"
    ESCALATED = "escalated"
    RESOLVED = "resolved"

@dataclass
class ValidatedAlert:
    """Alerta validado e classificado"""
    alert_id: str
    original_signal: Dict[str, Any]
    risk_level: RiskLevel
    confidence_score: float
    correlated_events: List[str]
    recommended_actions: List[str]
    validation_timestamp: float
    validator_id: str
    status: AlertStatus

@dataclass
class CorrelationRule:
    """Regra de correlação de eventos"""
    rule_id: str
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    risk_multiplier: float
    enabled: bool = True

class WolfSentinel:
    """
    Lobo sentinela - valida e classifica alertas

    Funcionalidades:
    - Receber alertas dos scouts
    - Validar autenticidade e relevância
    - Classificar nível de risco
    - Correlacionar eventos relacionados
    - Decidir sobre escalação
    """

    def __init__(self, sentinel_id: Optional[str] = None):
        self.sentinel_id = sentinel_id or f"sentinel_{int(time.time())}"
        self.memory = CollectiveMemory()
        self.security = SecurityManager()

        # Estado
        self.active = False

        # Regras de correlação
        self.correlation_rules: Dict[str, CorrelationRule] = {}

        # Estatísticas
        self.alerts_processed = 0
        self.alerts_escalated = 0
        self.false_positives = 0

        # Callbacks
        self.escalation_callbacks: List[callable] = []

        # Inicializar regras
        self._initialize_correlation_rules()

        logger.info(f"WolfSentinel {self.sentinel_id} initialized")

    def _initialize_correlation_rules(self):
        """Inicializa regras de correlação"""
        self.correlation_rules = {
            "multiple_high_cpu": CorrelationRule(
                rule_id="multiple_high_cpu",
                name="Multiple High CPU Alerts",
                description="Multiple high CPU usage alerts in short time",
                conditions=[
                    {"type": "signal_type", "value": "behavior_analysis"},
                    {"type": "severity", "value": "high"},
                    {"type": "count", "value": 3, "time_window": 300}  # 3 alerts in 5 minutes
                ],
                risk_multiplier=1.5
            ),
            "network_and_memory": CorrelationRule(
                rule_id="network_and_memory",
                name="Network and Memory Anomaly",
                description="Network activity combined with memory issues",
                conditions=[
                    {"type": "signal_types", "values": ["network_activity", "system_metrics"]},
                    {"type": "time_window", "value": 600}  # within 10 minutes
                ],
                risk_multiplier=2.0
            ),
            "log_error_spike": CorrelationRule(
                rule_id="log_error_spike",
                name="Log Error Spike",
                description="Sudden increase in error logs",
                conditions=[
                    {"type": "error_count_increase", "threshold": 10},
                    {"type": "time_window", "value": 300}
                ],
                risk_multiplier=1.8
            ),
            "suspicious_process_network": CorrelationRule(
                rule_id="suspicious_process_network",
                name="Suspicious Process with Network",
                description="Suspicious process with network connections",
                conditions=[
                    {"type": "signal_type", "value": "network_activity"},
                    {"type": "has_suspicious_process", "value": True}
                ],
                risk_multiplier=2.5
            )
        }

    async def start_sentinel(self):
        """Inicia o monitoramento de alertas"""
        self.active = True
        logger.info(f"WolfSentinel {self.sentinel_id} started sentinel duty")

        while self.active:
            try:
                # Processar alertas pendentes
                await self._process_pending_alerts()

                # Verificar correlações
                await self._check_correlations()

                # Limpar alertas antigos
                await self._cleanup_old_alerts()

                # Aguardar próximo ciclo
                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"WolfSentinel {self.sentinel_id} error: {e}")
                await asyncio.sleep(10)

    async def _process_pending_alerts(self):
        """Processa alertas pendentes"""
        # Buscar alertas não validados
        pending_alerts = await self.memory.get_pending_alerts()

        for alert in pending_alerts:
            try:
                # Validar alerta
                validated_alert = await self._validate_alert(alert)

                # Armazenar alerta validado
                await self._store_validated_alert(validated_alert)

                # Decidir sobre escalação
                if validated_alert.status == AlertStatus.ESCALATED:
                    await self._escalate_alert(validated_alert)

                self.alerts_processed += 1

            except Exception as e:
                logger.error(f"Failed to process alert {alert.get('id')}: {e}")

    async def _validate_alert(self, alert: Dict[str, Any]) -> ValidatedAlert:
        """
        Valida um alerta

        Args:
            alert: Dados do alerta

        Returns:
            Alerta validado
        """
        alert_id = alert.get('signal_id', alert.get('id', f"alert_{int(time.time())}"))

        # Verificar se é falso positivo
        if await self._is_false_positive(alert):
            return ValidatedAlert(
                alert_id=alert_id,
                original_signal=alert,
                risk_level=RiskLevel.LOW,
                confidence_score=0.9,
                correlated_events=[],
                recommended_actions=["Dismiss alert"],
                validation_timestamp=time.time(),
                validator_id=self.sentinel_id,
                status=AlertStatus.FALSE_POSITIVE
            )

        # Classificar risco
        risk_level, confidence = await self._classify_risk(alert)

        # Encontrar eventos correlacionados
        correlated = await self._find_correlated_events(alert)

        # Aplicar regras de correlação
        risk_level, confidence = await self._apply_correlation_rules(
            alert, correlated, risk_level, confidence
        )

        # Decidir status
        status = self._determine_alert_status(risk_level, confidence, correlated)

        # Gerar ações recomendadas
        recommended_actions = self._generate_recommended_actions(risk_level, alert)

        return ValidatedAlert(
            alert_id=alert_id,
            original_signal=alert,
            risk_level=risk_level,
            confidence_score=confidence,
            correlated_events=[e.get('id', str(i)) for i, e in enumerate(correlated)],
            recommended_actions=recommended_actions,
            validation_timestamp=time.time(),
            validator_id=self.sentinel_id,
            status=status
        )

    async def _is_false_positive(self, alert: Dict[str, Any]) -> bool:
        """
        Verifica se alerta é falso positivo

        Args:
            alert: Dados do alerta

        Returns:
            True se for falso positivo
        """
        # Verificar padrões de falso positivo
        severity = alert.get('severity', 'low')

        # Alertas de baixa severidade com dados insuficientes
        if severity == 'low':
            data_keys = len(alert.get('data', {}))
            if data_keys < 2:
                return True

        # Verificar se alerta já foi visto recentemente
        recent_similar = await self.memory.get_similar_alerts(alert, hours=1)
        if len(recent_similar) > 5:  # muitos alertas similares
            return True

        # Verificar dados inconsistentes
        data = alert.get('data', {})
        if not data or not isinstance(data, dict):
            return True

        return False

    async def _classify_risk(self, alert: Dict[str, Any]) -> Tuple[RiskLevel, float]:
        """
        Classifica nível de risco do alerta

        Args:
            alert: Dados do alerta

        Returns:
            Tupla (nível de risco, confiança)
        """
        severity = alert.get('severity', 'low')
        signal_type = alert.get('type', '')

        # Mapeamento básico de severidade
        severity_map = {
            'low': RiskLevel.LOW,
            'medium': RiskLevel.MEDIUM,
            'high': RiskLevel.HIGH,
            'critical': RiskLevel.CRITICAL
        }

        base_risk = severity_map.get(severity, RiskLevel.LOW)
        confidence = 0.7  # confiança base

        # Ajustar baseado no tipo de sinal
        if signal_type == 'network_activity':
            base_risk = RiskLevel(max(base_risk.value + 1, RiskLevel.LOW.value))
            confidence += 0.1
        elif signal_type == 'behavior_analysis':
            if severity == 'high':
                base_risk = RiskLevel.HIGH
                confidence += 0.2

        # Ajustar baseado em dados específicos
        data = alert.get('data', {})

        # Alto uso de CPU/memória
        if data.get('cpu_percent', 0) > 90 or data.get('memory_percent', 0) > 95:
            base_risk = RiskLevel.CRITICAL
            confidence += 0.3

        # Conexões suspeitas
        if 'connections' in data and len(data['connections']) > 10:
            base_risk = RiskLevel(max(base_risk.value + 1, RiskLevel.MEDIUM.value))
            confidence += 0.2

        return RiskLevel(base_risk), min(confidence, 1.0)

    async def _find_correlated_events(self, alert: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Encontra eventos correlacionados

        Args:
            alert: Alerta base

        Returns:
            Lista de eventos correlacionados
        """
        # Buscar alertas similares no período recente
        time_window = 1800  # 30 minutos
        similar_alerts = await self.memory.get_similar_alerts(alert, seconds=time_window)

        # Filtrar eventos realmente correlacionados
        correlated = []
        alert_time = alert.get('timestamp', time.time())

        for similar in similar_alerts:
            similar_time = similar.get('timestamp', 0)
            time_diff = abs(alert_time - similar_time)

            # Mesmo tipo de sinal e próximo no tempo
            if (similar.get('type') == alert.get('type') and
                time_diff < 600):  # 10 minutos
                correlated.append(similar)

        return correlated[:5]  # limitar a 5

    async def _apply_correlation_rules(
        self,
        alert: Dict[str, Any],
        correlated: List[Dict[str, Any]],
        current_risk: RiskLevel,
        current_confidence: float
    ) -> Tuple[RiskLevel, float]:
        """
        Aplica regras de correlação

        Args:
            alert: Alerta atual
            correlated: Eventos correlacionados
            current_risk: Risco atual
            current_confidence: Confiança atual

        Returns:
            Tupla (risco ajustado, confiança ajustada)
        """
        risk_value = current_risk.value
        confidence = current_confidence

        for rule in self.correlation_rules.values():
            if not rule.enabled:
                continue

            if await self._rule_matches(rule, alert, correlated):
                # Aplicar multiplicador de risco
                risk_value = min(risk_value * rule.risk_multiplier, RiskLevel.CRITICAL.value)
                confidence = min(confidence + 0.1, 1.0)

                logger.info(f"Correlation rule {rule.rule_id} applied to alert")

        return RiskLevel(int(risk_value)), confidence

    async def _rule_matches(
        self,
        rule: CorrelationRule,
        alert: Dict[str, Any],
        correlated: List[Dict[str, Any]]
    ) -> bool:
        """
        Verifica se uma regra de correlação combina

        Args:
            rule: Regra a verificar
            alert: Alerta atual
            correlated: Eventos correlacionados

        Returns:
            True se combina
        """
        for condition in rule.conditions:
            cond_type = condition.get('type')

            if cond_type == 'signal_type':
                if alert.get('type') != condition.get('value'):
                    return False

            elif cond_type == 'severity':
                if alert.get('severity') != condition.get('value'):
                    return False

            elif cond_type == 'count':
                required_count = condition.get('value', 0)
                if len(correlated) + 1 < required_count:  # +1 para o alerta atual
                    return False

            elif cond_type == 'signal_types':
                required_types = set(condition.get('values', []))
                found_types = {alert.get('type')}
                found_types.update(c.get('type') for c in correlated)

                if not required_types.issubset(found_types):
                    return False

            elif cond_type == 'error_count_increase':
                # Verificar aumento no contador de erros
                threshold = condition.get('threshold', 0)
                if not self._check_error_increase(alert, correlated, threshold):
                    return False

        return True

    def _check_error_increase(
        self,
        alert: Dict[str, Any],
        correlated: List[Dict[str, Any]],
        threshold: int
    ) -> bool:
        """Verifica aumento no contador de erros"""
        current_errors = alert.get('data', {}).get('error_count', 0)

        # Somar erros dos eventos correlacionados
        total_errors = current_errors
        for corr in correlated:
            total_errors += corr.get('data', {}).get('error_count', 0)

        return total_errors >= threshold

    def _determine_alert_status(
        self,
        risk_level: RiskLevel,
        confidence: float,
        correlated: List[Dict[str, Any]]
    ) -> AlertStatus:
        """Determina status do alerta"""
        if risk_level == RiskLevel.CRITICAL:
            return AlertStatus.ESCALATED
        elif risk_level == RiskLevel.HIGH and confidence > 0.8:
            return AlertStatus.ESCALATED
        elif risk_level == RiskLevel.HIGH and len(correlated) > 2:
            return AlertStatus.ESCALATED
        else:
            return AlertStatus.VALIDATED

    def _generate_recommended_actions(self, risk_level: RiskLevel, alert: Dict[str, Any]) -> List[str]:
        """Gera ações recomendadas"""
        actions = []

        if risk_level == RiskLevel.CRITICAL:
            actions.extend([
                "Immediate isolation of affected components",
                "Alert security team",
                "Initiate incident response protocol"
            ])
        elif risk_level == RiskLevel.HIGH:
            actions.extend([
                "Increase monitoring of affected systems",
                "Review recent changes",
                "Prepare contingency measures"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            actions.extend([
                "Log detailed information",
                "Monitor for escalation",
                "Review system configuration"
            ])
        else:
            actions.append("Continue normal monitoring")

        # Ações específicas baseadas no tipo de alerta
        alert_type = alert.get('type')
        if alert_type == 'network_activity':
            actions.append("Review network access logs")
        elif alert_type == 'behavior_analysis':
            actions.append("Check process activity")

        return actions

    async def _store_validated_alert(self, validated_alert: ValidatedAlert):
        """
        Armazena alerta validado

        Args:
            validated_alert: Alerta a armazenar
        """
        alert_data = {
            'alert_id': validated_alert.alert_id,
            'original_signal': validated_alert.original_signal,
            'risk_level': validated_alert.risk_level.value,
            'confidence_score': validated_alert.confidence_score,
            'correlated_events': validated_alert.correlated_events,
            'recommended_actions': validated_alert.recommended_actions,
            'validation_timestamp': validated_alert.validation_timestamp,
            'validator_id': validated_alert.validator_id,
            'status': validated_alert.status.value
        }

        await self.memory.store_validated_alert(alert_data)

    async def _escalate_alert(self, validated_alert: ValidatedAlert):
        """
        Escala alerta para resposta

        Args:
            validated_alert: Alerta a escalar
        """
        self.alerts_escalated += 1

        logger.warning(f"WolfSentinel {self.sentinel_id} escalating alert {validated_alert.alert_id}")

        # Disparar callbacks de escalação
        for callback in self.escalation_callbacks:
            try:
                await callback(validated_alert)
            except Exception as e:
                logger.error(f"Failed to execute escalation callback: {e}")

    async def _check_correlations(self):
        """Verifica correlações entre alertas recentes"""
        # Buscar alertas validados recentes
        recent_alerts = await self.memory.get_recent_validated_alerts(hours=1)

        # Agrupar por tipo e verificar padrões
        type_groups = {}
        for alert in recent_alerts:
            alert_type = alert.get('original_signal', {}).get('type', 'unknown')
            if alert_type not in type_groups:
                type_groups[alert_type] = []
            type_groups[alert_type].append(alert)

        # Verificar grupos grandes
        for alert_type, alerts in type_groups.items():
            if len(alerts) > 10:  # muitos alertas do mesmo tipo
                await self._create_correlation_alert(alert_type, alerts)

    async def _create_correlation_alert(self, alert_type: str, alerts: List[Dict[str, Any]]):
        """
        Cria alerta de correlação

        Args:
            alert_type: Tipo dos alertas
            alerts: Lista de alertas
        """
        correlation_alert = {
            'signal_id': f"correlation_{alert_type}_{int(time.time())}",
            'type': 'correlation',
            'severity': 'high',
            'description': f"High volume of {alert_type} alerts: {len(alerts)}",
            'data': {
                'alert_type': alert_type,
                'count': len(alerts),
                'time_span': '1 hour',
                'sample_alerts': alerts[:3]
            },
            'timestamp': time.time(),
            'source': f"correlation_detector_{self.sentinel_id}"
        }

        # Processar como alerta normal
        validated = await self._validate_alert(correlation_alert)
        await self._store_validated_alert(validated)

        if validated.status == AlertStatus.ESCALATED:
            await self._escalate_alert(validated)

    async def _cleanup_old_alerts(self):
        """Limpa alertas antigos"""
        # TODO: Implementar limpeza
        pass

    def add_escalation_callback(self, callback):
        """
        Adiciona callback para escalação

        Args:
            callback: Função a ser chamada quando alerta é escalado
        """
        self.escalation_callbacks.append(callback)

    async def get_sentinel_status(self) -> Dict[str, Any]:
        """Retorna status do sentinela"""
        return {
            'sentinel_id': self.sentinel_id,
            'active': self.active,
            'alerts_processed': self.alerts_processed,
            'alerts_escalated': self.alerts_escalated,
            'false_positives': self.false_positives,
            'enabled_rules': [
                rid for rid, rule in self.correlation_rules.items() if rule.enabled
            ]
        }

    def stop_sentinel(self):
        """Para o sentinela"""
        self.active = False
        logger.info(f"WolfSentinel {self.sentinel_id} stopped sentinel duty")

    async def assess_task_risk(self, orchestrator_task: Any, exploration_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Avalia risco de uma tarefa do orquestrador

        Args:
            orchestrator_task: Tarefa do orquestrador
            exploration_results: Resultados da exploração

        Returns:
            Avaliação de risco
        """
        try:
            # Analisar comando do usuário
            command = orchestrator_task.user_command.lower()

            # Fatores de risco
            risk_factors = []

            # Verificar palavras-chave de risco
            high_risk_keywords = ["delete", "remove", "drop", "destroy", "kill", "terminate", "shutdown", "format"]
            medium_risk_keywords = ["modify", "change", "update", "alter", "execute", "run", "install"]

            if any(keyword in command for keyword in high_risk_keywords):
                risk_factors.append("high_risk_keywords")
            elif any(keyword in command for keyword in medium_risk_keywords):
                risk_factors.append("medium_risk_keywords")

            # Verificar complexidade da exploração
            exploration_complexity = len(exploration_results)
            if exploration_complexity > 10:
                risk_factors.append("high_exploration_complexity")

            # Verificar se há erros nos resultados
            error_count = sum(1 for r in exploration_results if "error" in r)
            if error_count > 0:
                risk_factors.append("exploration_errors")

            # Calcular nível de risco
            if "high_risk_keywords" in risk_factors:
                risk_level = "critical"
                confidence = 0.9
            elif len(risk_factors) >= 2:
                risk_level = "high"
                confidence = 0.7
            elif len(risk_factors) == 1:
                risk_level = "medium"
                confidence = 0.5
            else:
                risk_level = "low"
                confidence = 0.3

            assessment = {
                "level": risk_level,
                "confidence": confidence,
                "risk_factors": risk_factors,
                "recommendations": self._generate_risk_recommendations(risk_level, risk_factors),
                "requires_approval": risk_level in ["high", "critical"]
            }

            logger.info(f"Risk assessment for task {orchestrator_task.id}: {risk_level} ({confidence:.2f} confidence)")

            return assessment

        except Exception as e:
            logger.error(f"Error assessing task risk: {e}")
            return {
                "level": "unknown",
                "confidence": 0.0,
                "error": str(e),
                "risk_factors": ["assessment_error"],
                "requires_approval": True
            }

    def _generate_risk_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Gera recomendações baseadas no nível de risco"""
        recommendations = []

        if risk_level == "critical":
            recommendations.extend([
                "Require explicit user approval before execution",
                "Execute in isolated sandbox environment",
                "Prepare rollback procedures",
                "Monitor execution closely"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Execute with additional validation",
                "Limit scope of operations",
                "Have contingency plans ready"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Log all operations",
                "Monitor for unexpected behavior",
                "Be prepared to interrupt if needed"
            ])
        else:
            recommendations.append("Proceed with standard monitoring")

        # Recomendações específicas baseadas em fatores
        if "exploration_errors" in risk_factors:
            recommendations.append("Review exploration results for potential issues")
        if "high_exploration_complexity" in risk_factors:
            recommendations.append("Consider breaking task into smaller components")

        return recommendations

    async def activate_defense_measures(self, orchestrator_task: Any, risk_assessment: Dict[str, Any]):
        """
        Ativa medidas de defesa para tarefa de alto risco

        Args:
            orchestrator_task: Tarefa do orquestrador
            risk_assessment: Avaliação de risco
        """
        try:
            risk_level = risk_assessment["level"]

            if risk_level in ["high", "critical"]:
                logger.warning(f"Activating defense measures for high-risk task {orchestrator_task.id}")

                # Criar alerta de defesa
                defense_alert = {
                    'signal_id': f"defense_activation_{orchestrator_task.id}_{int(time.time())}",
                    'type': 'task_defense',
                    'severity': 'high' if risk_level == 'high' else 'critical',
                    'description': f"Defense measures activated for {risk_level} risk task",
                    'data': {
                        'task_id': orchestrator_task.id,
                        'risk_level': risk_level,
                        'risk_factors': risk_assessment.get('risk_factors', []),
                        'user_command': orchestrator_task.user_command
                    },
                    'timestamp': time.time(),
                    'source': f"orchestrator_defense_{self.sentinel_id}"
                }

                # Processar alerta
                validated = await self._validate_alert(defense_alert)
                await self._store_validated_alert(validated)

                # Para risco crítico, escalar imediatamente
                if risk_level == "critical":
                    await self._escalate_alert(validated)

                # Medidas específicas de defesa
                await self._implement_defense_measures(orchestrator_task, risk_assessment)

            else:
                logger.info(f"No defense measures needed for {risk_level} risk task {orchestrator_task.id}")

        except Exception as e:
            logger.error(f"Error activating defense measures: {e}")

    async def _implement_defense_measures(self, orchestrator_task: Any, risk_assessment: Dict[str, Any]):
        """
        Implementa medidas de defesa específicas

        Args:
            orchestrator_task: Tarefa do orquestrador
            risk_assessment: Avaliação de risco
        """
        # Medidas baseadas no nível de risco
        risk_level = risk_assessment["level"]

        if risk_level == "critical":
            # Isolamento completo
            await self._isolate_task_execution(orchestrator_task)
            # Aumentar monitoramento
            await self._increase_monitoring(orchestrator_task)
            # Preparar rollback
            await self._prepare_rollback(orchestrator_task)

        elif risk_level == "high":
            # Isolamento parcial
            await self._limit_task_scope(orchestrator_task)
            # Aumentar logging
            await self._increase_logging(orchestrator_task)

        # Log das medidas implementadas
        logger.info(f"Defense measures implemented for task {orchestrator_task.id}")

    async def _isolate_task_execution(self, orchestrator_task: Any):
        """Isola execução da tarefa"""
        # TODO: Implementar isolamento real (containers, recursos limitados, etc.)
        logger.info(f"Task {orchestrator_task.id} execution isolated")

    async def _increase_monitoring(self, orchestrator_task: Any):
        """Aumenta monitoramento da tarefa"""
        # TODO: Implementar monitoramento aumentado
        logger.info(f"Monitoring increased for task {orchestrator_task.id}")

    async def _prepare_rollback(self, orchestrator_task: Any):
        """Prepara procedimentos de rollback"""
        # TODO: Implementar preparação de rollback
        logger.info(f"Rollback prepared for task {orchestrator_task.id}")

    async def _limit_task_scope(self, orchestrator_task: Any):
        """Limita escopo da tarefa"""
        # TODO: Implementar limitação de escopo
        logger.info(f"Scope limited for task {orchestrator_task.id}")

    async def _increase_logging(self, orchestrator_task: Any):
        """Aumenta logging da tarefa"""
        # TODO: Implementar logging aumentado
        logger.info(f"Logging increased for task {orchestrator_task.id}")