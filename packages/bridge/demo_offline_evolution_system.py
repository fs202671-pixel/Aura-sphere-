#!/usr/bin/env python3
"""
Demo do sistema de evolução offline e geração de variantes de código.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from agent.offline_scheduler import OfflineEvolutionScheduler, ExecutionMode
from agent.alternative_code_generator import AlternativeCodeGenerator
from agent.evolution import EvolutionManager


def demo_offline_evolution_system():
    print("🧠 Demo: Sistema de Evolução Offline e Geração de Códigos Alternativos")
    print("=" * 75)

    evolution_manager = EvolutionManager()
    scheduler = OfflineEvolutionScheduler(evolution_manager)
    generator = AlternativeCodeGenerator()

    print("🔧 Agendando tarefas de evolução offline...")
    scheduler.schedule_task(
        description="Gerar variação de arquitetura interna para teste offline",
        task_type="version_generation",
        priority=9
    )
    scheduler.schedule_task(
        description="Otimizar algoritmo de processamento de dados",
        task_type="optimization",
        priority=8
    )
    scheduler.schedule_task(
        description="Reorganizar módulos do agente para melhor modularidade",
        task_type="reorganization",
        priority=7
    )

    print("✅ Tarefas agendadas:")
    for task in scheduler.get_pending_tasks():
        print(f"  - {task['task_id']}: {task['description']} ({task['task_type']})")

    print("\n🚀 Colocando scheduler em modo EVOLUTION...")
    scheduler.set_execution_mode(ExecutionMode.EVOLUTION)
    scheduler.start_scheduler()

    print("⏱️ Aguardando execução das tarefas...")
    import time
    time.sleep(6)

    print("\n✅ Tarefas completadas:")
    for task in scheduler.get_completed_tasks():
        print(f"  - {task['task_id']}: {task['description']} (status={task['status']})")

    print("\n💡 Gerando variantes de código alternativo...")
    variant_a = generator.generate_optimization_variant(
        module_name="agent.service",
        description="Melhoria de performance com cache e algoritmo otimizado"
    )
    variant_b = generator.generate_refactor_variant(
        module_name="agent.service",
        description="Refatoração para separar responsabilidades e melhorar manutenção"
    )

    print(f"  - Variante A: {variant_a.variant_id} ({variant_a.variant_type})")
    print(f"  - Variante B: {variant_b.variant_id} ({variant_b.variant_type})")

    comparison = generator.compare_variants(variant_a, variant_b)
    print("\n⚖️ Comparação de variantes:")
    print(f"  {comparison['recommendation']}")

    print("\n🎯 Demo concluída!")


if __name__ == '__main__':
    demo_offline_evolution_system()
