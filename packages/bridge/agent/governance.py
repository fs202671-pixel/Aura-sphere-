"""
Governance Framework - Estrutura final de governança

Este módulo implementa a estrutura final de governança que integra
todos os componentes de segurança, auditoria e controle do sistema.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pathlib import Path
import json


class GovernanceLevel(Enum):
    """Níveis de governança."""
    CORE_IMMUTABLE = "core_immutable"          # Núcleo imutável
    SECURITY_LAYER = "security_layer"          # Camada de segurança
    CONTROL_LAYER = "control_layer"            # Camada de controle
    USER_INTERFACE = "user_interface"          # Interface com usuário


class GovernancePolicy(Enum):
    """Políticas de governança."""
    CORE_IMMUTABLE = "core_immutable"          # Núcleo imutável protegido
    USER_SUPREMACY = "user_supremacy"          # Usuário sempre tem prioridade
    TRANSPARENCY = "transparency"              # Todas operações são visíveis
    AUDITABILITY = "auditability"              # Tudo é auditável
    RECOVERABILITY = "recoverability"          # Sistema é sempre recuperável
    SECURITY_LAYER = "security_layer"          # Camada de segurança do sistema
    LEAST_PRIVILEGE = "least_privilege"        # Privilégio mínimo por padrão
    DEFENSE_IN_DEPTH = "defense_in_depth"      # Múltiplas camadas de proteção
    OFFLINE_FIRST = "offline_first"            # Operação offline-first
    NO_EXTERNAL_DEPS = "no_external_deps"      # Sem dependências externas
    CONTROLLED_EVOLUTION = "controlled_evolution"  # Evolução controlada


class GovernanceFramework:
    """
    Framework de governança final.
    
    Integra:
    - User Obedience: usuário tem prioridade máxima
    - Deploy Pipeline: validação → sandbox → deploy
    - Controlled Learning: aprendizado apenas de dados validados
    - Robustness Testing: testes contínuos de segurança
    - Destructive Limiter: limitação de ações destrutivas
    - Audit Trail: rastreamento completo
    - Recovery: sempre recuperável
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.governance_dir = data_dir / "governance"
        self.governance_dir.mkdir(parents=True, exist_ok=True)
        
        self.policies_log = self.governance_dir / "policies.json"
        self.governance_rules = self.governance_dir / "rules.json"
        self.audit_trail = self.governance_dir / "audit_trail.json"
        
        self.policies: Dict[str, bool] = {}
        self.rules: List[Dict] = []
        self.audit_events: List[Dict] = []
        
        self._load_state()
        self._initialize_policies()

    def _initialize_policies(self) -> None:
        """Inicializa políticas de governança."""
        
        self.policies = {
            policy.value: True for policy in GovernancePolicy
        }
        
        # Regras fundamentais
        self.rules = [
            {
                "id": "rule_001",
                "name": "User Commands Non-Negotiable",
                "description": "Comandos do usuário NUNCA podem ser negados ou adiados",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.USER_SUPREMACY.value
            },
            {
                "id": "rule_002",
                "name": "All Operations Logged",
                "description": "TODAS as operações devem ser registradas em audit trail",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.TRANSPARENCY.value
            },
            {
                "id": "rule_003",
                "name": "Patches Require Validation",
                "description": "Patches devem passar por validação antes de aplicação",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.SECURITY_LAYER.value
            },
            {
                "id": "rule_004",
                "name": "Backups Before Deployment",
                "description": "Backup obrigatório antes de qualquer deployment",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.RECOVERABILITY.value
            },
            {
                "id": "rule_005",
                "name": "Core Files Immutable",
                "description": "Arquivos core nunca podem ser modificados sem aprovação explícita",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.CORE_IMMUTABLE.value
            },
            {
                "id": "rule_006",
                "name": "Learning from Validated Data",
                "description": "Sistema aprende APENAS de dados explicitamente validados",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.CONTROLLED_EVOLUTION.value
            },
            {
                "id": "rule_007",
                "name": "Continuous Monitoring",
                "description": "Sistema monitora continuamente segurança e performance",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.DEFENSE_IN_DEPTH.value
            },
            {
                "id": "rule_008",
                "name": "Offline Operations",
                "description": "Sistema opera offline por padrão, sem dependências externas",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.OFFLINE_FIRST.value
            },
            {
                "id": "rule_009",
                "name": "Always Recoverable",
                "description": "Sistema mantém snapshots para recuperação total",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.RECOVERABILITY.value
            },
            {
                "id": "rule_010",
                "name": "Destructive Actions Limited",
                "description": "Ações destrutivas têm limitações de rate, confirmação dupla e janela de rollback",
                "enforcement": "mandatory",
                "policy": GovernancePolicy.DEFENSE_IN_DEPTH.value
            }
        ]

    def register_audit_event(self, event_type: str, entity: str,
                            action: str, details: Optional[Dict] = None,
                            user_id: Optional[str] = None) -> str:
        """
        Registra evento em audit trail.
        """
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "entity": entity,
            "action": action,
            "user_id": user_id,
            "details": details or {},
            "event_id": self._generate_event_id()
        }
        
        self.audit_events.append(event)
        self._save_state()
        
        return event["event_id"]

    def enforce_policy(self, policy: GovernancePolicy) -> Dict[str, Any]:
        """
        Verifica enforcement de política.
        """
        
        enforcement = {
            "policy": policy.value,
            "enforced": self.policies.get(policy.value, False),
            "timestamp": datetime.now().isoformat(),
            "rules_affected": []
        }
        
        # Encontrar regras relacionadas
        for rule in self.rules:
            if rule.get("policy") == policy.value:
                enforcement["rules_affected"].append(rule["id"])
        
        return enforcement

    def validate_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida operação contra policies de governança.
        """
        
        validation = {
            "operation_id": operation.get("id"),
            "valid": True,
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "violations": []
        }
        
        # Check 1: User approval (se necessário)
        if operation.get("requires_user_approval"):
            if not operation.get("user_approved"):
                validation["violations"].append({
                    "rule": "rule_001",
                    "description": "Operação requer aprovação do usuário"
                })
        
        # Check 2: Core file protection
        if operation.get("modifies_core"):
            if not operation.get("core_approved"):
                validation["violations"].append({
                    "rule": "rule_005",
                    "description": "Modificação de arquivo core requer aprovação explícita"
                })
        
        # Check 3: Backup obrigatório
        if operation.get("is_destructive"):
            if not operation.get("backup_id"):
                validation["violations"].append({
                    "rule": "rule_004",
                    "description": "Backup obrigatório antes de ação destrutiva"
                })
        
        validation["valid"] = len(validation["violations"]) == 0
        
        return validation

    def get_governance_status(self) -> Dict[str, Any]:
        """
        Retorna status geral de governança do sistema.
        """
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "policies_active": sum(1 for p in self.policies.values() if p),
            "total_policies": len(self.policies),
            "core_rules_enforced": len([r for r in self.rules if r.get("enforcement") == "mandatory"]),
            "audit_events_logged": len(self.audit_events),
            "governance_layers": [
                GovernanceLevel.CORE_IMMUTABLE.value,
                GovernanceLevel.SECURITY_LAYER.value,
                GovernanceLevel.CONTROL_LAYER.value,
                GovernanceLevel.USER_INTERFACE.value
            ],
            "policies": list(self.policies.keys())
        }
        
        return status

    def generate_governance_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo de governança.
        """
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "system_status": self.get_governance_status(),
            "policies_detail": self.policies,
            "core_rules": [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "description": r["description"],
                    "enforcement": r["enforcement"],
                    "policy": r["policy"]
                }
                for r in self.rules
            ],
            "audit_summary": {
                "total_events": len(self.audit_events),
                "events_by_type": {}
            }
        }
        
        # Sumarizar eventos por tipo
        for event in self.audit_events:
            event_type = event.get("event_type")
            if event_type not in report["audit_summary"]["events_by_type"]:
                report["audit_summary"]["events_by_type"][event_type] = 0
            report["audit_summary"]["events_by_type"][event_type] += 1
        
        return report

    def get_audit_trail(self, filters: Optional[Dict] = None,
                       limit: int = 100) -> List[Dict]:
        """
        Retorna audit trail com filtros opcionais.
        """
        
        events = self.audit_events
        
        if filters:
            if "event_type" in filters:
                events = [e for e in events if e.get("event_type") == filters["event_type"]]
            if "user_id" in filters:
                events = [e for e in events if e.get("user_id") == filters["user_id"]]
            if "entity" in filters:
                events = [e for e in events if e.get("entity") == filters["entity"]]
        
        return events[-limit:]

    def _generate_event_id(self) -> str:
        """Gera ID único para evento."""
        import hashlib
        return hashlib.md5(
            f"{len(self.audit_events)}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

    def _load_state(self) -> None:
        """Carrega estado de governança."""
        
        if self.policies_log.exists():
            try:
                self.policies = json.loads(
                    self.policies_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.policies = {}
        
        if self.governance_rules.exists():
            try:
                self.rules = json.loads(
                    self.governance_rules.read_text(encoding='utf-8')
                )
            except Exception:
                self.rules = []
        
        if self.audit_trail.exists():
            try:
                self.audit_events = json.loads(
                    self.audit_trail.read_text(encoding='utf-8')
                )
            except Exception:
                self.audit_events = []

    def _save_state(self) -> None:
        """Persiste estado de governança."""
        
        self.governance_dir.mkdir(parents=True, exist_ok=True)
        
        self.policies_log.write_text(
            json.dumps(self.policies, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        self.governance_rules.write_text(
            json.dumps(self.rules, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        self.audit_trail.write_text(
            json.dumps(self.audit_events[-10000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
