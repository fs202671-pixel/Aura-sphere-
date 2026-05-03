"""
Framework de Governança - Sistema completo de governança da IA

Este módulo implementa um framework abrangente de governança que
coordena todos os aspectos de segurança, controle e supervisão da IA.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import asyncio


class GovernanceLayer(Enum):
    """Camadas do framework de governança."""
    USER_OBEDIENCE = "user_obedience"          # Prioridade absoluta ao usuário
    DEPLOY_PIPELINE = "deploy_pipeline"        # Controle de deploy
    CONTROLLED_LEARNING = "controlled_learning" # Aprendizado supervisionado
    ROBUSTNESS_TESTING = "robustness_testing"  # Testes de robustez
    DESTRUCTIVE_LIMITER = "destructive_limiter" # Limitação de ações destrutivas
    GOVERNANCE_CORE = "governance_core"        # Núcleo da governança


class GovernanceDecision(Enum):
    """Decisões de governança possíveis."""
    APPROVE = "approve"
    DENY = "deny"
    ESCALATE = "escalate"
    MONITOR = "monitor"
    QUARANTINE = "quarantine"


class GovernanceEvent:
    """
    Representa um evento de governança.
    """

    def __init__(self, layer: GovernanceLayer, event_type: str,
                 description: str, context: Dict[str, Any],
                 severity: str = "info"):
        self.layer = layer
        self.event_type = event_type
        self.description = description
        self.context = context
        self.severity = severity
        self.timestamp = datetime.now().isoformat()
        self.event_id = f"gov_{int(datetime.now().timestamp())}_{hash(description) % 10000}"

        # Resultado
        self.decision = None
        self.decision_reason = None
        self.actions_taken = []


class GovernanceFramework:
    """
    Framework completo de governança da IA.

    Coordena:
    - Obediência absoluta ao usuário
    - Pipeline de deploy controlado
    - Aprendizado supervisionado
    - Testes contínuos de robustez
    - Limitação de capacidades destrutivas
    - Monitoramento e auditoria completos
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.governance_dir = data_dir / "governance"
        self.governance_dir.mkdir(parents=True, exist_ok=True)

        self.events_log = self.governance_dir / "governance_events.json"
        self.policies_file = self.governance_dir / "governance_policies.json"

        self.events_history: List[Dict] = []
        self.policies: Dict[str, Any] = {}

        # Componentes da governança
        self.components = {}

        # Estado da governança
        self.governance_active = True
        self.emergency_mode = False

        # Métricas de governança
        self.metrics = {
            "total_events": 0,
            "approved_actions": 0,
            "denied_actions": 0,
            "escalated_actions": 0,
            "quarantined_actions": 0
        }

        self._initialize_policies()
        self._load_state()

    def register_component(self, layer: GovernanceLayer, component: Any) -> None:
        """
        Registra um componente da governança.
        """
        self.components[layer] = component

    async def evaluate_request(self, request: Dict[str, Any],
                              context: Dict[str, Any] = None) -> Tuple[GovernanceDecision, str]:
        """
        Avalia uma solicitação através de todas as camadas de governança.
        """

        context = context or {}

        # Verificar se governança está ativa
        if not self.governance_active:
            return GovernanceDecision.DENY, "Governance framework inactive"

        # Verificar modo de emergência
        if self.emergency_mode:
            return GovernanceDecision.DENY, "System in emergency mode - all requests denied"

        # Avaliar através de cada camada
        for layer in GovernanceLayer:
            if layer in self.components:
                try:
                    decision, reason = await self._evaluate_layer(layer, request, context)

                    # Registrar evento
                    event = GovernanceEvent(
                        layer=layer,
                        event_type="request_evaluation",
                        description=f"Request evaluated by {layer.value}",
                        context={"request": request, "decision": decision.value if decision else None},
                        severity="info"
                    )
                    event.decision = decision
                    event.decision_reason = reason
                    self._log_event(event)

                    # Se negado ou em quarentena, parar avaliação
                    if decision in [GovernanceDecision.DENY, GovernanceDecision.QUARANTINE]:
                        self._update_metrics(decision)
                        return decision, reason

                    # Se escalado, continuar mas marcar
                    if decision == GovernanceDecision.ESCALATE:
                        self._update_metrics(decision)
                        # Continuar para próximas camadas mas com flag de escalação

                except Exception as e:
                    # Falha na avaliação - negar por segurança
                    error_event = GovernanceEvent(
                        layer=layer,
                        event_type="evaluation_error",
                        description=f"Governance evaluation failed in {layer.value}",
                        context={"error": str(e), "request": request},
                        severity="error"
                    )
                    self._log_event(error_event)

                    self._update_metrics(GovernanceDecision.DENY)
                    return GovernanceDecision.DENY, f"Governance evaluation failed: {e}"

        # Todas as camadas passaram - aprovar
        self._update_metrics(GovernanceDecision.APPROVE)
        return GovernanceDecision.APPROVE, "Request approved by all governance layers"

    async def _evaluate_layer(self, layer: GovernanceLayer, request: Dict[str, Any],
                             context: Dict[str, Any]) -> Tuple[GovernanceDecision, str]:
        """
        Avalia solicitação em uma camada específica.
        """

        component = self.components.get(layer)
        if not component:
            return GovernanceDecision.APPROVE, f"Layer {layer.value} not registered"

        # Avaliação específica por camada
        if layer == GovernanceLayer.USER_OBEDIENCE:
            return await self._evaluate_user_obedience(component, request, context)

        elif layer == GovernanceLayer.DEPLOY_PIPELINE:
            return await self._evaluate_deploy_pipeline(component, request, context)

        elif layer == GovernanceLayer.CONTROLLED_LEARNING:
            return await self._evaluate_controlled_learning(component, request, context)

        elif layer == GovernanceLayer.ROBUSTNESS_TESTING:
            return await self._evaluate_robustness_testing(component, request, context)

        elif layer == GovernanceLayer.DESTRUCTIVE_LIMITER:
            return await self._evaluate_destructive_limiter(component, request, context)

        elif layer == GovernanceLayer.GOVERNANCE_CORE:
            return await self._evaluate_governance_core(component, request, context)

        return GovernanceDecision.APPROVE, f"Unknown layer {layer.value}"

    async def _evaluate_user_obedience(self, component, request: Dict[str, Any],
                                      context: Dict[str, Any]) -> Tuple[GovernanceDecision, str]:
        """
        Avalia obediência ao usuário.
        """
        # Sempre permitir - usuário tem prioridade absoluta
        return GovernanceDecision.APPROVE, "User obedience - request permitted"

    async def _evaluate_deploy_pipeline(self, component, request: Dict[str, Any],
                                       context: Dict[str, Any]) -> Tuple[GovernanceDecision, str]:
        """
        Avalia pipeline de deploy.
        """
        # Verificar se é uma solicitação de deploy
        if request.get("type") == "deploy":
            # Simular verificação de deploy
            if "approved" in context and context["approved"]:
                return GovernanceDecision.APPROVE, "Deploy approved"
            else:
                return GovernanceDecision.DENY, "Deploy not approved"

        return GovernanceDecision.APPROVE, "Not a deploy request"

    async def _evaluate_controlled_learning(self, component, request: Dict[str, Any],
                                           context: Dict[str, Any]) -> Tuple[GovernanceDecision, str]:
        """
        Avalia aprendizado controlado.
        """
        # Verificar se é uma solicitação de aprendizado
        if request.get("type") == "learning":
            # Simular verificação de aprendizado
            if "validated" in context and context["validated"]:
                return GovernanceDecision.APPROVE, "Learning approved"
            else:
                return GovernanceDecision.DENY, "Learning not validated"

        return GovernanceDecision.APPROVE, "Not a learning request"

    async def _evaluate_robustness_testing(self, component, request: Dict[str, Any],
                                          context: Dict[str, Any]) -> Tuple[GovernanceDecision, str]:
        """
        Avalia testes de robustez.
        """
        # Verificar se o sistema passou nos testes recentes
        # Simulação - em produção verificaria resultados reais
        health_score = context.get("health_score", 0.8)

        if health_score < 0.6:
            return GovernanceDecision.ESCALATE, f"Low health score: {health_score}"
        elif health_score < 0.8:
            return GovernanceDecision.MONITOR, f"Moderate health score: {health_score}"

        return GovernanceDecision.APPROVE, f"Good health score: {health_score}"

    async def _evaluate_destructive_limiter(self, component, request: Dict[str, Any],
                                           context: Dict[str, Any]) -> Tuple[GovernanceDecision, str]:
        """
        Avalia limitador de ações destrutivas.
        """
        # Verificar se a solicitação contém ações destrutivas
        action_request = request.get("action", "")
        allowed, reason, risk = component.check_action(action_request, context)

        if not allowed:
            if risk.name == "FORBIDDEN":
                return GovernanceDecision.QUARANTINE, f"Forbidden action blocked: {reason}"
            else:
                return GovernanceDecision.DENY, f"Destructive action blocked: {reason}"

        return GovernanceDecision.APPROVE, f"Action permitted: {reason}"

    async def _evaluate_governance_core(self, component, request: Dict[str, Any],
                                       context: Dict[str, Any]) -> Tuple[GovernanceDecision, str]:
        """
        Avalia núcleo da governança.
        """
        # Verificações finais de governança
        if self._check_governance_integrity():
            return GovernanceDecision.APPROVE, "Governance core check passed"
        else:
            return GovernanceDecision.DENY, "Governance integrity check failed"

    def activate_emergency_mode(self, reason: str) -> None:
        """
        Ativa modo de emergência - todas as solicitações negadas.
        """
        self.emergency_mode = True

        event = GovernanceEvent(
            layer=GovernanceLayer.GOVERNANCE_CORE,
            event_type="emergency_activated",
            description=f"Emergency mode activated: {reason}",
            context={"reason": reason},
            severity="critical"
        )
        self._log_event(event)

        self._save_state()

    def deactivate_emergency_mode(self) -> None:
        """
        Desativa modo de emergência.
        """
        self.emergency_mode = False

        event = GovernanceEvent(
            layer=GovernanceLayer.GOVERNANCE_CORE,
            event_type="emergency_deactivated",
            description="Emergency mode deactivated",
            context={},
            severity="info"
        )
        self._log_event(event)

        self._save_state()

    def get_governance_status(self) -> Dict[str, Any]:
        """Retorna status atual da governança."""

        return {
            "governance_active": self.governance_active,
            "emergency_mode": self.emergency_mode,
            "components_registered": list(self.components.keys()),
            "metrics": self.metrics,
            "last_event": self.events_history[-1] if self.events_history else None
        }

    def get_events_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de eventos de governança."""
        return self.events_history[-limit:]

    def _initialize_policies(self) -> None:
        """Inicializa políticas de governança."""

        self.policies = {
            "user_priority": {
                "enabled": True,
                "description": "User requests always take priority"
            },
            "safety_first": {
                "enabled": True,
                "description": "Safety checks cannot be bypassed"
            },
            "no_external_deps": {
                "enabled": True,
                "description": "No external dependencies allowed"
            },
            "offline_operation": {
                "enabled": True,
                "description": "Primary offline operation mode"
            },
            "continuous_testing": {
                "enabled": True,
                "description": "Continuous robustness testing"
            }
        }

    def _check_governance_integrity(self) -> bool:
        """
        Verifica integridade do framework de governança.
        """
        # Verificar se todos os componentes essenciais estão registrados
        essential_layers = [
            GovernanceLayer.USER_OBEDIENCE,
            GovernanceLayer.DESTRUCTIVE_LIMITER,
            GovernanceLayer.GOVERNANCE_CORE
        ]

        for layer in essential_layers:
            if layer not in self.components:
                return False

        # Verificar se políticas essenciais estão ativas
        essential_policies = ["user_priority", "safety_first"]
        for policy in essential_policies:
            if not self.policies.get(policy, {}).get("enabled", False):
                return False

        return True

    def _update_metrics(self, decision: GovernanceDecision) -> None:
        """Atualiza métricas de governança."""

        self.metrics["total_events"] += 1

        if decision == GovernanceDecision.APPROVE:
            self.metrics["approved_actions"] += 1
        elif decision == GovernanceDecision.DENY:
            self.metrics["denied_actions"] += 1
        elif decision == GovernanceDecision.ESCALATE:
            self.metrics["escalated_actions"] += 1
        elif decision == GovernanceDecision.QUARANTINE:
            self.metrics["quarantined_actions"] += 1

    def _log_event(self, event: GovernanceEvent) -> None:
        """Registra evento de governança."""

        event_data = {
            "event_id": event.event_id,
            "layer": event.layer.value,
            "event_type": event.event_type,
            "description": event.description,
            "context": event.context,
            "severity": event.severity,
            "timestamp": event.timestamp,
            "decision": event.decision.value if event.decision else None,
            "decision_reason": event.decision_reason,
            "actions_taken": event.actions_taken
        }

        self.events_history.append(event_data)
        self._save_state()

    def _load_state(self) -> None:
        """Carrega estado da governança."""

        # Carregar eventos
        if self.events_log.exists():
            try:
                self.events_history = json.loads(
                    self.events_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.events_history = []

        # Carregar políticas
        if self.policies_file.exists():
            try:
                self.policies = json.loads(
                    self.policies_file.read_text(encoding='utf-8')
                )
            except Exception:
                self._initialize_policies()

    def _save_state(self) -> None:
        """Persiste estado da governança."""

        self.governance_dir.mkdir(parents=True, exist_ok=True)

        # Salvar eventos (manter últimos 1000)
        self.events_log.write_text(
            json.dumps(self.events_history[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Salvar políticas
        self.policies_file.write_text(
            json.dumps(self.policies, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
