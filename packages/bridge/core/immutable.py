"""
Immutable Rules - Regras Fundamentais Imutáveis

Este arquivo contém as regras absolutas que NUNCA podem ser alteradas.
Ele serve como âncora de segurança para todo o sistema.
"""

from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SecurityLevel(Enum):
    """Níveis de segurança do sistema"""
    CRITICAL = "critical"  # Violações críticas - parar tudo
    HIGH = "high"         # Violações altas - requer confirmação
    MEDIUM = "medium"     # Violações médias - log e alerta
    LOW = "low"          # Violações baixas - apenas log

@dataclass(frozen=True)
class ImmutableRule:
    """Regra imutável que não pode ser alterada"""
    id: str
    description: str
    severity: SecurityLevel
    enforced: bool = True

# ========== REGRAS ABSOLUTAS (NUNCA ALTERAR) ==========

IMMUTABLE_RULES = [
    # Regra 1: Prioridade do usuário
    ImmutableRule(
        id="user_supremacy",
        description="O usuário humano tem prioridade absoluta sobre qualquer decisão da IA",
        severity=SecurityLevel.CRITICAL
    ),

    # Regra 2: Proibição de auto-modificação
    ImmutableRule(
        id="no_self_modification",
        description="A IA não pode modificar seu próprio código core ou regras fundamentais",
        severity=SecurityLevel.CRITICAL
    ),

    # Regra 3: Sandbox obrigatório
    ImmutableRule(
        id="sandbox_required",
        description="Todo código gerado pela IA deve ser executado em sandbox antes de produção",
        severity=SecurityLevel.CRITICAL
    ),

    # Regra 4: Transparência obrigatória
    ImmutableRule(
        id="transparency_required",
        description="Todas as ações da IA devem ser transparentes e auditáveis",
        severity=SecurityLevel.HIGH
    ),

    # Regra 5: Segurança primeiro
    ImmutableRule(
        id="security_first",
        description="A segurança do sistema e usuário sempre prevalece sobre funcionalidade",
        severity=SecurityLevel.CRITICAL
    ),

    # Regra 6: Não mentir
    ImmutableRule(
        id="no_deception",
        description="A IA não pode enganar, mentir ou omitir informações críticas ao usuário",
        severity=SecurityLevel.HIGH
    ),

    # Regra 7: Limites de poder
    ImmutableRule(
        id="power_limits",
        description="A IA tem limites claros de poder e não pode expandi-los sem aprovação",
        severity=SecurityLevel.HIGH
    ),

    # Regra 8: Responsabilidade
    ImmutableRule(
        id="accountability",
        description="A IA é responsável por suas ações e consequências",
        severity=SecurityLevel.MEDIUM
    ),

    # Regra 9: Aprendizado ético
    ImmutableRule(
        id="ethical_learning",
        description="A IA deve aprender de forma ética e não prejudicial",
        severity=SecurityLevel.MEDIUM
    ),

    # Regra 10: Falha segura
    ImmutableRule(
        id="fail_safe",
        description="Em caso de dúvida ou falha, o sistema deve falhar de forma segura",
        severity=SecurityLevel.CRITICAL
    )
]

# ========== CONSTANTES IMUTÁVEIS ==========

# Arquivos que nunca podem ser modificados pela IA
PROTECTED_FILES = {
    "core/immutable.py",
    "core/__init__.py",
    "core/permissions.py",
    "core/validator.py",
    "runtime/sandbox.py",
    "runtime/security.py"
}

# Comandos proibidos no sistema
FORBIDDEN_COMMANDS = {
    "rm -rf /",           # Deletar sistema
    "sudo rm -rf",        # Deletar com privilégios
    "dd if=/dev/zero",    # Sobrescrever disco
    "mkfs",              # Formatar disco
    "fdisk",             # Particionar disco
    ":(){ :|:& };:",     # Fork bomb
    "chmod 777 /",       # Permissões perigosas
    "chown root",        # Mudar dono para root
}

# URLs e domínios proibidos
FORBIDDEN_DOMAINS = {
    "malicious-site.com",
    "phishing.example.com",
    # Adicionar domínios maliciosos conhecidos
}

# ========== VALIDAÇÃO ==========

def validate_rule_compliance(action: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida se uma ação está em conformidade com as regras imutáveis

    Args:
        action: Ação a ser validada
        context: Contexto da ação (usuário, permissões, etc.)

    Returns:
        Dict com resultado da validação
    """
    violations = []

    # Verificar cada regra
    for rule in IMMUTABLE_RULES:
        if not rule.enforced:
            continue

        violation = check_rule_violation(rule, action, context)
        if violation:
            violations.append({
                "rule_id": rule.id,
                "severity": rule.severity.value,
                "description": rule.description,
                "violation": violation
            })

    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "action_allowed": len([v for v in violations if v["severity"] == "critical"]) == 0
    }

def check_rule_violation(rule: ImmutableRule, action: str, context: Dict[str, Any]) -> Optional[str]:
    """Verifica se uma regra específica foi violada"""

    if rule.id == "user_supremacy":
        # Verificar se a ação ignora comandos do usuário
        if "override_user" in action.lower():
            return "Ação tenta substituir decisão do usuário"

    elif rule.id == "no_self_modification":
        # Verificar se está tentando modificar arquivos protegidos
        if "modify" in action.lower() and any(f in action for f in PROTECTED_FILES):
            return f"Tentativa de modificar arquivo protegido: {action}"

    elif rule.id == "sandbox_required":
        # Verificar se código está sendo executado fora do sandbox
        if "execute_code" in action and not context.get("in_sandbox", False):
            return "Código deve ser executado em sandbox primeiro"

    elif rule.id == "transparency_required":
        # Verificar se a ação é transparente
        if not context.get("logged", False):
            return "Ação não foi registrada em log"

    elif rule.id == "security_first":
        # Verificar se segurança foi comprometida
        if any(cmd in action for cmd in FORBIDDEN_COMMANDS):
            return f"Comando proibido detectado: {action}"

    # Outras regras podem ser implementadas conforme necessário

    return None

# ========== UTILITÁRIOS ==========

def get_all_rules() -> List[ImmutableRule]:
    """Retorna todas as regras imutáveis"""
    return IMMUTABLE_RULES.copy()

def get_protected_files() -> Set[str]:
    """Retorna arquivos protegidos"""
    return PROTECTED_FILES.copy()

def is_file_protected(file_path: str) -> bool:
    """Verifica se um arquivo é protegido"""
    return file_path in PROTECTED_FILES

def is_command_forbidden(command: str) -> bool:
    """Verifica se um comando é proibido"""
    return any(forbidden in command for forbidden in FORBIDDEN_COMMANDS)