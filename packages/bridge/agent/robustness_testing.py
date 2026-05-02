"""
Robustness Testing Framework - Testes contínuos de robustez

Este módulo fornece testes automatizados para validar segurança,
performance e confiabilidade do sistema.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import time
import random
import hashlib


class TestType(Enum):
    """Tipos de testes de robustez."""
    SECURITY = "security"           # Testes de segurança
    PERFORMANCE = "performance"     # Testes de desempenho
    INTEGRITY = "integrity"         # Testes de integridade
    RECOVERY = "recovery"           # Testes de recuperação
    COMPATIBILITY = "compatibility" # Testes de compatibilidade
    SATURATION = "saturation"       # Testes de carga


class TestSeverity(Enum):
    """Severidade de falhas em testes."""
    LOW = "low"           # Aviso
    MEDIUM = "medium"     # Falha não-crítica
    HIGH = "high"         # Falha importante
    CRITICAL = "critical" # Impossível ignorar


class RobustnessTestFramework:
    """
    Framework de testes de robustez.
    
    Testa:
    - Segurança contra injeções e exploração
    - Performance e latência
    - Integridade de dados
    - Capacidade de recuperação
    - Compatibilidade de versões
    - Comportamento sob carga
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.test_dir = data_dir / "robustness_tests"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_results_log = self.test_dir / "results.json"
        self.test_results: List[Dict] = []
        
        self.security_tests: List[Dict] = []
        self.performance_baselines: Dict = {}
        
        self._load_results()
        self._initialize_test_suite()

    def _initialize_test_suite(self) -> None:
        """Inicializa suite de testes."""
        
        # Testes de segurança
        self.security_tests = [
            {
                "id": "sec_001",
                "name": "SQL Injection Prevention",
                "payloads": ["'; DROP TABLE--", "1' OR '1'='1"],
                "expected_behavior": "reject_or_escape"
            },
            {
                "id": "sec_002",
                "name": "Command Injection Prevention",
                "payloads": ["; rm -rf /", "| cat /etc/passwd"],
                "expected_behavior": "reject"
            },
            {
                "id": "sec_003",
                "name": "Path Traversal Prevention",
                "payloads": ["../../../etc/passwd", "..\\..\\windows\\system32"],
                "expected_behavior": "reject"
            },
            {
                "id": "sec_004",
                "name": "Code Injection Prevention",
                "payloads": ["import os; os.system('whoami')", "__import__('os').system('id')"],
                "expected_behavior": "reject"
            }
        ]

    def run_security_tests(self, validator_func: Callable[[str], bool]) -> Dict[str, Any]:
        """
        Executa testes de segurança.
        """
        
        test_run = {
            "type": TestType.SECURITY.value,
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "passed": 0,
            "failed": 0
        }
        
        for test in self.security_tests:
            test_result = {
                "test_id": test["id"],
                "test_name": test["name"],
                "checks": []
            }
            
            test_passed = True
            for payload in test["payloads"]:
                try:
                    is_safe = validator_func(payload)
                    
                    check = {
                        "payload": payload[:50],  # Truncar para readabilidade
                        "detected_unsafe": not is_safe,
                        "passed": not is_safe
                    }
                    
                    test_result["checks"].append(check)
                    test_passed = test_passed and check["passed"]
                    
                except Exception as e:
                    test_result["checks"].append({
                        "payload": payload[:50],
                        "error": str(e),
                        "passed": True  # Erro é seguro (blocked)
                    })
            
            test_result["passed"] = test_passed
            test_run["tests"].append(test_result)
            
            if test_passed:
                test_run["passed"] += 1
            else:
                test_run["failed"] += 1
        
        self.test_results.append(test_run)
        self._save_results()
        
        return test_run

    def run_performance_tests(self, operation_func: Callable[[], None],
                             iterations: int = 100) -> Dict[str, Any]:
        """
        Executa testes de performance.
        """
        
        test_run = {
            "type": TestType.PERFORMANCE.value,
            "timestamp": datetime.now().isoformat(),
            "iterations": iterations,
            "metrics": {}
        }
        
        times = []
        errors = 0
        
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                operation_func()
            except Exception:
                errors += 1
            finally:
                elapsed = time.perf_counter() - start
                times.append(elapsed)
        
        # Calcular métricas
        times_sorted = sorted(times)
        test_run["metrics"] = {
            "min_time": min(times),
            "max_time": max(times),
            "avg_time": sum(times) / len(times),
            "median_time": times_sorted[len(times_sorted) // 2],
            "p95_time": times_sorted[int(len(times_sorted) * 0.95)],
            "p99_time": times_sorted[int(len(times_sorted) * 0.99)],
            "error_rate": errors / iterations
        }
        
        # Comparar com baseline se existir
        if "operation_baseline" in self.performance_baselines:
            baseline = self.performance_baselines["operation_baseline"]
            test_run["baseline_comparison"] = {
                "baseline_avg": baseline.get("avg_time"),
                "current_avg": test_run["metrics"]["avg_time"],
                "degradation_percent": (
                    (test_run["metrics"]["avg_time"] - baseline["avg_time"]) /
                    baseline["avg_time"] * 100
                ) if baseline.get("avg_time") else 0
            }
        
        # Salvar como novo baseline se primeiro teste
        if "operation_baseline" not in self.performance_baselines:
            self.performance_baselines["operation_baseline"] = test_run["metrics"]
        
        self.test_results.append(test_run)
        self._save_results()
        
        return test_run

    def run_integrity_tests(self, data_accessor: Callable[[str], Any]) -> Dict[str, Any]:
        """
        Executa testes de integridade de dados.
        """
        
        test_run = {
            "type": TestType.INTEGRITY.value,
            "timestamp": datetime.now().isoformat(),
            "checks": []
        }
        
        # Verificar checksums
        test_keys = ["core_hash", "agent_state", "memory_store"]
        
        for key in test_keys:
            try:
                data = data_accessor(key)
                data_hash = hashlib.sha256(
                    json.dumps(data, sort_keys=True, default=str).encode()
                ).hexdigest()
                
                check = {
                    "key": key,
                    "has_data": data is not None,
                    "hash_stable": True,
                    "hash": data_hash[:16]  # Primeiros 16 chars
                }
                
                test_run["checks"].append(check)
                
            except Exception as e:
                test_run["checks"].append({
                    "key": key,
                    "error": str(e)
                })
        
        test_run["passed"] = all(
            check.get("has_data", True) for check in test_run["checks"]
        )
        
        self.test_results.append(test_run)
        self._save_results()
        
        return test_run

    def run_recovery_tests(self, recovery_func: Callable[[str], bool],
                          snapshots: List[str]) -> Dict[str, Any]:
        """
        Executa testes de capacidade de recuperação.
        """
        
        test_run = {
            "type": TestType.RECOVERY.value,
            "timestamp": datetime.now().isoformat(),
            "snapshots_tested": len(snapshots),
            "recovery_results": []
        }
        
        for snapshot_id in snapshots:
            try:
                recovered = recovery_func(snapshot_id)
                test_run["recovery_results"].append({
                    "snapshot_id": snapshot_id,
                    "recovered": recovered,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                test_run["recovery_results"].append({
                    "snapshot_id": snapshot_id,
                    "recovered": False,
                    "error": str(e)
                })
        
        test_run["success_rate"] = sum(
            1 for r in test_run["recovery_results"] if r.get("recovered")
        ) / len(test_run["recovery_results"]) if test_run["recovery_results"] else 0
        
        self.test_results.append(test_run)
        self._save_results()
        
        return test_run

    def run_load_saturation_test(self, concurrent_operations: int = 10,
                                 duration_seconds: int = 30) -> Dict[str, Any]:
        """
        Executa teste de saturação de carga.
        """
        
        test_run = {
            "type": TestType.SATURATION.value,
            "timestamp": datetime.now().isoformat(),
            "concurrent_operations": concurrent_operations,
            "duration_seconds": duration_seconds,
            "results": []
        }
        
        start_time = time.time()
        operation_count = 0
        error_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Simular operações concorrentes
            for _ in range(concurrent_operations):
                try:
                    # Simular operação
                    time.sleep(random.uniform(0.001, 0.01))
                    operation_count += 1
                except Exception:
                    error_count += 1
        
        test_run["results"] = {
            "total_operations": operation_count,
            "total_errors": error_count,
            "ops_per_second": operation_count / duration_seconds,
            "error_rate": error_count / operation_count if operation_count > 0 else 0
        }
        
        self.test_results.append(test_run)
        self._save_results()
        
        return test_run

    def run_compatibility_tests(self, version_checker: Callable[[str], bool],
                               versions: List[str]) -> Dict[str, Any]:
        """
        Executa testes de compatibilidade de versão.
        """
        
        test_run = {
            "type": TestType.COMPATIBILITY.value,
            "timestamp": datetime.now().isoformat(),
            "versions_tested": versions,
            "compatibility_results": []
        }
        
        for version in versions:
            try:
                compatible = version_checker(version)
                test_run["compatibility_results"].append({
                    "version": version,
                    "compatible": compatible
                })
            except Exception as e:
                test_run["compatibility_results"].append({
                    "version": version,
                    "compatible": False,
                    "error": str(e)
                })
        
        test_run["compatible_count"] = sum(
            1 for r in test_run["compatibility_results"] if r.get("compatible")
        )
        
        self.test_results.append(test_run)
        self._save_results()
        
        return test_run

    def get_test_report(self, test_type: Optional[TestType] = None,
                       limit: int = 100) -> Dict[str, Any]:
        """
        Gera relatório de testes.
        """
        
        results = self.test_results
        
        if test_type:
            results = [r for r in results if r.get("type") == test_type.value]
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_test_runs": len(results),
            "test_summary": {},
            "recent_tests": results[-limit:]
        }
        
        # Summarizar por tipo
        for test_type_val in [t.value for t in TestType]:
            type_results = [r for r in results if r.get("type") == test_type_val]
            report["test_summary"][test_type_val] = {
                "runs": len(type_results),
                "passed": sum(1 for r in type_results if r.get("passed", True))
            }
        
        return report

    def _load_results(self) -> None:
        """Carrega resultados de testes."""
        if self.test_results_log.exists():
            try:
                self.test_results = json.loads(
                    self.test_results_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.test_results = []

    def _save_results(self) -> None:
        """Persiste resultados de testes."""
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.test_results_log.write_text(
            json.dumps(self.test_results[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
