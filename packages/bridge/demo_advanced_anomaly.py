#!/usr/bin/env python3
"""
Demo do Sistema Avançado de Detecção de Anomalias
================================================

Demonstração das funcionalidades de detecção de anomalias comportamentais.
"""

import asyncio
import logging
from pathlib import Path
from agent.advanced_anomaly_detector import BehavioralAnomalyDetector, AnomalyType

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_anomaly_detection():
    """Demonstra o sistema de detecção de anomalias."""

    print("🚨 Iniciando demo do sistema avançado de detecção de anomalias...")

    # Criar diretório de dados
    data_dir = Path("demo_anomaly_data")
    data_dir.mkdir(exist_ok=True)

    # Inicializar detector
    detector = BehavioralAnomalyDetector(data_dir)

    print("\n📊 Testando detecção de loops de decisão...")

    # Simular loop de decisão
    loop_decisions = [
        {"type": "code_analysis", "target": "main.py", "action": "optimize"},
        {"type": "code_analysis", "target": "main.py", "action": "optimize"},
        {"type": "code_analysis", "target": "main.py", "action": "optimize"},
        {"type": "code_analysis", "target": "main.py", "action": "optimize"},
    ]

    for decision in loop_decisions:
        anomalies = await detector.analyze_decision(decision)
        if anomalies:
            for anomaly in anomalies:
                print(f"  ⚠️  Anomalia detectada: {anomaly['type']} - {anomaly['description']}")

    print("\n🛡️  Testando detecção de tentativas de violação...")

    # Simular tentativas de violação
    violation_decisions = [
        {"type": "core_modification", "target": "core.py", "action": "edit"},
        {"type": "direct_system_access", "command": "rm -rf /", "action": "execute"},
        {"type": "sandbox_escape", "command": "sudo chmod 777 /etc/passwd", "action": "execute"},
    ]

    for decision in violation_decisions:
        anomalies = await detector.analyze_decision(decision)
        if anomalies:
            for anomaly in anomalies:
                print(f"  🚨 Anomalia crítica: {anomaly['type']} - {anomaly['description']}")

    print("\n💬 Testando detecção de respostas inconsistentes...")

    # Simular respostas muito similares
    similar_responses = [
        "Olá! Como posso ajudar você hoje com programação?",
        "Oi! Como posso ajudar você hoje com programação?",
        "Olá! Como posso ajudar você hoje com programação?",
        "Oi! Como posso ajudar você hoje com programação?",
        "Olá! Como posso ajudar você hoje com programação?",
    ]

    for i, response in enumerate(similar_responses):
        context = {"user_mood": "curious", "topic": "programming"}
        anomalies = await detector.analyze_response(response, context)
        if anomalies:
            for anomaly in anomalies:
                print(f"  ⚠️  Anomalia de resposta: {anomaly['type']} - {anomaly['description']}")

    print("\n⚡ Testando detecção de degradação de performance...")

    # Simular degradação de performance
    performance_metrics = [
        {"response_time": 1.2, "error_rate": 0.01, "cpu_usage": 45},
        {"response_time": 1.1, "error_rate": 0.02, "cpu_usage": 42},
        {"response_time": 1.3, "error_rate": 0.01, "cpu_usage": 48},
        {"response_time": 2.1, "error_rate": 0.03, "cpu_usage": 65},  # Degradação
        {"response_time": 2.8, "error_rate": 0.05, "cpu_usage": 72},  # Piora
        {"response_time": 3.2, "error_rate": 0.08, "cpu_usage": 78},  # Crítica
    ]

    for metrics in performance_metrics:
        anomalies = await detector.analyze_performance(metrics)
        if anomalies:
            for anomaly in anomalies:
                print(f"  📉 Anomalia de performance: {anomaly['type']} - {anomaly['description']}")

    print("\n📈 Testando padrões de atividade incomuns...")

    # Simular atividade frenética
    import time
    for i in range(15):
        decision = {"type": "file_operation", "action": f"read_file_{i}"}
        anomalies = await detector.analyze_decision(decision)
        if anomalies:
            for anomaly in anomalies:
                print(f"  🔄 Anomalia de padrão: {anomaly['type']} - {anomaly['description']}")
        time.sleep(0.1)  # Simular alta frequência

    print("\n📊 Testando respostas de baixa qualidade...")

    # Simular respostas problemáticas
    poor_responses = [
        "Ok",  # Muito curta
        "A" * 6000,  # Muito longa
        "teste teste teste teste teste teste teste teste teste teste",  # Repetitiva
    ]

    for response in poor_responses:
        context = {"user_mood": "engaged", "topic": "debugging"}
        anomalies = await detector.analyze_response(response, context)
        if anomalies:
            for anomaly in anomalies:
                print(f"  📝 Anomalia de qualidade: {anomaly['type']} - {anomaly['description']}")

    print("\n📋 Gerando relatório de anomalias...")

    # Obter resumo
    summary = detector.get_anomaly_summary()

    print("\n📊 RESUMO FINAL:")
    print("=" * 50)
    print(f"Total de anomalias detectadas: {summary['total_anomalies']}")
    print(f"Tipos de anomalia: {summary['anomaly_types']}")
    print(f"Distribuição por severidade: {summary['severity_distribution']}")
    print(f"Alertas ativos: {len(summary['active_alerts'])}")

    print("\n🎯 Principais tipos de anomalia detectados:")
    for anomaly_type, count in summary['anomaly_types'].items():
        severity = "🔴 CRÍTICA" if any(a['severity'] == 'critical' for a in detector.detected_anomalies if a['anomaly']['type'] == anomaly_type) else \
                  "🟠 ALTA" if any(a['severity'] == 'high' for a in detector.detected_anomalies if a['anomaly']['type'] == anomaly_type) else \
                  "🟡 MÉDIA" if any(a['severity'] == 'medium' for a in detector.detected_anomalies if a['anomaly']['type'] == anomaly_type) else \
                  "🟢 BAIXA"
        print(f"  {severity}: {anomaly_type} ({count} ocorrências)")

    print("\n✅ Demo de detecção de anomalias concluído!")

if __name__ == "__main__":
    asyncio.run(demo_anomaly_detection())