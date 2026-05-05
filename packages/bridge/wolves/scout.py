"""
Wolf Scout - Lobo Batedor
========================

Agente de monitoramento e detecção precoce.
Características:
- Monitoramento contínuo de logs e sinais
- Detecção de anomalias comportamentais
- Coleta de métricas de sistema
- Alerta precoce de ameaças
"""

import asyncio
import time
import psutil
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import json

from memory.collective import CollectiveMemory
from core.security import SecurityManager

logger = logging.getLogger(__name__)

class SignalType(Enum):
    SYSTEM_METRICS = "system_metrics"
    LOG_ANALYSIS = "log_analysis"
    BEHAVIOR_ANALYSIS = "behavior_analysis"
    NETWORK_ACTIVITY = "network_activity"
    RESOURCE_USAGE = "resource_usage"

@dataclass
class SystemSignal:
    """Sinal do sistema detectado"""
    signal_id: str
    signal_type: SignalType
    severity: str
    description: str
    data: Dict[str, Any]
    timestamp: float
    source: str

@dataclass
class AnomalyPattern:
    """Padrão de anomalia"""
    pattern_id: str
    name: str
    description: str
    threshold: float
    detection_logic: Callable
    enabled: bool = True

class WolfScout:
    """
    Lobo batedor - monitora e detecta anomalias

    Funcionalidades:
    - Monitorar métricas do sistema
    - Analisar logs em tempo real
    - Detectar comportamentos suspeitos
    - Coletar sinais de alerta
    """

    def __init__(self, scout_id: Optional[str] = None):
        self.scout_id = scout_id or f"scout_{int(time.time())}"
        self.memory = CollectiveMemory()
        self.security = SecurityManager()

        # Estado do monitoramento
        self.active = False
        self.monitoring_interval = 5  # segundos

        # Padrões de anomalia
        self.anomaly_patterns: Dict[str, AnomalyPattern] = {}
        self.baseline_metrics: Dict[str, float] = {}

        # Estatísticas
        self.signals_detected = 0
        self.anomalies_found = 0

        # Callbacks para alertas
        self.alert_callbacks: List[Callable] = []

        # Inicializar padrões de anomalia
        self._initialize_anomaly_patterns()

        logger.info(f"WolfScout {self.scout_id} initialized")

    def _initialize_anomaly_patterns(self):
        """Inicializa padrões de detecção de anomalia"""
        self.anomaly_patterns = {
            "high_cpu_usage": AnomalyPattern(
                pattern_id="high_cpu_usage",
                name="High CPU Usage",
                description="CPU usage above threshold",
                threshold=80.0,
                detection_logic=self._detect_high_cpu
            ),
            "memory_leak": AnomalyPattern(
                pattern_id="memory_leak",
                name="Memory Leak Detection",
                description="Memory usage increasing over time",
                threshold=10.0,  # % increase per minute
                detection_logic=self._detect_memory_leak
            ),
            "unusual_network": AnomalyPattern(
                pattern_id="unusual_network",
                name="Unusual Network Activity",
                description="Network connections above normal",
                threshold=50,  # connections
                detection_logic=self._detect_unusual_network
            ),
            "suspicious_processes": AnomalyPattern(
                pattern_id="suspicious_processes",
                name="Suspicious Processes",
                description="Processes with suspicious names or behavior",
                threshold=0.0,
                detection_logic=self._detect_suspicious_processes
            ),
            "log_anomalies": AnomalyPattern(
                pattern_id="log_anomalies",
                name="Log Anomalies",
                description="Unusual patterns in log files",
                threshold=5,  # unusual entries per minute
                detection_logic=self._detect_log_anomalies
            )
        }

    async def start_scouting(self):
        """Inicia o monitoramento"""
        self.active = True
        logger.info(f"WolfScout {self.scout_id} started scouting")

        # Estabelecer baseline inicial
        await self._establish_baseline()

        while self.active:
            try:
                # Coletar sinais do sistema
                signals = await self._collect_system_signals()

                # Analisar sinais
                anomalies = await self._analyze_signals(signals)

                # Reportar anomalias
                for anomaly in anomalies:
                    await self._report_anomaly(anomaly)

                # Aguardar próximo ciclo
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"WolfScout {self.scout_id} error: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _establish_baseline(self):
        """Estabelece baseline das métricas normais"""
        logger.info(f"WolfScout {self.scout_id} establishing baseline...")

        # Coletar métricas por alguns minutos
        baseline_samples = []
        for _ in range(12):  # 1 minuto de amostragem
            metrics = self._collect_current_metrics()
            baseline_samples.append(metrics)
            await asyncio.sleep(5)

        # Calcular médias
        if baseline_samples:
            self.baseline_metrics = {}
            for key in baseline_samples[0].keys():
                values = [sample.get(key, 0) for sample in baseline_samples]
                self.baseline_metrics[key] = sum(values) / len(values)

        logger.info(f"WolfScout {self.scout_id} baseline established: {self.baseline_metrics}")

    def _collect_current_metrics(self) -> Dict[str, float]:
        """Coleta métricas atuais do sistema"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections()),
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {}

    async def _collect_system_signals(self) -> List[SystemSignal]:
        """
        Coleta sinais do sistema

        Returns:
            Lista de sinais coletados
        """
        signals = []

        # Métricas do sistema
        metrics = self._collect_current_metrics()
        if metrics:
            signals.append(SystemSignal(
                signal_id=f"metrics_{int(time.time())}",
                signal_type=SignalType.SYSTEM_METRICS,
                severity="info",
                description="System metrics collected",
                data=metrics,
                timestamp=time.time(),
                source="system_monitor"
            ))

        # Análise de logs
        log_signals = await self._analyze_recent_logs()
        signals.extend(log_signals)

        # Atividade de rede
        network_signals = await self._monitor_network_activity()
        signals.extend(network_signals)

        # Análise comportamental
        behavior_signals = await self._analyze_behavior()
        signals.extend(behavior_signals)

        return signals

    async def _analyze_recent_logs(self) -> List[SystemSignal]:
        """Analisa logs recentes"""
        signals = []

        try:
            # Buscar entradas de log recentes da memória coletiva
            recent_logs = await self.memory.get_recent_logs(limit=100)

            # Analisar padrões
            error_count = sum(1 for log in recent_logs if 'error' in log.get('level', '').lower())
            warning_count = sum(1 for log in recent_logs if 'warning' in log.get('level', '').lower())

            if error_count > 10:  # threshold
                signals.append(SystemSignal(
                    signal_id=f"log_errors_{int(time.time())}",
                    signal_type=SignalType.LOG_ANALYSIS,
                    severity="high",
                    description=f"High error count in logs: {error_count}",
                    data={'error_count': error_count, 'logs': recent_logs[:5]},
                    timestamp=time.time(),
                    source="log_analyzer"
                ))

            if warning_count > 20:  # threshold
                signals.append(SystemSignal(
                    signal_id=f"log_warnings_{int(time.time())}",
                    signal_type=SignalType.LOG_ANALYSIS,
                    severity="medium",
                    description=f"High warning count in logs: {warning_count}",
                    data={'warning_count': warning_count, 'logs': recent_logs[:5]},
                    timestamp=time.time(),
                    source="log_analyzer"
                ))

        except Exception as e:
            logger.error(f"Failed to analyze logs: {e}")

        return signals

    async def _monitor_network_activity(self) -> List[SystemSignal]:
        """Monitora atividade de rede"""
        signals = []

        try:
            connections = psutil.net_connections()
            connection_count = len(connections)

            # Verificar conexões suspeitas
            suspicious_ports = [22, 23, 3389, 5900]  # SSH, Telnet, RDP, VNC
            suspicious_connections = [
                conn for conn in connections
                if conn.laddr and conn.laddr.port in suspicious_ports
            ]

            if suspicious_connections:
                signals.append(SystemSignal(
                    signal_id=f"suspicious_ports_{int(time.time())}",
                    signal_type=SignalType.NETWORK_ACTIVITY,
                    severity="high",
                    description=f"Suspicious network connections detected: {len(suspicious_connections)}",
                    data={
                        'connections': [
                            {
                                'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}",
                                'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                                'status': conn.status
                            } for conn in suspicious_connections[:5]
                        ]
                    },
                    timestamp=time.time(),
                    source="network_monitor"
                ))

        except Exception as e:
            logger.error(f"Failed to monitor network: {e}")

        return signals

    async def _analyze_behavior(self) -> List[SystemSignal]:
        """Analisa comportamento do sistema"""
        signals = []

        try:
            # Verificar processos com alto consumo
            high_cpu_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['cpu_percent'] > 50:  # threshold
                        high_cpu_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if high_cpu_processes:
                signals.append(SystemSignal(
                    signal_id=f"high_cpu_processes_{int(time.time())}",
                    signal_type=SignalType.BEHAVIOR_ANALYSIS,
                    severity="medium",
                    description=f"Processes with high CPU usage: {len(high_cpu_processes)}",
                    data={'processes': high_cpu_processes[:10]},
                    timestamp=time.time(),
                    source="behavior_analyzer"
                ))

        except Exception as e:
            logger.error(f"Failed to analyze behavior: {e}")

        return signals

    async def _analyze_signals(self, signals: List[SystemSignal]) -> List[SystemSignal]:
        """
        Analisa sinais para detectar anomalias

        Args:
            signals: Sinais coletados

        Returns:
            Lista de anomalias detectadas
        """
        anomalies = []

        for signal in signals:
            # Aplicar padrões de anomalia
            for pattern in self.anomaly_patterns.values():
                if not pattern.enabled:
                    continue

                try:
                    is_anomaly = await pattern.detection_logic(signal, pattern.threshold)
                    if is_anomaly:
                        # Criar sinal de anomalia
                        anomaly_signal = SystemSignal(
                            signal_id=f"anomaly_{pattern.pattern_id}_{int(time.time())}",
                            signal_type=signal.signal_type,
                            severity="high",
                            description=f"Anomaly detected: {pattern.name} - {pattern.description}",
                            data={
                                'pattern': pattern.pattern_id,
                                'original_signal': signal.signal_id,
                                'threshold': pattern.threshold,
                                'signal_data': signal.data
                            },
                            timestamp=time.time(),
                            source=f"anomaly_detector_{pattern.pattern_id}"
                        )
                        anomalies.append(anomaly_signal)

                except Exception as e:
                    logger.error(f"Failed to apply pattern {pattern.pattern_id}: {e}")

        return anomalies

    async def _detect_high_cpu(self, signal: SystemSignal, threshold: float) -> bool:
        """Detecta uso alto de CPU"""
        if signal.signal_type != SignalType.SYSTEM_METRICS:
            return False

        cpu_percent = signal.data.get('cpu_percent', 0)
        return cpu_percent > threshold

    async def _detect_memory_leak(self, signal: SystemSignal, threshold: float) -> bool:
        """Detecta vazamento de memória"""
        if signal.signal_type != SignalType.SYSTEM_METRICS:
            return False

        current_memory = signal.data.get('memory_percent', 0)
        baseline_memory = self.baseline_metrics.get('memory_percent', 50)

        # Verificar se memória aumentou significativamente
        increase = current_memory - baseline_memory
        return increase > threshold

    async def _detect_unusual_network(self, signal: SystemSignal, threshold: float) -> bool:
        """Detecta atividade de rede incomum"""
        if signal.signal_type != SignalType.SYSTEM_METRICS:
            return False

        connections = signal.data.get('network_connections', 0)
        baseline_connections = self.baseline_metrics.get('network_connections', 10)

        return connections > baseline_connections + threshold

    async def _detect_suspicious_processes(self, signal: SystemSignal, threshold: float) -> bool:
        """Detecta processos suspeitos"""
        # TODO: Implementar detecção de processos suspeitos
        return False

    async def _detect_log_anomalies(self, signal: SystemSignal, threshold: float) -> bool:
        """Detecta anomalias em logs"""
        if signal.signal_type != SignalType.LOG_ANALYSIS:
            return False

        # Verificar contadores altos
        error_count = signal.data.get('error_count', 0)
        warning_count = signal.data.get('warning_count', 0)

        return error_count > threshold or warning_count > threshold * 2

    async def _report_anomaly(self, anomaly: SystemSignal):
        """
        Reporta anomalia detectada

        Args:
            anomaly: Anomalia a reportar
        """
        self.anomalies_found += 1

        logger.warning(f"WolfScout {self.scout_id} detected anomaly: {anomaly.description}")

        # Armazenar na memória coletiva
        anomaly_data = {
            'signal_id': anomaly.signal_id,
            'type': anomaly.signal_type.value,
            'severity': anomaly.severity,
            'description': anomaly.description,
            'data': anomaly.data,
            'timestamp': anomaly.timestamp,
            'source': anomaly.source,
            'scout_id': self.scout_id
        }

        await self.memory.store_anomaly(anomaly_data)

        # Disparar callbacks de alerta
        for callback in self.alert_callbacks:
            try:
                await callback(anomaly)
            except Exception as e:
                logger.error(f"Failed to execute alert callback: {e}")

    def add_alert_callback(self, callback: Callable):
        """
        Adiciona callback para alertas

        Args:
            callback: Função a ser chamada quando anomalia é detectada
        """
        self.alert_callbacks.append(callback)

    def enable_pattern(self, pattern_id: str):
        """Habilita padrão de detecção"""
        if pattern_id in self.anomaly_patterns:
            self.anomaly_patterns[pattern_id].enabled = True

    def disable_pattern(self, pattern_id: str):
        """Desabilita padrão de detecção"""
        if pattern_id in self.anomaly_patterns:
            self.anomaly_patterns[pattern_id].enabled = False

    async def get_scout_status(self) -> Dict[str, Any]:
        """Retorna status do scout"""
        return {
            'scout_id': self.scout_id,
            'active': self.active,
            'signals_detected': self.signals_detected,
            'anomalies_found': self.anomalies_found,
            'baseline_metrics': self.baseline_metrics,
            'enabled_patterns': [
                pid for pid, pattern in self.anomaly_patterns.items() if pattern.enabled
            ]
        }

    def stop_scouting(self):
        """Para o monitoramento"""
        self.active = False
        logger.info(f"WolfScout {self.scout_id} stopped scouting")