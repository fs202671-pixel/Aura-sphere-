#!/usr/bin/env python3
"""
Demo Isolado do Sistema Avançado de Avaliação de Qualidade
=========================================================

Demonstração independente das funcionalidades avançadas de avaliação da IA.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Adicionar o diretório atual ao path para importações
sys.path.insert(0, str(Path(__file__).parent / "agent"))

# Importar diretamente os módulos necessários
import importlib.util

# Carregar módulos diretamente
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Carregar módulos
quality_metrics = load_module("quality_metrics", Path(__file__).parent / "agent" / "quality_metrics.py")
advanced_quality_evaluator = load_module("advanced_quality_evaluator", Path(__file__).parent / "agent" / "advanced_quality_evaluator.py")

# Obter classes
QualityMetricsCollector = quality_metrics.QualityMetricsCollector
AdvancedQualityEvaluator = advanced_quality_evaluator.AdvancedQualityEvaluator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_advanced_quality_evaluation():
    """Demonstra o sistema avançado de avaliação de qualidade."""

    print("🚀 Iniciando demo isolado do sistema avançado de avaliação de qualidade...")

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

    print("\n✅ Demo isolado concluído!")

if __name__ == "__main__":
    asyncio.run(demo_advanced_quality_evaluation())