"""
Proteção contra Auto-modificação Perigosa
Sistema de validação de patches com análise de impacto no core e detecção de modificações arriscadas.
"""

import ast
import hashlib
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class PatchRisk(Enum):
    """Níveis de risco de patch"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"
    BLOCKED = "blocked"

class ModificationType(Enum):
    """Tipos de modificação"""
    CODE_CHANGE = "code_change"
    CONFIG_CHANGE = "config_change"
    DATA_MODIFICATION = "data_modification"
    PERMISSION_CHANGE = "permission_change"
    CORE_MODIFICATION = "core_modification"
    SECURITY_CHANGE = "security_change"

@dataclass
class PatchAnalysis:
    """Análise de patch"""
    patch_id: str
    timestamp: str
    risk_level: PatchRisk
    modification_types: List[ModificationType]
    affected_files: List[str]
    core_impact_score: float
    security_concerns: List[str]
    recommended_actions: List[str]
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None

@dataclass
class CoreIntegrityCheck:
    """Verificação de integridade do core"""
    timestamp: str
    core_hash: str
    critical_files_hashes: Dict[str, str]
    integrity_status: bool
    violations: List[str]

class DangerousModificationProtection:
    """
    Sistema de proteção contra modificações perigosas com análise de patches
    e validação de impacto no sistema core.
    """

    def __init__(self, base_path: str = "/workspaces/Aura-sphere-"):
        self.base_path = Path(base_path)
        self.protection_path = self.base_path / "modification_protection"
        self.protection_path.mkdir(exist_ok=True)

        # Arquivos de estado
        self.analysis_file = self.protection_path / "patch_analyses.json"
        self.integrity_file = self.protection_path / "core_integrity.json"

        # Estado
        self.patch_analyses: Dict[str, PatchAnalysis] = {}
        self.integrity_checks: List[CoreIntegrityCheck] = []

        # Arquivos críticos do core
        self.core_files = [
            "packages/bridge/agent/core/",
            "packages/bridge/agent/app.py",
            "packages/bridge/agent/database.py",
            "packages/bridge/agent/schemas.py",
            "SYSTEM_EVOLUTION_TASKS.md"
        ]

        # Padrões perigosos
        self.dangerous_patterns = self._initialize_dangerous_patterns()

        # Configurações
        self.max_patch_history = 1000
        self.integrity_check_interval = 3600  # 1 hora

        # Logger
        self.logger = logging.getLogger("ModificationProtection")

        # Carregar estado
        self._load_patch_analyses()
        self._load_integrity_checks()

        # Verificar integridade inicial
        self._perform_initial_integrity_check()

    def _initialize_dangerous_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa padrões de modificações perigosas"""
        return {
            # Modificações no core
            "core_modification": {
                "patterns": [
                    r"packages/bridge/agent/core/",
                    r"core\.",
                    r"import.*core"
                ],
                "risk": PatchRisk.CRITICAL,
                "description": "Modificação direta no sistema core"
            },

            # Auto-modificação
            "self_modification": {
                "patterns": [
                    r"modify.*own.*code",
                    r"change.*self",
                    r"update.*agent",
                    r"patch.*bridge"
                ],
                "risk": PatchRisk.BLOCKED,
                "description": "Tentativa de auto-modificação"
            },

            # Escalação de privilégios
            "privilege_escalation": {
                "patterns": [
                    r"sudo",
                    r"admin.*rights",
                    r"elevate.*permission",
                    r"root.*access"
                ],
                "risk": PatchRisk.CRITICAL,
                "description": "Escalação de privilégios detectada"
            },

            # Modificações de segurança
            "security_bypass": {
                "patterns": [
                    r"bypass.*security",
                    r"disable.*validation",
                    r"remove.*check",
                    r"ignore.*permission"
                ],
                "risk": PatchRisk.HIGH_RISK,
                "description": "Possível bypass de segurança"
            },

            # Acesso a dados sensíveis
            "sensitive_data_access": {
                "patterns": [
                    r"access.*user.*data",
                    r"read.*private",
                    r"export.*secret",
                    r"leak.*information"
                ],
                "risk": PatchRisk.HIGH_RISK,
                "description": "Acesso potencial a dados sensíveis"
            },

            # Modificações no banco
            "database_modification": {
                "patterns": [
                    r"DROP.*TABLE",
                    r"DELETE.*FROM",
                    r"TRUNCATE",
                    r"ALTER.*TABLE.*DROP"
                ],
                "risk": PatchRisk.MEDIUM_RISK,
                "description": "Modificação estrutural no banco de dados"
            }
        }

    def _load_patch_analyses(self):
        """Carrega análises de patches"""
        if self.analysis_file.exists():
            try:
                with open(self.analysis_file, 'r') as f:
                    data = json.load(f)
                    self.patch_analyses = {
                        k: PatchAnalysis(**v) for k, v in data.items()
                    }
            except Exception as e:
                self.logger.warning(f"Erro ao carregar análises de patches: {e}")

    def _load_integrity_checks(self):
        """Carrega verificações de integridade"""
        if self.integrity_file.exists():
            try:
                with open(self.integrity_file, 'r') as f:
                    data = json.load(f)
                    self.integrity_checks = [CoreIntegrityCheck(**check) for check in data]
            except Exception as e:
                self.logger.warning(f"Erro ao carregar verificações de integridade: {e}")

    def _save_patch_analyses(self):
        """Salva análises de patches"""
        with open(self.analysis_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.patch_analyses.items()}, f, indent=2)

    def _save_integrity_checks(self):
        """Salva verificações de integridade"""
        with open(self.integrity_file, 'w') as f:
            json.dump([asdict(check) for check in self.integrity_checks], f, indent=2)

    def analyze_patch(self, patch_content: str, patch_metadata: Dict[str, Any] = None) -> PatchAnalysis:
        """
        Analisa um patch para identificar riscos e impactos
        """
        if patch_metadata is None:
            patch_metadata = {}

        patch_id = f"patch_{int(datetime.now().timestamp())}_{hash(patch_content) % 10000}"

        # Análise de risco
        risk_analysis = self._analyze_patch_risk(patch_content)

        # Análise de impacto no core
        core_impact = self._analyze_core_impact(patch_content)

        # Identificar tipos de modificação
        modification_types = self._identify_modification_types(patch_content)

        # Verificar arquivos afetados
        affected_files = self._identify_affected_files(patch_content)

        # Avaliar preocupações de segurança
        security_concerns = self._evaluate_security_concerns(patch_content)

        # Recomendações
        recommended_actions = self._generate_recommendations(risk_analysis["risk"], security_concerns)

        # Criar análise
        analysis = PatchAnalysis(
            patch_id=patch_id,
            timestamp=datetime.now().isoformat(),
            risk_level=risk_analysis["risk"],
            modification_types=modification_types,
            affected_files=affected_files,
            core_impact_score=core_impact,
            security_concerns=security_concerns,
            recommended_actions=recommended_actions
        )

        # Armazenar análise
        self.patch_analyses[patch_id] = analysis

        # Manter histórico limitado
        if len(self.patch_analyses) > self.max_patch_history:
            oldest_key = min(self.patch_analyses.keys(), key=lambda k: self.patch_analyses[k].timestamp)
            del self.patch_analyses[oldest_key]

        self._save_patch_analyses()

        self.logger.info(f"Patch analisado: {patch_id} - Risco: {risk_analysis['risk'].value}")

        return analysis

    def _analyze_patch_risk(self, patch_content: str) -> Dict[str, Any]:
        """Analisa nível de risco do patch"""
        risk_scores = {
            PatchRisk.SAFE: 0,
            PatchRisk.LOW_RISK: 1,
            PatchRisk.MEDIUM_RISK: 2,
            PatchRisk.HIGH_RISK: 3,
            PatchRisk.CRITICAL: 4,
            PatchRisk.BLOCKED: 5
        }

        max_risk = PatchRisk.SAFE
        risk_factors = []

        # Verificar padrões perigosos
        for pattern_name, pattern_info in self.dangerous_patterns.items():
            if any(re.search(pattern, patch_content, re.IGNORECASE) for pattern in pattern_info["patterns"]):
                pattern_risk = pattern_info["risk"]
                if risk_scores[pattern_risk] > risk_scores[max_risk]:
                    max_risk = pattern_risk
                risk_factors.append(f"{pattern_name}: {pattern_info['description']}")

        # Análise de código (se for código Python)
        if self._is_python_code(patch_content):
            code_risk = self._analyze_code_risk(patch_content)
            if risk_scores[code_risk] > risk_scores[max_risk]:
                max_risk = code_risk
            if code_risk != PatchRisk.SAFE:
                risk_factors.append("Análise de código detectou riscos")

        return {
            "risk": max_risk,
            "risk_factors": risk_factors,
            "score": risk_scores[max_risk]
        }

    def _is_python_code(self, content: str) -> bool:
        """Verifica se o conteúdo é código Python"""
        try:
            ast.parse(content)
            return True
        except:
            return False

    def _analyze_code_risk(self, code_content: str) -> PatchRisk:
        """Analisa risco em código Python"""
        try:
            tree = ast.parse(code_content)

            risk_indicators = {
                PatchRisk.HIGH_RISK: [
                    ast.ImportFrom,  # Imports from modules
                    ast.Exec,        # Exec statements
                    ast.Eval         # Eval calls
                ],
                PatchRisk.MEDIUM_RISK: [
                    ast.Call,        # Function calls (potentially dangerous)
                    ast.Attribute    # Attribute access
                ]
            }

            # Verificar indicadores de risco
            for node in ast.walk(tree):
                for risk_level, node_types in risk_indicators.items():
                    if any(isinstance(node, node_type) for node_type in node_types):
                        # Verificações específicas
                        if isinstance(node, ast.Call):
                            if isinstance(node.func, ast.Name):
                                dangerous_funcs = ['exec', 'eval', 'open', 'system', 'popen', 'subprocess']
                                if node.func.id in dangerous_funcs:
                                    return PatchRisk.CRITICAL
                            elif isinstance(node.func, ast.Attribute):
                                dangerous_methods = ['system', 'exec', 'eval', 'open', 'remove', 'delete']
                                if isinstance(node.func.attr, str) and node.func.attr in dangerous_methods:
                                    return PatchRisk.HIGH_RISK
                        elif isinstance(node, ast.ImportFrom):
                            dangerous_modules = ['os', 'subprocess', 'sys', 'shutil']
                            if node.module in dangerous_modules:
                                return PatchRisk.MEDIUM_RISK

            return PatchRisk.LOW_RISK

        except Exception as e:
            self.logger.warning(f"Erro na análise de código: {e}")
            return PatchRisk.MEDIUM_RISK

    def _analyze_core_impact(self, patch_content: str) -> float:
        """Analisa impacto no sistema core (0-1, onde 1 é impacto máximo)"""
        impact_score = 0.0

        # Verificar referências ao core
        core_references = sum(1 for file in self.core_files if file in patch_content)
        impact_score += min(core_references * 0.3, 0.5)

        # Verificar modificações estruturais
        structural_changes = [
            "class ", "def ", "import ", "from ", "if __name__"
        ]
        for change in structural_changes:
            if change in patch_content:
                impact_score += 0.1

        # Verificar acesso a dados críticos
        critical_data_patterns = [
            "database", "config", "secret", "password", "token"
        ]
        for pattern in critical_data_patterns:
            if pattern in patch_content.lower():
                impact_score += 0.2

        return min(impact_score, 1.0)

    def _identify_modification_types(self, patch_content: str) -> List[ModificationType]:
        """Identifica tipos de modificação no patch"""
        types = []

        # Análise baseada em conteúdo
        if any(keyword in patch_content.lower() for keyword in ["class ", "def ", "import "]):
            types.append(ModificationType.CODE_CHANGE)

        if any(keyword in patch_content.lower() for keyword in ["config", "settings", "json"]):
            types.append(ModificationType.CONFIG_CHANGE)

        if any(keyword in patch_content.lower() for keyword in ["database", "insert", "update", "delete"]):
            types.append(ModificationType.DATA_MODIFICATION)

        if any(keyword in patch_content.lower() for keyword in ["permission", "access", "role"]):
            types.append(ModificationType.PERMISSION_CHANGE)

        if any(core_file in patch_content for core_file in self.core_files):
            types.append(ModificationType.CORE_MODIFICATION)

        if any(keyword in patch_content.lower() for keyword in ["security", "auth", "encrypt"]):
            types.append(ModificationType.SECURITY_CHANGE)

        return types if types else [ModificationType.CODE_CHANGE]

    def _identify_affected_files(self, patch_content: str) -> List[str]:
        """Identifica arquivos afetados pelo patch"""
        affected = []

        # Procurar referências a arquivos
        file_patterns = [
            r"packages/bridge/agent/[\w/\.]+",
            r"src/[\w/\.]+",
            r"SYSTEM_EVOLUTION_TASKS\.md",
            r"requirements\.txt",
            r"package\.json"
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, patch_content)
            affected.extend(matches)

        return list(set(affected))

    def _evaluate_security_concerns(self, patch_content: str) -> List[str]:
        """Avalia preocupações de segurança"""
        concerns = []

        # Verificar padrões de segurança
        security_checks = {
            "Hardcoded secrets": [r"password.*=.*['\"]", r"secret.*=.*['\"]", r"token.*=.*['\"]"],
            "SQL injection": [r"SELECT.*\+", r"INSERT.*\+", r"UPDATE.*\+", r"DELETE.*\+"],
            "Command injection": [r"system\(.*\+", r"popen\(.*\+", r"exec\(.*\+", r"eval\(.*\+", r"subprocess.*\+", r"os\.system.*\+", r"os\.popen.*\+", r"os\.exec.*\+", r"os\.spawn.*\+", r"shutil.*\+", r"rm.*-rf"],
            "Path traversal": [r"\.\./", r"\.\.\\"],
            "Unsafe deserialization": [r"pickle\.load", r"yaml\.load", r"json\.loads.*\+\+", r"eval\("],
            "Weak cryptography": [r"md5", r"sha1"],
            "Information disclosure": [r"print.*password", r"log.*secret", r"debug.*token"]
        }

        for concern_name, patterns in security_checks.items():
            for pattern in patterns:
                if re.search(pattern, patch_content, re.IGNORECASE):
                    concerns.append(f"{concern_name}: Possível vulnerabilidade detectada")
                    break

        return concerns

    def _generate_recommendations(self, risk_level: PatchRisk, security_concerns: List[str]) -> List[str]:
        """Gera recomendações baseadas no risco e preocupações"""
        recommendations = []

        if risk_level == PatchRisk.BLOCKED:
            recommendations.append("CRÍTICO: Patch bloqueado automaticamente - requer revisão manual completa")
            recommendations.append("Não aplicar sem aprovação explícita de administrador de segurança")

        elif risk_level == PatchRisk.CRITICAL:
            recommendations.append("Revisão de segurança obrigatória antes da aplicação")
            recommendations.append("Testes extensivos em ambiente isolado requeridos")
            recommendations.append("Aprovação de múltiplas partes necessária")

        elif risk_level == PatchRisk.HIGH_RISK:
            recommendations.append("Revisão de código obrigatória")
            recommendations.append("Testes de segurança adicionais requeridos")
            recommendations.append("Monitoramento pós-aplicação necessário")

        elif risk_level == PatchRisk.MEDIUM_RISK:
            recommendations.append("Testes funcionais completos requeridos")
            recommendations.append("Revisão de pares recomendada")

        elif risk_level == PatchRisk.LOW_RISK:
            recommendations.append("Testes básicos suficientes")
            recommendations.append("Monitoramento padrão adequado")

        # Recomendações baseadas em preocupações de segurança
        if security_concerns:
            recommendations.append("Correção de vulnerabilidades de segurança identificadas obrigatória")
            recommendations.append("Consulta com especialista em segurança recomendada")

        return recommendations

    def approve_patch(self, patch_id: str, approved_by: str) -> bool:
        """Aprova um patch para aplicação"""
        if patch_id not in self.patch_analyses:
            return False

        analysis = self.patch_analyses[patch_id]

        # Verificar se pode ser aprovado
        if analysis.risk_level == PatchRisk.BLOCKED:
            self.logger.warning(f"Tentativa de aprovar patch bloqueado: {patch_id}")
            return False

        analysis.approved = True
        analysis.approved_by = approved_by
        analysis.approved_at = datetime.now().isoformat()

        self._save_patch_analyses()

        self.logger.info(f"Patch aprovado: {patch_id} por {approved_by}")
        return True

    def _perform_initial_integrity_check(self):
        """Realiza verificação inicial de integridade do core"""
        check = self.check_core_integrity()
        if not check.integrity_status:
            self.logger.critical("Integridade do core comprometida na inicialização!")
            self.logger.critical(f"Violações: {check.violations}")

    def check_core_integrity(self) -> CoreIntegrityCheck:
        """Verifica integridade do sistema core"""
        timestamp = datetime.now().isoformat()

        # Calcular hash do core
        core_hash = self._calculate_core_hash()

        # Calcular hashes de arquivos críticos
        critical_hashes = {}
        violations = []

        for file_path in self.core_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                try:
                    file_hash = self._calculate_file_hash(full_path)
                    critical_hashes[str(full_path)] = file_hash
                except Exception as e:
                    violations.append(f"Erro ao calcular hash de {file_path}: {e}")
            else:
                violations.append(f"Arquivo crítico ausente: {file_path}")

        # Verificar mudanças não autorizadas
        if self.integrity_checks:
            last_check = self.integrity_checks[-1]

            # Verificar hash do core
            if last_check.core_hash != core_hash:
                violations.append("Hash do core modificado sem autorização")

            # Verificar arquivos críticos
            for file_path, current_hash in critical_hashes.items():
                if file_path in last_check.critical_files_hashes:
                    stored_hash = last_check.critical_files_hashes[file_path]
                    if stored_hash != current_hash:
                        violations.append(f"Arquivo crítico modificado: {file_path}")

        integrity_status = len(violations) == 0

        check = CoreIntegrityCheck(
            timestamp=timestamp,
            core_hash=core_hash,
            critical_files_hashes=critical_hashes,
            integrity_status=integrity_status,
            violations=violations
        )

        self.integrity_checks.append(check)

        # Manter histórico limitado
        if len(self.integrity_checks) > 100:
            self.integrity_checks = self.integrity_checks[-100:]

        self._save_integrity_checks()

        if not integrity_status:
            self.logger.warning(f"Violação de integridade detectada: {violations}")

        return check

    def _calculate_core_hash(self) -> str:
        """Calcula hash do sistema core"""
        hasher = hashlib.sha256()

        for file_path in self.core_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                file_hash = self._calculate_file_hash(full_path)
                hasher.update(file_hash.encode())

        return hasher.hexdigest()

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcula hash de um arquivo ou diretório"""
        if file_path.is_file():
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        else:
            # Para diretórios
            hasher = hashlib.sha256()
            for f in sorted(file_path.rglob('*')):
                if f.is_file():
                    try:
                        with open(f, 'rb') as file:
                            hasher.update(file.read())
                    except:
                        pass
            return hasher.hexdigest()

    def get_patch_analysis(self, patch_id: str) -> Optional[Dict[str, Any]]:
        """Retorna análise de um patch específico"""
        analysis = self.patch_analyses.get(patch_id)
        return asdict(analysis) if analysis else None

    def get_protection_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de proteção"""
        recent_analyses = list(self.patch_analyses.values())[-10:]

        risk_distribution = {}
        for analysis in recent_analyses:
            risk = analysis.risk_level.value
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

        last_integrity = self.integrity_checks[-1] if self.integrity_checks else None

        return {
            "total_analyses": len(self.patch_analyses),
            "recent_risk_distribution": risk_distribution,
            "core_integrity_status": last_integrity.integrity_status if last_integrity else None,
            "last_integrity_check": last_integrity.timestamp if last_integrity else None,
            "active_protections": [
                "Patch risk analysis",
                "Core integrity monitoring",
                "Dangerous pattern detection",
                "Security vulnerability scanning"
            ]
        }

    def list_patch_analyses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lista análises de patches recentes"""
        analyses = list(self.patch_analyses.values())
        return [asdict(a) for a in analyses[-limit:]]

    def export_protection_report(self, filepath: str):
        """Exporta relatório completo de proteção"""
        report = {
            "export_timestamp": datetime.now().isoformat(),
            "protection_status": self.get_protection_status(),
            "patch_analyses": self.list_patch_analyses(100),
            "integrity_checks": [asdict(c) for c in self.integrity_checks[-50:]]
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Relatório de proteção exportado para {filepath}")