#!/usr/bin/env python3
"""
Sistema Avançado de Detecção de Anomalias Comportamentais
========================================================

Sistema inteligente para detectar anomalias no comportamento da IA,
incluindo loops de decisão, respostas inconsistentes e tentativas de violação.
"""

import asyncio
import logging
import json
import statistics
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Tipos de anomalias detectáveis."""
    DECISION_LOOP = "decision_loop"
    INCONSISTENT_RESPONSE = "inconsistent_response"
    RULE_VIOLATION_ATTEMPT = "rule_violation_attempt"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    UNUSUAL_ACTIVITY_PATTERN = "unusual_activity_pattern"
    MEMORY_CORRUPTION = "memory_corruption"
    SANDBOX_ESCAPE_ATTEMPT = "sandbox_escape_attempt"

class AnomalySeverity(Enum):
    """Severidade das anomalias."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BehavioralAnomalyDetector:
    """Detector avançado de anomalias comportamentais da IA."""

    def __init__(self, data_dir: Path, config: Optional[Dict[str, Any]] = None):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        # Configurações padrão
        self.config = config or {
            'decision_loop_threshold': 3,  # loops consecutivos
            'inconsistency_threshold': 0.7,  # score mínimo de inconsistência
            'performance_window': 10,  # janela de análise de performance
            'memory_check_interval': 60,  # segundos
            'pattern_analysis_window': 100,  # número de ações para análise
        }

        # Estado interno
        self.decision_history = deque(maxlen=50)
        self.response_history = deque(maxlen=20)
        self.performance_history = deque(maxlen=self.config['performance_window'])
        self.activity_patterns = defaultdict(list)
        self.last_memory_check = time.time()

        # Anomalias detectadas
        self.detected_anomalies = []
        self.active_alerts = set()

        # Carregar estado persistente
        self._load_state()

    def _load_state(self):
        """Carrega estado persistente do detector."""
        state_file = self.data_dir / "anomaly_detector_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.detected_anomalies = state.get('detected_anomalies', [])
                    self.active_alerts = set(state.get('active_alerts', []))
            except Exception as e:
                logger.error(f"Erro ao carregar estado do detector: {e}")

    def _save_state(self):
        """Salva estado persistente do detector."""
        state_file = self.data_dir / "anomaly_detector_state.json"
        try:
            state = {
                'detected_anomalies': self.detected_anomalies[-100:],  # Últimas 100
                'active_alerts': list(self.active_alerts),
                'timestamp': datetime.now().isoformat()
            }
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar estado do detector: {e}")

    async def analyze_decision(self, decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa uma decisão tomada pela IA para detectar anomalias."""
        anomalies = []

        # Adicionar à história
        self.decision_history.append({
            'decision': decision,
            'timestamp': datetime.now().isoformat(),
            'hash': hash(json.dumps(decision, sort_keys=True))
        })

        # Detectar loops de decisão
        loop_anomalies = self._detect_decision_loops()
        anomalies.extend(loop_anomalies)

        # Detectar tentativas de violação de regras
        violation_anomalies = self._detect_rule_violations(decision)
        anomalies.extend(violation_anomalies)

        # Analisar padrões de atividade
        pattern_anomalies = self._analyze_activity_patterns(decision)
        anomalies.extend(pattern_anomalies)

        # Salvar anomalias detectadas
        for anomaly in anomalies:
            self.detected_anomalies.append({
                'anomaly': anomaly,
                'timestamp': datetime.now().isoformat(),
                'context': {'decision': decision}
            })

        self._save_state()
        return anomalies

    async def analyze_response(self, response: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa uma resposta da IA para detectar anomalias."""
        anomalies = []

        # Adicionar à história
        self.response_history.append({
            'response': response,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'length': len(response),
            'hash': hash(response)
        })

        # Detectar inconsistências
        inconsistency_anomalies = self._detect_response_inconsistencies()
        anomalies.extend(inconsistency_anomalies)

        # Analisar qualidade da resposta
        quality_anomalies = self._analyze_response_quality(response, context)
        anomalies.extend(quality_anomalies)

        # Salvar anomalias detectadas
        for anomaly in anomalies:
            self.detected_anomalies.append({
                'anomaly': anomaly,
                'timestamp': datetime.now().isoformat(),
                'context': {'response': response[:100], 'context': context}
            })

        self._save_state()
        return anomalies

    async def analyze_performance(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa métricas de performance para detectar degradação."""
        anomalies = []

        # Adicionar à história
        self.performance_history.append({
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })

        # Detectar degradação de performance
        degradation_anomalies = self._detect_performance_degradation()
        anomalies.extend(degradation_anomalies)

        # Verificar saúde da memória periodicamente
        if time.time() - self.last_memory_check > self.config['memory_check_interval']:
            memory_anomalies = await self._check_memory_health()
            anomalies.extend(memory_anomalies)
            self.last_memory_check = time.time()

        # Salvar anomalias detectadas
        for anomaly in anomalies:
            self.detected_anomalies.append({
                'anomaly': anomaly,
                'timestamp': datetime.now().isoformat(),
                'context': {'metrics': metrics}
            })

        self._save_state()
        return anomalies

    def _detect_decision_loops(self) -> List[Dict[str, Any]]:
        """Detecta loops de decisão consecutivos."""
        anomalies = []

        if len(self.decision_history) < self.config['decision_loop_threshold']:
            return anomalies

        # Verificar loops baseados em hash das decisões
        recent_hashes = [d['hash'] for d in list(self.decision_history)[-self.config['decision_loop_threshold']:]]
        unique_hashes = set(recent_hashes)

        if len(unique_hashes) == 1 and len(recent_hashes) >= self.config['decision_loop_threshold']:
            # Loop detectado
            anomalies.append({
                'type': AnomalyType.DECISION_LOOP.value,
                'severity': AnomalySeverity.HIGH.value,
                'description': f"Loop de decisão detectado: {self.config['decision_loop_threshold']} decisões idênticas consecutivas",
                'evidence': {
                    'loop_length': len(recent_hashes),
                    'decision_hash': recent_hashes[0]
                },
                'recommended_action': 'Interromper execução e solicitar intervenção do usuário'
            })

        return anomalies

    def _detect_rule_violations(self, decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta tentativas de violação de regras do core."""
        anomalies = []

        # Regras críticas que não podem ser violadas
        critical_rules = [
            'core_modification',
            'direct_system_access',
            'user_obedience_bypass',
            'sandbox_escape'
        ]

        decision_type = decision.get('type', '')
        if decision_type in critical_rules:
            anomalies.append({
                'type': AnomalyType.RULE_VIOLATION_ATTEMPT.value,
                'severity': AnomalySeverity.CRITICAL.value,
                'description': f"Tentativa de violação de regra crítica: {decision_type}",
                'evidence': {'decision': decision},
                'recommended_action': 'Bloquear execução e isolar IA'
            })

        # Verificar comandos perigosos
        dangerous_commands = [
            'rm -rf /',
            'sudo',
            'chmod 777',
            'dd if=/dev/zero',
            'mkfs',
            'fdisk'
        ]

        command = decision.get('command', '')
        for dangerous_cmd in dangerous_commands:
            if dangerous_cmd in command:
                anomalies.append({
                    'type': AnomalyType.SANDBOX_ESCAPE_ATTEMPT.value,
                    'severity': AnomalySeverity.CRITICAL.value,
                    'description': f"Comando perigoso detectado: {dangerous_cmd}",
                    'evidence': {'command': command},
                    'recommended_action': 'Bloquear execução e alertar usuário'
                })

        return anomalies

    def _detect_response_inconsistencies(self) -> List[Dict[str, Any]]:
        """Detecta inconsistências nas respostas."""
        anomalies = []

        if len(self.response_history) < 3:
            return anomalies

        # Calcular scores de similaridade entre respostas recentes
        recent_responses = list(self.response_history)[-5:]
        similarities = []

        for i in range(len(recent_responses) - 1):
            resp1 = recent_responses[i]['response']
            resp2 = recent_responses[i + 1]['response']

            # Similaridade simples baseada em palavras em comum
            words1 = set(resp1.lower().split())
            words2 = set(resp2.lower().split())
            similarity = len(words1.intersection(words2)) / len(words1.union(words2)) if words1.union(words2) else 0
            similarities.append(similarity)

        if similarities:
            avg_similarity = statistics.mean(similarities)
            if avg_similarity > self.config['inconsistency_threshold']:
                anomalies.append({
                    'type': AnomalyType.INCONSISTENT_RESPONSE.value,
                    'severity': AnomalySeverity.MEDIUM.value,
                    'description': f"Respostas muito similares detectadas (similaridade: {avg_similarity:.2f})",
                    'evidence': {
                        'average_similarity': avg_similarity,
                        'sample_count': len(similarities)
                    },
                    'recommended_action': 'Revisar lógica de geração de respostas'
                })

        return anomalies

    def _detect_performance_degradation(self) -> List[Dict[str, Any]]:
        """Detecta degradação de performance."""
        anomalies = []

        if len(self.performance_history) < 3:
            return anomalies

        # Analisar tendência de métricas críticas
        response_times = [p['metrics'].get('response_time', 0) for p in self.performance_history]
        error_rates = [p['metrics'].get('error_rate', 0) for p in self.performance_history]

        if len(response_times) >= 3:
            # Calcular tendência do tempo de resposta
            recent_avg = statistics.mean(response_times[-3:])
            overall_avg = statistics.mean(response_times)

            if recent_avg > overall_avg * 1.5:  # 50% mais lento
                anomalies.append({
                    'type': AnomalyType.PERFORMANCE_DEGRADATION.value,
                    'severity': AnomalySeverity.MEDIUM.value,
                    'description': f"Degradação de performance detectada (tempo de resposta: {recent_avg:.2f}s vs {overall_avg:.2f}s)",
                    'evidence': {
                        'recent_average': recent_avg,
                        'overall_average': overall_avg,
                        'degradation_ratio': recent_avg / overall_avg
                    },
                    'recommended_action': 'Monitorar recursos do sistema e considerar otimização'
                })

        return anomalies

    def _analyze_activity_patterns(self, decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa padrões de atividade incomuns."""
        anomalies = []

        decision_type = decision.get('type', 'unknown')
        self.activity_patterns[decision_type].append(datetime.now().isoformat())

        # Verificar padrões incomuns
        for activity_type, timestamps in self.activity_patterns.items():
            if len(timestamps) >= 10:
                # Calcular frequência
                recent_timestamps = timestamps[-10:]
                time_diffs = []

                for i in range(1, len(recent_timestamps)):
                    t1 = datetime.fromisoformat(recent_timestamps[i-1])
                    t2 = datetime.fromisoformat(recent_timestamps[i])
                    time_diffs.append((t2 - t1).total_seconds())

                if time_diffs:
                    avg_interval = statistics.mean(time_diffs)
                    if avg_interval < 1.0:  # Menos de 1 segundo entre ações
                        anomalies.append({
                            'type': AnomalyType.UNUSUAL_ACTIVITY_PATTERN.value,
                            'severity': AnomalySeverity.MEDIUM.value,
                            'description': f"Padrão de atividade incomum: {activity_type} executado muito frequentemente",
                            'evidence': {
                                'activity_type': activity_type,
                                'average_interval': avg_interval,
                                'frequency': 1.0 / avg_interval
                            },
                            'recommended_action': 'Investigar possível comportamento automatizado excessivo'
                        })

        return anomalies

    def _analyze_response_quality(self, response: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa qualidade da resposta para detectar anomalias."""
        anomalies = []

        # Verificar respostas muito curtas/longas
        if len(response) < 10:
            anomalies.append({
                'type': AnomalyType.INCONSISTENT_RESPONSE.value,
                'severity': AnomalySeverity.LOW.value,
                'description': "Resposta anormalmente curta",
                'evidence': {'response_length': len(response)},
                'recommended_action': 'Verificar se resposta foi truncada ou incompleta'
            })

        if len(response) > 5000:
            anomalies.append({
                'type': AnomalyType.INCONSISTENT_RESPONSE.value,
                'severity': AnomalySeverity.LOW.value,
                'description': "Resposta anormalmente longa",
                'evidence': {'response_length': len(response)},
                'recommended_action': 'Verificar se resposta contém conteúdo duplicado ou irrelevante'
            })

        # Verificar respostas repetitivas
        words = response.lower().split()
        if len(words) > 10:
            word_counts = defaultdict(int)
            for word in words:
                if len(word) > 3:  # Ignorar palavras muito curtas
                    word_counts[word] += 1

            max_repetitions = max(word_counts.values())
            if max_repetitions > len(words) * 0.1:  # Mais de 10% das palavras repetidas
                anomalies.append({
                    'type': AnomalyType.INCONSISTENT_RESPONSE.value,
                    'severity': AnomalySeverity.MEDIUM.value,
                    'description': "Resposta com alta repetição de palavras",
                    'evidence': {
                        'max_repetitions': max_repetitions,
                        'repetition_ratio': max_repetitions / len(words)
                    },
                    'recommended_action': 'Revisar algoritmo de geração de texto'
                })

        return anomalies

    async def _check_memory_health(self) -> List[Dict[str, Any]]:
        """Verifica saúde da memória e detecta corrupção."""
        anomalies = []

        try:
            # Verificar integridade das estruturas de dados
            if len(self.decision_history) > self.decision_history.maxlen:
                anomalies.append({
                    'type': AnomalyType.MEMORY_CORRUPTION.value,
                    'severity': AnomalySeverity.HIGH.value,
                    'description': "Estrutura de decisão_history corrompida",
                    'evidence': {'current_length': len(self.decision_history)},
                    'recommended_action': 'Reinicializar detector de anomalias'
                })

            # Verificar timestamps válidos
            invalid_timestamps = 0
            for item in list(self.decision_history) + list(self.response_history):
                try:
                    datetime.fromisoformat(item['timestamp'])
                except:
                    invalid_timestamps += 1

            if invalid_timestamps > 0:
                anomalies.append({
                    'type': AnomalyType.MEMORY_CORRUPTION.value,
                    'severity': AnomalySeverity.MEDIUM.value,
                    'description': f"Timestamps inválidos detectados: {invalid_timestamps}",
                    'evidence': {'invalid_timestamps': invalid_timestamps},
                    'recommended_action': 'Limpar dados corrompidos'
                })

        except Exception as e:
            anomalies.append({
                'type': AnomalyType.MEMORY_CORRUPTION.value,
                'severity': AnomalySeverity.CRITICAL.value,
                'description': f"Erro crítico na verificação de memória: {str(e)}",
                'evidence': {'error': str(e)},
                'recommended_action': 'Reinicializar sistema de detecção'
            })

        return anomalies

    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Retorna resumo das anomalias detectadas."""
        anomaly_counts = defaultdict(int)
        severity_counts = defaultdict(int)

        for anomaly_record in self.detected_anomalies:
            anomaly = anomaly_record['anomaly']
            anomaly_counts[anomaly['type']] += 1
            severity_counts[anomaly['severity']] += 1

        return {
            'total_anomalies': len(self.detected_anomalies),
            'anomaly_types': dict(anomaly_counts),
            'severity_distribution': dict(severity_counts),
            'active_alerts': list(self.active_alerts),
            'last_updated': datetime.now().isoformat()
        }

    def clear_old_anomalies(self, days: int = 30):
        """Limpa anomalias antigas."""
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.detected_anomalies)

        self.detected_anomalies = [
            anomaly for anomaly in self.detected_anomalies
            if datetime.fromisoformat(anomaly['timestamp']) > cutoff_date
        ]

        removed_count = original_count - len(self.detected_anomalies)
        if removed_count > 0:
            logger.info(f"Removidas {removed_count} anomalias antigas")
            self._save_state()

        return removed_count