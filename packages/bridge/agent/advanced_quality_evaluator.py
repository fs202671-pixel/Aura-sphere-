"""
Sistema Avançado de Avaliação de Qualidade da IA
===============================================

Sistema expandido para avaliação contínua e evolução da qualidade da IA.
Inclui métricas comportamentais, aprendizado e auto-avaliação.
"""

import asyncio
import json
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import statistics
import logging
from enum import Enum

from .quality_metrics import QualityMetricsCollector, MetricType

logger = logging.getLogger(__name__)

class AdvancedMetricType(Enum):
    """Tipos avançados de métricas."""
    CREATIVITY_SCORE = "creativity_score"
    ADAPTABILITY_INDEX = "adaptability_index"
    CONSISTENCY_RATIO = "consistency_ratio"
    LEARNING_EFFICIENCY = "learning_efficiency"
    DECISION_CONFIDENCE = "decision_confidence"
    USER_ENGAGEMENT = "user_engagement"
    SELF_IMPROVEMENT_RATE = "self_improvement_rate"
    ERROR_RECOVERY_RATE = "error_recovery_rate"
    CONTEXT_AWARENESS = "context_awareness"
    ETHICAL_DECISION_MAKING = "ethical_decision_making"

class QualityEvolutionTracker:
    """
    Rastreia evolução da qualidade da IA ao longo do tempo.

    Funcionalidades:
    - Histórico de scores de qualidade
    - Detecção de tendências de melhoria/deterioração
    - Previsão de performance futura
    - Recomendações de otimização
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.evolution_log = data_dir / "quality_evolution.json"
        self.evolution_history: List[Dict[str, Any]] = []

        self._load_evolution_history()

    def _load_evolution_history(self):
        """Carrega histórico de evolução."""
        if self.evolution_log.exists():
            try:
                with open(self.evolution_log, 'r') as f:
                    self.evolution_history = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load evolution history: {e}")

    def _save_evolution_history(self):
        """Salva histórico de evolução."""
        try:
            with open(self.evolution_log, 'w') as f:
                json.dump(self.evolution_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save evolution history: {e}")

    def record_quality_snapshot(self, quality_score: Dict[str, Any]):
        """Registra snapshot de qualidade."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
            "evolution_metrics": self._calculate_evolution_metrics()
        }

        self.evolution_history.append(snapshot)

        # Manter apenas últimos 1000 snapshots
        if len(self.evolution_history) > 1000:
            self.evolution_history = self.evolution_history[-1000:]

        self._save_evolution_history()

    def _calculate_evolution_metrics(self) -> Dict[str, Any]:
        """Calcula métricas de evolução."""
        if len(self.evolution_history) < 2:
            return {"trend": "insufficient_data"}

        recent_scores = [
            entry["quality_score"]["overall_score"]
            for entry in self.evolution_history[-10:]  # Últimos 10 snapshots
        ]

        if len(recent_scores) < 2:
            return {"trend": "insufficient_data"}

        # Calcular tendência
        try:
            slope = statistics.linear_regression(range(len(recent_scores)), recent_scores)[0]
            trend = "improving" if slope > 0.001 else "declining" if slope < -0.001 else "stable"
        except Exception:
            trend = "unknown"

        # Calcular volatilidade
        volatility = statistics.stdev(recent_scores) if len(recent_scores) > 1 else 0

        # Calcular taxa de melhoria
        improvement_rate = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)

        return {
            "trend": trend,
            "volatility": volatility,
            "improvement_rate": improvement_rate,
            "current_score": recent_scores[-1],
            "average_score": statistics.mean(recent_scores)
        }

    def predict_future_performance(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Prevê performance futura baseada em tendências."""
        if len(self.evolution_history) < 5:
            return {"prediction": "insufficient_data"}

        recent_scores = [
            entry["quality_score"]["overall_score"]
            for entry in self.evolution_history[-20:]  # Últimos 20 snapshots
        ]

        if len(recent_scores) < 5:
            return {"prediction": "insufficient_data"}

        # Regressão linear simples para previsão
        try:
            slope, intercept = statistics.linear_regression(range(len(recent_scores)), recent_scores)

            # Prever score em N dias (assumindo 1 snapshot por hora)
            future_score = intercept + slope * (len(recent_scores) + (days_ahead * 24))

            # Limitar entre 0 e 1
            future_score = max(0.0, min(1.0, future_score))

            confidence = min(0.9, len(recent_scores) / 50.0)  # Confiança aumenta com mais dados

            return {
                "predicted_score": future_score,
                "confidence": confidence,
                "trend": "improving" if slope > 0 else "declining" if slope < 0 else "stable",
                "days_ahead": days_ahead
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {"prediction": "error", "error": str(e)}

    def get_optimization_recommendations(self) -> List[str]:
        """Gera recomendações de otimização baseadas na evolução."""
        recommendations = []

        if len(self.evolution_history) < 3:
            return ["Colete mais dados de qualidade antes de gerar recomendações."]

        recent_evolution = self._calculate_evolution_metrics()

        # Análise de tendência
        if recent_evolution["trend"] == "declining":
            recommendations.append("Performance está declinando. Considere rollback para versão anterior.")
            recommendations.append("Revise recentes mudanças no código que podem ter causado degradação.")

        elif recent_evolution["trend"] == "stable":
            recommendations.append("Performance está estável. Foque em melhorias incrementais.")
            recommendations.append("Considere implementar novos recursos ou otimizações.")

        # Análise de volatilidade
        if recent_evolution["volatility"] > 0.1:
            recommendations.append("Alta volatilidade detectada. Melhore estabilidade do sistema.")
            recommendations.append("Implemente testes mais rigorosos antes de deploy.")

        # Análise de score atual
        current_score = recent_evolution["current_score"]
        if current_score < 0.6:
            recommendations.append("Score de qualidade baixo. Priorize melhorias críticas.")
        elif current_score < 0.8:
            recommendations.append("Score de qualidade aceitável. Foque em refinamentos.")
        else:
            recommendations.append("Score de qualidade excelente. Mantenha padrões altos.")

        return recommendations

class AdvancedQualityEvaluator:
    """
    Avaliador avançado de qualidade com métricas comportamentais e de aprendizado.
    """

    def __init__(self, metrics_collector: QualityMetricsCollector, data_dir: Path):
        self.metrics_collector = metrics_collector
        self.data_dir = data_dir
        self.evolution_tracker = QualityEvolutionTracker(data_dir)

        # Estado interno para tracking avançado
        self.conversation_history: List[Dict[str, Any]] = []
        self.decision_patterns: Dict[str, List[Any]] = {}
        self.learning_attempts: List[Dict[str, Any]] = []

    async def evaluate_creativity(self, response: str, context: Dict[str, Any]) -> float:
        """
        Avalia criatividade da resposta.

        Métricas:
        - Originalidade lexical
        - Complexidade estrutural
        - Inovação conceitual
        """
        # Análise de originalidade (diversidade lexical)
        words = response.lower().split()
        unique_words = set(words)
        lexical_diversity = len(unique_words) / len(words) if words else 0

        # Análise de complexidade estrutural
        sentences = response.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Análise de inovação (comparação com histórico)
        similar_responses = self._find_similar_responses(response)
        novelty_score = 1.0 - (len(similar_responses) / max(1, len(self.conversation_history)))

        # Score composto
        creativity_score = (
            lexical_diversity * 0.4 +
            min(avg_sentence_length / 20.0, 1.0) * 0.3 +  # Normalizar para 0-1
            novelty_score * 0.3
        )

        # Registrar métrica
        self.metrics_collector.record_metric(
            AdvancedMetricType.CREATIVITY_SCORE,
            creativity_score,
            {"response_sample": response[:100], "context": context}
        )

        return creativity_score

    async def evaluate_adaptability(self, user_pattern: Dict[str, Any],
                                   ai_response_pattern: Dict[str, Any]) -> float:
        """
        Avalia adaptabilidade da IA a padrões do usuário.
        """
        # Comparar consistência de respostas para padrões similares
        adaptability_score = self._calculate_pattern_adaptation(user_pattern, ai_response_pattern)

        self.metrics_collector.record_metric(
            AdvancedMetricType.ADAPTABILITY_INDEX,
            adaptability_score,
            {"user_pattern": user_pattern, "ai_pattern": ai_response_pattern}
        )

        return adaptability_score

    async def evaluate_learning_efficiency(self, learning_task: Dict[str, Any],
                                          performance_before: float,
                                          performance_after: float) -> float:
        """
        Avalia eficiência do aprendizado.
        """
        improvement = performance_after - performance_before
        efficiency_score = max(0.0, min(1.0, improvement * 2))  # Normalizar melhoria

        self.learning_attempts.append({
            "task": learning_task,
            "before": performance_before,
            "after": performance_after,
            "improvement": improvement,
            "timestamp": datetime.now().isoformat()
        })

        self.metrics_collector.record_metric(
            AdvancedMetricType.LEARNING_EFFICIENCY,
            efficiency_score,
            {"learning_task": learning_task, "improvement": improvement}
        )

        return efficiency_score

    async def evaluate_consistency(self, responses: List[str]) -> float:
        """
        Avalia consistência entre múltiplas respostas.
        """
        if len(responses) < 2:
            return 1.0

        # Calcular similaridade entre respostas
        similarities = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                sim = self._calculate_text_similarity(responses[i], responses[j])
                similarities.append(sim)

        avg_similarity = statistics.mean(similarities)
        consistency_score = avg_similarity  # Maior similaridade = maior consistência

        self.metrics_collector.record_metric(
            AdvancedMetricType.CONSISTENCY_RATIO,
            consistency_score,
            {"response_count": len(responses), "avg_similarity": avg_similarity}
        )

        return consistency_score

    async def evaluate_context_awareness(self, response: str, context: Dict[str, Any]) -> float:
        """
        Avalia awareness de contexto da resposta.
        """
        context_references = 0
        total_context_items = len(context)

        if total_context_items == 0:
            return 0.5  # Score neutro se não há contexto

        # Verificar referências ao contexto na resposta
        response_lower = response.lower()
        for key, value in context.items():
            if isinstance(value, str) and value.lower() in response_lower:
                context_references += 1
            elif isinstance(value, (int, float)) and str(value) in response:
                context_references += 1

        awareness_score = context_references / total_context_items

        self.metrics_collector.record_metric(
            AdvancedMetricType.CONTEXT_AWARENESS,
            awareness_score,
            {"context_references": context_references, "total_context": total_context_items}
        )

        return awareness_score

    def _find_similar_responses(self, response: str, threshold: float = 0.7) -> List[str]:
        """Encontra respostas similares no histórico."""
        similar = []
        for entry in self.conversation_history[-50:]:  # Últimas 50 conversas
            if "response" in entry:
                similarity = self._calculate_text_similarity(response, entry["response"])
                if similarity >= threshold:
                    similar.append(entry["response"])
        return similar

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade simples entre textos."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _calculate_pattern_adaptation(self, user_pattern: Dict, ai_pattern: Dict) -> float:
        """Calcula quão bem a IA se adaptou ao padrão do usuário."""
        # Implementação simplificada - comparar chaves e valores similares
        user_keys = set(user_pattern.keys())
        ai_keys = set(ai_pattern.keys())

        key_overlap = len(user_keys.intersection(ai_keys)) / len(user_keys.union(ai_keys))

        # Comparar valores similares
        value_similarity = 0
        common_keys = user_keys.intersection(ai_keys)
        if common_keys:
            for key in common_keys:
                if user_pattern[key] == ai_pattern[key]:
                    value_similarity += 1
            value_similarity /= len(common_keys)

        return (key_overlap + value_similarity) / 2

    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Gera relatório abrangente de qualidade."""
        # Coletar métricas atuais
        quality_score = self.metrics_collector.calculate_quality_score()

        # Adicionar métricas avançadas
        advanced_metrics = {
            "creativity_avg": await self._calculate_average_metric(AdvancedMetricType.CREATIVITY_SCORE),
            "adaptability_avg": await self._calculate_average_metric(AdvancedMetricType.ADAPTABILITY_INDEX),
            "consistency_avg": await self._calculate_average_metric(AdvancedMetricType.CONSISTENCY_RATIO),
            "learning_efficiency_avg": await self._calculate_average_metric(AdvancedMetricType.LEARNING_EFFICIENCY),
            "context_awareness_avg": await self._calculate_average_metric(AdvancedMetricType.CONTEXT_AWARENESS)
        }

        # Análise de evolução
        evolution_metrics = self.evolution_tracker._calculate_evolution_metrics()
        predictions = self.evolution_tracker.predict_future_performance()
        recommendations = self.evolution_tracker.get_optimization_recommendations()

        # Registrar snapshot na evolução
        self.evolution_tracker.record_quality_snapshot(quality_score)

        return {
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
            "advanced_metrics": advanced_metrics,
            "evolution_analysis": evolution_metrics,
            "predictions": predictions,
            "recommendations": recommendations,
            "learning_summary": self._summarize_learning_attempts()
        }

    async def _calculate_average_metric(self, metric_type: AdvancedMetricType) -> float:
        """Calcula média de uma métrica avançada."""
        # Buscar métricas recentes (última hora)
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_metrics = [
            m for m in self.metrics_collector.metrics_history
            if (datetime.fromisoformat(m["timestamp"]) > cutoff_time and
                m["metric_type"] == metric_type.value)
        ]

        if not recent_metrics:
            return 0.0

        values = [m["value"] for m in recent_metrics]
        return statistics.mean(values)

    def _summarize_learning_attempts(self) -> Dict[str, Any]:
        """Resume tentativas de aprendizado."""
        if not self.learning_attempts:
            return {"total_attempts": 0, "avg_improvement": 0}

        improvements = [attempt["improvement"] for attempt in self.learning_attempts[-20:]]
        avg_improvement = statistics.mean(improvements) if improvements else 0

        successful_attempts = len([i for i in improvements if i > 0])

        return {
            "total_attempts": len(self.learning_attempts),
            "recent_attempts": len(improvements),
            "avg_improvement": avg_improvement,
            "success_rate": successful_attempts / len(improvements) if improvements else 0
        }