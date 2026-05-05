#!/usr/bin/env python3
"""
Demo do Sistema de Evolução - Teste do pipeline completo de deploy controlado.
"""

import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from agent.evolution import EvolutionManager, AgentVersion

def demo_evolution_pipeline():
    """Demonstra o pipeline completo de evolução."""
    print("🚀 Demo: Sistema de Evolução da Aura Sphere")
    print("=" * 50)
    
    # Inicializar gerenciador de evolução
    evolution = EvolutionManager()
    
    print("📊 Versões atuais:")
    versions = evolution.list_versions()
    for v in versions:
        print(f"  - {v.version_id}: {v.description}")
    
    # Criar versão de teste
    print("\n🔧 Criando nova versão candidata...")
    test_version = evolution.add_version(
        description="Versão de teste com melhorias de performance",
        metrics={
            "quality_score": 8.0,
            "stability": 0.9,
            "security": 0.95,
            "performance": 0.85,
            "compatibility": 0.9,
            "errors": 0
        },
        metadata={
            "patch_code": """
def improved_function():
    return "Melhoria implementada"
""",
            "affected_files": ["agent/service.py"],
            "core_integrity_maintained": True,
            "compatibility_tests_passed": 5,
            "total_compatibility_tests": 5
        }
    )
    
    print(f"✅ Versão criada: {test_version.version_id}")
    
    # Código de teste
    test_code = """
# Teste da nova funcionalidade
result = improved_function()
print(f"Resultado: {result}")
assert result == "Melhoria implementada"
print("✅ Teste passou!")
"""
    
    # Executar pipeline de deploy
    print("\n🔄 Executando pipeline de deploy...")
    deploy_result = evolution.deploy_version(test_version, test_code, user_approval=False)
    
    print(f"📋 Resultado do deploy: {deploy_result['stage']}")
    if deploy_result['success']:
        print("✅ Deploy bem-sucedido!")
        print(f"Versão implantada: {deploy_result['deployed_version']}")
    else:
        print("❌ Deploy falhou:")
        for error in deploy_result['errors']:
            print(f"  - {error}")
    
    # Comparar versões
    print("\n⚖️ Comparação de versões:")
    best = evolution.choose_best_version()
    if best:
        comparison = evolution.compare_versions(test_version, best)
        print(f"Melhor versão: {comparison['better_version']}")
        print(f"Score {test_version.version_id}: {comparison['score_a']:.2f}")
        print(f"Score {best.version_id}: {comparison['score_b']:.2f}")
    
    # Score detalhado
    print("\n📈 Score detalhado da nova versão:")
    detailed = evolution.score_version_detailed(test_version)
    print(f"Score total: {detailed['total_score']:.2f}")
    for component, value in detailed['components'].items():
        print(f"  {component}: {value:.2f}")
    
    print("\n🎯 Demo concluída!")

if __name__ == "__main__":
    demo_evolution_pipeline()