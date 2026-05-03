#!/usr/bin/env python3
"""
Demo Standalone do Sistema Avançado de Avaliação de Qualidade
===========================================================

Demonstração independente das funcionalidades avançadas de avaliação da IA.
Código copiado para evitar problemas de importação.
"""

import asyncio
import logging
import json
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Copiar classes necessárias diretamente
class MetricType(Enum):
    """Tipos de métricas de qualidade."""
    ACCURACY = "accuracy"
    CREATIVITY = "creativity"
    CONSISTENCY = "consistency"
    CONTEXT_AWARENESS = "context_awareness"
    LEARNING_EFFICIENCY = "learning_efficiency"
    ADAPTABILITY = "adaptability"
    RESPONSE_TIME = "response_time"
    USER_SATISFACTION = "user_satisfaction"

class QualityMetricsCollector:
    """Coletor avançado de métricas de qualidade."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.metrics_file = data_dir / "quality_metrics.json"
        self.collection_active = False
        self.metrics_buffer = []

    def start_collection(self):
        """Inicia a coleta de métricas."""
        self.collection_active = True
        logger.info("Coleta de métricas iniciada")

    def stop_collection(self):
        """Para a coleta de métricas."""
        self.collection_active = False
        self._save_metrics()
        logger.info("Coleta de métricas parada")

    def _save_metrics(self):
        """Salva métricas no arquivo."""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics_buffer, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")

class AdvancedQualityEvaluator:
    """Avaliador avançado de qualidade da IA com evolução e predições."""

    def __init__(self, metrics_collector: QualityMetricsCollector, data_dir: Path):
        self.metrics_collector = metrics_collector
        self.data_dir = data_dir
        self.evolution_tracker = QualityEvolutionTracker(data_dir)
        self.thresholds = {
            'creativity': 0.7,
            'consistency': 0.8,
            'context_awareness': 0.75,
            'learning_efficiency': 0.6,
            'adaptability': 0.7,
            'overall': 0.75
        }

    async def evaluate_creativity(self, response: str, context: Dict[str, Any]) -> float:
        """Avalia a criatividade da resposta."""
        # Lógica simplificada de avaliação de criatividade
        score = 0.0

        # Verificar diversidade de vocabulário
        words = response.lower().split()
        unique_words = set(words)
        vocab_diversity = len(unique_words) / len(words) if words else 0
        score += vocab_diversity * 0.4

        # Verificar originalidade baseada no contexto
        topic = context.get('topic', '')
        if topic in response.lower():
            score += 0.3

        # Verificar estrutura não-linear
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        if len(sentences) > 1:
            score += 0.3

        return min(score, 1.0)

    async def evaluate_consistency(self, responses: List[str]) -> float:
        """Avalia a consistência entre múltiplas respostas."""
        if len(responses) < 2:
            return 1.0

        # Calcular similaridade baseada em comprimento
        lengths = [len(r) for r in responses]
        avg_length = statistics.mean(lengths)
        length_variance = statistics.variance(lengths) if len(lengths) > 1 else 0

        # Menor variância = maior consistência
        consistency = 1.0 - min(length_variance / (avg_length ** 2), 1.0)
        return consistency

    async def evaluate_context_awareness(self, response: str, context: Dict[str, Any]) -> float:
        """Avalia o awareness de contexto."""
        score = 0.0

        # Verificar referência ao humor do usuário
        user_mood = context.get('user_mood', '')
        mood_keywords = {
            'curious': ['entendo', 'vou explicar', 'vamos ver'],
            'confused': ['entendo', 'vou esclarecer', 'explicar'],
            'focused': ['ótimo', 'vamos', 'continuar'],
            'satisfied': ['excelente', 'ótimo', 'continuar'],
            'engaged': ['interessante', 'vamos explorar', 'ótimo']
        }

        if user_mood in mood_keywords:
            for keyword in mood_keywords[user_mood]:
                if keyword in response.lower():
                    score += 0.3
                    break

        # Verificar referência ao tópico
        topic = context.get('topic', '')
        if topic and topic in response.lower():
            score += 0.4

        # Verificar adequação do tom
        if user_mood in ['focused', 'engaged']:
            if any(word in response.lower() for word in ['técnico', 'detalhado', 'preciso']):
                score += 0.3

        return min(score, 1.0)

    async def evaluate_learning_efficiency(self, task: Dict[str, Any],
                                         before_score: float, after_score: float) -> float:
        """Avalia a eficiência de aprendizado."""
        improvement = after_score - before_score
        if improvement <= 0:
            return 0.0

        # Eficiência baseada na magnitude da melhoria
        efficiency = min(improvement * 2, 1.0)  # Normalizar para 0-1
        return efficiency

    async def evaluate_adaptability(self, user_preferences: Dict[str, Any],
                                   response_style: Dict[str, Any]) -> float:
        """Avalia a adaptabilidade às preferências do usuário."""
        score = 0.0

        # Verificar alinhamento de estilo de comunicação
        pref_style = user_preferences.get('communication_style', '')
        resp_style = response_style.get('response_style', '')

        if pref_style == resp_style:
            score += 0.4

        # Verificar nível de detalhe
        pref_detail = user_preferences.get('detail_level', '')
        has_examples = response_style.get('code_examples', False)
        detailed_explanations = response_style.get('explanations', '') == 'detailed'

        if pref_detail == 'high' and (has_examples or detailed_explanations):
            score += 0.6

        return min(score, 1.0)

    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Gera relatório abrangente de qualidade."""
        # Métricas simuladas para demo
        advanced_metrics = {
            'creativity': 0.82,
            'consistency': 0.89,
            'context_awareness': 0.76,
            'learning_efficiency': 0.71,
            'adaptability': 0.85
        }

        overall_score = statistics.mean(advanced_metrics.values())

        return {
            'quality_score': {
                'overall_score': overall_score,
                'meets_threshold': overall_score >= self.thresholds['overall']
            },
            'advanced_metrics': advanced_metrics,
            'evolution_analysis': {
                'trend': 'improving',
                'improvement_rate': 0.05,
                'stability': 0.92
            },
            'predictions': {
                'predicted_score': overall_score + 0.02,
                'confidence': 0.78
            },
            'recommendations': [
                'Continuar melhorando adaptabilidade',
                'Focar em criatividade para tópicos técnicos',
                'Manter consistência atual'
            ],
            'learning_summary': {
                'total_attempts': 45,
                'success_rate': 0.87,
                'overall_improvement': 0.15
            }
        }

class QualityEvolutionTracker:
    """Rastreador de evolução da qualidade."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.history_file = data_dir / "quality_history.json"
        self.history = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        """Carrega histórico de qualidade."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar histórico: {e}")
        return []

async def demo_advanced_quality_evaluation():
    """Demonstra o sistema avançado de avaliação de qualidade."""

    print("🚀 Iniciando demo standalone do sistema avançado de avaliação de qualidade...")

    # Criar diretório de dados
    data_dir = Path("demo_quality_data")
    data_dir.mkdir(exist_ok=True)

    # Inicializar componentes
    metrics_collector = QualityMetricsCollector(data_dir)
    quality_evaluator = AdvancedQualityEvaluator(metrics_collector, data_dir)

    # Iniciar coleta de métricas
    metrics_collector.start_collection()

    print("\n📊 Simulando interações e coletando métricas...")

    # Simular algumas interações
    test_responses = [
        "Olá! Como posso ajudar você hoje?",
        "Entendo sua pergunta sobre Python. Vou explicar de forma clara e objetiva.",
        "Aqui está uma função recursiva bem estruturada para calcular Fibonacci.",
        "Essa abordagem é mais eficiente e evita problemas de performance.",
        "Posso sugerir uma otimização adicional no seu código?"
    ]

    test_contexts = [
        {"user_mood": "curious", "topic": "programming"},
        {"user_mood": "confused", "topic": "python"},
        {"user_mood": "focused", "topic": "algorithms"},
        {"user_mood": "satisfied", "topic": "optimization"},
        {"user_mood": "engaged", "topic": "code_review"}
    ]

    # Avaliar criatividade
    print("\n🎨 Avaliando criatividade das respostas...")
    creativity_scores = []
    for response, context in zip(test_responses, test_contexts):
        score = await quality_evaluator.evaluate_creativity(response, context)
        creativity_scores.append(score)
        print(f"  Criatividade: {score:.3f}")

    # Avaliar consistência
    print("\n🔄 Avaliando consistência entre respostas...")
    consistency_score = await quality_evaluator.evaluate_consistency(test_responses)
    print(f"  Consistência: {consistency_score:.3f}")

    # Avaliar awareness de contexto
    print("\n🎯 Avaliando awareness de contexto...")
    context_scores = []
    for response, context in zip(test_responses, test_contexts):
        score = await quality_evaluator.evaluate_context_awareness(response, context)
        context_scores.append(score)
        print(f"  Awareness: {score:.3f}")

    # Simular aprendizado
    print("\n🧠 Simulando tentativas de aprendizado...")
    learning_score = await quality_evaluator.evaluate_learning_efficiency(
        {"type": "code_optimization", "skill": "fibonacci_algorithm"},
        0.6,  # performance antes
        0.85  # performance depois
    )
    print(f"  Eficiência de Aprendizado: {learning_score:.3f}")

    # Avaliar adaptabilidade
    print("\n🔧 Avaliando adaptabilidade...")
    adaptability_score = await quality_evaluator.evaluate_adaptability(
        {"communication_style": "technical", "detail_level": "high"},
        {"response_style": "technical", "code_examples": True, "explanations": "detailed"}
    )
    print(f"  Adaptabilidade: {adaptability_score:.3f}")

    # Gerar relatório abrangente
    print("\n📈 Gerando relatório abrangente...")
    report = await quality_evaluator.generate_comprehensive_report()

    print("\n📊 RESULTADOS FINAIS:")
    print("=" * 50)
    print(f"Score de Qualidade Geral: {report['quality_score']['overall_score']:.3f}")
    print(f"Atende Threshold: {report['quality_score']['meets_threshold']}")

    print("\n🎨 Métricas Avançadas:")
    print(f"  Criatividade: {report['advanced_metrics']['creativity']:.3f}")
    print(f"  Consistência: {report['advanced_metrics']['consistency']:.3f}")
    print(f"  Awareness de Contexto: {report['advanced_metrics']['context_awareness']:.3f}")
    print(f"  Eficiência de Aprendizado: {report['advanced_metrics']['learning_efficiency']:.3f}")
    print(f"  Adaptabilidade: {report['advanced_metrics']['adaptability']:.3f}")

    print("\n📈 Análise de Evolução:")
    evolution = report['evolution_analysis']
    print(f"Tendência: {evolution['trend']}")
    print(f"Velocidade de Melhoria: {evolution['improvement_rate']:.3f}")
    print(f"Estabilidade: {evolution['stability']:.3f}")

    print("\n🔮 Previsões:")
    predictions = report['predictions']
    if predictions.get('predicted_score'):
        print(f"Score Previsto: {predictions['predicted_score']:.3f}")
        print(f"Confiança: {predictions['confidence']:.3f}")
    else:
        print(f"Previsão: {predictions.get('prediction', 'N/A')}")

    print("\n💡 Recomendações:")
    for rec in report['recommendations'][:3]:  # Top 3
        print(f"• {rec}")

    print("\n📚 Resumo de Aprendizado:")
    learning = report['learning_summary']
    print(f"Total de tentativas: {learning['total_attempts']}")
    print(f"Taxa de Sucesso: {learning['success_rate']:.3f}")
    print(f"Melhoria Geral: {learning['overall_improvement']:.1%}")

    # Parar coleta
    metrics_collector.stop_collection()

    print("\n✅ Demo standalone concluído!")

if __name__ == "__main__":
    asyncio.run(demo_advanced_quality_evaluation())