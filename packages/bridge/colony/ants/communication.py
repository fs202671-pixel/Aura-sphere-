"""
Ant Communication - Sistema de Comunicação Indireta
===================================================

Comunicação entre formigas através de memória compartilhada.
Características:
- Comunicação indireta (sem mensagens diretas)
- Trilhas como mecanismo de compartilhamento
- Memória coletiva acessível
- Isolamento entre agentes
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from memory.collective import CollectiveMemory

logger = logging.getLogger(__name__)

@dataclass
class Trail:
    """Trilha deixada por uma formiga"""
    ant_id: str
    task_type: str
    finding_type: str
    relevance: float
    strength: float
    timestamp: float
    expires_at: float
    metadata: Dict[str, Any]

class AntCommunication:
    """
    Sistema de comunicação indireta entre formigas

    Funcionalidades:
    - Deixar trilhas na memória coletiva
    - Seguir trilhas de outros agentes
    - Receber tarefas do orquestrador
    - Reportar resultados indiretamente
    """

    def __init__(self):
        self.memory = CollectiveMemory()
        self.ant_id = None  # Será definido quando a formiga for criada

    def set_ant_id(self, ant_id: str):
        """Define o ID da formiga para comunicação"""
        self.ant_id = ant_id

    async def leave_trail(self, result: Any):
        """
        Deixa uma trilha na memória coletiva

        Args:
            result: Resultado da exploração ou outro dado relevante
        """
        if not self.ant_id:
            raise ValueError("Ant ID not set")

        trail_data = {
            'ant_id': self.ant_id,
            'type': 'exploration_result',
            'data': result,
            'timestamp': time.time(),
            'expires_at': time.time() + 3600  # Expira em 1 hora
        }

        # Armazenar na memória coletiva
        await self.memory.store_trail(trail_data)

        logger.debug(f"Ant {self.ant_id} left trail: {result}")

    async def follow_trails(self, task_type: str, limit: int = 10) -> List[Trail]:
        """
        Segue trilhas relevantes para um tipo de tarefa

        Args:
            task_type: Tipo de tarefa
            limit: Número máximo de trilhas a retornar

        Returns:
            Lista de trilhas relevantes
        """
        # Buscar trilhas na memória coletiva
        trails_data = await self.memory.get_trails_by_type(task_type, limit)

        trails = []
        for trail_data in trails_data:
            trail = Trail(
                ant_id=trail_data['ant_id'],
                task_type=trail_data.get('task_type', 'unknown'),
                finding_type=trail_data.get('finding_type', 'unknown'),
                relevance=trail_data.get('relevance', 0.0),
                strength=trail_data.get('strength', 0.0),
                timestamp=trail_data['timestamp'],
                expires_at=trail_data['expires_at'],
                metadata=trail_data.get('metadata', {})
            )
            trails.append(trail)

        return trails

    async def receive_task(self) -> Optional[Dict[str, Any]]:
        """
        Recebe tarefa do orquestrador através da memória coletiva

        Returns:
            Tarefa disponível ou None
        """
        # Verificar se há tarefas disponíveis para esta formiga
        tasks = await self.memory.get_pending_tasks(self.ant_id)

        if tasks:
            # Pegar primeira tarefa disponível
            task = tasks[0]

            # Marcar como em processamento
            await self.memory.update_task_status(task['id'], 'processing', self.ant_id)

            logger.info(f"Ant {self.ant_id} received task: {task['id']}")
            return task

        return None

    async def report_result(self, result: Any):
        """
        Reporta resultado da exploração através da memória

        Args:
            result: Resultado a ser reportado
        """
        if not self.ant_id:
            raise ValueError("Ant ID not set")

        report_data = {
            'ant_id': self.ant_id,
            'type': 'exploration_report',
            'result': result,
            'timestamp': time.time()
        }

        # Armazenar relatório na memória coletiva
        await self.memory.store_report(report_data)

        logger.info(f"Ant {self.ant_id} reported result")

    async def get_swarm_intelligence(self, task_type: str) -> Dict[str, Any]:
        """
        Obtém inteligência coletiva sobre um tipo de tarefa

        Args:
            task_type: Tipo de tarefa

        Returns:
            Dados agregados da colônia
        """
        # Agregar dados de múltiplas trilhas
        trails = await self.follow_trails(task_type, limit=50)

        if not trails:
            return {'confidence': 0.0, 'patterns': [], 'recommendations': []}

        # Calcular confiança baseada na força das trilhas
        total_strength = sum(trail.strength for trail in trails)
        avg_strength = total_strength / len(trails)

        # Identificar padrões comuns
        patterns = self._identify_patterns(trails)

        # Gerar recomendações
        recommendations = self._generate_recommendations(trails, patterns)

        return {
            'confidence': min(avg_strength, 1.0),
            'patterns': patterns,
            'recommendations': recommendations,
            'trail_count': len(trails)
        }

    def _identify_patterns(self, trails: List[Trail]) -> List[Dict[str, Any]]:
        """Identifica padrões comuns nas trilhas"""
        patterns = []

        # Agrupar por tipo de achado
        findings_by_type = {}
        for trail in trails:
            if trail.finding_type not in findings_by_type:
                findings_by_type[trail.finding_type] = []
            findings_by_type[trail.finding_type].append(trail)

        # Identificar padrões significativos
        for finding_type, type_trails in findings_by_type.items():
            if len(type_trails) >= 3:  # Pelo menos 3 formigas encontraram
                avg_relevance = sum(t.relevance for t in type_trails) / len(type_trails)

                if avg_relevance > 0.6:  # Relevância significativa
                    patterns.append({
                        'type': finding_type,
                        'frequency': len(type_trails),
                        'avg_relevance': avg_relevance,
                        'confidence': min(len(type_trails) / 10, 1.0)  # Confiança baseada na frequência
                    })

        return patterns

    def _generate_recommendations(self, trails: List[Trail], patterns: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas nas trilhas e padrões"""
        recommendations = []

        # Recomendação baseada nos padrões mais confiáveis
        if patterns:
            best_pattern = max(patterns, key=lambda p: p['confidence'])
            recommendations.append(f"Focar em {best_pattern['type']} (confiança: {best_pattern['confidence']:.2f})")

        # Recomendação baseada na diversidade
        unique_types = len(set(t.finding_type for t in trails))
        if unique_types > 5:
            recommendations.append("Exploração está diversificada - manter estratégia atual")
        elif unique_types < 2:
            recommendations.append("Pouca diversidade - considerar expandir busca")

        # Recomendação baseada no tempo
        if trails:
            oldest_trail = min(trails, key=lambda t: t.timestamp)
            newest_trail = max(trails, key=lambda t: t.timestamp)

            time_span = newest_trail.timestamp - oldest_trail.timestamp
            if time_span > 1800:  # 30 minutos
                recommendations.append("Trilhas antigas detectadas - considerar refresh")

        return recommendations