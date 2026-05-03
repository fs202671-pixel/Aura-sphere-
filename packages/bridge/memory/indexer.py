"""
Memory Indexer - Sistema de Indexação de Memória
===============================================

Sistema de indexação e busca semântica para memória estruturada.
Características:
- Indexação por categorias (usuário, sistema, código, eventos)
- Busca semântica com embeddings
- Categorização automática de conteúdo
- Busca por similaridade
"""

import asyncio
import json
import os
import time
import hashlib
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class MemoryCategory(Enum):
    """Categorias de memória"""
    USER = "user"           # Interações com usuário
    SYSTEM = "system"       # Eventos do sistema
    CODE = "code"           # Código gerado/modificado
    EVENT = "event"         # Eventos diversos
    LEARNING = "learning"   # Aprendizado da IA
    ERROR = "error"         # Erros e falhas
    SECURITY = "security"   # Eventos de segurança

@dataclass
class MemoryIndex:
    """Índice de entrada de memória"""
    id: str
    category: MemoryCategory
    content_hash: str
    keywords: Set[str]
    semantic_vector: Optional[List[float]] = None
    timestamp: float = 0.0
    access_count: int = 0
    last_access: float = 0.0
    relevance_score: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def update_access(self):
        """Atualiza estatísticas de acesso"""
        self.access_count += 1
        self.last_access = time.time()

    def calculate_relevance(self, query_keywords: Set[str]) -> float:
        """Calcula relevância baseada em palavras-chave"""
        if not self.keywords:
            return 0.0

        intersection = len(self.keywords.intersection(query_keywords))
        union = len(self.keywords.union(query_keywords))

        if union == 0:
            return 0.0

        # Jaccard similarity
        jaccard = intersection / union

        # Boost por frequência de acesso
        access_boost = min(self.access_count / 10.0, 2.0)

        # Decay por tempo (mais recente = mais relevante)
        time_decay = max(0.1, 1.0 - (time.time() - self.last_access) / (30 * 24 * 3600))  # 30 dias

        return jaccard * access_boost * time_decay

class MemoryIndexer:
    """
    Sistema de indexação de memória com busca semântica

    Funcionalidades:
    - Indexação automática por categoria
    - Busca por palavras-chave
    - Busca semântica (se embeddings disponíveis)
    - Categorização inteligente de conteúdo
    - Estatísticas de acesso e relevância
    """

    def __init__(self, index_path: str = "memory_index.json", embedding_service=None):
        self.index_path = index_path
        self.embedding_service = embedding_service
        self.index: Dict[str, MemoryIndex] = {}
        self.category_index: Dict[MemoryCategory, Set[str]] = defaultdict(set)
        self.keyword_index: Dict[str, Set[str]] = defaultdict(set)

        # Carregar índice existente
        self._load_index()

        logger.info(f"MemoryIndexer initialized with {len(self.index)} indexed entries")

    def _load_index(self):
        """Carrega índice do disco"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for entry_data in data.get('entries', []):
                    category = MemoryCategory(entry_data['category'])
                    index_entry = MemoryIndex(
                        id=entry_data['id'],
                        category=category,
                        content_hash=entry_data['content_hash'],
                        keywords=set(entry_data['keywords']),
                        semantic_vector=entry_data.get('semantic_vector'),
                        timestamp=entry_data['timestamp'],
                        access_count=entry_data['access_count'],
                        last_access=entry_data['last_access'],
                        relevance_score=entry_data['relevance_score'],
                        metadata=entry_data.get('metadata', {})
                    )

                    self.index[entry_data['id']] = index_entry
                    self.category_index[category].add(entry_data['id'])

                    # Reconstruir índice de palavras-chave
                    for keyword in index_entry.keywords:
                        self.keyword_index[keyword].add(entry_data['id'])

                logger.info(f"Loaded {len(self.index)} indexed entries")

            except Exception as e:
                logger.error(f"Failed to load memory index: {e}")

    def _save_index(self):
        """Salva índice no disco"""
        try:
            data = {
                'entries': [],
                'metadata': {
                    'total_entries': len(self.index),
                    'categories': {cat.value: len(ids) for cat, ids in self.category_index.items()},
                    'last_updated': time.time()
                }
            }

            for entry in self.index.values():
                entry_data = asdict(entry)
                entry_data['category'] = entry.category.value
                entry_data['keywords'] = list(entry.keywords)
                data['entries'].append(entry_data)

            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to save memory index: {e}")

    def _extract_keywords(self, content: str) -> Set[str]:
        """Extrai palavras-chave do conteúdo"""
        # Normalizar texto
        content = content.lower()

        # Remover pontuação
        content = re.sub(r'[^\w\s]', ' ', content)

        # Tokenizar
        words = content.split()

        # Filtrar palavras comuns e curtas
        stop_words = {'de', 'da', 'do', 'em', 'no', 'na', 'a', 'o', 'e', 'ou', 'mas', 'por', 'para', 'com', 'sem'}
        keywords = {word for word in words if len(word) > 2 and word not in stop_words}

        return keywords

    def _categorize_content(self, content: str, metadata: Dict[str, Any]) -> MemoryCategory:
        """Categoriza conteúdo automaticamente"""
        content_lower = content.lower()

        # Verificar metadados primeiro
        if metadata.get('source') == 'user':
            return MemoryCategory.USER
        elif metadata.get('type') == 'error':
            return MemoryCategory.ERROR
        elif metadata.get('type') == 'security':
            return MemoryCategory.SECURITY

        # Análise de conteúdo
        if any(keyword in content_lower for keyword in ['def ', 'class ', 'import ', 'function', 'code']):
            return MemoryCategory.CODE
        elif any(keyword in content_lower for keyword in ['error', 'exception', 'failed', 'crash']):
            return MemoryCategory.ERROR
        elif any(keyword in content_lower for keyword in ['login', 'auth', 'security', 'attack']):
            return MemoryCategory.SECURITY
        elif any(keyword in content_lower for keyword in ['learn', 'training', 'model', 'ai']):
            return MemoryCategory.LEARNING
        elif metadata.get('role') == 'system':
            return MemoryCategory.SYSTEM
        else:
            return MemoryCategory.EVENT

    async def index_memory(self, memory_id: str, content: str, metadata: Dict[str, Any] = None):
        """
        Indexa uma entrada de memória

        Args:
            memory_id: ID único da entrada
            content: Conteúdo textual da memória
            metadata: Metadados adicionais
        """
        if metadata is None:
            metadata = {}

        # Verificar se já existe
        if memory_id in self.index:
            logger.debug(f"Memory entry {memory_id} already indexed")
            return

        # Extrair palavras-chave
        keywords = self._extract_keywords(content)

        # Categorizar
        category = self._categorize_content(content, metadata)

        # Calcular hash do conteúdo
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Gerar embedding semântico (se disponível)
        semantic_vector = None
        if self.embedding_service:
            try:
                semantic_vector = await self.embedding_service.generate_embedding(content)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for {memory_id}: {e}")

        # Criar entrada de índice
        index_entry = MemoryIndex(
            id=memory_id,
            category=category,
            content_hash=content_hash,
            keywords=keywords,
            semantic_vector=semantic_vector,
            timestamp=time.time(),
            metadata=metadata
        )

        # Adicionar aos índices
        self.index[memory_id] = index_entry
        self.category_index[category].add(memory_id)

        for keyword in keywords:
            self.keyword_index[keyword].add(memory_id)

        # Salvar
        self._save_index()

        logger.debug(f"Indexed memory entry: {memory_id} (category: {category.value})")

    async def search_memory(self, query: str, category: MemoryCategory = None,
                          limit: int = 10, semantic_search: bool = False) -> List[Dict[str, Any]]:
        """
        Busca entradas de memória

        Args:
            query: Consulta de busca
            category: Filtrar por categoria (opcional)
            limit: Número máximo de resultados
            semantic_search: Usar busca semântica se disponível

        Returns:
            Lista de resultados com scores de relevância
        """
        query_keywords = self._extract_keywords(query)
        results = []

        # Filtrar por categoria se especificada
        candidate_ids = set()
        if category:
            candidate_ids = self.category_index.get(category, set())
        else:
            candidate_ids = set(self.index.keys())

        # Busca semântica (se disponível)
        if semantic_search and self.embedding_service:
            try:
                query_vector = await self.embedding_service.generate_embedding(query)

                for memory_id in candidate_ids:
                    entry = self.index.get(memory_id)
                    if not entry or not entry.semantic_vector:
                        continue

                    # Calcular similaridade coseno
                    similarity = self._cosine_similarity(query_vector, entry.semantic_vector)

                    # Combinar com relevância baseada em keywords
                    keyword_relevance = entry.calculate_relevance(query_keywords)
                    combined_score = (similarity * 0.7) + (keyword_relevance * 0.3)

                    results.append({
                        'id': memory_id,
                        'score': combined_score,
                        'category': entry.category.value,
                        'metadata': entry.metadata
                    })

            except Exception as e:
                logger.warning(f"Semantic search failed: {e}")
                semantic_search = False

        # Busca por palavras-chave (fallback ou combinação)
        if not semantic_search:
            for memory_id in candidate_ids:
                entry = self.index.get(memory_id)
                if not entry:
                    continue

                relevance = entry.calculate_relevance(query_keywords)
                if relevance > 0:
                    results.append({
                        'id': memory_id,
                        'score': relevance,
                        'category': entry.category.value,
                        'metadata': entry.metadata
                    })

        # Ordenar por score e limitar
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade do cosseno entre dois vetores"""
        import math

        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do índice de memória"""
        total_entries = len(self.index)
        category_stats = {cat.value: len(ids) for cat, ids in self.category_index.items()}

        # Estatísticas de acesso
        total_accesses = sum(entry.access_count for entry in self.index.values())
        avg_accesses = total_accesses / max(total_entries, 1)

        # Palavras-chave mais frequentes
        keyword_freq = {}
        for keyword, ids in self.keyword_index.items():
            keyword_freq[keyword] = len(ids)

        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'total_entries': total_entries,
            'categories': category_stats,
            'avg_accesses_per_entry': avg_accesses,
            'top_keywords': top_keywords,
            'semantic_search_available': self.embedding_service is not None
        }

    async def cleanup_old_entries(self, max_age_days: int = 90):
        """Remove entradas antigas do índice"""
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        old_ids = []

        for memory_id, entry in self.index.items():
            if entry.timestamp < cutoff_time and entry.access_count == 0:
                old_ids.append(memory_id)

        for memory_id in old_ids:
            entry = self.index[memory_id]
            self.category_index[entry.category].discard(memory_id)

            for keyword in entry.keywords:
                self.keyword_index[keyword].discard(memory_id)

            del self.index[memory_id]

        if old_ids:
            self._save_index()
            logger.info(f"Cleaned up {len(old_ids)} old index entries")

    def update_memory_access(self, memory_id: str):
        """Atualiza estatísticas de acesso de uma entrada"""
        if memory_id in self.index:
            self.index[memory_id].update_access()
            self._save_index()