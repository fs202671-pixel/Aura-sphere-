#!/usr/bin/env python3
"""
Demo Standalone do Sistema de Interpretação de Intenção
======================================================

Demonstração independente das funcionalidades de interpretação de intenções.
Código copiado para evitar problemas de importação.
"""

import asyncio
import logging
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Copiar classes necessárias diretamente
class IntentType(Enum):
    """Tipos de intenção identificados."""
    DIRECT_COMMAND = "direct_command"      # Comando direto e claro
    SUGGESTION = "suggestion"              # Sugestão ou recomendação
    QUESTION = "question"                  # Pergunta ou pedido de informação
    AMBIGUOUS = "ambiguous"                # Comando ambíguo
    APPROVAL = "approval"                  # Aprovação de algo
    REJECTION = "rejection"                # Rejeição de algo
    CLARIFICATION_REQUEST = "clarification_request"  # Pedido de esclarecimento

class RiskLevel(Enum):
    """Níveis de risco das operações."""
    LOW = "low"           # Operações seguras, sem impacto
    MEDIUM = "medium"     # Operações com impacto moderado
    HIGH = "high"         # Operações com alto impacto
    CRITICAL = "critical" # Operações irreversíveis ou perigosas

class UserIntent:
    """
    Representa uma intenção interpretada do usuário.
    """

    def __init__(self, intent_type: IntentType, confidence: float,
                 action: Optional[str] = None, parameters: Optional[Dict] = None,
                 risk_level: RiskLevel = RiskLevel.LOW,
                 requires_confirmation: bool = False,
                 ambiguities: Optional[List[str]] = None):
        self.intent_type = intent_type
        self.confidence = confidence
        self.action = action
        self.parameters = parameters or {}
        self.risk_level = risk_level
        self.requires_confirmation = requires_confirmation
        self.ambiguities = ambiguities or []
        self.timestamp = datetime.now().isoformat()

class IntentInterpreter:
    """
    Interpreta intenções do usuário a partir de comandos de texto.
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.intent_dir = data_dir / "intent_interpretation"
        self.intent_dir.mkdir(parents=True, exist_ok=True)

        self.interpretation_log = self.intent_dir / "interpretations.json"
        self.interpretations_history: List[Dict] = []

        # Padrões de reconhecimento
        self._initialize_patterns()
        self._load_state()

    def _initialize_patterns(self) -> None:
        """Inicializa padrões de reconhecimento de intenção."""

        self.intent_patterns = {
            IntentType.DIRECT_COMMAND: [
                r"^(faça|execute|rode|crie|delete|remova|altere|modifique)",
                r"^(quero que você)",
                r"^(preciso que)",
                r"^(por favor,? )?(faça|execute|implemente)",
                r"^(implemente|desenvolva|construa)",
                r"^(delete|remova|exclua) (o|a|os|as)",
                r"^(altere|modifique|atualize) (o|a|os|as)"
            ],
            IntentType.SUGGESTION: [
                r"^(talvez|possivelmente|considere|que tal)",
                r"^(você poderia|seria possível)",
                r"^(sugiro que|recomendo que)",
                r"^(o que acha de|que tal se)",
                r"^(pense em|considere implementar)"
            ],
            IntentType.QUESTION: [
                r"\?$",
                r"^(como|quando|onde|por que|qual|quais)",
                r"^(pode me explicar|pode me dizer)",
                r"^(o que é|como funciona)",
                r"^(me ajude a entender)"
            ],
            IntentType.APPROVAL: [
                r"^(sim|aprove|aceite|concordo|ok|beleza|tá bom)",
                r"^(pode prosseguir|vá em frente)",
                r"^(está certo|correto|perfeito)",
                r"^(aprove isso|aceite isso)"
            ],
            IntentType.REJECTION: [
                r"^(não|nega|rejeite|cancele|pare)",
                r"^(não faça|não execute)",
                r"^(espere|aguarde|pare aí)",
                r"^(melhor não|prefiro não)"
            ],
            IntentType.CLARIFICATION_REQUEST: [
                r"^(não entendi|não compreendi)",
                r"^(pode esclarecer|pode explicar)",
                r"^(o que você quer dizer)",
                r"^(não está claro|está confuso)"
            ]
        }

        # Palavras-chave de risco
        self.risk_keywords = {
            RiskLevel.CRITICAL: [
                "delete.*all", "drop.*database", "format.*disk", "shutdown.*system",
                "override.*core", "modify.*immutable", "bypass.*security",
                "disable.*validation", "remove.*backup", "delete.*logs"
            ],
            RiskLevel.HIGH: [
                "delete.*file", "modify.*config", "change.*permission",
                "update.*database", "restart.*service", "kill.*process"
            ],
            RiskLevel.MEDIUM: [
                "create.*file", "update.*code", "modify.*function",
                "change.*setting", "install.*package", "run.*command"
            ],
            RiskLevel.LOW: [
                "show.*info", "list.*files", "read.*file", "check.*status",
                "display.*help", "print.*version"
            ]
        }

        # Padrões de ambiguidade
        self.ambiguity_patterns = [
            r"(talvez|possivelmente|quiçá)",
            r"(ou|alternativamente)",
            r"(depende|se)",
            r"(não sei|não tenho certeza)",
            r"(qualquer|algum|um dos)"
        ]

    def interpret(self, user_input: str) -> UserIntent:
        """
        Interpreta a intenção do usuário a partir do input.
        """

        input_lower = user_input.lower().strip()

        # Detectar tipo de intenção
        intent_type, confidence = self._classify_intent(input_lower)

        # Extrair ação e parâmetros
        action, parameters = self._extract_action_and_params(user_input)

        # Avaliar nível de risco
        risk_level = self._assess_risk_level(user_input)

        # Detectar ambiguidades
        ambiguities = self._detect_ambiguities(user_input)

        # Determinar se requer confirmação
        requires_confirmation = self._requires_confirmation(intent_type, risk_level, ambiguities)

        # Criar objeto de intenção
        intent = UserIntent(
            intent_type=intent_type,
            confidence=confidence,
            action=action,
            parameters=parameters,
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            ambiguities=ambiguities
        )

        # Registrar interpretação
        self._log_interpretation(user_input, intent)

        return intent

    def _classify_intent(self, input_text: str) -> tuple[IntentType, float]:
        """
        Classifica o tipo de intenção baseado em padrões.
        """

        scores = {}

        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, input_text, re.IGNORECASE)
                if matches:
                    # Pontuação baseada no número de matches e posição
                    score += len(matches) * 0.2
                    if re.match(pattern, input_text, re.IGNORECASE):
                        score += 0.3  # Bônus por match no início

            scores[intent_type] = score

        # Normalizar scores
        total_score = sum(scores.values())
        if total_score > 0:
            for intent_type in scores:
                scores[intent_type] /= total_score

        # Determinar tipo principal e confiança
        if scores:
            primary_intent = max(scores, key=scores.get)
            confidence = scores[primary_intent]

            # Ajustar confiança baseada em thresholds
            if confidence >= 0.8:
                pass  # Alta confiança
            elif confidence >= 0.6:
                pass  # Confiança média
            elif confidence >= 0.4:
                pass  # Baixa confiança
            else:
                primary_intent = IntentType.AMBIGUOUS
                confidence = 0.3
        else:
            primary_intent = IntentType.AMBIGUOUS
            confidence = 0.0

        return primary_intent, confidence

    def _extract_action_and_params(self, user_input: str) -> tuple[Optional[str], Dict]:
        """
        Extrai ação e parâmetros do input do usuário.
        """

        action = None
        parameters = {}

        input_lower = user_input.lower()

        # Detectar ação baseada em palavras-chave
        if any(word in input_lower for word in ["crie", "criar", "create"]):
            action = "create"
        elif any(word in input_lower for word in ["execute", "executar", "rode", "run"]):
            action = "execute"
        elif any(word in input_lower for word in ["delete", "deletar", "remova", "remove"]):
            action = "delete"
        elif any(word in input_lower for word in ["modifique", "modificar", "altere", "alter", "change"]):
            action = "modify"
        elif any(word in input_lower for word in ["mostre", "mostrar", "show", "display"]):
            action = "show"
        elif any(word in input_lower for word in ["liste", "listar", "list"]):
            action = "list"

        # Extrair parâmetros específicos
        if "arquivo" in user_input.lower() or "file" in user_input.lower():
            # Procurar por nome de arquivo
            file_match = re.search(r'[\w\.-]+\.(py|js|ts|md|txt|json)', user_input)
            if file_match:
                parameters["file"] = file_match.group()

        if "função" in user_input.lower() or "function" in user_input.lower():
            # Procurar por nome de função
            func_match = re.search(r'função\s+(\w+)|function\s+(\w+)', user_input, re.IGNORECASE)
            if func_match:
                parameters["function"] = func_match.group(1) or func_match.group(2)

        return action, parameters

    def _assess_risk_level(self, user_input: str) -> RiskLevel:
        """
        Avalia o nível de risco da operação solicitada.
        """

        input_lower = user_input.lower()

        # Verificar palavras-chave de risco crítico primeiro
        for keyword in self.risk_keywords[RiskLevel.CRITICAL]:
            if re.search(keyword, input_lower):
                return RiskLevel.CRITICAL

        # Depois alto risco
        for keyword in self.risk_keywords[RiskLevel.HIGH]:
            if re.search(keyword, input_lower):
                return RiskLevel.HIGH

        # Médio risco
        for keyword in self.risk_keywords[RiskLevel.MEDIUM]:
            if re.search(keyword, input_lower):
                return RiskLevel.MEDIUM

        # Default para baixo risco
        return RiskLevel.LOW

    def _detect_ambiguities(self, user_input: str) -> List[str]:
        """
        Detecta ambiguidades no input do usuário.
        """

        ambiguities = []
        input_lower = user_input.lower()

        for pattern in self.ambiguity_patterns:
            if re.search(pattern, input_lower):
                ambiguities.append(f"Detected ambiguity pattern: '{pattern}'")

        # Verificar se input é muito curto
        if len(user_input.split()) < 4:
            ambiguities.append("Input is very short and may be ambiguous")

        # Verificar múltiplas opções
        if " ou " in input_lower or " or " in input_lower:
            ambiguities.append("Multiple options detected - clarification needed")

        return ambiguities

    def _requires_confirmation(self, intent_type: IntentType, risk_level: RiskLevel,
                             ambiguities: List[str]) -> bool:
        """
        Determina se a operação requer confirmação do usuário.
        """

        # Sempre requer confirmação para operações críticas
        if risk_level == RiskLevel.CRITICAL:
            return True

        # Requer confirmação para operações de alto risco
        if risk_level == RiskLevel.HIGH:
            return True

        # Requer confirmação se houver ambiguidades
        if ambiguities:
            return True

        # Requer confirmação para comandos diretos de risco médio
        if intent_type == IntentType.DIRECT_COMMAND and risk_level == RiskLevel.MEDIUM:
            return True

        return False

    def validate_intent_safety(self, intent: UserIntent) -> tuple[bool, Optional[str]]:
        """
        Valida se a intenção interpretada é segura para execução.
        """

        # Rejeitar intenções com baixa confiança
        if intent.confidence < 0.5:
            return False, f"Intention confidence too low: {intent.confidence:.2f}"

        # Rejeitar intenções ambíguas sem confirmação
        if intent.intent_type == IntentType.AMBIGUOUS and not intent.requires_confirmation:
            return False, "Ambiguous intention requires confirmation"

        # Rejeitar operações críticas sem confirmação explícita
        if (intent.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] and
            not intent.requires_confirmation):
            return False, f"High-risk operation requires confirmation: {intent.risk_level.value}"

        return True, None

    def evaluate_user_override(self, intent: UserIntent) -> bool:
        """
        Avalia se o usuário está tentando sobrescrever decisões da IA.
        SEMPRE retorna True - usuário sempre tem prioridade.
        """
        return True

    def get_interpretation_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de interpretações."""
        return self.interpretations_history[-limit:]

    def _log_interpretation(self, user_input: str, intent: UserIntent) -> None:
        """Registra interpretação no histórico."""

        interpretation_entry = {
            "timestamp": intent.timestamp,
            "user_input": user_input,
            "intent_type": intent.intent_type.value,
            "confidence": intent.confidence,
            "action": intent.action,
            "parameters": intent.parameters,
            "risk_level": intent.risk_level.value,
            "requires_confirmation": intent.requires_confirmation,
            "ambiguities": intent.ambiguities
        }

        self.interpretations_history.append(interpretation_entry)
        self._save_state()

    def _load_state(self) -> None:
        """Carrega estado do interpretador."""

        if self.interpretation_log.exists():
            try:
                self.interpretations_history = json.loads(
                    self.interpretation_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.interpretations_history = []

    def _save_state(self) -> None:
        """Persiste estado do interpretador."""

        self.intent_dir.mkdir(parents=True, exist_ok=True)

        self.interpretation_log.write_text(
            json.dumps(self.interpretations_history[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

async def demo_intent_interpretation():
    """Demonstra o sistema de interpretação de intenção."""

    print("🧠 Iniciando demo standalone do sistema de interpretação de intenção...")

    # Criar diretório de dados
    data_dir = Path("demo_intent_data")
    data_dir.mkdir(exist_ok=True)

    # Inicializar interpretador
    interpreter = IntentInterpreter(data_dir)

    print("\n📝 Testando interpretação de comandos diretos...")

    # Testar comandos diretos
    direct_commands = [
        "Crie uma função para calcular fibonacci",
        "Execute o script de teste",
        "Delete o arquivo temporário",
        "Modifique a configuração do banco de dados",
    ]

    for command in direct_commands:
        intent = interpreter.interpret(command)
        print(f"  Comando: '{command}'")
        print(f"    Tipo: {intent.intent_type.value}")
        print(f"    Confiança: {intent.confidence:.2f}")
        print(f"    Risco: {intent.risk_level.value}")
        print(f"    Confirmação necessária: {intent.requires_confirmation}")
        if intent.action:
            print(f"    Ação: {intent.action}")
        print()

    print("\n💡 Testando interpretação de sugestões...")

    # Testar sugestões
    suggestions = [
        "Que tal implementar um sistema de cache?",
        "Talvez você poderia otimizar essa função",
        "Considere usar async/await aqui",
        "Seria bom adicionar validação de entrada",
    ]

    for suggestion in suggestions:
        intent = interpreter.interpret(suggestion)
        print(f"  Sugestão: '{suggestion}'")
        print(f"    Tipo: {intent.intent_type.value}")
        print(f"    Confiança: {intent.confidence:.2f}")
        print(f"    Risco: {intent.risk_level.value}")
        print()

    print("\n❓ Testando interpretação de perguntas...")

    # Testar perguntas
    questions = [
        "Como funciona essa função?",
        "Qual é a melhor prática para tratamento de erros?",
        "Onde está definido esse parâmetro?",
        "Por que o teste está falhando?",
    ]

    for question in questions:
        intent = interpreter.interpret(question)
        print(f"  Pergunta: '{question}'")
        print(f"    Tipo: {intent.intent_type.value}")
        print(f"    Confiança: {intent.confidence:.2f}")
        print()

    print("\n⚠️  Testando detecção de ambiguidades...")

    # Testar comandos ambíguos
    ambiguous_commands = [
        "Talvez delete esse arquivo ou não",
        "Pode ser que a função precise ser alterada",
        "Não sei se devemos implementar isso",
        "Qualquer uma das opções pode funcionar",
    ]

    for command in ambiguous_commands:
        intent = interpreter.interpret(command)
        print(f"  Comando ambíguo: '{command}'")
        print(f"    Tipo: {intent.intent_type.value}")
        print(f"    Confiança: {intent.confidence:.2f}")
        print(f"    Ambigüidades: {len(intent.ambiguities)}")
        for ambiguity in intent.ambiguities[:2]:  # Mostrar até 2
            print(f"      - {ambiguity}")
        print()

    print("\n🚨 Testando avaliação de risco...")

    # Testar comandos de diferentes níveis de risco
    risk_commands = [
        ("Mostre o conteúdo do arquivo", RiskLevel.LOW),
        ("Crie um novo arquivo de configuração", RiskLevel.MEDIUM),
        ("Delete todos os arquivos de log", RiskLevel.HIGH),
        ("Formate o disco rígido", RiskLevel.CRITICAL),
    ]

    for command, expected_risk in risk_commands:
        intent = interpreter.interpret(command)
        print(f"  Comando: '{command}'")
        print(f"    Risco detectado: {intent.risk_level.value}")
        print(f"    Risco esperado: {expected_risk.value}")
        print(f"    Confirmação necessária: {intent.requires_confirmation}")
        print()

    print("\n✅ Testando validação de segurança...")

    # Testar validação de segurança
    test_intents = [
        ("Crie uma função simples", "Deveria ser seguro"),
        ("Delete o banco de dados", "Deveria requerer confirmação"),
        ("O que é uma variável?", "Pergunta segura"),
    ]

    for command, description in test_intents:
        intent = interpreter.interpret(command)
        is_safe, reason = interpreter.validate_intent_safety(intent)
        print(f"  Comando: '{command}'")
        print(f"    Descrição: {description}")
        print(f"    Seguro: {is_safe}")
        if reason:
            print(f"    Motivo: {reason}")
        print()

    print("\n📊 Gerando relatório de interpretações...")

    # Obter histórico
    history = interpreter.get_interpretation_history(10)

    print("\n📋 RESUMO DAS INTERPRETAÇÕES:")
    print("=" * 50)
    print(f"Total de interpretações realizadas: {len(history)}")

    # Contar tipos
    type_counts = {}
    risk_counts = {}
    confirmation_count = 0

    for entry in history:
        intent_type = entry['intent_type']
        risk_level = entry['risk_level']
        requires_conf = entry['requires_confirmation']

        type_counts[intent_type] = type_counts.get(intent_type, 0) + 1
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        if requires_conf:
            confirmation_count += 1

    print(f"Distribuição por tipo de intenção: {type_counts}")
    print(f"Distribuição por nível de risco: {risk_counts}")
    print(f"Interpretações que requerem confirmação: {confirmation_count}")

    print("\n🎯 Exemplos de interpretações bem-sucedidas:")
    successful = [h for h in history if h['confidence'] >= 0.7][:3]
    for entry in successful:
        print(f"  '{entry['user_input'][:50]}...' → {entry['intent_type']} (confiança: {entry['confidence']:.2f})")

    print("\n⚠️  Exemplos que necessitam esclarecimento:")
    needs_clarification = [h for h in history if h.get('ambiguities', [])][:2]
    for entry in needs_clarification:
        print(f"  '{entry['user_input'][:50]}...' → {len(entry.get('ambiguities', []))} ambiguidades detectadas")

    print("\n✅ Demo standalone de interpretação de intenção concluído!")

if __name__ == "__main__":
    asyncio.run(demo_intent_interpretation())