"""
Dashboard de Observabilidade Completo
Sistema de monitoramento em tempo real do estado, versões, ações, recursos e eventos de segurança.
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import deque
import threading

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_connections: int
    active_threads: int
    open_files: int

@dataclass
class SecurityEvent:
    """Evento de segurança"""
    timestamp: str
    event_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    source: str
    details: Dict[str, Any]

@dataclass
class ActionLog:
    """Log de ação do sistema"""
    timestamp: str
    action_type: str
    component: str
    status: str  # "started", "completed", "failed"
    duration_ms: Optional[int]
    details: Dict[str, Any]

@dataclass
class VersionInfo:
    """Informações de versão"""
    component: str
    version: str
    last_updated: str
    status: str  # "stable", "testing", "unstable"
    hash: str

class ObservabilityDashboard:
    """
    Dashboard completo de observabilidade com monitoramento em tempo real
    """

    def __init__(self, base_path: str = "/workspaces/Aura-sphere-"):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger("ObservabilityDashboard")

        # Métricas em tempo real
        self.metrics_history: deque[SystemMetrics] = deque(maxlen=1000)
        self.security_events: deque[SecurityEvent] = deque(maxlen=500)
        self.action_logs: deque[ActionLog] = deque(maxlen=1000)

        # Estado do sistema
        self.system_versions: Dict[str, VersionInfo] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        self.performance_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage": 90.0
        }

        # Callbacks para alertas
        self.alert_callbacks: List[Callable] = []

        # Thread de monitoramento
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False

        # Arquivos de estado
        self.state_file = self.base_path / "observability_state.json"

        # Carregar estado salvo
        self._load_state()

    def _load_state(self):
        """Carrega estado salvo do dashboard"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    # Carregar alertas ativas
                    self.active_alerts = data.get("active_alerts", [])
            except Exception as e:
                self.logger.warning(f"Erro ao carregar estado: {e}")

    def _save_state(self):
        """Salva estado do dashboard"""
        try:
            data = {
                "active_alerts": self.active_alerts,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Erro ao salvar estado: {e}")

    def start_monitoring(self):
        """Inicia monitoramento em tempo real"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Monitoramento de observabilidade iniciado")

    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Monitoramento de observabilidade parado")

    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                # Coletar métricas
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)

                # Verificar thresholds
                self._check_thresholds(metrics)

                # Limpar dados antigos (manter últimas 24h)
                self._cleanup_old_data()

                time.sleep(5)  # Coletar a cada 5 segundos

            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(10)

    def _collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_connections()
            threads = threading.active_count()

            # Contar arquivos abertos (aproximado)
            try:
                open_files = len(psutil.Process().open_files())
            except:
                open_files = 0

            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage=disk.percent,
                network_connections=len(network),
                active_threads=threads,
                open_files=open_files
            )
        except Exception as e:
            self.logger.warning(f"Erro ao coletar métricas: {e}")
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage=0.0,
                network_connections=0,
                active_threads=0,
                open_files=0
            )

    def _check_thresholds(self, metrics: SystemMetrics):
        """Verifica se métricas ultrapassam thresholds"""
        alerts_triggered = []

        if metrics.cpu_percent > self.performance_thresholds["cpu_percent"]:
            alerts_triggered.append({
                "type": "cpu_high",
                "message": f"CPU usage high: {metrics.cpu_percent:.1f}%",
                "severity": "medium"
            })

        if metrics.memory_percent > self.performance_thresholds["memory_percent"]:
            alerts_triggered.append({
                "type": "memory_high",
                "message": f"Memory usage high: {metrics.memory_percent:.1f}%",
                "severity": "high"
            })

        if metrics.disk_usage > self.performance_thresholds["disk_usage"]:
            alerts_triggered.append({
                "type": "disk_high",
                "message": f"Disk usage high: {metrics.disk_usage:.1f}%",
                "severity": "high"
            })

        # Adicionar alertas
        for alert in alerts_triggered:
            self.add_security_event(
                event_type="performance_alert",
                severity=alert["severity"],
                description=alert["message"],
                source="system_monitor",
                details={"metric": alert["type"], "value": metrics}
            )

            # Notificar callbacks
            self._notify_alert_callbacks(alert)

    def _notify_alert_callbacks(self, alert: Dict[str, Any]):
        """Notifica callbacks de alerta"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.warning(f"Erro no callback de alerta: {e}")

    def _cleanup_old_data(self):
        """Limpa dados antigos"""
        cutoff_time = datetime.now() - timedelta(hours=24)

        # Limpar métricas antigas
        while self.metrics_history and datetime.fromisoformat(self.metrics_history[0].timestamp) < cutoff_time:
            self.metrics_history.popleft()

        # Limpar logs antigos
        while self.action_logs and datetime.fromisoformat(self.action_logs[0].timestamp) < cutoff_time:
            self.action_logs.popleft()

        # Limpar eventos antigos (manter 7 dias)
        cutoff_security = datetime.now() - timedelta(days=7)
        while self.security_events and datetime.fromisoformat(self.security_events[0].timestamp) < cutoff_security:
            self.security_events.popleft()

    def add_security_event(self, event_type: str, severity: str, description: str,
                          source: str, details: Dict[str, Any] = None):
        """Adiciona evento de segurança"""
        if details is None:
            details = {}

        event = SecurityEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            severity=severity,
            description=description,
            source=source,
            details=details
        )

        self.security_events.append(event)

        # Log crítico para eventos high/critical
        if severity in ["high", "critical"]:
            self.logger.warning(f"Security Event [{severity}]: {description}")

    def log_action(self, action_type: str, component: str, status: str,
                   duration_ms: Optional[int] = None, details: Dict[str, Any] = None):
        """Registra ação do sistema"""
        if details is None:
            details = {}

        action = ActionLog(
            timestamp=datetime.now().isoformat(),
            action_type=action_type,
            component=component,
            status=status,
            duration_ms=duration_ms,
            details=details
        )

        self.action_logs.append(action)

        # Log baseado no status
        if status == "failed":
            self.logger.error(f"Action failed: {action_type} in {component}")
        elif status == "completed":
            self.logger.info(f"Action completed: {action_type} in {component}")

    def update_version_info(self, component: str, version: str, status: str, hash_val: str):
        """Atualiza informações de versão"""
        version_info = VersionInfo(
            component=component,
            version=version,
            last_updated=datetime.now().isoformat(),
            status=status,
            hash=hash_val
        )

        self.system_versions[component] = version_info
        self.logger.info(f"Version updated: {component} v{version} ({status})")

    def add_alert_callback(self, callback: Callable):
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados completos do dashboard"""
        return {
            "current_metrics": asdict(self.metrics_history[-1]) if self.metrics_history else None,
            "metrics_history": [asdict(m) for m in list(self.metrics_history)[-50:]],  # Últimas 50
            "security_events": [asdict(e) for e in list(self.security_events)[-20:]],  # Últimas 20
            "action_logs": [asdict(a) for a in list(self.action_logs)[-50:]],  # Últimas 50
            "system_versions": {k: asdict(v) for k, v in self.system_versions.items()},
            "active_alerts": self.active_alerts,
            "system_health": self._calculate_system_health(),
            "performance_summary": self._get_performance_summary()
        }

    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calcula saúde geral do sistema"""
        if not self.metrics_history:
            return {"status": "unknown", "score": 0}

        recent_metrics = list(self.metrics_history)[-10:]  # Últimas 10 medições

        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)

        # Calcular score (0-100)
        cpu_score = max(0, 100 - avg_cpu)
        memory_score = max(0, 100 - avg_memory)
        disk_score = max(0, 100 - avg_disk)

        overall_score = (cpu_score + memory_score + disk_score) / 3

        # Determinar status
        if overall_score >= 80:
            status = "healthy"
        elif overall_score >= 60:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "score": round(overall_score, 1),
            "metrics": {
                "cpu_score": round(cpu_score, 1),
                "memory_score": round(memory_score, 1),
                "disk_score": round(disk_score, 1)
            }
        }

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance"""
        if not self.metrics_history:
            return {}

        recent = list(self.metrics_history)[-60:]  # Última hora (60 * 5s = 5min)

        return {
            "avg_cpu": round(sum(m.cpu_percent for m in recent) / len(recent), 1),
            "avg_memory": round(sum(m.memory_percent for m in recent) / len(recent), 1),
            "avg_disk": round(sum(m.disk_usage for m in recent) / len(recent), 1),
            "peak_cpu": max(m.cpu_percent for m in recent),
            "peak_memory": max(m.memory_percent for m in recent),
            "total_measurements": len(self.metrics_history)
        }

    def get_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Gera relatório de segurança"""
        cutoff = datetime.now() - timedelta(hours=hours)

        relevant_events = [
            e for e in self.security_events
            if datetime.fromisoformat(e.timestamp) > cutoff
        ]

        severity_counts = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }

        for event in relevant_events:
            severity_counts[event.severity] += 1

        return {
            "period_hours": hours,
            "total_events": len(relevant_events),
            "severity_breakdown": severity_counts,
            "recent_events": [asdict(e) for e in relevant_events[-10:]],
            "most_common_types": self._get_most_common_event_types(relevant_events)
        }

    def _get_most_common_event_types(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Retorna tipos de evento mais comuns"""
        from collections import Counter

        types = Counter(e.event_type for e in events)
        return [{"type": t, "count": c} for t, c in types.most_common(5)]

    def export_dashboard_data(self, filepath: str):
        """Exporta dados do dashboard para arquivo"""
        data = self.get_dashboard_data()
        data["export_timestamp"] = datetime.now().isoformat()

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        self.logger.info(f"Dashboard data exported to {filepath}")

    def clear_old_data(self, days: int = 7):
        """Limpa dados antigos"""
        cutoff = datetime.now() - timedelta(days=days)

        # Limpar métricas
        while self.metrics_history and datetime.fromisoformat(self.metrics_history[0].timestamp) < cutoff:
            self.metrics_history.popleft()

        # Limpar logs
        while self.action_logs and datetime.fromisoformat(self.action_logs[0].timestamp) < cutoff:
            self.action_logs.popleft()

        # Limpar eventos de segurança (manter 30 dias)
        security_cutoff = datetime.now() - timedelta(days=30)
        while self.security_events and datetime.fromisoformat(self.security_events[0].timestamp) < security_cutoff:
            self.security_events.popleft()

        self.logger.info(f"Old data cleared (keeping {days} days)")

    def get_component_status(self, component: str) -> Dict[str, Any]:
        """Retorna status de um componente específico"""
        version_info = self.system_versions.get(component)

        # Buscar ações recentes do componente
        recent_actions = [
            a for a in list(self.action_logs)[-100:]
            if a.component == component
        ]

        # Buscar eventos de segurança relacionados
        security_events = [
            e for e in list(self.security_events)[-100:]
            if e.source == component or component in e.details.get("component", "")
        ]

        return {
            "component": component,
            "version_info": asdict(version_info) if version_info else None,
            "recent_actions": [asdict(a) for a in recent_actions[-5:]],
            "security_events": [asdict(e) for e in security_events[-5:]],
            "status": version_info.status if version_info else "unknown"
        }