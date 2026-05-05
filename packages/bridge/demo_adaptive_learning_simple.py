#!/usr/bin/env python3
"""
Demo Simplificado de Integração do Sistema de Ensino Adaptativo

Este demo mostra como usar o sistema de aprendizagem personalizada
integrado ao AgentService da Aura Sphere, sem dependências externas.
"""

import sys
from pathlib import Path

# Adicionar o caminho do bridge ao sys.path
root = Path(__file__).resolve().parent
bridge = root / "packages" / "bridge"
sys.path.insert(0, str(bridge))

from agent.learning.learning_controller import LearningController


def demo_ensino_simples():
    """Demonstra o sistema de ensino de forma independente."""
    print("🎓 Demo Simplificado: Sistema de Ensino Adaptativo\n")

    # Instancia o controlador de aprendizado
    controller = LearningController()

    print("1. Verificando status inicial...")
    print(f"   Modo aprendizado ativo: {controller.is_learning_active()}\n")

    print("2. Iniciando aprendizado de inglês...")
    result = controller.start_learning("inglês")
    print(f"   Status: {result['status']}")
    print(f"   Tópico: {result['topic']}")
    print(f"   Modo ensino: {result['learning_mode']}")
    print(f"   Lição inicial: {result['initial_lesson']['lesson']}\n")

    print("3. Recebendo primeira lição...")
    result = controller.teach("inglês")
    print(f"   Lição: {result['lesson']}")
    print(f"   Nível: {result['level']}")
    print(f"   Explicação: {result['explanation']}")
    print(f"   Exemplo: {result['example']}\n")

    print("4. Avaliando resposta do usuário...")
    user_response = "Eu entendi que preciso aprender vocabulário básico e frases simples."
    result = controller.evaluate("inglês", user_response)
    print(f"   Avaliação: {result['outcome']}")
    print(f"   Feedback: {result['feedback']}")
    print(f"   Nível atual: {result['current_level']}\n")

    print("5. Verificando progresso...")
    result = controller.progress("inglês")
    print(f"   Tópico: {result['topic']}")
    print(f"   Nível: {result['level']}")
    print(f"   Pontuação: {result['score']}")
    print(f"   Acertos: {result['correct']}")
    print(f"   Erros: {result['incorrect']}\n")

    print("6. Iniciando aprendizado de estilo...")
    result = controller.start_learning("como se vestir")
    print(f"   Status: {result['status']}")
    print(f"   Tópico: {result['topic']}\n")

    print("7. Ensinando estilo...")
    result = controller.teach("como se vestir")
    print(f"   Lição: {result['lesson']}")
    print(f"   Explicação: {result['explanation']}\n")

    print("8. Verificando se modo está ativo...")
    print(f"   Modo aprendizado ativo: {controller.is_learning_active()}\n")

    print("9. Finalizando aprendizado...")
    result = controller.stop_learning()
    print(f"   Status: {result['status']}")
    print(f"   Tópico finalizado: {result['topic']}")
    print(f"   Modo ensino: {result['learning_mode']}\n")

    print("10. Status final...")
    print(f"    Modo aprendizado ativo: {controller.is_learning_active()}\n")


def demo_multiplos_topicos():
    """Demonstra aprendizado de múltiplos tópicos."""
    print("📚 Demo: Múltiplos Tópicos Independentes\n")

    controller = LearningController()

    # Inglês
    print("1. Inglês:")
    controller.start_learning("inglês")
    result = controller.teach("inglês")
    print(f"   Lição: {result['lesson']}")
    controller.stop_learning()

    # Estilo
    print("\n2. Estilo:")
    controller.start_learning("como se vestir")
    result = controller.teach("como se vestir")
    print(f"   Lição: {result['lesson']}")
    controller.stop_learning()

    # Programação
    print("\n3. Programação:")
    controller.start_learning("programação")
    result = controller.teach("programação")
    print(f"   Lição: {result['lesson']}")
    controller.stop_learning()

    print("\n✅ Todos os tópicos demonstrados!\n")


def demo_persistencia():
    """Demonstra persistência de dados."""
    print("💾 Demo: Persistência de Dados\n")

    # Primeira sessão
    print("Sessão 1:")
    controller1 = LearningController()
    controller1.start_learning("inglês")
    controller1.evaluate("inglês", "Resposta correta sobre vocabulário")
    progress1 = controller1.progress("inglês")
    print(f"   Pontuação após sessão 1: {progress1['score']}")
    controller1.stop_learning()

    # Segunda sessão (deve carregar dados salvos)
    print("\nSessão 2:")
    controller2 = LearningController()
    progress2 = controller2.progress("inglês")
    score = progress2.get('score', 0)
    correct = progress2.get('correct', 0)
    print(f"   Pontuação carregada: {score}")
    print(f"   Acertos: {correct}")

    print("\n✅ Persistência demonstrada!\n")


def main():
    """Executa todos os demos simplificados."""
    print("🚀 Sistema de Ensino Adaptativo - Demo Simplificado")
    print("=" * 55)

    try:
        demo_ensino_simples()
        demo_multiplos_topicos()
        demo_persistencia()

        print("🎉 Todos os demos executados com sucesso!")
        print("\n💡 Como integrar com AgentService:")
        print("   # No AgentService, adicionar:")
        print("   from agent.learning.learning_controller import LearningController")
        print("   self.learning_controller = LearningController()")
        print("   ")
        print("   # Métodos públicos:")
        print("   def start_adaptive_learning(self, topic):")
        print("       return self.learning_controller.start_learning(topic)")
        print("   def teach_topic(self, topic):")
        print("       return self.learning_controller.teach(topic)")
        print("   def evaluate_learning_response(self, topic, response):")
        print("       return self.learning_controller.evaluate(topic, response)")
        print("   def stop_adaptive_learning(self):")
        print("       return self.learning_controller.stop_learning()")

    except Exception as e:
        print(f"❌ Erro no demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()