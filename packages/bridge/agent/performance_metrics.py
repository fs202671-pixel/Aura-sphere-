"""
Módulo de Métricas de Performance - Coleta e análise de métricas do sistema

Este módulo implementa coleta abrangente de métricas de performance,
análise de tendências e relatórios para otimização do sistema.
"""

from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import psutil
import asyncio
from collections import defaultdict, deque
import statistics
import threading
import time


class MetricType(Enum):
    """Tipos de métricas."""
    COUNTER = "counter"          # Contador incremental
    GAUGE = "gauge"             # Valor atual
    HISTOGRAM = "histogram"     # Distribuição de valores
    SUMMARY = "summary"         # Estatísticas resumidas


class MetricCategory(Enum):
    """Categorias de métricas."""
    SYSTEM = "system"           # Métricas do sistema
    APPLICATION = "application" # Métricas da aplicação
    BUSINESS = "business"       # Métricas de negócio
    PERFORMANCE = "performance" # Métricas de performance
    SECURITY = "security"       # Métricas de segurança


class MetricData:
    """
    Dados de uma métrica específica.
    """

    def __init__(self, name: str, metric_type: MetricType,
                 category: MetricCategory, description: str = ""):
        self.name = name
        self.type = metric_type
        self.category = category
        self.description = description

        self.values: deque = deque(maxlen=1000)  # Últimos 1000 valores
        self.timestamps: deque = deque(maxlen=1000)

        self.labels: Dict[str, str] = {}

        # Estatísticas calculadas
        self.last_value = None
        self.last_timestamp = None
        self.min_value = None
        self.max_value = None
        self.avg_value = None
        self.median_value = None
        self.std_dev = None

    def add_value(self, value: float, timestamp: datetime = None,
                  labels: Dict[str, str] = None) -> None:
        """Adiciona um novo valor à métrica."""

        if timestamp is None:
            timestamp = datetime.now()

        self.values.append(value)
        self.timestamps.append(timestamp)

        if labels:
            self.labels.update(labels)

        self.last_value = value
        self.last_timestamp = timestamp

        self._update_statistics()

    def _update_statistics(self) -> None:
        """Atualiza estatísticas calculadas."""

        if not self.values:
            return

        values_list = list(self.values)

        self.min_value = min(values_list)
        self.max_value = max(values_list)
        self.avg_value = statistics.mean(values_list)

        if len(values_list) > 1:
            self.median_value = statistics.median(values_list)
            self.std_dev = statistics.stdev(values_list)

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas da métrica."""

        return {
            "name": self.name,
            "type": self.type.value,
            "category": self.category.value,
            "description": self.description,
            "count": len(self.values),
            "last_value": self.last_value,
            "last_timestamp": self.last_timestamp.isoformat() if self.last_timestamp else None,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "avg_value": self.avg_value,
            "median_value": self.median_value,
            "std_dev": self.std_dev,
            "labels": self.labels.copy()
        }

    def get_recent_trend(self, hours: int = 1) -> Dict[str, Any]:
        """Retorna tendência recente da métrica."""

        cutoff = datetime.now() - timedelta(hours=hours)

        recent_values = []
        recent_timestamps = []

        for i, ts in enumerate(self.timestamps):
            if ts >= cutoff:
                recent_values.append(self.values[i])
                recent_timestamps.append(ts)

        if len(recent_values) < 2:
            return {"trend": "insufficient_data", "change_percent": 0.0}

        # Calcular tendência linear simples
        x = [(ts - recent_timestamps[0]).total_seconds() for ts in recent_timestamps]
        y = recent_values

        if len(x) > 1:
            slope = statistics.linear_regression(x, y)[0]
            avg_value = statistics.mean(y)

            if avg_value != 0:
                change_percent = (slope * 3600) / avg_value * 100  # Por hora
            else:
                change_percent = 0.0

            trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"

            return {
                "trend": trend,
                "change_percent_per_hour": change_percent,
                "slope": slope,
                "data_points": len(recent_values)
            }

        return {"trend": "stable", "change_percent": 0.0}


class PerformanceMetricsCollector:
    """
    Coletor de métricas de performance.

    Funcionalidades:
    - Coleta automática de métricas do sistema
    - Métricas customizadas da aplicação
    - Análise de tendências e anomalias
    - Relatórios de performance
    - Alertas baseados em thresholds
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.metrics_dir = data_dir / "performance_metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_file = self.metrics_dir / "metrics_data.json"
        self.alerts_file = self.metrics_dir / "alerts_log.json"

        self.metrics: Dict[str, MetricData] = {}
        self.alerts: List[Dict[str, Any]] = []

        # Configurações
        self.collection_interval_seconds = 30
        self.retention_days = 7
        self.alert_thresholds = {
            "cpu_usage_percent": 80.0,
            "memory_usage_percent": 85.0,
            "disk_usage_percent": 90.0,
            "response_time_seconds": 2.0,
            "error_rate_percent": 5.0
        }

        # Callbacks para alertas
        self.alert_callbacks: List[Callable] = []

        # Estatísticas globais
        self.stats = {
            "total_metrics": 0,
            "total_alerts": 0,
            "collection_count": 0,
            "avg_collection_time_seconds": 0.0
        }

        self._load_state()
        self._initialize_system_metrics()

    def _initialize_system_metrics(self) -> None:
        """Inicializa métricas do sistema."""

        # CPU
        self.register_metric("system_cpu_percent", MetricType.GAUGE,
                           MetricCategory.SYSTEM, "CPU usage percentage")

        # Memória
        self.register_metric("system_memory_percent", MetricType.GAUGE,
                           MetricCategory.SYSTEM, "Memory usage percentage")
        self.register_metric("system_memory_used_gb", MetricType.GAUGE,
                           MetricCategory.SYSTEM, "Memory used in GB")

        # Disco
        self.register_metric("system_disk_percent", MetricType.GAUGE,
                           MetricCategory.SYSTEM, "Disk usage percentage")
        self.register_metric("system_disk_used_gb", MetricType.GAUGE,
                           MetricCategory.SYSTEM, "Disk used in GB")

        # Rede
        self.register_metric("system_network_bytes_sent", MetricType.COUNTER,
                           MetricCategory.SYSTEM, "Network bytes sent")
        self.register_metric("system_network_bytes_recv", MetricType.COUNTER,
                           MetricCategory.SYSTEM, "Network bytes received")

        # Aplicação
        self.register_metric("app_response_time_seconds", MetricType.HISTOGRAM,
                           MetricCategory.PERFORMANCE, "Application response time")
        self.register_metric("app_requests_total", MetricType.COUNTER,
                           MetricCategory.APPLICATION, "Total requests")
        self.register_metric("app_errors_total", MetricType.COUNTER,
                           MetricCategory.APPLICATION, "Total errors")
        self.register_metric("app_active_connections", MetricType.GAUGE,
                           MetricCategory.APPLICATION, "Active connections")

    async def start_collection(self) -> None:
        """
        Inicia coleta automática de métricas.
        """

        while True:
            try:
                start_time = time.time()
                await self._collect_system_metrics()
                await self._check_alerts()

                collection_time = time.time() - start_time
                self.stats["collection_count"] += 1
                self.stats["avg_collection_time_seconds"] = (
                    (self.stats["avg_collection_time_seconds"] * (self.stats["collection_count"] - 1)) +
                    collection_time
                ) / self.stats["collection_count"]

                await asyncio.sleep(self.collection_interval_seconds)

            except Exception as e:
                print(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)  # Aguardar 1 minuto em caso de erro

    async def _collect_system_metrics(self) -> None:
        """Coleta métricas do sistema."""

        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system_cpu_percent", cpu_percent)

            # Memória
            memory = psutil.virtual_memory()
            self.record_metric("system_memory_percent", memory.percent)
            self.record_metric("system_memory_used_gb", memory.used / (1024**3))

            # Disco
            disk = psutil.disk_usage('/')
            self.record_metric("system_disk_percent", disk.percent)
            self.record_metric("system_disk_used_gb", disk.used / (1024**3))

            # Rede
            network = psutil.net_io_counters()
            self.record_metric("system_network_bytes_sent", network.bytes_sent)
            self.record_metric("system_network_bytes_recv", network.bytes_recv)

        except Exception as e:
            print(f"Error collecting system metrics: {e}")

    def register_metric(self, name: str, metric_type: MetricType,
                       category: MetricCategory, description: str = "") -> None:
        """Registra uma nova métrica."""

        if name not in self.metrics:
            self.metrics[name] = MetricData(name, metric_type, category, description)
            self.stats["total_metrics"] += 1
            self._save_state()

    def record_metric(self, name: str, value: float,
                     labels: Dict[str, str] = None) -> None:
        """Registra um valor para uma métrica."""

        if name in self.metrics:
            self.metrics[name].add_value(value, labels=labels)

    def record_request(self, response_time: float, success: bool = True,
                      endpoint: str = "") -> None:
        """Registra uma requisição."""

        self.record_metric("app_requests_total", 1, {"endpoint": endpoint})
        self.record_metric("app_response_time_seconds", response_time, {"endpoint": endpoint})

        if not success:
            self.record_metric("app_errors_total", 1, {"endpoint": endpoint})

    def record_error(self, error_type: str, message: str = "") -> None:
        """Registra um erro."""

        self.record_metric("app_errors_total", 1, {"error_type": error_type})

    async def _check_alerts(self) -> None:
        """Verifica condições de alerta."""

        alerts_triggered = []

        for name, metric in self.metrics.items():
            if metric.last_value is None:
                continue

            threshold_key = None
            if "cpu" in name and "percent" in name:
                threshold_key = "cpu_usage_percent"
            elif "memory" in name and "percent" in name:
                threshold_key = "memory_usage_percent"
            elif "disk" in name and "percent" in name:
                threshold_key = "disk_usage_percent"
            elif "response_time" in name:
                threshold_key = "response_time_seconds"
            elif "error" in name and "rate" in name:
                threshold_key = "error_rate_percent"

            if threshold_key and threshold_key in self.alert_thresholds:
                threshold = self.alert_thresholds[threshold_key]

                if metric.last_value > threshold:
                    alert = {
                        "timestamp": datetime.now().isoformat(),
                        "metric": name,
                        "value": metric.last_value,
                        "threshold": threshold,
                        "severity": "warning" if metric.last_value < threshold * 1.5 else "critical",
                        "message": f"{name} exceeded threshold: {metric.last_value:.2f} > {threshold}"
                    }

                    alerts_triggered.append(alert)
                    self.alerts.append(alert)
                    self.stats["total_alerts"] += 1

        # Notificar callbacks
        for alert in alerts_triggered:
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    print(f"Error in alert callback: {e}")

    def add_alert_callback(self, callback: Callable) -> None:
        """Adiciona callback para alertas."""

        self.alert_callbacks.append(callback)

    def get_metric_statistics(self, name: str) -> Optional[Dict[str, Any]]:
        """Retorna estatísticas de uma métrica específica."""

        metric = self.metrics.get(name)
        return metric.get_statistics() if metric else None

    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo de todas as métricas."""

        summary = {
            "total_metrics": len(self.metrics),
            "categories": defaultdict(int),
            "types": defaultdict(int),
            "alerts_today": 0,
            "recent_trends": {}
        }

        today = datetime.now().date()

        for name, metric in self.metrics.items():
            summary["categories"][metric.category.value] += 1
            summary["types"][metric.type.value] += 1

            # Contar alertas de hoje
            for alert in self.alerts:
                alert_date = datetime.fromisoformat(alert["timestamp"]).date()
                if alert_date == today:
                    summary["alerts_today"] += 1

            # Tendências recentes
            trend = metric.get_recent_trend(hours=1)
            if trend["trend"] != "insufficient_data":
                summary["recent_trends"][name] = trend

        return dict(summary)

    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Gera relatório de performance."""

        report = {
            "period_hours": hours,
            "generated_at": datetime.now().isoformat(),
            "system_performance": {},
            "application_performance": {},
            "alerts_summary": {},
            "recommendations": []
        }

        cutoff = datetime.now() - timedelta(hours=hours)

        # Performance do sistema
        system_metrics = ["system_cpu_percent", "system_memory_percent", "system_disk_percent"]
        for metric_name in system_metrics:
            metric = self.metrics.get(metric_name)
            if metric:
                trend = metric.get_recent_trend(hours)
                report["system_performance"][metric_name] = {
                    "current": metric.last_value,
                    "average": metric.avg_value,
                    "trend": trend
                }

        # Performance da aplicação
        app_metrics = ["app_response_time_seconds", "app_requests_total", "app_errors_total"]
        for metric_name in app_metrics:
            metric = self.metrics.get(metric_name)
            if metric:
                trend = metric.get_recent_trend(hours)
                report["application_performance"][metric_name] = {
                    "current": metric.last_value,
                    "average": metric.avg_value,
                    "trend": trend
                }

        # Resumo de alertas
        recent_alerts = [a for a in self.alerts
                        if datetime.fromisoformat(a["timestamp"]) >= cutoff]

        report["alerts_summary"] = {
            "total": len(recent_alerts),
            "by_severity": defaultdict(int),
            "by_metric": defaultdict(int)
        }

        for alert in recent_alerts:
            report["alerts_summary"]["by_severity"][alert["severity"]] += 1
            report["alerts_summary"]["by_metric"][alert["metric"]] += 1

        # Recomendações baseadas nos dados
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas no relatório."""

        recommendations = []

        # Verificar uso de CPU alto
        cpu_metric = report["system_performance"].get("system_cpu_percent", {})
        if cpu_metric.get("current", 0) > 70:
            recommendations.append("High CPU usage detected. Consider optimizing CPU-intensive operations.")

        # Verificar uso de memória alto
        memory_metric = report["system_performance"].get("system_memory_percent", {})
        if memory_metric.get("current", 0) > 80:
            recommendations.append("High memory usage detected. Consider memory optimization or increasing RAM.")

        # Verificar tempo de resposta lento
        response_metric = report["application_performance"].get("app_response_time_seconds", {})
        if response_metric.get("current", 0) > 1.0:
            recommendations.append("Slow response times detected. Consider optimizing database queries or caching.")

        # Verificar alta taxa de erros
        errors_metric = report["application_performance"].get("app_errors_total", {})
        requests_metric = report["application_performance"].get("app_requests_total", {})

        if requests_metric.get("current", 0) > 0:
            error_rate = errors_metric.get("current", 0) / requests_metric.get("current", 0) * 100
            if error_rate > 5:
                recommendations.append(f"High error rate ({error_rate:.1f}%). Investigate error causes.")

        # Verificar tendências negativas
        for metric_name, data in report["system_performance"].items():
            trend = data.get("trend", {})
            if trend.get("trend") == "increasing" and trend.get("change_percent_per_hour", 0) > 10:
                recommendations.append(f"{metric_name} is trending upward rapidly. Monitor closely.")

        if not recommendations:
            recommendations.append("System performance is within normal parameters.")

        return recommendations

    def export_metrics(self, format_type: str = "json") -> str:
        """Exporta métricas em formato específico."""

        if format_type == "json":
            metrics_data = {}
            for name, metric in self.metrics.items():
                metrics_data[name] = metric.get_statistics()

            return json.dumps(metrics_data, ensure_ascii=False, indent=2, default=str)

        elif format_type == "prometheus":
            lines = []
            for name, metric in self.metrics.items():
                if metric.last_value is not None:
                    lines.append(f"# HELP {name} {metric.description}")
                    lines.append(f"# TYPE {name} {metric.type.value}")
                    lines.append(f"{name} {metric.last_value}")
            return "\n".join(lines)

        return ""

    def cleanup_old_data(self) -> int:
        """Limpa dados antigos baseado na retenção configurada."""

        cutoff = datetime.now() - timedelta(days=self.retention_days)
        cleaned_count = 0

        for metric in self.metrics.values():
            # Remover valores antigos
            while metric.timestamps and metric.timestamps[0] < cutoff:
                metric.values.popleft()
                metric.timestamps.popleft()
                cleaned_count += 1

            # Recalcular estatísticas
            metric._update_statistics()

        # Limpar alertas antigos
        original_count = len(self.alerts)
        self.alerts = [a for a in self.alerts
                      if datetime.fromisoformat(a["timestamp"]) >= cutoff]
        cleaned_count += original_count - len(self.alerts)

        self._save_state()

        return cleaned_count

    def _load_state(self) -> None:
        """Carrega estado das métricas."""

        if self.metrics_file.exists():
            try:
                data = json.loads(self.metrics_file.read_text(encoding='utf-8'))

                for metric_data in data.get("metrics", []):
                    metric = MetricData(
                        metric_data["name"],
                        MetricType(metric_data["type"]),
                        MetricCategory(metric_data["category"]),
                        metric_data.get("description", "")
                    )

                    # Restaurar valores
                    for value, timestamp_str in zip(
                        metric_data.get("values", []),
                        metric_data.get("timestamps", [])
                    ):
                        timestamp = datetime.fromisoformat(timestamp_str)
                        metric.add_value(value, timestamp)

                    # Restaurar labels
                    metric.labels = metric_data.get("labels", {})

                    self.metrics[metric.name] = metric

                # Carregar estatísticas
                if "stats" in data:
                    self.stats.update(data["stats"])

            except Exception as e:
                print(f"Error loading metrics state: {e}")

        # Carregar alertas
        if self.alerts_file.exists():
            try:
                self.alerts = json.loads(self.alerts_file.read_text(encoding='utf-8'))
            except Exception:
                self.alerts = []

    def _save_state(self) -> None:
        """Persiste estado das métricas."""

        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Serializar métricas
        metrics_data = {
            "metrics": [],
            "stats": self.stats,
            "last_updated": datetime.now().isoformat()
        }

        for metric in self.metrics.values():
            metric_data = metric.get_statistics()
            metric_data["values"] = list(metric.values)
            metric_data["timestamps"] = [ts.isoformat() for ts in metric.timestamps]

            metrics_data["metrics"].append(metric_data)

        self.metrics_file.write_text(
            json.dumps(metrics_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Salvar alertas
        self.alerts_file.write_text(
            json.dumps(self.alerts[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
