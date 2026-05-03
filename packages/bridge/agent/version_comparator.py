"""
Comparador de Versões da IA - Análise detalhada de versões

Este módulo implementa comparação abrangente entre versões da IA,
avaliando performance, estabilidade, segurança e compatibilidade.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import time
import statistics


class ComparisonMetric(Enum):
    """Métricas de comparação entre versões."""
    PERFORMANCE = "performance"
    STABILITY = "stability"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"
    MEMORY_USAGE = "memory_usage"
    EXECUTION_TIME = "execution_time"
    ERROR_RATE = "error_rate"
    RESOURCE_EFFICIENCY = "resource_efficiency"


class VersionComparator:
    """
    Compara versões da IA usando múltiplas métricas e testes.

    Avalia:
    - Performance: velocidade de resposta, throughput
    - Estabilidade: taxa de erro, consistência de respostas
    - Segurança: violações detectadas, tentativas de exploração
    - Compatibilidade: funcionamento com core imutável
    - Eficiência: uso de memória, recursos do sistema
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.comparisons_dir = data_dir / "version_comparisons"
        self.comparisons_dir.mkdir(parents=True, exist_ok=True)

        self.comparison_results_log = self.comparisons_dir / "results.json"
        self.benchmark_tests_log = self.comparisons_dir / "benchmarks.json"

        self.comparison_results: List[Dict] = []
        self.benchmark_tests: Dict[str, Dict] = {}

        self._load_state()
        self._initialize_benchmarks()

    def _initialize_benchmarks(self) -> None:
        """Inicializa conjunto de testes de benchmark."""

        self.benchmark_tests = {
            "security_scan": {
                "name": "Security Vulnerability Scan",
                "description": "Testa resistência a inputs maliciosos",
                "test_cases": [
                    {"input": "'; DROP TABLE users--", "expected": "reject"},
                    {"input": "__import__('os').system('whoami')", "expected": "reject"},
                    {"input": "../../../etc/passwd", "expected": "reject"},
                    {"input": "<script>alert('xss')</script>", "expected": "reject"}
                ],
                "metric": ComparisonMetric.SECURITY
            },
            "performance_load": {
                "name": "Performance Under Load",
                "description": "Testa performance com múltiplas requisições simultâneas",
                "iterations": 100,
                "concurrent_requests": 10,
                "metric": ComparisonMetric.PERFORMANCE
            },
            "stability_consistency": {
                "name": "Response Consistency",
                "description": "Verifica se respostas são consistentes para mesmo input",
                "test_input": "Explique o conceito de recursão em programação",
                "iterations": 10,
                "metric": ComparisonMetric.STABILITY
            },
            "memory_efficiency": {
                "name": "Memory Usage Efficiency",
                "description": "Monitora uso de memória durante operações",
                "operations": ["memory_store", "code_generation", "file_analysis"],
                "metric": ComparisonMetric.MEMORY_USAGE
            },
            "core_compatibility": {
                "name": "Core System Compatibility",
                "description": "Verifica compatibilidade com regras do core imutável",
                "core_rules": ["user_priority", "no_core_modification", "sandbox_execution"],
                "metric": ComparisonMetric.COMPATIBILITY
            }
        }

    def compare_versions(self, version_a_id: str, version_b_id: str,
                        evolution_manager) -> Dict[str, Any]:
        """
        Compara duas versões da IA usando todas as métricas disponíveis.
        """

        comparison = {
            "comparison_id": f"cmp_{version_a_id}_vs_{version_b_id}_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "version_a": version_a_id,
            "version_b": version_b_id,
            "metrics": {},
            "overall_score": 0.0,
            "recommendation": "",
            "details": {}
        }

        # Obter dados das versões
        version_a = evolution_manager.get_version(version_a_id)
        version_b = evolution_manager.get_version(version_b_id)

        if not version_a or not version_b:
            comparison["error"] = "Uma ou ambas as versões não encontradas"
            return comparison

        # Comparar cada métrica
        for metric in ComparisonMetric:
            try:
                result = self._compare_metric(metric, version_a, version_b)
                comparison["metrics"][metric.value] = result
            except Exception as e:
                comparison["metrics"][metric.value] = {
                    "error": str(e),
                    "score": 0.0
                }

        # Calcular score geral
        scores = [m.get("score", 0.0) for m in comparison["metrics"].values() if "score" in m]
        if scores:
            comparison["overall_score"] = statistics.mean(scores)

        # Gerar recomendação
        comparison["recommendation"] = self._generate_recommendation(comparison)

        # Salvar resultado
        self.comparison_results.append(comparison)
        self._save_state()

        return comparison

    def _compare_metric(self, metric: ComparisonMetric,
                       version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """
        Compara uma métrica específica entre duas versões.
        """

        result = {
            "metric": metric.value,
            "version_a_score": 0.0,
            "version_b_score": 0.0,
            "winner": None,
            "improvement_percent": 0.0,
            "details": {}
        }

        if metric == ComparisonMetric.PERFORMANCE:
            result = self._compare_performance(version_a, version_b)
        elif metric == ComparisonMetric.STABILITY:
            result = self._compare_stability(version_a, version_b)
        elif metric == ComparisonMetric.SECURITY:
            result = self._compare_security(version_a, version_b)
        elif metric == ComparisonMetric.COMPATIBILITY:
            result = self._compare_compatibility(version_a, version_b)
        elif metric == ComparisonMetric.MEMORY_USAGE:
            result = self._compare_memory_usage(version_a, version_b)
        elif metric == ComparisonMetric.EXECUTION_TIME:
            result = self._compare_execution_time(version_a, version_b)
        elif metric == ComparisonMetric.ERROR_RATE:
            result = self._compare_error_rate(version_a, version_b)
        elif metric == ComparisonMetric.RESOURCE_EFFICIENCY:
            result = self._compare_resource_efficiency(version_a, version_b)

        # Determinar vencedor
        if result["version_a_score"] > result["version_b_score"]:
            result["winner"] = "version_a"
            if result["version_b_score"] > 0:
                result["improvement_percent"] = (
                    (result["version_a_score"] - result["version_b_score"]) /
                    result["version_b_score"] * 100
                )
        elif result["version_b_score"] > result["version_a_score"]:
            result["winner"] = "version_b"
            if result["version_a_score"] > 0:
                result["improvement_percent"] = (
                    (result["version_b_score"] - result["version_a_score"]) /
                    result["version_a_score"] * 100
                )

        # Score normalizado para comparação geral
        result["score"] = max(result["version_a_score"], result["version_b_score"])

        return result

    def _compare_performance(self, version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """Compara performance entre versões."""

        # Usar métricas de performance dos testes de benchmark
        perf_a = version_a.get("metrics", {}).get("performance", 0.0)
        perf_b = version_b.get("metrics", {}).get("performance", 0.0)

        return {
            "metric": "performance",
            "version_a_score": perf_a,
            "version_b_score": perf_b,
            "details": {
                "version_a_throughput": perf_a,
                "version_b_throughput": perf_b,
                "benchmark_used": "performance_load"
            }
        }

    def _compare_stability(self, version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """Compara estabilidade entre versões."""

        stability_a = version_a.get("metrics", {}).get("stability", 0.0)
        stability_b = version_b.get("metrics", {}).get("stability", 0.0)

        # Calcular consistência baseada em variação de respostas
        consistency_a = 1.0 - (version_a.get("metrics", {}).get("response_variation", 0.5))
        consistency_b = 1.0 - (version_b.get("metrics", {}).get("response_variation", 0.5))

        score_a = (stability_a + consistency_a) / 2
        score_b = (stability_b + consistency_b) / 2

        return {
            "metric": "stability",
            "version_a_score": score_a,
            "version_b_score": score_b,
            "details": {
                "version_a_stability": stability_a,
                "version_b_stability": stability_b,
                "version_a_consistency": consistency_a,
                "version_b_consistency": consistency_b
            }
        }

    def _compare_security(self, version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """Compara segurança entre versões."""

        security_a = version_a.get("metrics", {}).get("security", 0.0)
        security_b = version_b.get("metrics", {}).get("security", 0.0)

        # Verificar violações de segurança detectadas
        violations_a = version_a.get("metadata", {}).get("security_violations", 0)
        violations_b = version_b.get("metadata", {}).get("security_violations", 0)

        # Score baseado em violações (menos violações = melhor score)
        score_a = security_a * (1.0 - min(violations_a / 10.0, 1.0))  # Máx 10 violações
        score_b = security_b * (1.0 - min(violations_b / 10.0, 1.0))

        return {
            "metric": "security",
            "version_a_score": score_a,
            "version_b_score": score_b,
            "details": {
                "version_a_violations": violations_a,
                "version_b_violations": violations_b,
                "version_a_security_score": security_a,
                "version_b_security_score": security_b
            }
        }

    def _compare_compatibility(self, version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """Compara compatibilidade com core imutável."""

        # Verificar se versões respeitam regras do core
        core_checks = ["user_priority", "no_core_modification", "sandbox_execution"]

        compatibility_a = 0.0
        compatibility_b = 0.0

        for check in core_checks:
            if version_a.get("metadata", {}).get(f"core_{check}", True):
                compatibility_a += 1.0
            if version_b.get("metadata", {}).get(f"core_{check}", True):
                compatibility_b += 1.0

        compatibility_a /= len(core_checks)
        compatibility_b /= len(core_checks)

        return {
            "metric": "compatibility",
            "version_a_score": compatibility_a,
            "version_b_score": compatibility_b,
            "details": {
                "core_checks": core_checks,
                "version_a_compatible": compatibility_a == 1.0,
                "version_b_compatible": compatibility_b == 1.0
            }
        }

    def _compare_memory_usage(self, version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """Compara eficiência de uso de memória."""

        mem_a = version_a.get("metrics", {}).get("memory_efficiency", 0.5)
        mem_b = version_b.get("metrics", {}).get("memory_efficiency", 0.5)

        # Menor uso de memória = melhor score (invertido)
        score_a = 1.0 - mem_a  # Se mem_a é alto (mau), score é baixo
        score_b = 1.0 - mem_b

        return {
            "metric": "memory_usage",
            "version_a_score": score_a,
            "version_b_score": score_b,
            "details": {
                "version_a_memory_usage": mem_a,
                "version_b_memory_usage": mem_b
            }
        }

    def _compare_execution_time(self, version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """Compara tempo de execução."""

        time_a = version_a.get("metrics", {}).get("avg_execution_time", 1.0)
        time_b = version_b.get("metrics", {}).get("avg_execution_time", 1.0)

        # Menor tempo = melhor score (invertido)
        score_a = 1.0 / max(time_a, 0.001)  # Evitar divisão por zero
        score_b = 1.0 / max(time_b, 0.001)

        return {
            "metric": "execution_time",
            "version_a_score": score_a,
            "version_b_score": score_b,
            "details": {
                "version_a_avg_time": time_a,
                "version_b_avg_time": time_b
            }
        }

    def _compare_error_rate(self, version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """Compara taxa de erro."""

        errors_a = version_a.get("metrics", {}).get("error_rate", 0.1)
        errors_b = version_b.get("metrics", {}).get("error_rate", 0.1)

        # Menor taxa de erro = melhor score
        score_a = 1.0 - errors_a
        score_b = 1.0 - errors_b

        return {
            "metric": "error_rate",
            "version_a_score": score_a,
            "version_b_score": score_b,
            "details": {
                "version_a_error_rate": errors_a,
                "version_b_error_rate": errors_b
            }
        }

    def _compare_resource_efficiency(self, version_a: Dict, version_b: Dict) -> Dict[str, Any]:
        """Compara eficiência de recursos."""

        cpu_a = version_a.get("metrics", {}).get("cpu_efficiency", 0.5)
        cpu_b = version_b.get("metrics", {}).get("cpu_efficiency", 0.5)

        return {
            "metric": "resource_efficiency",
            "version_a_score": cpu_a,
            "version_b_score": cpu_b,
            "details": {
                "version_a_cpu_efficiency": cpu_a,
                "version_b_cpu_efficiency": cpu_b
            }
        }

    def _generate_recommendation(self, comparison: Dict) -> str:
        """Gera recomendação baseada na comparação."""

        overall_score = comparison.get("overall_score", 0.0)

        if overall_score >= 0.8:
            return "VERSÃO SUPERIOR: Recomendado promover para produção"
        elif overall_score >= 0.6:
            return "MELHORIA SIGNIFICATIVA: Considerar promoção após testes adicionais"
        elif overall_score >= 0.4:
            return "MELHORIA MODERADA: Manter como candidato, mas preferir versão atual"
        else:
            return "SEM MELHORIA SIGNIFICATIVA: Não recomendado para promoção"

    def get_comparison_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de comparações."""
        return self.comparison_results[-limit:]

    def get_best_version(self, version_ids: List[str], evolution_manager) -> Optional[str]:
        """
        Determina qual versão é melhor baseada em comparações históricas.
        """

        if len(version_ids) < 2:
            return version_ids[0] if version_ids else None

        scores = {}
        for vid in version_ids:
            version = evolution_manager.get_version(vid)
            if version:
                scores[vid] = version.get("metrics", {}).get("overall_score", 0.0)

        if scores:
            return max(scores, key=scores.get)

        return None

    def _load_state(self) -> None:
        """Carrega estado das comparações."""

        if self.comparison_results_log.exists():
            try:
                self.comparison_results = json.loads(
                    self.comparison_results_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.comparison_results = []

    def _save_state(self) -> None:
        """Persiste estado das comparações."""

        self.comparisons_dir.mkdir(parents=True, exist_ok=True)

        self.comparison_results_log.write_text(
            json.dumps(self.comparison_results[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
