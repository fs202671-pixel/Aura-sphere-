"""
Observability Dashboard - Visibilidade interna do sistema.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json


class ObservabilityDashboard:
    """Fornece visibilidade interna do estado do sistema."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.metrics_file = data_dir / "metrics.json"
        self.metrics: List[Dict[str, Any]] = []
        self._load_metrics()

    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Registra uma métrica."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "value": value,
            "tags": tags or {}
        }
        self.metrics.append(entry)
        # Manter últimas 1000 métricas
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
        self._save_metrics()

    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status geral do sistema."""
        return {
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0",
            "components": {
                "core": "operational",
                "agent": "operational",
                "runtime": "operational",
                "sandbox": "operational"
            },
            "mode": "offline",
            "safe_mode": False,
            "memory_usage_percent": self._estimate_memory_usage(),
            "cpu_usage_percent": self._estimate_cpu_usage(),
            "active_sessions": 1
        }

    def get_agent_status(self, agent_service: Any) -> Dict[str, Any]:
        """Retorna status detalhado do agente."""
        session = agent_service.session_state
        supervisor = agent_service.supervisor

        return {
            "timestamp": datetime.now().isoformat(),
            "session_id": session.session_id,
            "agent_id": session.agent_id,
            "user_id": session.user_id,
            "uptime_seconds": self._calculate_uptime(session.started_at),
            "offline_mode": agent_service.offline_mode,
            "safe_mode": supervisor.safe_mode,
            "recent_tasks": len(session.tasks),
            "pending_tasks": len([t for t in session.tasks if t.status != "completed"]),
            "completed_tasks": len([t for t in session.tasks if t.status == "completed"]),
            "pending_approvals": len([p for p in session.modification_proposals if p.status == "pending"]),
            "approved_modifications": len([p for p in session.modification_proposals if p.status == "approved"]),
            "rejected_modifications": len([p for p in session.modification_proposals if p.status == "rejected"])
        }

    def get_memory_snapshot(self, agent_service: Any) -> Dict[str, Any]:
        """Retorna snapshot de uso de memória."""
        memory_store = agent_service.memory_store
        entries = memory_store.entries

        by_layer = {}
        for entry in entries:
            layer = entry.layer
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append({
                "entry_id": entry.entry_id,
                "size_bytes": len(entry.content.encode('utf-8')),
                "created_at": entry.created_at
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "total_entries": len(entries),
            "by_layer": {layer: {"count": len(items), "size_bytes": sum(i["size_bytes"] for i in items)} for layer, items in by_layer.items()},
            "total_size_mb": sum(sum(i["size_bytes"] for i in items) for items in by_layer.values()) / (1024 * 1024)
        }

    def get_version_status(self, evolution_manager: Any) -> Dict[str, Any]:
        """Retorna status de versões."""
        versions = evolution_manager.list_versions(limit=10)
        best_version = evolution_manager.choose_best_version()

        return {
            "timestamp": datetime.now().isoformat(),
            "total_versions": len(evolution_manager.versions),
            "recent_versions": [
                {
                    "version_id": v.version_id,
                    "created_at": v.created_at,
                    "score": evolution_manager.score_version(v),
                    "description": v.description
                }
                for v in versions
            ],
            "best_version": {
                "version_id": best_version.version_id,
                "score": evolution_manager.score_version(best_version),
                "description": best_version.description
            } if best_version else None
        }

    def get_security_status(self, agent_service: Any) -> Dict[str, Any]:
        """Retorna status de segurança."""
        anomalies = agent_service.get_active_anomalies()

        return {
            "timestamp": datetime.now().isoformat(),
            "active_anomalies": len(anomalies),
            "critical_anomalies": len([a for a in anomalies if a["severity"] == "critical"]),
            "safe_mode_active": agent_service.supervisor.safe_mode,
            "recent_anomalies": anomalies[-5:] if anomalies else []
        }

    def get_performance_metrics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Retorna métricas de performance."""
        cutoff = datetime.now() - timedelta(minutes=time_window_minutes)
        recent = [m for m in self.metrics if datetime.fromisoformat(m["timestamp"]) >= cutoff]

        metrics_by_name = {}
        for metric in recent:
            name = metric["metric"]
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            metrics_by_name[name].append(metric["value"])

        aggregated = {}
        for name, values in metrics_by_name.items():
            aggregated[name] = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1] if values else None
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "time_window_minutes": time_window_minutes,
            "metrics": aggregated
        }

    def get_full_dashboard(self, agent_service: Any) -> Dict[str, Any]:
        """Retorna dashboard completo."""
        return {
            "generated_at": datetime.now().isoformat(),
            "system_status": self.get_system_status(),
            "agent_status": self.get_agent_status(agent_service),
            "memory_usage": self.get_memory_snapshot(agent_service),
            "versions": self.get_version_status(agent_service.evolution_manager),
            "security": self.get_security_status(agent_service),
            "performance": self.get_performance_metrics()
        }

    def _calculate_uptime(self, started_at: str) -> int:
        """Calcula uptime em segundos."""
        try:
            start = datetime.fromisoformat(started_at)
            return int((datetime.now() - start).total_seconds())
        except Exception:
            return 0

    def _estimate_memory_usage(self) -> float:
        """Estima uso de memória (simplificado)."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            total_memory = psutil.virtual_memory().total
            return (memory_info.rss / total_memory) * 100
        except Exception:
            return 0.0

    def _estimate_cpu_usage(self) -> float:
        """Estima uso de CPU (simplificado)."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0

    def _load_metrics(self) -> None:
        """Carrega métricas."""
        if self.metrics_file.exists():
            try:
                self.metrics = json.loads(self.metrics_file.read_text(encoding='utf-8'))
            except Exception:
                self.metrics = []

    def _save_metrics(self) -> None:
        """Persiste métricas."""
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_file.write_text(json.dumps(self.metrics, ensure_ascii=False, indent=2), encoding='utf-8')
