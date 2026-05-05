#!/usr/bin/env python3
"""
Demo de Integração do Sistema de Ensino Adaptativo

Este demo mostra como usar o sistema de aprendizagem personalizada
integrado ao AgentService da Aura Sphere.
"""

import sys
from pathlib import Path

# Adicionar o caminho do bridge ao sys.path
root = Path(__file__).resolve().parent
bridge = root / "packages" / "bridge"
sys.path.insert(0, str(bridge))

from agent.service import get_agent_service


def demo_integracao_ensino():
    """Demonstra integração completa do sistema de ensino."""
    print("🎓 Demo: Integração do Sistema de Ensino Adaptativo com AgentService\n")

    # Obtém instância do serviço
    service = get_agent_service(user_id="demo-user", agent_id="aura-teacher")

    print("1. Verificando status inicial do sistema...")
    status = service.get_learning_status()
    print(f"   Modo aprendizado ativo: {status['learning_mode_active']}")
    print(f"   Tópicos disponíveis: {status['available_topics']}")
    print(f"   Capacidades: {', '.join(status['learning_capabilities'])}\n")

    print("2. Iniciando aprendizado de inglês...")
    result = service.start_adaptive_learning("inglês")
    print(f"   Status: {result['status']}")
    print(f"   Tópico: {result['topic']}")
    print(f"   Modo ensino: {result['learning_mode']}")
    print(f"   Lição inicial: {result['initial_lesson']['lesson']}\n")

    print("3. Recebendo primeira lição...")
    result = service.teach_topic("inglês")
    print(f"   Lição: {result['lesson']}")
    print(f"   Nível: {result['level']}")
    print(f"   Explicação: {result['explanation']}")
    print(f"   Exemplo: {result['example']}\n")

    print("4. Avaliando resposta do usuário...")
    user_response = "Eu entendi que preciso aprender vocabulário básico e frases simples."
    result = service.evaluate_learning_response("inglês", user_response)
    print(f"   Avaliação: {result['outcome']}")
    print(f"   Feedback: {result['feedback']}")
    print(f"   Nível atual: {result['current_level']}\n")

    print("5. Verificando progresso...")
    result = service.get_learning_progress("inglês")
    print(f"   Tópico: {result['topic']}")
    print(f"   Nível: {result['level']}")
    print(f"   Pontuação: {result['score']}")
    print(f"   Acertos: {result['correct']}")
    print(f"   Erros: {result['incorrect']}\n")

    print("6. Iniciando aprendizado de estilo...")
    result = service.start_adaptive_learning("como se vestir")
    print(f"   Status: {result['status']}")
    print(f"   Tópico: {result['topic']}\n")

    print("7. Ensinando estilo...")
    result = service.teach_topic("como se vestir")
    print(f"   Lição: {result['lesson']}")
    print(f"   Explicação: {result['explanation']}\n")

    print("8. Verificando status do sistema...")
    status = service.get_learning_status()
    print(f"   Modo aprendizado ativo: {status['learning_mode_active']}")
    print(f"   Tópico atual: {status['current_topic']}\n")

    print("9. Finalizando aprendizado...")
    result = service.stop_adaptive_learning()
    print(f"   Status: {result['status']}")
    print(f"   Tópico finalizado: {result['topic']}")
    print(f"   Modo ensino: {result['learning_mode']}\n")

    print("10. Status final do sistema...")
    status = service.get_learning_status()
    print(f"    Modo aprendizado ativo: {status['learning_mode_active']}")
    print(f"    Tópicos aprendidos: {status['available_topics']}\n")


def demo_multiplos_topicos():
    """Demonstra aprendizado de múltiplos tópicos."""
    print("📚 Demo: Múltiplos Tópicos via AgentService\n")

    service = get_agent_service(user_id="multi-user", agent_id="aura-multi-teacher")

    # Inglês
    print("1. Inglês:")
    service.start_adaptive_learning("inglês")
    result = service.teach_topic("inglês")
    print(f"   Lição: {result['lesson']}")
    service.stop_adaptive_learning()

    # Estilo
    print("\n2. Estilo:")
    service.start_adaptive_learning("como se vestir")
    result = service.teach_topic("como se vestir")
    print(f"   Lição: {result['lesson']}")
    service.stop_adaptive_learning()

    # Programação
    print("\n3. Programação:")
    service.start_adaptive_learning("programação")
    result = service.teach_topic("programação")
    print(f"   Lição: {result['lesson']}")
    service.stop_adaptive_learning()

    print("\n✅ Todos os tópicos demonstrados!\n")


def demo_auditoria():
    """Demonstra auditoria do sistema de ensino."""
    print("📊 Demo: Auditoria do Sistema de Ensino\n")

    service = get_agent_service(user_id="audit-user", agent_id="aura-audit-teacher")

    # Atividade de aprendizado
    service.start_adaptive_learning("inglês")
    service.teach_topic("inglês")
    service.evaluate_learning_response("inglês", "Resposta de teste")
    service.stop_adaptive_learning()

    # Ver relatório de sessão
    print("Relatório de sessão:")
    report = service.get_session_report()
    print(f"- Sessão ID: {report['session_id']}")
    print(f"- Total de tarefas: {report['total_tasks']}")
    print(f"- Tarefas completadas: {report['completed_tasks']}")

    print("\n✅ Auditoria demonstrada!\n")


def main():
    """Executa todos os demos de integração."""
    print("🚀 Sistema de Ensino Adaptativo - Integração com AgentService")
    print("=" * 60)

    try:
        demo_integracao_ensino()
        demo_multiplos_topicos()
        demo_auditoria()

        print("🎉 Todas as integrações testadas com sucesso!")
        print("\n💡 Como usar no código:")
        print("   from agent.service import get_agent_service")
        print("   service = get_agent_service()")
        print("   service.start_adaptive_learning('inglês')")
        print("   service.teach_topic('inglês')")
        print("   service.evaluate_learning_response('inglês', 'resposta')")
        print("   service.stop_adaptive_learning()")

    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()