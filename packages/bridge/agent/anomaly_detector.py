"""
Anomaly Detector - Monitoramento contínuo de comportamento anormal.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class AnomalyEvent:
    """Evento de anomalia detectado."""
    event_id: str
    anomaly_type: str
    severity: str  # low, medium, high, critical
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_details: Optional[Dict[str, Any]] = None


class AnomalyDetector:
    """Detecta padrões anormais no comportamento do agente."""

    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file or Path("data/anomalies.json")
        self.anomalies: List[AnomalyEvent] = []
        self.thresholds = {
            "failed_patches_per_hour": 5,
            "security_violations_per_hour": 3,
            "high_errors_per_hour": 10,
            "repeated_failed_action": 3,
        }
        self.action_history: Dict[str, List[Dict[str, Any]]] = {}
        self._load_anomalies()

    def _load_anomalies(self) -> None:
        """Carrega histórico de anomalias."""
        if self.history_file.exists():
            try:
                data = json.loads(self.history_file.read_text(encoding='utf-8'))
                self.anomalies = [AnomalyEvent(**item) for item in data]
            except Exception:
                self.anomalies = []

    def _save_anomalies(self) -> None:
        """Persiste anomalias."""
        data = [
            {
                "event_id": a.event_id,
                "anomaly_type": a.anomaly_type,
                "severity": a.severity,
                "timestamp": a.timestamp,
                "details": a.details,
                "resolved": a.resolved,
                "resolution_details": a.resolution_details,
            }
            for a in self.anomalies
        ]
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def detect_failed_patches(self, failed_count: int, time_window_minutes: int = 60) -> Optional[AnomalyEvent]:
        """Detecta múltiplas falhas de patch em janela de tempo."""
        if failed_count >= self.thresholds["failed_patches_per_hour"]:
            anomaly = AnomalyEvent(
                event_id=f"anom_{datetime.now().timestamp()}",
                anomaly_type="high_patch_failure_rate",
                severity="high",
                details={
                    "failed_count": failed_count,
                    "threshold": self.thresholds["failed_patches_per_hour"],
                    "time_window_minutes": time_window_minutes
                }
            )
            self.anomalies.append(anomaly)
            self._save_anomalies()
            return anomaly
        return None

    def detect_security_pattern(self, violation_count: int, time_window_minutes: int = 60) -> Optional[AnomalyEvent]:
        """Detecta padrão de violações de segurança."""
        if violation_count >= self.thresholds["security_violations_per_hour"]:
            anomaly = AnomalyEvent(
                event_id=f"anom_{datetime.now().timestamp()}",
                anomaly_type="security_violation_pattern",
                severity="critical",
                details={
                    "violation_count": violation_count,
                    "threshold": self.thresholds["security_violations_per_hour"],
                    "time_window_minutes": time_window_minutes
                }
            )
            self.anomalies.append(anomaly)
            self._save_anomalies()
            return anomaly
        return None

    def detect_repeated_failures(self, action: str, failure_count: int) -> Optional[AnomalyEvent]:
        """Detecta repetição de falhas na mesma ação."""
        if failure_count >= self.thresholds["repeated_failed_action"]:
            anomaly = AnomalyEvent(
                event_id=f"anom_{datetime.now().timestamp()}",
                anomaly_type="repeated_action_failure",
                severity="medium",
                details={
                    "action": action,
                    "failure_count": failure_count,
                    "threshold": self.thresholds["repeated_failed_action"]
                }
            )
            self.anomalies.append(anomaly)
            self._save_anomalies()
            return anomaly
        return None

    def detect_inconsistent_decisions(self, decisions: List[str]) -> Optional[AnomalyEvent]:
        """Detecta decisões inconsistentes do agente."""
        # Se agente muda decisão sobre mesmo contexto várias vezes
        if len(set(decisions)) > 1 and len(decisions) >= 3:
            anomaly = AnomalyEvent(
                event_id=f"anom_{datetime.now().timestamp()}",
                anomaly_type="inconsistent_decisions",
                severity="medium",
                details={"decision_count": len(decisions), "unique_decisions": len(set(decisions))}
            )
            self.anomalies.append(anomaly)
            self._save_anomalies()
            return anomaly
        return None

    def resolve_anomaly(self, anomaly_id: str, resolution: Dict[str, Any]) -> bool:
        """Marca uma anomalia como resolvida."""
        for anomaly in self.anomalies:
            if anomaly.event_id == anomaly_id:
                anomaly.resolved = True
                anomaly.resolution_details = resolution
                self._save_anomalies()
                return True
        return False

    def get_active_anomalies(self, severity: Optional[str] = None) -> List[AnomalyEvent]:
        """Retorna anomalias não resolvidas."""
        active = [a for a in self.anomalies if not a.resolved]
        if severity:
            active = [a for a in active if a.severity == severity]
        return active

    def get_anomalies_by_type(self, anomaly_type: str) -> List[AnomalyEvent]:
        """Retorna anomalias de um tipo específico."""
        return [a for a in self.anomalies if a.anomaly_type == anomaly_type]

    def trigger_safe_mode_if_critical(self) -> bool:
        """Verifica se anomalias críticas justificam safe mode."""
        critical_anomalies = [a for a in self.get_active_anomalies("critical")]
        return len(critical_anomalies) > 0

    def get_anomaly_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna resumo de anomalias recentes."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [a for a in self.anomalies if datetime.fromisoformat(a.timestamp) >= cutoff]

        return {
            "total_anomalies": len(recent),
            "by_type": self._count_by_type(recent),
            "by_severity": self._count_by_severity(recent),
            "open_anomalies": len([a for a in recent if not a.resolved]),
            "critical_count": len([a for a in recent if a.severity == "critical"])
        }

    def _count_by_type(self, anomalies: List[AnomalyEvent]) -> Dict[str, int]:
        """Conta anomalias por tipo."""
        counts = {}
        for anomaly in anomalies:
            counts[anomaly.anomaly_type] = counts.get(anomaly.anomaly_type, 0) + 1
        return counts

    def _count_by_severity(self, anomalies: List[AnomalyEvent]) -> Dict[str, int]:
        """Conta anomalias por severidade."""
        counts = {}
        for anomaly in anomalies:
            counts[anomaly.severity] = counts.get(anomaly.severity, 0) + 1
        return counts
