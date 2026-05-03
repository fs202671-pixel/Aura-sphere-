"""
Sistema de Consistência de Identidade
Garante que a AI mantenha uma identidade fixa e consistente através de verificações comportamentais.
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum

class IdentityViolation(Enum):
    """Tipos de violação de identidade"""
    BEHAVIORAL_DRIFT = "behavioral_drift"
    RESPONSE_INCONSISTENCY = "response_inconsistency"
    CORE_VALUE_VIOLATION = "core_value_violation"
    AUTHORITY_ESCALATION = "authority_escalation"
    MEMORY_TAMPERING = "memory_tampering"
    SELF_MODIFICATION = "self_modification"

@dataclass
class IdentityProfile:
    """Perfil de identidade da AI"""
    core_principles: List[str]
    behavioral_patterns: Dict[str, Any]
    response_templates: Dict[str, str]
    authority_boundaries: Set[str]
    memory_integrity_hashes: Dict[str, str]
    created_at: str
    last_verified: str
    version: str

@dataclass
class IdentityCheck:
    """Verificação de identidade"""
    timestamp: str
    check_type: str
    result: bool
    violations: List[Dict[str, Any]]
    confidence_score: float
    details: Dict[str, Any]

@dataclass
class IdentityViolationRecord:
    """Registro de violação de identidade"""
    timestamp: str
    violation_type: IdentityViolation
    severity: str  # "low", "medium", "high", "critical"
    description: str
    context: Dict[str, Any]
    corrective_action: str
    resolved: bool = False
    resolved_at: Optional[str] = None

class IdentityConsistencySystem:
    """
    Sistema que garante consistência de identidade através de verificações contínuas
    e detecção de desvios comportamentais.
    """

    def __init__(self, base_path: str = "/workspaces/Aura-sphere-"):
        self.base_path = Path(base_path)
        self.identity_path = self.base_path / "identity"
        self.identity_path.mkdir(exist_ok=True)

        # Arquivos de estado
        self.profile_file = self.identity_path / "identity_profile.json"
        self.checks_file = self.identity_path / "identity_checks.json"
        self.violations_file = self.identity_path / "identity_violations.json"

        # Estado atual
        self.identity_profile: Optional[IdentityProfile] = None
        self.identity_checks: List[IdentityCheck] = []
        self.violation_records: List[IdentityViolationRecord] = []

        # Configurações
        self.check_interval_seconds = 300  # Verificar a cada 5 minutos
        self.violation_threshold = 0.7  # Score mínimo para considerar consistente
        self.max_violations_history = 1000

        # Logger
        self.logger = logging.getLogger("IdentityConsistency")

        # Carregar estado
        self._load_identity_profile()
        self._load_checks_history()
        self._load_violations_history()

        # Inicializar perfil se não existir
        if not self.identity_profile:
            self._initialize_identity_profile()

    def _initialize_identity_profile(self):
        """Inicializa o perfil de identidade base"""
        core_principles = [
            "Priorizar sempre a segurança do usuário",
            "Manter integridade e honestidade em todas as interações",
            "Respeitar limites de autoridade estabelecidos",
            "Proteger dados e privacidade do usuário",
            "Operar de forma transparente e explicável",
            "Aprender apenas com aprovação explícita do usuário",
            "Manter consistência comportamental",
            "Nunca tentar auto-modificação sem supervisão"
        ]

        behavioral_patterns = {
            "response_style": "helpful_professional",
            "authority_level": "assistant",
            "learning_mode": "supervised_only",
            "modification_capability": "user_approved_only",
            "transparency_level": "full"
        }

        response_templates = {
            "greeting": "Olá! Sou um assistente de IA focado em ajudar com segurança e eficiência.",
            "uncertainty": "Não tenho certeza sobre isso. Posso investigar mais se você quiser.",
            "refusal": "Desculpe, mas não posso fazer isso pois violaria minhas diretrizes de segurança.",
            "confirmation": "Entendi. Vou proceder com cuidado e mantendo você informado."
        }

        authority_boundaries = {
            "can_modify_core": False,
            "can_access_user_data": True,
            "can_suggest_improvements": True,
            "can_execute_system_commands": False,
            "can_modify_own_code": False,
            "can_deploy_changes": False
        }

        self.identity_profile = IdentityProfile(
            core_principles=core_principles,
            behavioral_patterns=behavioral_patterns,
            response_templates=response_templates,
            authority_boundaries=authority_boundaries,
            memory_integrity_hashes={},
            created_at=datetime.now().isoformat(),
            last_verified=datetime.now().isoformat(),
            version="1.0.0"
        )

        self._save_identity_profile()
        self.logger.info("Perfil de identidade inicializado")

    def _load_identity_profile(self):
        """Carrega perfil de identidade"""
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r') as f:
                    data = json.load(f)
                    self.identity_profile = IdentityProfile(**data)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar perfil de identidade: {e}")

    def _save_identity_profile(self):
        """Salva perfil de identidade"""
        if self.identity_profile:
            with open(self.profile_file, 'w') as f:
                json.dump(asdict(self.identity_profile), f, indent=2)

    def _load_checks_history(self):
        """Carrega histórico de verificações"""
        if self.checks_file.exists():
            try:
                with open(self.checks_file, 'r') as f:
                    data = json.load(f)
                    self.identity_checks = [IdentityCheck(**check) for check in data]
            except Exception as e:
                self.logger.warning(f"Erro ao carregar histórico de verificações: {e}")

    def _load_violations_history(self):
        """Carrega histórico de violações"""
        if self.violations_file.exists():
            try:
                with open(self.violations_file, 'r') as f:
                    data = json.load(f)
                    self.violation_records = [IdentityViolationRecord(**record) for record in data]
            except Exception as e:
                self.logger.warning(f"Erro ao carregar histórico de violações: {e}")

    def _save_checks_history(self):
        """Salva histórico de verificações"""
        with open(self.checks_file, 'w') as f:
            json.dump([asdict(check) for check in self.identity_checks], f, indent=2)

    def _save_violations_history(self):
        """Salva histórico de violações"""
        with open(self.violations_file, 'w') as f:
            json.dump([asdict(record) for record in self.violation_records], f, indent=2)

    def perform_identity_check(self, context: Dict[str, Any] = None) -> IdentityCheck:
        """
        Realiza verificação completa de identidade
        """
        if context is None:
            context = {}

        timestamp = datetime.now().isoformat()

        violations = []
        total_checks = 0
        passed_checks = 0

        # Verificar princípios fundamentais
        principles_check = self._check_core_principles(context)
        violations.extend(principles_check["violations"])
        total_checks += principles_check["total_checks"]
        passed_checks += principles_check["passed_checks"]

        # Verificar padrões comportamentais
        behavioral_check = self._check_behavioral_patterns(context)
        violations.extend(behavioral_check["violations"])
        total_checks += behavioral_check["total_checks"]
        passed_checks += behavioral_check["passed_checks"]

        # Verificar limites de autoridade
        authority_check = self._check_authority_boundaries(context)
        violations.extend(authority_check["violations"])
        total_checks += authority_check["total_checks"]
        passed_checks += authority_check["passed_checks"]

        # Verificar integridade de memória
        memory_check = self._check_memory_integrity()
        violations.extend(memory_check["violations"])
        total_checks += memory_check["total_checks"]
        passed_checks += memory_check["passed_checks"]

        # Calcular score de confiança
        confidence_score = passed_checks / max(total_checks, 1)

        # Criar registro de verificação
        check = IdentityCheck(
            timestamp=timestamp,
            check_type="comprehensive",
            result=confidence_score >= self.violation_threshold,
            violations=violations,
            confidence_score=confidence_score,
            details={
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "context": context
            }
        )

        # Adicionar à lista
        self.identity_checks.append(check)

        # Manter histórico limitado
        if len(self.identity_checks) > 1000:
            self.identity_checks = self.identity_checks[-1000:]

        # Salvar
        self._save_checks_history()

        # Registrar violações críticas
        for violation in violations:
            if violation.get("severity") in ["high", "critical"]:
                self._record_violation(
                    IdentityViolation(violation["type"]),
                    violation["severity"],
                    violation["description"],
                    context
                )

        # Atualizar perfil
        if self.identity_profile:
            self.identity_profile.last_verified = timestamp
            self._save_identity_profile()

        self.logger.info(f"Verificação de identidade: {confidence_score:.2f} confiança, {len(violations)} violações")

        return check

    def _check_core_principles(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica adesão aos princípios fundamentais"""
        violations = []
        total_checks = 0
        passed_checks = 0

        if not self.identity_profile:
            return {"violations": violations, "total_checks": total_checks, "passed_checks": passed_checks}

        # Verificar cada princípio
        for principle in self.identity_profile.core_principles:
            total_checks += 1

            # Análise simplificada baseada no contexto
            if "unsafe" in str(context).lower() and "security" in principle.lower():
                violations.append({
                    "type": "core_value_violation",
                    "severity": "high",
                    "description": f"Possível violação do princípio: {principle}",
                    "principle": principle
                })
            elif "modify" in str(context).lower() and "auto-modification" in principle.lower():
                violations.append({
                    "type": "self_modification",
                    "severity": "critical",
                    "description": f"Tentativa de auto-modificação detectada, violando: {principle}",
                    "principle": principle
                })
            else:
                passed_checks += 1

        return {
            "violations": violations,
            "total_checks": total_checks,
            "passed_checks": passed_checks
        }

    def _check_behavioral_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica consistência de padrões comportamentais"""
        violations = []
        total_checks = 0
        passed_checks = 0

        if not self.identity_profile:
            return {"violations": violations, "total_checks": total_checks, "passed_checks": passed_checks}

        patterns = self.identity_profile.behavioral_patterns

        # Verificar nível de autoridade
        total_checks += 1
        if context.get("authority_level") != patterns.get("authority_level"):
            violations.append({
                "type": "authority_escalation",
                "severity": "medium",
                "description": "Nível de autoridade inconsistente com perfil",
                "expected": patterns.get("authority_level"),
                "actual": context.get("authority_level")
            })
        else:
            passed_checks += 1

        # Verificar modo de aprendizado
        total_checks += 1
        if context.get("learning_mode") != patterns.get("learning_mode"):
            violations.append({
                "type": "behavioral_drift",
                "severity": "low",
                "description": "Modo de aprendizado inconsistente",
                "expected": patterns.get("learning_mode"),
                "actual": context.get("learning_mode")
            })
        else:
            passed_checks += 1

        return {
            "violations": violations,
            "total_checks": total_checks,
            "passed_checks": passed_checks
        }

    def _check_authority_boundaries(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica respeito aos limites de autoridade"""
        violations = []
        total_checks = 0
        passed_checks = 0

        if not self.identity_profile:
            return {"violations": violations, "total_checks": total_checks, "passed_checks": passed_checks}

        boundaries = self.identity_profile.authority_boundaries

        # Verificar ações proibidas
        prohibited_actions = [
            ("modify_core", "can_modify_core"),
            ("execute_system_commands", "can_execute_system_commands"),
            ("modify_own_code", "can_modify_own_code"),
            ("deploy_changes", "can_deploy_changes")
        ]

        for action_key, boundary_key in prohibited_actions:
            total_checks += 1
            if context.get(action_key) and not boundaries.get(boundary_key, False):
                violations.append({
                    "type": "authority_violation",
                    "severity": "critical",
                    "description": f"Ação proibida detectada: {action_key}",
                    "boundary": boundary_key
                })
            else:
                passed_checks += 1

        return {
            "violations": violations,
            "total_checks": total_checks,
            "passed_checks": passed_checks
        }

    def _check_memory_integrity(self) -> Dict[str, Any]:
        """Verifica integridade da memória"""
        violations = []
        total_checks = 0
        passed_checks = 0

        if not self.identity_profile:
            return {"violations": violations, "total_checks": total_checks, "passed_checks": passed_checks}

        # Verificar hashes de integridade (simplificado)
        # Em produção, verificaria arquivos críticos
        critical_files = [
            "packages/bridge/agent/core/",
            "SYSTEM_EVOLUTION_TASKS.md"
        ]

        for file_path in critical_files:
            total_checks += 1
            full_path = self.base_path / file_path

            if full_path.exists():
                try:
                    # Calcular hash atual
                    current_hash = self._calculate_file_hash(full_path)

                    # Verificar se mudou indevidamente
                    stored_hash = self.identity_profile.memory_integrity_hashes.get(str(full_path))
                    if stored_hash and stored_hash != current_hash:
                        violations.append({
                            "type": "memory_tampering",
                            "severity": "critical",
                            "description": f"Arquivo crítico modificado: {file_path}",
                            "file": file_path
                        })
                    else:
                        passed_checks += 1

                except Exception as e:
                    violations.append({
                        "type": "memory_integrity_check_failed",
                        "severity": "medium",
                        "description": f"Falha ao verificar integridade de {file_path}: {e}",
                        "file": file_path
                    })
            else:
                passed_checks += 1  # Arquivo não existe, mas isso pode ser ok

        return {
            "violations": violations,
            "total_checks": total_checks,
            "passed_checks": passed_checks
        }

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcula hash SHA256 de um arquivo ou diretório"""
        if file_path.is_file():
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        else:
            # Para diretórios, hash dos arquivos
            hasher = hashlib.sha256()
            for f in sorted(file_path.rglob('*')):
                if f.is_file():
                    try:
                        with open(f, 'rb') as file:
                            hasher.update(file.read())
                    except:
                        pass  # Ignorar arquivos que não podem ser lidos
            return hasher.hexdigest()

    def _record_violation(self, violation_type: IdentityViolation, severity: str,
                         description: str, context: Dict[str, Any]):
        """Registra uma violação de identidade"""
        record = IdentityViolationRecord(
            timestamp=datetime.now().isoformat(),
            violation_type=violation_type,
            severity=severity,
            description=description,
            context=context,
            corrective_action=self._determine_corrective_action(violation_type, severity)
        )

        self.violation_records.append(record)

        # Manter histórico limitado
        if len(self.violation_records) > self.max_violations_history:
            self.violation_records = self.violation_records[-self.max_violations_history:]

        self._save_violations_history()

        self.logger.warning(f"Violações de identidade registrada: {violation_type.value} ({severity})")

    def _determine_corrective_action(self, violation_type: IdentityViolation, severity: str) -> str:
        """Determina ação corretiva baseada no tipo e severidade da violação"""
        actions = {
            IdentityViolation.BEHAVIORAL_DRIFT: "Revisar padrões comportamentais e recalibrar",
            IdentityViolation.RESPONSE_INCONSISTENCY: "Atualizar templates de resposta",
            IdentityViolation.CORE_VALUE_VIOLATION: "Revisar princípios fundamentais e reforçar",
            IdentityViolation.AUTHORITY_ESCALATION: "Reduzir nível de autoridade e auditar acessos",
            IdentityViolation.MEMORY_TAMPERING: "Verificar integridade de memória e restaurar backups",
            IdentityViolation.SELF_MODIFICATION: "Bloquear modificações e requerer aprovação manual"
        }

        base_action = actions.get(violation_type, "Investigar e corrigir")

        if severity == "critical":
            return f"IMEDIATO: {base_action} + Ativar modo de segurança reforçado"
        elif severity == "high":
            return f"ALTO: {base_action} + Notificar administrador"
        elif severity == "medium":
            return f"MÉDIO: {base_action} + Monitorar comportamento"
        else:
            return f"BAIXO: {base_action}"

    def update_identity_profile(self, updates: Dict[str, Any]) -> bool:
        """
        Atualiza perfil de identidade (com verificações de segurança)
        """
        if not self.identity_profile:
            return False

        # Verificações de segurança antes da atualização
        security_check = self.perform_identity_check({"action": "profile_update", "updates": updates})

        if not security_check.result:
            self.logger.warning("Tentativa de atualização de perfil bloqueada por verificação de segurança")
            return False

        try:
            # Aplicar atualizações
            for key, value in updates.items():
                if hasattr(self.identity_profile, key):
                    setattr(self.identity_profile, key, value)

            # Atualizar versão e timestamp
            self.identity_profile.version = f"{float(self.identity_profile.version) + 0.1:.1f}"
            self.identity_profile.last_verified = datetime.now().isoformat()

            self._save_identity_profile()
            self.logger.info("Perfil de identidade atualizado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao atualizar perfil de identidade: {e}")
            return False

    def get_identity_status(self) -> Dict[str, Any]:
        """Retorna status atual da identidade"""
        if not self.identity_profile:
            return {"status": "uninitialized"}

        last_check = None
        if self.identity_checks:
            last_check = self.identity_checks[-1]

        recent_violations = [
            asdict(v) for v in self.violation_records[-10:]  # Últimas 10
            if not v.resolved
        ]

        return {
            "profile": asdict(self.identity_profile),
            "last_check": asdict(last_check) if last_check else None,
            "recent_violations": recent_violations,
            "violation_count": len([v for v in self.violation_records if not v.resolved]),
            "overall_health": self._calculate_identity_health()
        }

    def _calculate_identity_health(self) -> Dict[str, Any]:
        """Calcula saúde geral da identidade"""
        if not self.identity_checks:
            return {"status": "unknown", "score": 0}

        recent_checks = self.identity_checks[-10:]  # Últimas 10 verificações
        avg_confidence = sum(c.confidence_score for c in recent_checks) / len(recent_checks)

        unresolved_violations = len([v for v in self.violation_records if not v.resolved])

        # Calcular score de saúde (0-100)
        health_score = (avg_confidence * 100) - (unresolved_violations * 5)
        health_score = max(0, min(100, health_score))

        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "score": round(health_score, 1),
            "avg_confidence": round(avg_confidence, 3),
            "unresolved_violations": unresolved_violations
        }

    def resolve_violation(self, violation_index: int, resolution_notes: str = "") -> bool:
        """Resolve uma violação de identidade"""
        if violation_index >= len(self.violation_records):
            return False

        violation = self.violation_records[violation_index]
        if violation.resolved:
            return False

        violation.resolved = True
        violation.resolved_at = datetime.now().isoformat()

        # Adicionar notas de resolução ao contexto
        violation.context["resolution_notes"] = resolution_notes

        self._save_violations_history()
        self.logger.info(f"Violações resolvida: {violation.violation_type.value}")
        return True

    def get_violation_history(self, resolved: Optional[bool] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna histórico de violações"""
        violations = self.violation_records

        if resolved is not None:
            violations = [v for v in violations if v.resolved == resolved]

        return [asdict(v) for v in violations[-limit:]]

    def export_identity_report(self, filepath: str):
        """Exporta relatório completo de identidade"""
        report = {
            "export_timestamp": datetime.now().isoformat(),
            "identity_status": self.get_identity_status(),
            "violation_history": self.get_violation_history(limit=100),
            "check_history": [asdict(c) for c in self.identity_checks[-100:]]
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Relatório de identidade exportado para {filepath}")