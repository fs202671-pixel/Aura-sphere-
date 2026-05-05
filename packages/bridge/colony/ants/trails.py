"""
Trail System - Sistema de Trilhas de Reforço
============================================

Sistema de reforço baseado em trilhas deixadas pelas formigas.
Características:
- Reforço de caminhos eficientes
- Atenuação de caminhos ruins
- Aprendizado coletivo
- Decaimento temporal
"""

import time
import math
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TrailPheromone:
    """Feromônio de trilha"""
    source_ant: str
    target_type: str
    strength: float
    timestamp: float
    decay_rate: float = 0.1  # Taxa de decaimento por hora

    def get_current_strength(self) -> float:
        """Calcula força atual considerando decaimento temporal"""
        elapsed_hours = (time.time() - self.timestamp) / 3600
        decayed_strength = self.strength * math.exp(-self.decay_rate * elapsed_hours)
        return max(decayed_strength, 0.0)

    def is_expired(self, max_age_hours: float = 24) -> bool:
        """Verifica se a trilha expirou"""
        elapsed_hours = (time.time() - self.timestamp) / 3600
        return elapsed_hours > max_age_hours

class TrailSystem:
    """
    Sistema de trilhas para reforço de soluções

    Funcionalidades:
    - Manutenção de feromônios de trilha
    - Reforço de caminhos bem-sucedidos
    - Atenuação de caminhos ineficientes
    - Recomendação de caminhos ótimos
    """

    def __init__(self):
        self.trails: Dict[str, List[TrailPheromone]] = {}
        self.evaporation_rate = 0.05  # Taxa de evaporação global
        self.min_strength_threshold = 0.01  # Limite mínimo de força

        logger.info("TrailSystem initialized")

    def add_trail(self, source_ant: str, target_type: str, strength: float):
        """
        Adiciona uma nova trilha

        Args:
            source_ant: ID da formiga que deixou a trilha
            target_type: Tipo de alvo (tarefa, solução, etc.)
            strength: Força inicial da trilha
        """
        if target_type not in self.trails:
            self.trails[target_type] = []

        pheromone = TrailPheromone(
            source_ant=source_ant,
            target_type=target_type,
            strength=strength,
            timestamp=time.time()
        )

        self.trails[target_type].append(pheromone)

        # Limitar número de trilhas por tipo para evitar crescimento excessivo
        if len(self.trails[target_type]) > 100:
            # Remover trilhas mais antigas e fracas
            self.trails[target_type].sort(key=lambda p: p.get_current_strength())
            self.trails[target_type] = self.trails[target_type][-50:]  # Manter 50 melhores

        logger.debug(f"Added trail from {source_ant} to {target_type} with strength {strength}")

    def reinforce_trail(self, target_type: str, reinforcement: float):
        """
        Reforça uma trilha existente

        Args:
            target_type: Tipo de alvo
            reinforcement: Quantidade de reforço
        """
        if target_type not in self.trails:
            return

        # Reforçar todas as trilhas para este tipo
        for pheromone in self.trails[target_type]:
            pheromone.strength = min(pheromone.strength + reinforcement, 1.0)

        logger.debug(f"Reinforced trails for {target_type} by {reinforcement}")

    def evaporate_trails(self):
        """Evapora trilhas antigas e fracas"""
        current_time = time.time()

        for target_type in list(self.trails.keys()):
            # Filtrar trilhas expiradas
            self.trails[target_type] = [
                p for p in self.trails[target_type]
                if not p.is_expired()
            ]

            # Aplicar evaporação
            for pheromone in self.trails[target_type]:
                elapsed_hours = (current_time - pheromone.timestamp) / 3600
                evaporation = self.evaporation_rate * elapsed_hours
                pheromone.strength = max(pheromone.strength - evaporation, 0.0)

            # Remover trilhas muito fracas
            self.trails[target_type] = [
                p for p in self.trails[target_type]
                if p.get_current_strength() > self.min_strength_threshold
            ]

            # Remover tipos sem trilhas
            if not self.trails[target_type]:
                del self.trails[target_type]

    def get_best_trail(self, target_type: str) -> Optional[TrailPheromone]:
        """
        Retorna a melhor trilha para um tipo de alvo

        Args:
            target_type: Tipo de alvo

        Returns:
            Melhor trilha ou None
        """
        if target_type not in self.trails:
            return None

        # Encontrar trilha com maior força atual
        best_trail = max(self.trails[target_type], key=lambda p: p.get_current_strength())

        return best_trail if best_trail.get_current_strength() > self.min_strength_threshold else None

    def get_trail_strength(self, target_type: str) -> float:
        """
        Retorna força total das trilhas para um tipo

        Args:
            target_type: Tipo de alvo

        Returns:
            Força total agregada
        """
        if target_type not in self.trails:
            return 0.0

        total_strength = sum(p.get_current_strength() for p in self.trails[target_type])
        return min(total_strength, 1.0)  # Limitar a 1.0

    def get_recommendations(self, available_targets: List[str], top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Recomenda os melhores alvos baseados nas trilhas

        Args:
            available_targets: Lista de alvos disponíveis
            top_n: Número de recomendações

        Returns:
            Lista de (alvo, força) ordenada por força
        """
        recommendations = []

        for target in available_targets:
            strength = self.get_trail_strength(target)
            if strength > 0:
                recommendations.append((target, strength))

        # Ordenar por força decrescente
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:top_n]

    def analyze_trail_patterns(self) -> Dict[str, Any]:
        """
        Analisa padrões nas trilhas para insights

        Returns:
            Análise dos padrões encontrados
        """
        analysis = {
            'total_trails': sum(len(trails) for trails in self.trails.values()),
            'active_types': len(self.trails),
            'strongest_trails': {},
            'emerging_patterns': []
        }

        # Encontrar trilhas mais fortes por tipo
        for target_type, pheromones in self.trails.items():
            if pheromones:
                strongest = max(pheromones, key=lambda p: p.get_current_strength())
                analysis['strongest_trails'][target_type] = {
                    'strength': strongest.get_current_strength(),
                    'ant_count': len(pheromones),
                    'avg_age_hours': sum((time.time() - p.timestamp) / 3600 for p in pheromones) / len(pheromones)
                }

        # Identificar padrões emergentes
        for target_type, data in analysis['strongest_trails'].items():
            if data['strength'] > 0.7 and data['ant_count'] >= 3:
                analysis['emerging_patterns'].append({
                    'type': target_type,
                    'confidence': data['strength'],
                    'support': data['ant_count']
                })

        return analysis

    def cleanup_expired_trails(self):
        """Remove trilhas expiradas completamente"""
        expired_types = []

        for target_type in self.trails:
            # Verificar se todas as trilhas expiraram
            if all(p.is_expired() for p in self.trails[target_type]):
                expired_types.append(target_type)

        for target_type in expired_types:
            del self.trails[target_type]
            logger.debug(f"Removed expired trail type: {target_type}")

    def export_trails(self) -> Dict[str, Any]:
        """
        Exporta estado atual das trilhas para persistência

        Returns:
            Dados das trilhas para serialização
        """
        export_data = {}

        for target_type, pheromones in self.trails.items():
            export_data[target_type] = [
                {
                    'source_ant': p.source_ant,
                    'strength': p.strength,
                    'timestamp': p.timestamp,
                    'decay_rate': p.decay_rate
                }
                for p in pheromones
            ]

        return export_data

    def import_trails(self, trail_data: Dict[str, Any]):
        """
        Importa trilhas de dados persistidos

        Args:
            trail_data: Dados das trilhas para importação
        """
        for target_type, pheromones_data in trail_data.items():
            self.trails[target_type] = []

            for p_data in pheromones_data:
                pheromone = TrailPheromone(
                    source_ant=p_data['source_ant'],
                    target_type=target_type,
                    strength=p_data['strength'],
                    timestamp=p_data['timestamp'],
                    decay_rate=p_data.get('decay_rate', 0.1)
                )
                self.trails[target_type].append(pheromone)

        logger.info(f"Imported {len(trail_data)} trail types")