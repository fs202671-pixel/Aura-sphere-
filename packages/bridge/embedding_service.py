"""
Embedding Service - Gera e busca por embeddings semânticos
Usa sentence-transformers para criar representações vetoriais de texto
"""

import os
import numpy as np
from typing import List, Optional
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class EmbeddingService:
    """Serviço para geração e busca de embeddings semânticos"""
    
    def __init__(self, model_name: str = None):
        """
        Inicializar serviço de embeddings
        
        Args:
            model_name: Nome do modelo sentence-transformers
                       Default: "sentence-transformers/all-MiniLM-L6-v2"
        """
        self.model_name = model_name or os.getenv(
            "EMBEDDINGS_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        
        if SentenceTransformer is None:
            self.model = None
            print(
                "Aviso: sentence-transformers não está instalado. "
                "Buscas semânticas serão desabilitadas e retornos serão baseados em fallback local."
            )
            return
        
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar modelo {self.model_name}: {str(e)}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Gerar embedding para um texto
        
        Args:
            text: Texto para embeddingg
            
        Returns:
            Lista de floats representando o embedding
        """
        if not text or not text.strip():
            # Retornar embedding vazio se texto está vazio
            return [0.0] * 384  # Dimensão padrão do MiniLM

        if self.model is None:
            # Sem modelo de embeddings disponível
            return [0.0] * 384
        
        try:
            embedding = self.model.encode(text.strip(), convert_to_tensor=False)
            return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        except Exception as e:
            print(f"Erro ao gerar embedding: {str(e)}")
            return [0.0] * 384
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Gerar embeddings para múltiplos textos
        
        Args:
            texts: Lista de textos
            batch_size: Tamanho do lote para processamento
            
        Returns:
            Lista de embeddings (lista de listas de floats)
        """
        if not texts:
            return []

        if self.model is None:
            return [[0.0] * 384 for _ in texts]
        
        try:
            embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_tensor=False)
            return [e.tolist() if hasattr(e, 'tolist') else list(e) for e in embeddings]
        except Exception as e:
            print(f"Erro ao gerar embeddings em batch: {str(e)}")
            return [[0.0] * 384 for _ in texts]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcular similaridade cosseno entre dois vetores
        
        Args:
            vec1: Primeiro vetor
            vec2: Segundo vetor
            
        Returns:
            Score de similaridade entre 0 e 1
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def search_similar(
        self, 
        query: str, 
        candidates: List[tuple],  # (id, embedding, content)
        top_k: int = 5,
        threshold: float = 0.3
    ) -> List[dict]:
        """
        Buscar textos similares a uma query
        
        Args:
            query: Texto da busca
            candidates: Lista de (id, embedding, content)
            top_k: Número de resultados a retornar
            threshold: Score mínimo de similaridade
            
        Returns:
            Lista de resultados ordenados por similarity score
        """
        query_embedding = self.embed_text(query)
        
        results = []
        for item_id, embedding, content in candidates:
            similarity = self.cosine_similarity(query_embedding, embedding)
            if similarity >= threshold:
                results.append({
                    "id": item_id,
                    "similarity": similarity,
                    "content": content
                })
        
        # Ordenar por similaridade (descending)
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]


def get_embedding_service() -> EmbeddingService:
    """Factory para obter instância de EmbeddingService"""
    return EmbeddingService()
