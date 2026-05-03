#!/usr/bin/env python3
"""
Script para testar integrações com repositórios externos
"""

import asyncio
import sys
from pathlib import Path

# Adicionar caminho do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.bridge.agent.service import AgentService

async def test_integrations():
    """Testa todas as integrações disponíveis"""

    print("🧪 Iniciando testes de integração...")

    # Inicializar AgentService
    agent_service = AgentService()
    await agent_service.initialize()

    print("\n" + "="*50)
    print("📊 STATUS DAS INTEGRAÇÕES")
    print("="*50)

    # Testar OpenJarvis
    print("\n🤖 OpenJarvis Integration:")
    if agent_service.openjarvis_adapter.is_openjarvis_available():
        print("  ✅ OpenJarvis disponível")
        skills = agent_service.openjarvis_adapter.get_available_skills()
        print(f"  📚 Skills disponíveis: {len(skills)}")
        print(f"  🔧 Skills: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
    else:
        print("  ⚠️ OpenJarvis não disponível (usando fallback)")

    # Testar MemPalace
    print("\n🧠 MemPalace Integration:")
    if agent_service.mempalace_adapter.is_mempalace_available():
        print("  ✅ MemPalace disponível")
        wings = agent_service.mempalace_adapter.list_wings()
        print(f"  🏗️ Wings disponíveis: {len(wings)}")
        print(f"  🏛️ Wings: {', '.join(wings)}")
    else:
        print("  ⚠️ MemPalace não disponível (usando mock)")

    print("\n" + "="*50)
    print("🧪 TESTES FUNCIONAIS")
    print("="*50)

    # Teste de processamento criativo
    print("\n🎨 Teste de processamento criativo:")
    test_request = "Generate an image of a sunset over mountains"
    test_context = {
        "style": "realistic",
        "user_id": "test_user",
        "session_id": "test_session_001"
    }

    try:
        result = await agent_service.openjarvis_adapter.process_creative_request(
            test_request, test_context
        )
        print(f"  ✅ Processamento: {result['source']}")
        print(f"  📊 Sucesso: {result['success']}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

    # Teste de armazenamento de memória
    print("\n💾 Teste de armazenamento de memória:")
    test_conversation = {
        "session_id": "test_session_001",
        "timestamp": "2024-01-01T12:00:00Z",
        "user_input": test_request,
        "agent_response": "Image generated successfully",
        "context": test_context,
        "skills_used": ["image_generation"],
        "metadata": {"test": True}
    }

    try:
        stored = await agent_service.mempalace_adapter.store_conversation(test_conversation)
        print(f"  ✅ Armazenamento: {'Sucesso' if stored else 'Falhou'}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

    # Teste de busca de memória
    print("\n🔍 Teste de busca de memória:")
    try:
        results = await agent_service.mempalace_adapter.search_conversations("sunset")
        print(f"  ✅ Busca: {len(results)} resultados encontrados")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

    print("\n" + "="*50)
    print("✅ Testes concluídos!")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(test_integrations())
