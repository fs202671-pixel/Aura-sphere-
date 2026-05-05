"""
Wolf Forensic - Lobo Forense
============================

Agente de análise forense e coleta de evidências.
Características:
- Coleta de evidências digitais
- Análise de logs e artefatos
- Preservação de cadeia de custódia
- Geração de relatórios forenses
"""

import asyncio
import time
import hashlib
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import shutil

from memory.collective import CollectiveMemory
from core.security import SecurityManager

logger = logging.getLogger(__name__)

class EvidenceType(Enum):
    LOG_FILES = "log_files"
    SYSTEM_STATE = "system_state"
    NETWORK_LOGS = "network_logs"
    PROCESS_INFO = "process_info"
    FILE_SYSTEM = "file_system"
    MEMORY_DUMP = "memory_dump"

class ForensicStatus(Enum):
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    PRESERVING = "preserving"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Evidence:
    """Evidência coletada"""
    evidence_id: str
    evidence_type: EvidenceType
    source: str
    collection_time: float
    data: Any
    hash_value: str
    metadata: Dict[str, Any]
    chain_of_custody: List[Dict[str, Any]]

@dataclass
class ForensicReport:
    """Relatório forense"""
    report_id: str
    incident_id: str
    collected_evidence: List[Evidence]
    analysis_results: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    conclusions: List[str]
    generated_time: float
    forensic_id: str

class WolfForensic:
    """
    Lobo forense - coleta e analisa evidências

    Funcionalidades:
    - Coletar evidências de incidentes
    - Preservar cadeia de custódia
    - Analisar artefatos
    - Gerar relatórios forenses
    """

    def __init__(self, forensic_id: Optional[str] = None):
        self.forensic_id = forensic_id or f"forensic_{int(time.time())}"
        self.memory = CollectiveMemory()
        self.security = SecurityManager()

        # Estado
        self.active = False

        # Evidências coletadas
        self.collected_evidence: Dict[str, Evidence] = {}

        # Estatísticas
        self.incidents_analyzed = 0
        self.evidence_collected = 0
        self.reports_generated = 0

        # Diretório de evidências
        self.evidence_dir = f"/tmp/wolf_forensic_{self.forensic_id}"
        os.makedirs(self.evidence_dir, exist_ok=True)

        logger.info(f"WolfForensic {self.forensic_id} initialized")

    async def start_forensic(self):
        """Inicia análise forense"""
        self.active = True
        logger.info(f"WolfForensic {self.forensic_id} started forensic analysis")

        while self.active:
            try:
                # Verificar incidentes pendentes
                await self._check_pending_incidents()

                # Processar evidências coletadas
                await self._process_collected_evidence()

                # Gerar relatórios
                await self._generate_pending_reports()

                # Aguardar próximo ciclo
                await asyncio.sleep(15)

            except Exception as e:
                logger.error(f"WolfForensic {self.forensic_id} error: {e}")
                await asyncio.sleep(15)

    async def _check_pending_incidents(self):
        """Verifica incidentes pendentes de análise"""
        # Buscar incidentes não analisados
        pending_incidents = await self.memory.get_pending_forensic_incidents()

        for incident in pending_incidents:
            try:
                # Iniciar análise forense
                await self._analyze_incident(incident)

                self.incidents_analyzed += 1

            except Exception as e:
                logger.error(f"Failed to analyze incident {incident.get('id')}: {e}")

    async def _analyze_incident(self, incident: Dict[str, Any]):
        """
        Analisa um incidente

        Args:
            incident: Dados do incidente
        """
        incident_id = incident.get('incident_id', incident.get('id'))

        logger.info(f"WolfForensic {self.forensic_id} analyzing incident {incident_id}")

        # Coletar evidências
        evidence_list = await self._collect_evidence(incident)

        # Analisar evidências
        analysis_results = await self._analyze_evidence(evidence_list)

        # Criar timeline
        timeline = await self._build_timeline(incident, evidence_list)

        # Gerar conclusões
        conclusions = self._generate_conclusions(analysis_results, timeline)

        # Criar relatório
        report = ForensicReport(
            report_id=f"report_{incident_id}_{int(time.time())}",
            incident_id=incident_id,
            collected_evidence=evidence_list,
            analysis_results=analysis_results,
            timeline=timeline,
            conclusions=conclusions,
            generated_time=time.time(),
            forensic_id=self.forensic_id
        )

        # Armazenar relatório
        await self._store_forensic_report(report)

        self.reports_generated += 1

        logger.info(f"WolfForensic {self.forensic_id} completed analysis for incident {incident_id}")

    async def _collect_evidence(self, incident: Dict[str, Any]) -> List[Evidence]:
        """
        Coleta evidências para um incidente

        Args:
            incident: Dados do incidente

        Returns:
            Lista de evidências coletadas
        """
        evidence_list = []
        alert_id = incident.get('alert_id')

        # Coletar logs relacionados
        if alert_id:
            log_evidence = await self._collect_log_evidence(alert_id)
            evidence_list.extend(log_evidence)

        # Coletar estado do sistema
        system_evidence = await self._collect_system_state_evidence()
        evidence_list.extend(system_evidence)

        # Coletar informações de rede
        network_evidence = await self._collect_network_evidence()
        evidence_list.extend(network_evidence)

        # Coletar informações de processos
        process_evidence = await self._collect_process_evidence()
        evidence_list.extend(process_evidence)

        return evidence_list

    async def _collect_log_evidence(self, alert_id: str) -> List[Evidence]:
        """Coleta evidências de logs"""
        evidence_list = []

        try:
            # Buscar logs relacionados ao alerta
            related_logs = await self.memory.get_logs_for_alert(alert_id, hours=24)

            if related_logs:
                evidence = Evidence(
                    evidence_id=f"logs_{alert_id}_{int(time.time())}",
                    evidence_type=EvidenceType.LOG_FILES,
                    source=f"alert_{alert_id}",
                    collection_time=time.time(),
                    data=related_logs,
                    hash_value=self._calculate_hash(related_logs),
                    metadata={
                        'alert_id': alert_id,
                        'log_count': len(related_logs),
                        'time_range': '24 hours'
                    },
                    chain_of_custody=[{
                        'action': 'collected',
                        'timestamp': time.time(),
                        'collector': self.forensic_id
                    }]
                )

                evidence_list.append(evidence)
                self.evidence_collected += 1

        except Exception as e:
            logger.error(f"Failed to collect log evidence for {alert_id}: {e}")

        return evidence_list

    async def _collect_system_state_evidence(self) -> List[Evidence]:
        """Coleta evidências do estado do sistema"""
        evidence_list = []

        try:
            import psutil

            # Coletar informações do sistema
            system_info = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': dict(psutil.virtual_memory()._asdict()),
                'disk': dict(psutil.disk_usage('/')._asdict()),
                'network': dict(psutil.net_io_counters()._asdict()),
                'boot_time': psutil.boot_time(),
                'users': [dict(u._asdict()) for u in psutil.users()]
            }

            evidence = Evidence(
                evidence_id=f"system_state_{int(time.time())}",
                evidence_type=EvidenceType.SYSTEM_STATE,
                source="system_monitor",
                collection_time=time.time(),
                data=system_info,
                hash_value=self._calculate_hash(system_info),
                metadata={'collection_method': 'psutil'},
                chain_of_custody=[{
                    'action': 'collected',
                    'timestamp': time.time(),
                    'collector': self.forensic_id
                }]
            )

            evidence_list.append(evidence)
            self.evidence_collected += 1

        except Exception as e:
            logger.error(f"Failed to collect system state evidence: {e}")

        return evidence_list

    async def _collect_network_evidence(self) -> List[Evidence]:
        """Coleta evidências de rede"""
        evidence_list = []

        try:
            import psutil

            # Coletar conexões de rede
            connections = []
            for conn in psutil.net_connections():
                conn_dict = {
                    'fd': conn.fd,
                    'family': conn.family,
                    'type': conn.type,
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid
                }
                connections.append(conn_dict)

            if connections:
                evidence = Evidence(
                    evidence_id=f"network_{int(time.time())}",
                    evidence_type=EvidenceType.NETWORK_LOGS,
                    source="network_monitor",
                    collection_time=time.time(),
                    data=connections,
                    hash_value=self._calculate_hash(connections),
                    metadata={'connection_count': len(connections)},
                    chain_of_custody=[{
                        'action': 'collected',
                        'timestamp': time.time(),
                        'collector': self.forensic_id
                    }]
                )

                evidence_list.append(evidence)
                self.evidence_collected += 1

        except Exception as e:
            logger.error(f"Failed to collect network evidence: {e}")

        return evidence_list

    async def _collect_process_evidence(self) -> List[Evidence]:
        """Coleta evidências de processos"""
        evidence_list = []

        try:
            import psutil

            # Coletar informações de processos
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    proc_dict = dict(proc.info)
                    proc_dict['create_time'] = time.ctime(proc_dict['create_time']) if proc_dict['create_time'] else None
                    processes.append(proc_dict)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if processes:
                evidence = Evidence(
                    evidence_id=f"processes_{int(time.time())}",
                    evidence_type=EvidenceType.PROCESS_INFO,
                    source="process_monitor",
                    collection_time=time.time(),
                    data=processes,
                    hash_value=self._calculate_hash(processes),
                    metadata={'process_count': len(processes)},
                    chain_of_custody=[{
                        'action': 'collected',
                        'timestamp': time.time(),
                        'collector': self.forensic_id
                    }]
                )

                evidence_list.append(evidence)
                self.evidence_collected += 1

        except Exception as e:
            logger.error(f"Failed to collect process evidence: {e}")

        return evidence_list

    def _calculate_hash(self, data: Any) -> str:
        """Calcula hash dos dados"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    async def _analyze_evidence(self, evidence_list: List[Evidence]) -> Dict[str, Any]:
        """
        Analisa evidências coletadas

        Args:
            evidence_list: Lista de evidências

        Returns:
            Resultados da análise
        """
        analysis = {
            'evidence_count': len(evidence_list),
            'evidence_types': {},
            'temporal_analysis': {},
            'correlation_findings': [],
            'anomalies': []
        }

        # Contar tipos de evidência
        for evidence in evidence_list:
            ev_type = evidence.evidence_type.value
            analysis['evidence_types'][ev_type] = analysis['evidence_types'].get(ev_type, 0) + 1

        # Análise temporal
        if evidence_list:
            timestamps = [e.collection_time for e in evidence_list]
            analysis['temporal_analysis'] = {
                'earliest': min(timestamps),
                'latest': max(timestamps),
                'span_seconds': max(timestamps) - min(timestamps)
            }

        # Procurar anomalias
        analysis['anomalies'] = await self._find_anomalies_in_evidence(evidence_list)

        return analysis

    async def _find_anomalies_in_evidence(self, evidence_list: List[Evidence]) -> List[Dict[str, Any]]:
        """Procura anomalias nas evidências"""
        anomalies = []

        for evidence in evidence_list:
            if evidence.evidence_type == EvidenceType.LOG_FILES:
                log_anomalies = self._analyze_log_anomalies(evidence.data)
                anomalies.extend(log_anomalies)

            elif evidence.evidence_type == EvidenceType.PROCESS_INFO:
                process_anomalies = self._analyze_process_anomalies(evidence.data)
                anomalies.extend(process_anomalies)

            elif evidence.evidence_type == EvidenceType.NETWORK_LOGS:
                network_anomalies = self._analyze_network_anomalies(evidence.data)
                anomalies.extend(network_anomalies)

        return anomalies

    def _analyze_log_anomalies(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analisa anomalias em logs"""
        anomalies = []

        error_count = sum(1 for log in logs if 'error' in log.get('level', '').lower())
        if error_count > 10:
            anomalies.append({
                'type': 'high_error_rate',
                'description': f'High error count: {error_count}',
                'severity': 'high'
            })

        return anomalies

    def _analyze_process_anomalies(self, processes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analisa anomalias em processos"""
        anomalies = []

        high_cpu_processes = [p for p in processes if p.get('cpu_percent', 0) > 80]
        if high_cpu_processes:
            anomalies.append({
                'type': 'high_cpu_processes',
                'description': f'Processes with high CPU: {len(high_cpu_processes)}',
                'severity': 'medium'
            })

        return anomalies

    def _analyze_network_anomalies(self, connections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analisa anomalias em conexões de rede"""
        anomalies = []

        suspicious_ports = [22, 23, 3389, 5900]  # SSH, Telnet, RDP, VNC
        suspicious_connections = [
            conn for conn in connections
            if conn.get('local_addr') and any(port in conn['local_addr'] for port in suspicious_ports)
        ]

        if suspicious_connections:
            anomalies.append({
                'type': 'suspicious_ports',
                'description': f'Suspicious port connections: {len(suspicious_connections)}',
                'severity': 'high'
            })

        return anomalies

    async def _build_timeline(self, incident: Dict[str, Any], evidence_list: List[Evidence]) -> List[Dict[str, Any]]:
        """
        Constrói timeline do incidente

        Args:
            incident: Dados do incidente
            evidence_list: Evidências coletadas

        Returns:
            Timeline ordenada
        """
        timeline_events = []

        # Adicionar evento do incidente
        timeline_events.append({
            'timestamp': incident.get('timestamp', time.time()),
            'event_type': 'incident_detected',
            'description': f'Incident {incident.get("incident_id")} detected',
            'source': 'incident_log'
        })

        # Adicionar eventos das evidências
        for evidence in evidence_list:
            timeline_events.append({
                'timestamp': evidence.collection_time,
                'event_type': 'evidence_collected',
                'description': f'Evidence {evidence.evidence_id} collected',
                'source': evidence.source,
                'evidence_type': evidence.evidence_type.value
            })

        # Ordenar por timestamp
        timeline_events.sort(key=lambda x: x['timestamp'])

        return timeline_events

    def _generate_conclusions(self, analysis: Dict[str, Any], timeline: List[Dict[str, Any]]) -> List[str]:
        """Gera conclusões da análise"""
        conclusions = []

        # Conclusões baseadas na análise
        evidence_count = analysis.get('evidence_count', 0)
        conclusions.append(f"Collected {evidence_count} pieces of evidence")

        anomalies = analysis.get('anomalies', [])
        if anomalies:
            conclusions.append(f"Found {len(anomalies)} anomalies during analysis")
            high_severity = [a for a in anomalies if a.get('severity') == 'high']
            if high_severity:
                conclusions.append(f"Critical anomalies detected: {len(high_severity)}")

        # Conclusões baseadas no timeline
        if timeline:
            span = timeline[-1]['timestamp'] - timeline[0]['timestamp']
            conclusions.append(f"Incident timeline spans {span:.2f} seconds")

        return conclusions

    async def _store_forensic_report(self, report: ForensicReport):
        """
        Armazena relatório forense

        Args:
            report: Relatório a armazenar
        """
        report_data = {
            'report_id': report.report_id,
            'incident_id': report.incident_id,
            'collected_evidence': [
                {
                    'evidence_id': e.evidence_id,
                    'type': e.evidence_type.value,
                    'source': e.source,
                    'collection_time': e.collection_time,
                    'hash_value': e.hash_value,
                    'metadata': e.metadata
                } for e in report.collected_evidence
            ],
            'analysis_results': report.analysis_results,
            'timeline': report.timeline,
            'conclusions': report.conclusions,
            'generated_time': report.generated_time,
            'forensic_id': report.forensic_id
        }

        await self.memory.store_forensic_report(report_data)

    async def _process_collected_evidence(self):
        """Processa evidências coletadas"""
        # TODO: Implementar processamento adicional
        pass

    async def _generate_pending_reports(self):
        """Gera relatórios pendentes"""
        # TODO: Implementar geração de relatórios adicionais
        pass

    async def get_forensic_status(self) -> Dict[str, Any]:
        """Retorna status do forense"""
        return {
            'forensic_id': self.forensic_id,
            'active': self.active,
            'incidents_analyzed': self.incidents_analyzed,
            'evidence_collected': self.evidence_collected,
            'reports_generated': self.reports_generated,
            'collected_evidence_count': len(self.collected_evidence)
        }

    def stop_forensic(self):
        """Para a análise forense"""
        self.active = False

        # Limpar diretório de evidências
        try:
            shutil.rmtree(self.evidence_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup evidence directory: {e}")

        logger.info(f"WolfForensic {self.forensic_id} stopped forensic analysis")