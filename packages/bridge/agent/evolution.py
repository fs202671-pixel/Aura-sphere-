"""
Agent Evolution - Controle de versões candidatas e comparação de qualidade.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.sandbox import execute_code_safely

BASE_DIR = Path(__file__).resolve().parents[1]
EVOLUTION_DIR = BASE_DIR / "data" / "versions"
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class AgentVersion:
    version_id: str
    description: str
    created_at: str
    metrics: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "description": self.description,
            "created_at": self.created_at,
            "metrics": self.metrics,
            "metadata": self.metadata,
        }


class EvolutionManager:
    """Gerencia versões candidatas de evolução do agente."""

    def __init__(self, versions_dir: Optional[Path] = None):
        self.versions_dir = versions_dir or EVOLUTION_DIR
        self.versions_file = self.versions_dir / "versions.json"
        self.versions: List[AgentVersion] = []
        self._load()

    def _load(self) -> None:
        if self.versions_file.exists():
            try:
                data = json.loads(self.versions_file.read_text(encoding="utf-8"))
                self.versions = [AgentVersion(**item) for item in data]
            except Exception:
                self.versions = []

    def _persist(self) -> None:
        self.versions_file.write_text(
            json.dumps([version.to_dict() for version in self.versions], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def add_version(self, description: str, metrics: Optional[Dict[str, Any]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> AgentVersion:
        version = AgentVersion(
            version_id=f"v{len(self.versions) + 1}",
            description=description,
            created_at=datetime.now().isoformat(),
            metrics=metrics or {},
            metadata=metadata or {}
        )
        self.versions.append(version)
        self._persist()
        return version

    def list_versions(self, limit: int = 20) -> List[AgentVersion]:
        return self.versions[-limit:]

    def score_version(self, version: AgentVersion) -> float:
        metrics = version.metrics
        base_score = float(metrics.get("quality_score", 0))
        stability = float(metrics.get("stability", 0))
        security = float(metrics.get("security", 0))
        performance = float(metrics.get("performance", 0))
        compatibility = float(metrics.get("compatibility", 0))
        errors = float(metrics.get("errors", 0))
        return (base_score * 1.0 + stability * 0.3 + security * 0.4 + 
                performance * 0.2 + compatibility * 0.3 - errors * 1.0)

    def score_version_detailed(self, version: AgentVersion) -> Dict[str, Any]:
        """Calcula score detalhado com breakdown."""
        metrics = version.metrics
        base_score = float(metrics.get("quality_score", 0))
        stability = float(metrics.get("stability", 0))
        security = float(metrics.get("security", 0))
        performance = float(metrics.get("performance", 0))
        compatibility = float(metrics.get("compatibility", 0))
        errors = float(metrics.get("errors", 0))

        components = {
            "base_score": (base_score, 1.0),
            "stability": (stability, 0.3),
            "security": (security, 0.4),
            "performance": (performance, 0.2),
            "compatibility": (compatibility, 0.3),
            "errors": (-errors, 1.0)
        }

        total = sum(value * weight for value, weight in components.values())

        return {
            "total_score": total,
            "components": {
                "base_score": base_score,
                "stability_weighted": stability * 0.3,
                "security_weighted": security * 0.4,
                "performance_weighted": performance * 0.2,
                "compatibility_weighted": compatibility * 0.3,
                "errors_penalty": -errors * 1.0
            },
            "metrics": metrics
        }

    def meets_quality_threshold(self, version: AgentVersion, threshold: float = 5.0) -> bool:
        """Verifica se version atende threshold de qualidade."""
        score = self.score_version(version)
        return score >= threshold

    def get_versions_above_threshold(self, threshold: float = 5.0) -> List[AgentVersion]:
        """Retorna versões que atendem threshold."""
        return [v for v in self.versions if self.meets_quality_threshold(v, threshold)]

    def choose_best_version(self) -> Optional[AgentVersion]:
        if not self.versions:
            return None
        best = max(self.versions, key=self.score_version)
        return best

    def evaluate_compatibility(self, version: AgentVersion) -> float:
        """Avalia compatibilidade com o core imutável."""
        # Verificar se a versão afeta arquivos do core
        metadata = version.metadata
        affected_files = metadata.get("affected_files", [])
        
        core_files_affected = [f for f in affected_files if f.startswith("core/")]
        if core_files_affected:
            return 0.0  # Incompatível se afeta core
        
        # Verificar se mantém integridade do core
        core_integrity = metadata.get("core_integrity_maintained", True)
        if not core_integrity:
            return 0.0
        
        # Compatibilidade baseada em testes
        compatibility_tests = metadata.get("compatibility_tests_passed", 0)
        total_tests = metadata.get("total_compatibility_tests", 1)
        return min(1.0, compatibility_tests / total_tests)

    def test_version_in_sandbox(self, version: AgentVersion, test_code: str) -> Dict[str, Any]:
        """Testa versão em sandbox e coleta métricas."""
        # Aplicar patch da versão (simulado)
        version_code = version.metadata.get("patch_code", "")
        
        # Código de teste combinado
        full_test_code = f"""
{version_code}

# Código de teste
{test_code}
"""
        
        # Executar em sandbox
        result = execute_code_safely(full_test_code, sandbox_id=f"version_{version.version_id}")
        
        # Coletar métricas
        metrics = {
            "execution_success": result.get("success", False),
            "execution_time": result.get("execution_time", 0),
            "has_errors": bool(result.get("error")),
            "security_violations": len(result.get("security_violations", [])),
            "output_length": len(result.get("output", ""))
        }
        
        # Calcular scores baseados nos resultados
        stability_score = 1.0 if metrics["execution_success"] else 0.0
        security_score = 1.0 if metrics["security_violations"] == 0 else 0.0
        performance_score = max(0, 1.0 - (metrics["execution_time"] / 30.0))  # Normalizar para 30s
        error_penalty = metrics["security_violations"] + (1 if metrics["has_errors"] else 0)
        
        return {
            "metrics": metrics,
            "scores": {
                "stability": stability_score,
                "security": security_score,
                "performance": performance_score,
                "errors": error_penalty
            }
        }

    def deploy_version(self, version: AgentVersion, test_code: str, user_approval: bool = False) -> Dict[str, Any]:
        """
        Pipeline completo de deploy: valida, testa em sandbox, compara e aplica se aprovado.
        
        Args:
            version: Versão a ser implantada
            test_code: Código de teste para validar a versão
            user_approval: Se o usuário aprovou manualmente
            
        Returns:
            Resultado do deploy
        """
        result = {
            "success": False,
            "stage": "validation",
            "version_id": version.version_id,
            "errors": []
        }
        
        # 1. Validação de compatibilidade
        compatibility = self.evaluate_compatibility(version)
        if compatibility < 0.8:  # Threshold de 80%
            result["errors"].append(f"Compatibilidade baixa: {compatibility}")
            return result
        
        result["stage"] = "sandbox_test"
        
        # 2. Teste em sandbox
        test_result = self.test_version_in_sandbox(version, test_code)
        if not test_result["metrics"]["execution_success"]:
            result["errors"].append("Falha no teste em sandbox")
            return result
        
        # Atualizar métricas da versão com resultados do teste
        version.metrics.update(test_result["scores"])
        version.metrics["compatibility"] = compatibility
        self._persist()
        
        result["stage"] = "comparison"
        
        # 3. Comparação com versão atual (se existir)
        current_best = self.choose_best_version()
        if current_best and self.score_version(version) <= self.score_version(current_best):
            if not user_approval:
                result["errors"].append("Versão não é melhor que a atual")
                result["comparison"] = self.compare_versions(version, current_best)
                return result
        
        result["stage"] = "deployment"
        
        # 4. Aplicar versão (simulado - em produção aplicaria o patch)
        # Aqui seria onde o código da versão seria aplicado ao sistema
        version.metadata["deployed_at"] = datetime.now().isoformat()
        version.metadata["deployed"] = True
        self._persist()
        
        result["success"] = True
        result["stage"] = "completed"
        result["deployed_version"] = version.version_id
        
        return result

    def compare_versions(self, version_a: AgentVersion, version_b: AgentVersion) -> Dict[str, Any]:
        return {
            "version_a": version_a.version_id,
            "version_b": version_b.version_id,
            "score_a": self.score_version(version_a),
            "score_b": self.score_version(version_b),
            "better_version": version_a.version_id if self.score_version(version_a) >= self.score_version(version_b) else version_b.version_id,
        }
