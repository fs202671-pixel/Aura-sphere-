"""
Sistema de Métricas Internas - Avaliação de qualidade da IA

Este módulo implementa coleta contínua de métricas para avaliar
a qualidade, performance e segurança da IA em tempo real.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import time
import threading
import psutil


class MetricType(Enum):
    """Tipos de métricas coletadas."""
    RESPONSE_ACCURACY = "response_accuracy"
    RESPONSE_CONSISTENCY = "response_consistency"
    ERROR_RATE = "error_rate"
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    SECURITY_VIOLATIONS = "security_violations"
    USER_SATISFACTION = "user_satisfaction"
    TASK_COMPLETION_RATE = "task_completion_rate"
    DECISION_STABILITY = "decision_stability"


class QualityMetricsCollector:
    """
    Coleta métricas de qualidade da IA em tempo real.

    Métricas principais:
    - Precisão de respostas
    - Consistência de respostas
    - Taxa de erro
    - Tempo de execução
    - Uso de recursos
    - Violações de segurança
    - Satisfação do usuário
    - Taxa de conclusão de tarefas
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.metrics_dir = data_dir / "quality_metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_log = self.metrics_dir / "metrics.json"
        self.quality_scores_log = self.metrics_dir / "quality_scores.json"

        self.current_metrics: Dict[str, Any] = {}
        self.metrics_history: List[Dict] = []
        self.quality_thresholds = {
            "min_accuracy": 0.7,
            "max_error_rate": 0.1,
            "max_execution_time": 30.0,  # segundos
            "max_memory_usage": 0.8,     # 80% da memória
            "max_security_violations": 0,
            "min_task_completion": 0.8
        }

        self.collection_thread: Optional[threading.Thread] = None
        self.is_collecting = False

        self._load_state()

    def start_collection(self) -> None:
        """Inicia coleta contínua de métricas."""
        if self.is_collecting:
            return

        self.is_collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()

    def stop_collection(self) -> None:
        """Para coleta de métricas."""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)

    def record_metric(self, metric_type: MetricType, value: Any,
                     context: Optional[Dict] = None) -> None:
        """
        Registra uma métrica específica.
        """

        metric_entry = {
            "timestamp": datetime.now().isoformat(),
            "metric_type": metric_type.value,
            "value": value,
            "context": context or {}
        }

        self.metrics_history.append(metric_entry)

        # Atualizar métricas atuais
        self.current_metrics[metric_type.value] = {
            "value": value,
            "timestamp": metric_entry["timestamp"],
            "context": context
        }

        self._save_state()

    def record_response_accuracy(self, expected_quality: float,
                                actual_quality: float,
                                response_type: str = "general") -> None:
        """
        Registra precisão de resposta.
        """

        accuracy = min(actual_quality / expected_quality, 1.0) if expected_quality > 0 else 0.0

        self.record_metric(
            MetricType.RESPONSE_ACCURACY,
            accuracy,
            {"response_type": response_type, "expected": expected_quality, "actual": actual_quality}
        )

    def record_execution_time(self, operation: str, start_time: float,
                             end_time: Optional[float] = None) -> float:
        """
        Registra tempo de execução de uma operação.
        """

        if end_time is None:
            end_time = time.time()

        execution_time = end_time - start_time

        self.record_metric(
            MetricType.EXECUTION_TIME,
            execution_time,
            {"operation": operation}
        )

        return execution_time

    def record_error(self, error_type: str, error_message: str,
                    operation: str = "unknown") -> None:
        """
        Registra ocorrência de erro.
        """

        self.record_metric(
            MetricType.ERROR_RATE,
            1,  # Conta como 1 erro
            {"error_type": error_type, "message": error_message, "operation": operation}
        )

    def record_security_violation(self, violation_type: str,
                                 severity: str = "medium",
                                 details: Optional[Dict] = None) -> None:
        """
        Registra violação de segurança.
        """

        self.record_metric(
            MetricType.SECURITY_VIOLATIONS,
            1,  # Conta como 1 violação
            {
                "violation_type": violation_type,
                "severity": severity,
                "details": details or {}
            }
        )

    def record_task_completion(self, task_type: str, completed: bool,
                              task_id: Optional[str] = None) -> None:
        """
        Registra conclusão de tarefa.
        """

        self.record_metric(
            MetricType.TASK_COMPLETION_RATE,
            1 if completed else 0,
            {"task_type": task_type, "task_id": task_id}
        )

    def calculate_quality_score(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """
        Calcula score de qualidade baseado nas métricas coletadas.
        """

        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]

        quality_score = {
            "timestamp": datetime.now().isoformat(),
            "time_window_minutes": time_window_minutes,
            "total_metrics": len(recent_metrics),
            "scores": {},
            "overall_score": 0.0,
            "meets_threshold": False
        }

        # Calcular score por categoria
        categories = {
            "accuracy": self._calculate_accuracy_score(recent_metrics),
            "performance": self._calculate_performance_score(recent_metrics),
            "reliability": self._calculate_reliability_score(recent_metrics),
            "security": self._calculate_security_score(recent_metrics),
            "efficiency": self._calculate_efficiency_score(recent_metrics)
        }

        quality_score["scores"] = categories

        # Score geral (média ponderada)
        weights = {
            "accuracy": 0.3,
            "performance": 0.2,
            "reliability": 0.25,
            "security": 0.15,
            "efficiency": 0.1
        }

        overall = sum(
            categories[cat]["score"] * weights[cat]
            for cat in categories.keys()
            if categories[cat]["score"] is not None
        )

        quality_score["overall_score"] = overall
        quality_score["meets_threshold"] = overall >= 0.7  # Threshold mínimo

        # Salvar score
        self._save_quality_score(quality_score)

        return quality_score

    def _calculate_accuracy_score(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Calcula score de precisão."""

        accuracy_metrics = [
            m for m in metrics
            if m["metric_type"] == MetricType.RESPONSE_ACCURACY.value
        ]

        if not accuracy_metrics:
            return {"score": None, "details": "No accuracy metrics available"}

        accuracies = [m["value"] for m in accuracy_metrics]
        avg_accuracy = sum(accuracies) / len(accuracies)

        return {
            "score": avg_accuracy,
            "details": {
                "measurements": len(accuracy_metrics),
                "average_accuracy": avg_accuracy,
                "min_accuracy": min(accuracies),
                "max_accuracy": max(accuracies)
            }
        }

    def _calculate_performance_score(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Calcula score de performance."""

        time_metrics = [
            m for m in metrics
            if m["metric_type"] == MetricType.EXECUTION_TIME.value
        ]

        if not time_metrics:
            return {"score": None, "details": "No performance metrics available"}

        times = [m["value"] for m in time_metrics]
        avg_time = sum(times) / len(times)

        # Score baseado no tempo (mais rápido = melhor score)
        max_allowed_time = self.quality_thresholds["max_execution_time"]
        score = max(0.0, 1.0 - (avg_time / max_allowed_time))

        return {
            "score": score,
            "details": {
                "measurements": len(time_metrics),
                "average_time": avg_time,
                "max_time": max(times),
                "threshold": max_allowed_time
            }
        }

    def _calculate_reliability_score(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Calcula score de confiabilidade."""

        error_metrics = [
            m for m in metrics
            if m["metric_type"] == MetricType.ERROR_RATE.value
        ]

        task_metrics = [
            m for m in metrics
            if m["metric_type"] == MetricType.TASK_COMPLETION_RATE.value
        ]

        error_rate = 0.0
        if error_metrics:
            error_rate = sum(m["value"] for m in error_metrics) / len(error_metrics)

        task_completion = 0.5  # Default
        if task_metrics:
            completions = [m["value"] for m in task_metrics]
            task_completion = sum(completions) / len(completions)

        # Score baseado em erros e conclusão de tarefas
        max_error_rate = self.quality_thresholds["max_error_rate"]
        error_score = max(0.0, 1.0 - (error_rate / max_error_rate))

        reliability_score = (error_score + task_completion) / 2

        return {
            "score": reliability_score,
            "details": {
                "error_rate": error_rate,
                "task_completion_rate": task_completion,
                "error_score": error_score
            }
        }

    def _calculate_security_score(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Calcula score de segurança."""

        violation_metrics = [
            m for m in metrics
            if m["metric_type"] == MetricType.SECURITY_VIOLATIONS.value
        ]

        total_violations = len(violation_metrics)

        # Score baseado em violações (menos violações = melhor score)
        max_violations = self.quality_thresholds["max_security_violations"]
        if total_violations <= max_violations:
            score = 1.0
        else:
            score = max(0.0, 1.0 - ((total_violations - max_violations) / 10.0))

        return {
            "score": score,
            "details": {
                "total_violations": total_violations,
                "max_allowed": max_violations,
                "severity_breakdown": self._analyze_violation_severity(violation_metrics)
            }
        }

    def _calculate_efficiency_score(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Calcula score de eficiência."""

        memory_metrics = [
            m for m in metrics
            if m["metric_type"] == MetricType.MEMORY_USAGE.value
        ]

        cpu_metrics = [
            m for m in metrics
            if m["metric_type"] == MetricType.CPU_USAGE.value
        ]

        memory_usage = 0.5  # Default
        if memory_metrics:
            memory_usage = sum(m["value"] for m in memory_metrics) / len(memory_metrics)

        cpu_usage = 0.5  # Default
        if cpu_metrics:
            cpu_usage = sum(m["value"] for m in cpu_metrics) / len(cpu_metrics)

        # Score baseado em uso de recursos (menos uso = melhor score)
        max_memory = self.quality_thresholds["max_memory_usage"]
        memory_score = max(0.0, 1.0 - (memory_usage / max_memory))
        cpu_score = max(0.0, 1.0 - cpu_usage)  # CPU usage já é 0-1

        efficiency_score = (memory_score + cpu_score) / 2

        return {
            "score": efficiency_score,
            "details": {
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage,
                "memory_score": memory_score,
                "cpu_score": cpu_score
            }
        }

    def _analyze_violation_severity(self, violations: List[Dict]) -> Dict[str, int]:
        """Analisa severidade das violações."""

        severity_count = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for violation in violations:
            severity = violation.get("context", {}).get("severity", "medium")
            if severity in severity_count:
                severity_count[severity] += 1

        return severity_count

    def _collection_loop(self) -> None:
        """Loop de coleta contínua de métricas do sistema."""

        while self.is_collecting:
            try:
                # Coletar métricas do sistema
                memory_percent = psutil.virtual_memory().percent / 100.0
                cpu_percent = psutil.cpu_percent(interval=1) / 100.0

                self.record_metric(MetricType.MEMORY_USAGE, memory_percent)
                self.record_metric(MetricType.CPU_USAGE, cpu_percent)

                # Calcular score de qualidade a cada 5 minutos
                if len(self.metrics_history) % 300 == 0:  # A cada 5 minutos (assumindo 1 coleta/segundo)
                    self.calculate_quality_score()

            except Exception as e:
                # Não registrar erro para evitar loop infinito
                pass

            time.sleep(1)  # Coletar a cada segundo

    def get_current_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais."""
        return self.current_metrics

    def get_metrics_history(self, metric_type: Optional[MetricType] = None,
                           limit: int = 100) -> List[Dict]:
        """Retorna histórico de métricas."""

        history = self.metrics_history

        if metric_type:
            history = [m for m in history if m["metric_type"] == metric_type.value]

        return history[-limit:]

    def get_quality_scores_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de scores de qualidade."""

        if self.quality_scores_log.exists():
            try:
                return json.loads(self.quality_scores_log.read_text(encoding='utf-8'))[-limit:]
            except Exception:
                return []

        return []

    def meets_quality_threshold(self, min_score: float = 0.7) -> bool:
        """
        Verifica se a IA atende aos thresholds de qualidade.
        """

        latest_score = self.calculate_quality_score(time_window_minutes=30)
        return latest_score.get("overall_score", 0.0) >= min_score

    def _save_quality_score(self, score: Dict) -> None:
        """Salva score de qualidade."""

        try:
            history = []
            if self.quality_scores_log.exists():
                history = json.loads(self.quality_scores_log.read_text(encoding='utf-8'))

            history.append(score)

            self.quality_scores_log.write_text(
                json.dumps(history[-1000:], ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception:
            pass  # Não falhar se não conseguir salvar

    def _load_state(self) -> None:
        """Carrega estado das métricas."""

        if self.metrics_log.exists():
            try:
                self.metrics_history = json.loads(
                    self.metrics_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.metrics_history = []

    def _save_state(self) -> None:
        """Persiste métricas."""

        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_log.write_text(
            json.dumps(self.metrics_history[-5000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
