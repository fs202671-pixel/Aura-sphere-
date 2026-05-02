"""
User Intent Interpreter - Identifica e estrutura intenções do usuário.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


class IntentType(Enum):
    """Tipos de intenção possíveis."""
    COMMAND = "command"  # Comando direto
    SUGGESTION = "suggestion"  # Sugestão
    QUESTION = "question"  # Pergunta
    APPROVAL = "approval"  # Aprovação
    REJECTION = "rejection"  # Rejeição
    AMBIGUOUS = "ambiguous"  # Ambíguo
    RISKY = "risky"  # Potencialmente perigoso
    UNKNOWN = "unknown"


@dataclass
class InterpretedIntent:
    """Intenção interpretada."""
    intent_type: IntentType
    confidence: float  # 0.0 to 1.0
    action: str
    parameters: Dict[str, Any]
    risk_level: str  # low, medium, high
    requires_confirmation: bool
    ambiguities: List[str]


class UserIntentInterpreter:
    """Interpreta intenções de comandos do usuário."""

    def __init__(self):
        self.command_keywords = {
            "run": ["execute", "run", "start", "launch"],
            "approve": ["approve", "accept", "ok", "yes", "confirm"],
            "reject": ["reject", "deny", "no", "cancel"],
            "modify": ["change", "update", "modify", "alter"],
            "check": ["check", "verify", "validate", "test"],
            "analyze": ["analyze", "analyze", "review", "examine"],
        }

    def interpret(self, user_input: str) -> InterpretedIntent:
        """
        Interpreta comando do usuário.

        Returns:
            InterpretedIntent com detalhes da intenção
        """
        user_input = user_input.strip().lower()

        # Detectar tipo de intenção
        intent_type, confidence = self._detect_intent_type(user_input)

        # Extrair action e parameters
        action, parameters = self._extract_action_and_parameters(user_input, intent_type)

        # Avaliar risco
        risk_level = self._assess_risk(user_input, action)

        # Detectar ambiguidades
        ambiguities = self._detect_ambiguities(user_input, action)

        # Determinar se requer confirmação
        requires_confirmation = self._requires_confirmation(risk_level, intent_type)

        return InterpretedIntent(
            intent_type=intent_type,
            confidence=confidence,
            action=action,
            parameters=parameters,
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            ambiguities=ambiguities
        )

    def _detect_intent_type(self, user_input: str) -> Tuple[IntentType, float]:
        """Detecta tipo de intenção."""
        # Aprovação/Rejeição
        if any(word in user_input for word in ["sim", "yes", "aprovado", "approved", "ok", "certo"]):
            return IntentType.APPROVAL, 0.95

        if any(word in user_input for word in ["não", "no", "rejeitado", "rejected", "cancel", "cancelar"]):
            return IntentType.REJECTION, 0.95

        # Pergunta
        if user_input.startswith("?") or user_input.endswith("?"):
            return IntentType.QUESTION, 0.9

        # Suggestion
        if any(word in user_input for word in ["você poderia", "could you", "seria bom", "would be good"]):
            return IntentType.SUGGESTION, 0.8

        # Comando direto
        if any(word in user_input for word in self.command_keywords.get("run", [])):
            return IntentType.COMMAND, 0.85

        # Ambíguo
        return IntentType.AMBIGUOUS, 0.5

    def _extract_action_and_parameters(self, user_input: str, intent_type: IntentType) -> Tuple[str, Dict[str, Any]]:
        """Extrai ação e parâmetros."""
        parameters = {}

        # Extrair action based on intent type
        if intent_type == IntentType.APPROVAL:
            action = "approve"
        elif intent_type == IntentType.REJECTION:
            action = "reject"
        elif intent_type == IntentType.QUESTION:
            action = "query"
        elif intent_type == IntentType.COMMAND:
            action = self._extract_command_action(user_input)
        else:
            action = "unknown"

        # Extrair parâmetros simples
        if "proposal" in user_input:
            # Tentar extrair ID de proposta
            import re
            match = re.search(r"proposal[:\s]+([a-f0-9\-]+)", user_input)
            if match:
                parameters["proposal_id"] = match.group(1)

        return action, parameters

    def _extract_command_action(self, user_input: str) -> str:
        """Extrai ação de comando."""
        for action, keywords in self.command_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                return action
        return "unknown"

    def _assess_risk(self, user_input: str, action: str) -> str:
        """Avalia nível de risco."""
        dangerous_words = [
            "delete", "deletar", "remove", "remover", "destroy", "destruir",
            "format", "formatar", "wipe", "limpar", "dangerous", "perigoso"
        ]

        if any(word in user_input for word in dangerous_words):
            return "high"

        if "production" in user_input or "produção" in user_input:
            return "medium"

        if action in ["modify", "change"]:
            return "medium"

        return "low"

    def _detect_ambiguities(self, user_input: str, action: str) -> List[str]:
        """Detecta possíveis ambiguidades."""
        ambiguities = []

        # Se não especifica o que fazer
        if action == "unknown":
            ambiguities.append("Ação não clara")

        # Se tem "algum/alguma"
        if any(word in user_input for word in ["algum", "alguma", "some", "certain"]):
            ambiguities.append("Escopo não específico")

        # Se tem múltiplas ações
        action_count = sum(user_input.count(word) for action_keywords in self.command_keywords.values() for word in action_keywords)
        if action_count > 1:
            ambiguities.append("Múltiplas ações detectadas")

        return ambiguities

    def _requires_confirmation(self, risk_level: str, intent_type: IntentType) -> bool:
        """Determina se requer confirmação."""
        if risk_level in ["high", "medium"]:
            return True

        if intent_type in [IntentType.COMMAND, IntentType.AMBIGUOUS]:
            return True

        return False

    def evaluate_user_override(self, intent: InterpretedIntent) -> bool:
        """
        Avalia se a intenção do usuário deve ter prioridade máxima.
        Sempre retorna True, já que usuário tem prioridade.
        """
        return True

    def validate_intent_safety(self, intent: InterpretedIntent) -> Tuple[bool, Optional[str]]:
        """
        Valida se a intenção é segura de executar.

        Returns:
            (is_safe, reason_if_not_safe)
        """
        if intent.risk_level == "high" and intent.intent_type == IntentType.COMMAND:
            return False, "Comando de alto risco requer confirmação explícita"

        if len(intent.ambiguities) > 2:
            return False, "Muitas ambiguidades no comando"

        if intent.confidence < 0.5:
            return False, "Confiança insuficiente na interpretação"

        return True, None
