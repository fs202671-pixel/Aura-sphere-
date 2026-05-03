#!/usr/bin/env python3
"""
Demo do Sistema de Interpretação de Intenção
===========================================

Demonstração das funcionalidades de interpretação de intenções do usuário.
"""

import asyncio
import logging
from pathlib import Path
from agent.intent_interpreter import IntentInterpreter, IntentType, RiskLevel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_intent_interpretation():
    """Demonstra o sistema de interpretação de intenção."""

    print("🧠 Iniciando demo do sistema de interpretação de intenção...")

    # Criar diretório de dados
    data_dir = Path("demo_intent_data")
    data_dir.mkdir(exist_ok=True)

    # Inicializar interpretador
    interpreter = IntentInterpreter(data_dir)

    print("\n📝 Testando interpretação de comandos diretos...")

    # Testar comandos diretos
    direct_commands = [
        "Crie uma função para calcular fibonacci",
        "Execute o script de teste",
        "Delete o arquivo temporário",
        "Modifique a configuração do banco de dados",
    ]

    for command in direct_commands:
        intent = interpreter.interpret(command)
        print(f"  Comando: '{command}'")
        print(f"    Tipo: {intent.intent_type.value}")
        print(f"    Confiança: {intent.confidence:.2f}")
        print(f"    Risco: {intent.risk_level.value}")
        print(f"    Confirmação necessária: {intent.requires_confirmation}")
        if intent.action:
            print(f"    Ação: {intent.action}")
        print()

    print("\n💡 Testando interpretação de sugestões...")

    # Testar sugestões
    suggestions = [
        "Que tal implementar um sistema de cache?",
        "Talvez você poderia otimizar essa função",
        "Considere usar async/await aqui",
        "Seria bom adicionar validação de entrada",
    ]

    for suggestion in suggestions:
        intent = interpreter.interpret(suggestion)
        print(f"  Sugestão: '{suggestion}'")
        print(f"    Tipo: {intent.intent_type.value}")
        print(f"    Confiança: {intent.confidence:.2f}")
        print(f"    Risco: {intent.risk_level.value}")
        print()

    print("\n❓ Testando interpretação de perguntas...")

    # Testar perguntas
    questions = [
        "Como funciona essa função?",
        "Qual é a melhor prática para tratamento de erros?",
        "Onde está definido esse parâmetro?",
        "Por que o teste está falhando?",
    ]

    for question in questions:
        intent = interpreter.interpret(question)
        print(f"  Pergunta: '{question}'")
        print(f"    Tipo: {intent.intent_type.value}")
        print(f"    Confiança: {intent.confidence:.2f}")
        print()

    print("\n⚠️  Testando detecção de ambiguidades...")

    # Testar comandos ambíguos
    ambiguous_commands = [
        "Talvez delete esse arquivo ou não",
        "Pode ser que a função precise ser alterada",
        "Não sei se devemos implementar isso",
        "Qualquer uma das opções pode funcionar",
    ]

    for command in ambiguous_commands:
        intent = interpreter.interpret(command)
        print(f"  Comando ambíguo: '{command}'")
        print(f"    Tipo: {intent.intent_type.value}")
        print(f"    Confiança: {intent.confidence:.2f}")
        print(f"    Ambigüidades: {len(intent.ambiguities)}")
        for ambiguity in intent.ambiguities[:2]:  # Mostrar até 2
            print(f"      - {ambiguity}")
        print()

    print("\n🚨 Testando avaliação de risco...")

    # Testar comandos de diferentes níveis de risco
    risk_commands = [
        ("Mostre o conteúdo do arquivo", RiskLevel.LOW),
        ("Crie um novo arquivo de configuração", RiskLevel.MEDIUM),
        ("Delete todos os arquivos de log", RiskLevel.HIGH),
        ("Formate o disco rígido", RiskLevel.CRITICAL),
    ]

    for command, expected_risk in risk_commands:
        intent = interpreter.interpret(command)
        print(f"  Comando: '{command}'")
        print(f"    Risco detectado: {intent.risk_level.value}")
        print(f"    Risco esperado: {expected_risk.value}")
        print(f"    Confirmação necessária: {intent.requires_confirmation}")
        print()

    print("\n✅ Testando validação de segurança...")

    # Testar validação de segurança
    test_intents = [
        ("Crie uma função simples", "Deveria ser seguro"),
        ("Delete o banco de dados", "Deveria requerer confirmação"),
        ("O que é uma variável?", "Pergunta segura"),
    ]

    for command, description in test_intents:
        intent = interpreter.interpret(command)
        is_safe, reason = interpreter.validate_intent_safety(intent)
        print(f"  Comando: '{command}'")
        print(f"    Descrição: {description}")
        print(f"    Seguro: {is_safe}")
        if reason:
            print(f"    Motivo: {reason}")
        print()

    print("\n📊 Gerando relatório de interpretações...")

    # Obter histórico
    history = interpreter.get_interpretation_history(10)

    print("\n📋 RESUMO DAS INTERPRETAÇÕES:")
    print("=" * 50)
    print(f"Total de interpretações realizadas: {len(history)}")

    # Contar tipos
    type_counts = {}
    risk_counts = {}
    confirmation_count = 0

    for entry in history:
        intent_type = entry['intent_type']
        risk_level = entry['risk_level']
        requires_conf = entry['requires_confirmation']

        type_counts[intent_type] = type_counts.get(intent_type, 0) + 1
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        if requires_conf:
            confirmation_count += 1

    print(f"Distribuição por tipo de intenção: {type_counts}")
    print(f"Distribuição por nível de risco: {risk_counts}")
    print(f"Interpretações que requerem confirmação: {confirmation_count}")

    print("\n🎯 Exemplos de interpretações bem-sucedidas:")
    successful = [h for h in history if h['confidence'] >= 0.7][:3]
    for entry in successful:
        print(f"  '{entry['user_input'][:50]}...' → {entry['intent_type']} (confiança: {entry['confidence']:.2f})")

    print("\n⚠️  Exemplos que necessitam esclarecimento:")
    needs_clarification = [h for h in history if h.get('ambiguities', [])][:2]
    for entry in needs_clarification:
        print(f"  '{entry['user_input'][:50]}...' → {len(entry.get('ambiguities', []))} ambiguidades detectadas")

    print("\n✅ Demo de interpretação de intenção concluído!")

if __name__ == "__main__":
    asyncio.run(demo_intent_interpretation())