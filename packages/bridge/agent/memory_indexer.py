"""
Módulo de Indexação de Memória - Indexação semântica de memórias

Este módulo implementa um sistema de indexação semântica para
memórias, permitindo buscas eficientes por similaridade.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import hashlib
import re
from collections import defaultdict


class MemoryType(Enum):
    """Tipos de memória indexáveis."""
    CONVERSATION = "conversation"
    DECISION = "decision"
    ERROR = "error"
    LEARNING = "learning"
    USER_PREFERENCE = "user_preference"
    SYSTEM_EVENT = "system_event"


class SemanticIndex:
    """
    Índice semântico para uma memória.
    """

    def __init__(self, memory_id: str, content: str, memory_type: MemoryType,
                 tags: List[str] = None, metadata: Dict[str, Any] = None):
        self.memory_id = memory_id
        self.content = content
        self.memory_type = memory_type
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()

        # Índice semântico
        self.keywords = self._extract_keywords()
        self.semantic_vector = self._generate_semantic_vector()
        self.similarity_score = 0.0

    def _extract_keywords(self) -> List[str]:
        """Extrai palavras-chave do conteúdo."""
        # Implementação simplificada - em produção usaria NLP mais avançado
        content_lower = self.content.lower()

        # Remover pontuação
        content_clean = re.sub(r'[^\w\s]', ' ', content_lower)

        # Palavras comuns a ignorar
        stop_words = {
            'a', 'o', 'as', 'os', 'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na',
            'nos', 'nas', 'por', 'para', 'com', 'sem', 'sobre', 'entre', 'até',
            'e', 'ou', 'mas', 'que', 'como', 'quando', 'onde', 'porque', 'se',
            'não', 'sim', 'mais', 'menos', 'muito', 'pouco', 'todo', 'toda',
            'todos', 'todas', 'este', 'esta', 'estes', 'estas', 'esse', 'essa',
            'isso', 'isto', 'aquele', 'aquela', 'aqueles', 'aquelas'
        }

        words = content_clean.split()
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        # Adicionar tags como keywords
        keywords.extend(self.tags)

        return list(set(keywords))  # Remover duplicatas

    def _generate_semantic_vector(self) -> Dict[str, float]:
        """Gera vetor semântico simplificado."""
        # Implementação básica - em produção usaria embeddings reais
        vector = {}

        # Frequência de termos
        for keyword in self.keywords:
            vector[keyword] = vector.get(keyword, 0) + 1

        # Normalizar
        total = sum(vector.values())
        if total > 0:
            for key in vector:
                vector[key] /= total

        return vector

    def calculate_similarity(self, query_vector: Dict[str, float]) -> float:
        """Calcula similaridade com um vetor de consulta."""
        # Similaridade de cosseno simplificada
        dot_product = 0.0
        norm_a = 0.0
        norm_b = 0.0

        all_keys = set(self.semantic_vector.keys()) | set(query_vector.keys())

        for key in all_keys:
            a_val = self.semantic_vector.get(key, 0)
            b_val = query_vector.get(key, 0)

            dot_product += a_val * b_val
            norm_a += a_val ** 2
            norm_b += b_val ** 2

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / ((norm_a ** 0.5) * (norm_b ** 0.5))


class MemoryIndexer:
    """
    Indexador semântico de memórias.

    Funcionalidades:
    - Indexação automática de novas memórias
    - Busca semântica por similaridade
    - Filtragem por tipo e tags
    - Recomendação de memórias relacionadas
    - Manutenção e otimização de índices
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.index_dir = data_dir / "memory_index"
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.index_dir / "semantic_index.json"
        self.metadata_file = self.index_dir / "index_metadata.json"

        self.indices: Dict[str, SemanticIndex] = {}
        self.metadata: Dict[str, Any] = {}

        # Estatísticas de indexação
        self.stats = {
            "total_memories": 0,
            "total_keywords": 0,
            "index_size_mb": 0.0,
            "last_indexed": None,
            "search_count": 0
        }

        self._load_index()

    def index_memory(self, memory_id: str, content: str, memory_type: MemoryType,
                    tags: List[str] = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Indexa uma nova memória.
        """

        try:
            # Criar índice semântico
            index = SemanticIndex(
                memory_id=memory_id,
                content=content,
                memory_type=memory_type,
                tags=tags,
                metadata=metadata
            )

            # Armazenar índice
            self.indices[memory_id] = index

            # Atualizar estatísticas
            self.stats["total_memories"] = len(self.indices)
            self.stats["total_keywords"] += len(index.keywords)
            self.stats["last_indexed"] = datetime.now().isoformat()

            # Salvar índice
            self._save_index()

            return True

        except Exception as e:
            print(f"Error indexing memory {memory_id}: {e}")
            return False

    def search_similar(self, query: str, limit: int = 10,
                      memory_type: MemoryType = None,
                      tags: List[str] = None,
                      min_similarity: float = 0.1) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Busca memórias similares à consulta.
        """

        # Gerar vetor de consulta
        query_vector = self._generate_query_vector(query)

        # Calcular similaridade para todos os índices
        results = []
        for memory_id, index in self.indices.items():
            # Filtrar por tipo se especificado
            if memory_type and index.memory_type != memory_type:
                continue

            # Filtrar por tags se especificadas
            if tags and not any(tag in index.tags for tag in tags):
                continue

            # Calcular similaridade
            similarity = index.calculate_similarity(query_vector)

            if similarity >= min_similarity:
                results.append((
                    memory_id,
                    similarity,
                    {
                        "type": index.memory_type.value,
                        "tags": index.tags,
                        "content_preview": index.content[:200] + "..." if len(index.content) > 200 else index.content,
                        "metadata": index.metadata
                    }
                ))

        # Ordenar por similaridade (decrescente)
        results.sort(key=lambda x: x[1], reverse=True)

        # Limitar resultados
        results = results[:limit]

        # Atualizar estatísticas
        self.stats["search_count"] += 1

        return results

    def find_related_memories(self, memory_id: str, limit: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Encontra memórias relacionadas a uma memória específica.
        """

        if memory_id not in self.indices:
            return []

        target_index = self.indices[memory_id]

        # Usar o vetor semântico da memória alvo como consulta
        return self.search_similar(
            query=" ".join(target_index.keywords),
            limit=limit + 1,  # +1 para excluir a própria memória
            memory_type=target_index.memory_type
        )[1:]  # Excluir a primeira (própria memória)

    def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de indexação."""

        # Calcular distribuição por tipo
        type_distribution = defaultdict(int)
        for index in self.indices.values():
            type_distribution[index.memory_type.value] += 1

        # Calcular tamanho do índice
        self.stats["index_size_mb"] = len(json.dumps(self._serialize_indices()).encode('utf-8')) / (1024 * 1024)

        return {
            **self.stats,
            "type_distribution": dict(type_distribution),
            "avg_keywords_per_memory": self.stats["total_keywords"] / max(self.stats["total_memories"], 1)
        }

    def remove_memory(self, memory_id: str) -> bool:
        """
        Remove uma memória do índice.
        """

        if memory_id in self.indices:
            index = self.indices[memory_id]
            self.stats["total_keywords"] -= len(index.keywords)
            del self.indices[memory_id]
            self.stats["total_memories"] = len(self.indices)
            self._save_index()
            return True

        return False

    def optimize_index(self) -> Dict[str, Any]:
        """
        Otimiza o índice removendo duplicatas e compactando.
        """

        # Implementação simplificada - em produção seria mais sofisticada
        original_count = len(self.indices)

        # Remover índices sem conteúdo
        to_remove = []
        for memory_id, index in self.indices.items():
            if not index.content.strip():
                to_remove.append(memory_id)

        for memory_id in to_remove:
            del self.indices[memory_id]

        # Recalcular estatísticas
        self.stats["total_memories"] = len(self.indices)
        self.stats["total_keywords"] = sum(len(index.keywords) for index in self.indices.values())

        self._save_index()

        return {
            "original_memories": original_count,
            "final_memories": len(self.indices),
            "removed_memories": len(to_remove),
            "optimization_ratio": len(self.indices) / max(original_count, 1)
        }

    def _generate_query_vector(self, query: str) -> Dict[str, float]:
        """Gera vetor semântico para consulta."""
        # Implementação simplificada similar ao índice
        query_lower = query.lower()
        query_clean = re.sub(r'[^\w\s]', ' ', query_lower)

        stop_words = {
            'a', 'o', 'as', 'os', 'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na',
            'nos', 'nas', 'por', 'para', 'com', 'sem', 'sobre', 'entre', 'até'
        }

        words = query_clean.split()
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        # Criar vetor de frequência
        vector = {}
        for keyword in keywords:
            vector[keyword] = vector.get(keyword, 0) + 1

        # Normalizar
        total = sum(vector.values())
        if total > 0:
            for key in vector:
                vector[key] /= total

        return vector

    def _serialize_indices(self) -> Dict[str, Dict[str, Any]]:
        """Serializa índices para salvamento."""
        serialized = {}
        for memory_id, index in self.indices.items():
            serialized[memory_id] = {
                "memory_id": index.memory_id,
                "content": index.content,
                "memory_type": index.memory_type.value,
                "tags": index.tags,
                "metadata": index.metadata,
                "created_at": index.created_at,
                "keywords": index.keywords,
                "semantic_vector": index.semantic_vector
            }
        return serialized

    def _deserialize_indices(self, data: Dict[str, Dict[str, Any]]) -> None:
        """Desserializa índices do salvamento."""
        for memory_id, index_data in data.items():
            # Recriar SemanticIndex
            index = SemanticIndex(
                memory_id=index_data["memory_id"],
                content=index_data["content"],
                memory_type=MemoryType(index_data["memory_type"]),
                tags=index_data.get("tags", []),
                metadata=index_data.get("metadata", {})
            )

            # Restaurar dados calculados
            index.created_at = index_data.get("created_at", index.created_at)
            index.keywords = index_data.get("keywords", index.keywords)
            index.semantic_vector = index_data.get("semantic_vector", index.semantic_vector)

            self.indices[memory_id] = index

    def _load_index(self) -> None:
        """Carrega índice do disco."""

        # Carregar índices
        if self.index_file.exists():
            try:
                index_data = json.loads(self.index_file.read_text(encoding='utf-8'))
                self._deserialize_indices(index_data)
            except Exception:
                self.indices = {}

        # Carregar metadados
        if self.metadata_file.exists():
            try:
                self.metadata = json.loads(self.metadata_file.read_text(encoding='utf-8'))
                # Atualizar stats se disponível
                if "stats" in self.metadata:
                    self.stats.update(self.metadata["stats"])
            except Exception:
                self.metadata = {}

    def _save_index(self) -> None:
        """Salva índice no disco."""

        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Salvar índices
        serialized_indices = self._serialize_indices()
        self.index_file.write_text(
            json.dumps(serialized_indices, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Salvar metadados
        self.metadata["stats"] = self.stats
        self.metadata["last_updated"] = datetime.now().isoformat()

        self.metadata_file.write_text(
            json.dumps(self.metadata, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
