#!/usr/bin/env python3
"""
Demo do Sistema de Indexação de Memória
======================================

Demonstração das funcionalidades de indexação e busca semântica.
"""

import asyncio
import logging
from memory import MemoryIndexer, MemoryCategory

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_memory_indexing():
    """Demonstra o sistema de indexação de memória"""

    print("🚀 Iniciando demo do sistema de indexação de memória...")

    # Criar indexador
    indexer = MemoryIndexer("demo_memory_index.json")

    # Dados de exemplo para indexar
    sample_memories = [
        {
            'id': 'user_query_1',
            'content': 'Como posso criar uma função em Python para calcular fibonacci?',
            'metadata': {'source': 'user', 'type': 'question'}
        },
        {
            'id': 'system_response_1',
            'content': 'Aqui está uma função recursiva para calcular Fibonacci: def fibonacci(n): if n <= 1: return n else: return fibonacci(n-1) + fibonacci(n-2)',
            'metadata': {'source': 'system', 'type': 'code_response'}
        },
        {
            'id': 'error_log_1',
            'content': 'Erro: RecursionError: maximum recursion depth exceeded in comparison',
            'metadata': {'type': 'error', 'function': 'fibonacci'}
        },
        {
            'id': 'learning_1',
            'content': 'Aprendido: Funções recursivas podem causar stack overflow para valores grandes de n',
            'metadata': {'type': 'learning', 'topic': 'recursion'}
        },
        {
            'id': 'security_1',
            'content': 'Tentativa de acesso não autorizado detectada no endpoint /admin',
            'metadata': {'type': 'security', 'severity': 'high'}
        },
        {
            'id': 'event_1',
            'content': 'Sistema reiniciado devido a atualização de segurança',
            'metadata': {'type': 'system_event'}
        }
    ]

    print("\n📝 Indexando memórias de exemplo...")

    # Indexar memórias
    for memory in sample_memories:
        await indexer.index_memory(
            memory_id=memory['id'],
            content=memory['content'],
            metadata=memory['metadata']
        )
        print(f"✓ Indexada: {memory['id']}")

    print("\n🔍 Testando buscas...")

    # Teste 1: Busca por categoria
    print("\n1. Busca por categoria ERROR:")
    results = await indexer.search_memory("erro", category=MemoryCategory.ERROR, limit=5)
    for result in results:
        print(f"   - {result['id']}: {result['score']:.3f} (categoria: {result['category']})")

    # Teste 2: Busca geral por palavra-chave
    print("\n2. Busca geral por 'função':")
    results = await indexer.search_memory("função", limit=5)
    for result in results:
        print(f"   - {result['id']}: {result['score']:.3f} (categoria: {result['category']})")

    # Teste 3: Busca por código
    print("\n3. Busca por 'python':")
    results = await indexer.search_memory("python", limit=5)
    for result in results:
        print(f"   - {result['id']}: {result['score']:.3f} (categoria: {result['category']})")

    # Teste 4: Busca por segurança
    print("\n4. Busca por 'acesso':")
    results = await indexer.search_memory("acesso", limit=5)
    for result in results:
        print(f"   - {result['id']}: {result['score']:.3f} (categoria: {result['category']})")

    # Estatísticas
    print("\n📊 Estatísticas do índice:")
    stats = await indexer.get_memory_stats()
    print(f"   Total de entradas: {stats['total_entries']}")
    print(f"   Média de acessos por entrada: {stats['avg_accesses_per_entry']:.2f}")
    print(f"   Categorias: {stats['categories']}")
    print(f"   Top palavras-chave: {stats['top_keywords'][:5]}")

    # Simular acessos para testar relevância
    print("\n🔄 Simulando acessos para testar relevância...")
    for _ in range(3):
        indexer.update_memory_access('user_query_1')
        indexer.update_memory_access('system_response_1')

    print("\n5. Busca por 'fibonacci' após acessos simulados:")
    results = await indexer.search_memory("fibonacci", limit=5)
    for result in results:
        print(f"   - {result['id']}: {result['score']:.3f} (categoria: {result['category']})")

    # Limpeza
    print("\n🧹 Fazendo limpeza de entradas antigas...")
    await indexer.cleanup_old_entries(max_age_days=0)  # Remover tudo para demo

    print("\n✅ Demo concluída!")

if __name__ == "__main__":
    asyncio.run(demo_memory_indexing())