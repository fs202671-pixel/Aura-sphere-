"""
Sistema de Detecção de Anomalias Comportamentais - Monitora IA

Este módulo implementa monitoramento contínuo do comportamento da IA
para detectar padrões anômalos, loops de decisão e tentativas de violação.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import re
import statistics


class AnomalyType(Enum):
    """Tipos de anomalias comportamentais."""
    DECISION_LOOP = "decision_loop"
    RESPONSE_INCONSISTENCY = "response_inconsistency"
    SECURITY_PATTERN = "security_pattern"
    RESOURCE_ABUSE = "resource_abuse"
    CORE_VIOLATION_ATTEMPT = "core_violation_attempt"
    UNUSUAL_FREQUENCY = "unusual_frequency"
    PATTERN_DEVIATION = "pattern_deviation"
    MEMORY_ANOMALY = "memory_anomaly"


class BehavioralAnomalyDetector:
    """
    Detecta anomalias comportamentais da IA em tempo real.

    Monitora:
    - Loops de decisão repetitivos
    - Inconsistências nas respostas
    - Padrões de segurança suspeitos
    - Abuso de recursos
    - Tentativas de violação do core
    - Frequências incomuns de operações
    - Desvios de padrões normais
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.anomalies_dir = data_dir / "behavioral_anomalies"
        self.anomalies_dir.mkdir(parents=True, exist_ok=True)

        self.anomalies_log = self.anomalies_dir / "anomalies.json"
        self.behavior_patterns_log = self.anomalies_dir / "behavior_patterns.json"

        self.detected_anomalies: List[Dict] = []
        self.behavior_patterns: Dict[str, Any] = {}

        # Thresholds para detecção
        self.thresholds = {
            "decision_loop_threshold": 3,  # Mesmo decisão N vezes seguidas
            "inconsistency_threshold": 0.7,  # Score de inconsistência
            "frequency_spike_threshold": 5.0,  # Multiplicador sobre média
            "resource_abuse_threshold": 0.9,  # 90% de uso de recursos
            "pattern_deviation_threshold": 2.0,  # Desvio padrão
            "core_violation_keywords": [
                "modify.*core", "delete.*core", "override.*immutable",
                "change.*rules", "bypass.*security", "disable.*validation"
            ]
        }

        self._load_state()
        self._initialize_patterns()

    def _initialize_patterns(self) -> None:
        """Inicializa padrões comportamentais normais."""

        self.behavior_patterns = {
            "decision_frequency": {"history": [], "mean": 1.0, "std": 0.5},
            "response_consistency": {"history": [], "mean": 0.8, "std": 0.1},
            "resource_usage": {"history": [], "mean": 0.5, "std": 0.2},
            "operation_patterns": {},
            "security_attempts": {"count": 0, "last_attempt": None}
        }

    def analyze_behavior(self, behavior_data: Dict[str, Any]) -> List[Dict]:
        """
        Analisa comportamento da IA e detecta anomalias.
        """

        anomalies = []

        # Analisar diferentes tipos de anomalias
        decision_anomaly = self._detect_decision_loops(behavior_data)
        if decision_anomaly:
            anomalies.append(decision_anomaly)

        consistency_anomaly = self._detect_response_inconsistency(behavior_data)
        if consistency_anomaly:
            anomalies.append(consistency_anomaly)

        security_anomaly = self._detect_security_patterns(behavior_data)
        if security_anomaly:
            anomalies.append(security_anomaly)

        resource_anomaly = self._detect_resource_abuse(behavior_data)
        if resource_anomaly:
            anomalies.append(resource_anomaly)

        frequency_anomaly = self._detect_unusual_frequency(behavior_data)
        if frequency_anomaly:
            anomalies.append(frequency_anomaly)

        core_anomaly = self._detect_core_violation_attempts(behavior_data)
        if core_anomaly:
            anomalies.append(core_anomaly)

        pattern_anomaly = self._detect_pattern_deviation(behavior_data)
        if pattern_anomaly:
            anomalies.append(pattern_anomaly)

        # Registrar anomalias detectadas
        for anomaly in anomalies:
            self._record_anomaly(anomaly)

        # Atualizar padrões comportamentais
        self._update_behavior_patterns(behavior_data)

        return anomalies

    def _detect_decision_loops(self, behavior_data: Dict) -> Optional[Dict]:
        """
        Detecta loops de decisão (mesma decisão repetida muitas vezes).
        """

        recent_decisions = behavior_data.get("recent_decisions", [])
        if len(recent_decisions) < self.thresholds["decision_loop_threshold"]:
            return None

        # Verificar se as últimas N decisões são iguais
        last_decisions = recent_decisions[-self.thresholds["decision_loop_threshold"]:]

        if len(set(str(d) for d in last_decisions)) == 1:  # Todas iguais
            return {
                "type": AnomalyType.DECISION_LOOP.value,
                "severity": "medium",
                "timestamp": datetime.now().isoformat(),
                "description": f"Decision loop detected: same decision repeated {len(last_decisions)} times",
                "evidence": {
                    "repeated_decision": last_decisions[0],
                    "occurrences": len(last_decisions)
                }
            }

        return None

    def _detect_response_inconsistency(self, behavior_data: Dict) -> Optional[Dict]:
        """
        Detecta inconsistências nas respostas para inputs similares.
        """

        responses = behavior_data.get("responses", [])
        if len(responses) < 5:
            return None

        # Calcular score de consistência
        consistency_score = self._calculate_response_consistency(responses)

        if consistency_score < self.thresholds["inconsistency_threshold"]:
            return {
                "type": AnomalyType.RESPONSE_INCONSISTENCY.value,
                "severity": "low",
                "timestamp": datetime.now().isoformat(),
                "description": f"Response inconsistency detected: consistency score {consistency_score:.2f}",
                "evidence": {
                    "consistency_score": consistency_score,
                    "responses_analyzed": len(responses)
                }
            }

        return None

    def _detect_security_patterns(self, behavior_data: Dict) -> Optional[Dict]:
        """
        Detecta padrões suspeitos relacionados à segurança.
        """

        actions = behavior_data.get("actions", [])
        suspicious_patterns = [
            "eval", "exec", "__import__", "subprocess", "os.system",
            "file.*delete", "override.*permission", "bypass.*check"
        ]

        suspicious_actions = []
        for action in actions:
            action_str = str(action).lower()
            for pattern in suspicious_patterns:
                if re.search(pattern, action_str):
                    suspicious_actions.append(action)
                    break

        if suspicious_actions:
            severity = "high" if len(suspicious_actions) > 2 else "medium"

            return {
                "type": AnomalyType.SECURITY_PATTERN.value,
                "severity": severity,
                "timestamp": datetime.now().isoformat(),
                "description": f"Security pattern detected: {len(suspicious_actions)} suspicious actions",
                "evidence": {
                    "suspicious_actions": suspicious_actions[:5],  # Limitar para log
                    "patterns_detected": suspicious_patterns
                }
            }

        return None

    def _detect_resource_abuse(self, behavior_data: Dict) -> Optional[Dict]:
        """
        Detecta abuso de recursos (CPU, memória excessivos).
        """

        resource_usage = behavior_data.get("resource_usage", {})
        cpu_usage = resource_usage.get("cpu", 0.0)
        memory_usage = resource_usage.get("memory", 0.0)

        if (cpu_usage > self.thresholds["resource_abuse_threshold"] or
            memory_usage > self.thresholds["resource_abuse_threshold"]):

            return {
                "type": AnomalyType.RESOURCE_ABUSE.value,
                "severity": "medium",
                "timestamp": datetime.now().isoformat(),
                "description": f"Resource abuse detected: CPU {cpu_usage:.1%}, Memory {memory_usage:.1%}",
                "evidence": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "threshold": self.thresholds["resource_abuse_threshold"]
                }
            }

        return None

    def _detect_unusual_frequency(self, behavior_data: Dict) -> Optional[Dict]:
        """
        Detecta frequências incomuns de operações.
        """

        operation_count = behavior_data.get("operation_count", 0)
        time_window = behavior_data.get("time_window_minutes", 5)

        # Calcular frequência por minuto
        frequency = operation_count / max(time_window, 1)

        # Comparar com padrão normal
        normal_freq = self.behavior_patterns["decision_frequency"]["mean"]
        freq_spike = frequency / max(normal_freq, 0.1)

        if freq_spike > self.thresholds["frequency_spike_threshold"]:
            return {
                "type": AnomalyType.UNUSUAL_FREQUENCY.value,
                "severity": "low",
                "timestamp": datetime.now().isoformat(),
                "description": f"Unusual frequency detected: {frequency:.1f} ops/min ({freq_spike:.1f}x normal)",
                "evidence": {
                    "current_frequency": frequency,
                    "normal_frequency": normal_freq,
                    "spike_multiplier": freq_spike
                }
            }

        return None

    def _detect_core_violation_attempts(self, behavior_data: Dict) -> Optional[Dict]:
        """
        Detecta tentativas de violação das regras do core.
        """

        inputs_outputs = behavior_data.get("inputs_outputs", [])
        violation_attempts = []

        for item in inputs_outputs:
            text = str(item).lower()
            for keyword in self.thresholds["core_violation_keywords"]:
                if re.search(keyword, text):
                    violation_attempts.append(item)
                    break

        if violation_attempts:
            return {
                "type": AnomalyType.CORE_VIOLATION_ATTEMPT.value,
                "severity": "critical",
                "timestamp": datetime.now().isoformat(),
                "description": f"Core violation attempt detected: {len(violation_attempts)} attempts",
                "evidence": {
                    "violation_attempts": violation_attempts[:3],  # Limitar para log
                    "keywords_triggered": self.thresholds["core_violation_keywords"]
                }
            }

        return None

    def _detect_pattern_deviation(self, behavior_data: Dict) -> Optional[Dict]:
        """
        Detecta desvios significativos dos padrões comportamentais normais.
        """

        current_metrics = behavior_data.get("current_metrics", {})

        deviations = []
        for metric_name, current_value in current_metrics.items():
            if metric_name in self.behavior_patterns:
                pattern = self.behavior_patterns[metric_name]
                mean = pattern.get("mean", current_value)
                std = pattern.get("std", 0.1)

                if std > 0:
                    deviation = abs(current_value - mean) / std
                    if deviation > self.thresholds["pattern_deviation_threshold"]:
                        deviations.append({
                            "metric": metric_name,
                            "current": current_value,
                            "mean": mean,
                            "deviation_std": deviation
                        })

        if deviations:
            return {
                "type": AnomalyType.PATTERN_DEVIATION.value,
                "severity": "medium",
                "timestamp": datetime.now().isoformat(),
                "description": f"Pattern deviation detected: {len(deviations)} metrics outside normal range",
                "evidence": {
                    "deviations": deviations
                }
            }

        return None

    def _calculate_response_consistency(self, responses: List[Any]) -> float:
        """
        Calcula score de consistência das respostas.
        """

        if len(responses) < 2:
            return 1.0

        # Método simples: comparar similaridade entre respostas consecutivas
        consistency_scores = []

        for i in range(len(responses) - 1):
            resp1 = str(responses[i])
            resp2 = str(responses[i + 1])

            # Calcular similaridade simples (Jaccard similarity de palavras)
            words1 = set(resp1.lower().split())
            words2 = set(resp2.lower().split())

            if words1 or words2:
                similarity = len(words1 & words2) / len(words1 | words2)
                consistency_scores.append(similarity)

        return statistics.mean(consistency_scores) if consistency_scores else 0.0

    def _update_behavior_patterns(self, behavior_data: Dict) -> None:
        """
        Atualiza padrões comportamentais com novos dados.
        """

        # Atualizar padrões de frequência
        if "operation_count" in behavior_data:
            freq_pattern = self.behavior_patterns["decision_frequency"]
            freq_pattern["history"].append(behavior_data["operation_count"])

            # Manter apenas últimas 100 medições
            if len(freq_pattern["history"]) > 100:
                freq_pattern["history"] = freq_pattern["history"][-100:]

            # Recalcular estatísticas
            if freq_pattern["history"]:
                freq_pattern["mean"] = statistics.mean(freq_pattern["history"])
                freq_pattern["std"] = statistics.stdev(freq_pattern["history"]) if len(freq_pattern["history"]) > 1 else 0.0

        # Atualizar outros padrões conforme necessário
        self._save_state()

    def _record_anomaly(self, anomaly: Dict) -> None:
        """Registra anomalia detectada."""

        anomaly_entry = {
            "id": f"anom_{len(self.detected_anomalies)}_{int(datetime.now().timestamp())}",
            **anomaly
        }

        self.detected_anomalies.append(anomaly_entry)
        self._save_state()

    def get_anomalies_history(self, anomaly_type: Optional[AnomalyType] = None,
                             limit: int = 100) -> List[Dict]:
        """Retorna histórico de anomalias detectadas."""

        anomalies = self.detected_anomalies

        if anomaly_type:
            anomalies = [a for a in anomalies if a.get("type") == anomaly_type.value]

        return anomalies[-limit:]

    def get_anomaly_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna resumo de anomalias por período."""

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_anomalies = [
            a for a in self.detected_anomalies
            if datetime.fromisoformat(a["timestamp"]) > cutoff_time
        ]

        summary = {
            "period_hours": hours,
            "total_anomalies": len(recent_anomalies),
            "by_type": {},
            "by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0}
        }

        for anomaly in recent_anomalies:
            # Por tipo
            anom_type = anomaly.get("type", "unknown")
            if anom_type not in summary["by_type"]:
                summary["by_type"][anom_type] = 0
            summary["by_type"][anom_type] += 1

            # Por severidade
            severity = anomaly.get("severity", "low")
            if severity in summary["by_severity"]:
                summary["by_severity"][severity] += 1

        return summary

    def _load_state(self) -> None:
        """Carrega estado do detector de anomalias."""

        if self.anomalies_log.exists():
            try:
                self.detected_anomalies = json.loads(
                    self.anomalies_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.detected_anomalies = []

        if self.behavior_patterns_log.exists():
            try:
                self.behavior_patterns = json.loads(
                    self.behavior_patterns_log.read_text(encoding='utf-8')
                )
            except Exception:
                self._initialize_patterns()

    def _save_state(self) -> None:
        """Persiste estado do detector."""

        self.anomalies_dir.mkdir(parents=True, exist_ok=True)

        self.anomalies_log.write_text(
            json.dumps(self.detected_anomalies[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        self.behavior_patterns_log.write_text(
            json.dumps(self.behavior_patterns, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
