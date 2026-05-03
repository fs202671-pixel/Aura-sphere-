"""
Módulo de Gerenciamento de Conteúdo Multimodal - Gestão integrada de conteúdo

Este módulo implementa gerenciamento abrangente de conteúdo multimodal
incluindo texto, imagens, vídeos, áudio e outros tipos de mídia.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import hashlib
import mimetypes
import base64
from io import BytesIO


class MediaType(Enum):
    """Tipos de mídia suportados."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    CODE = "code"
    STRUCTURED_DATA = "structured_data"


class ContentMetadata:
    """
    Metadados de um item de conteúdo.
    """

    def __init__(self, content_id: str, media_type: MediaType,
                 title: str = "", description: str = "",
                 tags: List[str] = None, source: str = "",
                 created_by: str = "system"):
        self.content_id = content_id
        self.media_type = media_type
        self.title = title
        self.description = description
        self.tags = tags or []
        self.source = source
        self.created_by = created_by

        # Metadados técnicos
        self.file_size = 0
        self.mime_type = ""
        self.dimensions = {}  # Para imagens/vídeos
        self.duration = 0.0   # Para áudio/vídeo
        self.language = ""
        self.encoding = ""

        # Metadados de qualidade
        self.quality_score = 0.0
        self.safety_rating = "unknown"
        self.content_hash = ""

        # Controle de versão
        self.version = 1
        self.parent_id = None  # Para versões derivadas

        # Timestamps
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.accessed_at = self.created_at

    def update_access(self) -> None:
        """Atualiza timestamp de acesso."""
        self.accessed_at = datetime.now().isoformat()

    def create_version(self, changes: Dict[str, Any]) -> 'ContentMetadata':
        """Cria nova versão do conteúdo."""
        new_metadata = ContentMetadata(
            content_id=f"{self.content_id}_v{self.version + 1}",
            media_type=self.media_type,
            title=changes.get("title", self.title),
            description=changes.get("description", self.description),
            tags=changes.get("tags", self.tags.copy()),
            source=self.source,
            created_by=changes.get("created_by", self.created_by)
        )

        new_metadata.version = self.version + 1
        new_metadata.parent_id = self.content_id

        return new_metadata


class ContentItem:
    """
    Item completo de conteúdo com metadados e dados.
    """

    def __init__(self, metadata: ContentMetadata, data: Any):
        self.metadata = metadata
        self.data = data  # Pode ser string, bytes, ou estrutura de dados

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "metadata": {
                "content_id": self.metadata.content_id,
                "media_type": self.metadata.media_type.value,
                "title": self.metadata.title,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "source": self.metadata.source,
                "created_by": self.metadata.created_by,
                "file_size": self.metadata.file_size,
                "mime_type": self.metadata.mime_type,
                "dimensions": self.metadata.dimensions,
                "duration": self.metadata.duration,
                "language": self.metadata.language,
                "encoding": self.metadata.encoding,
                "quality_score": self.metadata.quality_score,
                "safety_rating": self.metadata.safety_rating,
                "content_hash": self.metadata.content_hash,
                "version": self.metadata.version,
                "parent_id": self.metadata.parent_id,
                "created_at": self.metadata.created_at,
                "updated_at": self.metadata.updated_at,
                "accessed_at": self.metadata.accessed_at
            },
            "data": self._serialize_data()
        }

    def _serialize_data(self) -> Any:
        """Serializa dados baseado no tipo."""
        if isinstance(self.data, bytes):
            return base64.b64encode(self.data).decode('utf-8')
        elif isinstance(self.data, dict) or isinstance(self.data, list):
            return self.data
        else:
            return str(self.data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentItem':
        """Cria ContentItem de dicionário."""

        metadata_dict = data["metadata"]

        metadata = ContentMetadata(
            content_id=metadata_dict["content_id"],
            media_type=MediaType(metadata_dict["media_type"]),
            title=metadata_dict.get("title", ""),
            description=metadata_dict.get("description", ""),
            tags=metadata_dict.get("tags", []),
            source=metadata_dict.get("source", ""),
            created_by=metadata_dict.get("created_by", "system")
        )

        # Restaurar metadados técnicos
        metadata.file_size = metadata_dict.get("file_size", 0)
        metadata.mime_type = metadata_dict.get("mime_type", "")
        metadata.dimensions = metadata_dict.get("dimensions", {})
        metadata.duration = metadata_dict.get("duration", 0.0)
        metadata.language = metadata_dict.get("language", "")
        metadata.encoding = metadata_dict.get("encoding", "")
        metadata.quality_score = metadata_dict.get("quality_score", 0.0)
        metadata.safety_rating = metadata_dict.get("safety_rating", "unknown")
        metadata.content_hash = metadata_dict.get("content_hash", "")
        metadata.version = metadata_dict.get("version", 1)
        metadata.parent_id = metadata_dict.get("parent_id")
        metadata.created_at = metadata_dict.get("created_at", metadata.created_at)
        metadata.updated_at = metadata_dict.get("updated_at", metadata.updated_at)
        metadata.accessed_at = metadata_dict.get("accessed_at", metadata.accessed_at)

        # Desserializar dados
        raw_data = data["data"]
        if metadata.media_type in [MediaType.IMAGE, MediaType.VIDEO, MediaType.AUDIO]:
            item_data = base64.b64decode(raw_data)
        elif metadata.media_type == MediaType.STRUCTURED_DATA:
            item_data = raw_data if isinstance(raw_data, dict) else json.loads(raw_data)
        else:
            item_data = raw_data

        return cls(metadata, item_data)


class MultimodalContentManager:
    """
    Gerenciador integrado de conteúdo multimodal.

    Funcionalidades:
    - Armazenamento e recuperação de conteúdo multimodal
    - Indexação e busca semântica
    - Controle de versão
    - Validação de qualidade e segurança
    - Integração com outros módulos
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.content_dir = data_dir / "multimodal_content"
        self.content_dir.mkdir(parents=True, exist_ok=True)

        self.content_index_file = self.content_dir / "content_index.json"
        self.content_storage_dir = self.content_dir / "storage"

        self.content_items: Dict[str, ContentItem] = {}
        self.content_index: Dict[str, Dict[str, Any]] = {}  # Índice rápido

        # Configurações
        self.max_content_size_mb = 100
        self.enable_versioning = True
        self.enable_compression = True

        self._load_content()

    def store_content(self, media_type: MediaType, data: Any,
                     title: str = "", description: str = "",
                     tags: List[str] = None, source: str = "",
                     created_by: str = "system") -> str:
        """
        Armazena novo item de conteúdo.
        """

        # Gerar ID único
        content_hash = self._calculate_content_hash(data)
        content_id = f"{media_type.value}_{int(datetime.now().timestamp())}_{content_hash[:8]}"

        # Criar metadados
        metadata = ContentMetadata(
            content_id=content_id,
            media_type=media_type,
            title=title,
            description=description,
            tags=tags or [],
            source=source,
            created_by=created_by
        )

        # Extrair metadados técnicos
        self._extract_technical_metadata(metadata, data)

        # Validar conteúdo
        if not self._validate_content(metadata, data):
            raise ValueError("Content validation failed")

        # Calcular hash do conteúdo
        metadata.content_hash = content_hash

        # Criar item de conteúdo
        content_item = ContentItem(metadata, data)

        # Armazenar
        self.content_items[content_id] = content_item
        self._update_index(content_item)

        # Salvar em disco
        self._save_content_item(content_item)

        return content_id

    def retrieve_content(self, content_id: str) -> Optional[ContentItem]:
        """
        Recupera item de conteúdo.
        """

        content_item = self.content_items.get(content_id)
        if content_item:
            content_item.metadata.update_access()
            self._update_index(content_item)

        return content_item

    def search_content(self, query: Dict[str, Any]) -> List[ContentItem]:
        """
        Busca conteúdo baseado em critérios.
        """

        results = []

        # Busca no índice
        for content_id, index_data in self.content_index.items():
            if self._matches_query(index_data, query):
                content_item = self.content_items.get(content_id)
                if content_item:
                    results.append(content_item)

        # Ordenar por relevância (simplificado)
        results.sort(key=lambda x: x.metadata.accessed_at, reverse=True)

        return results

    def update_content(self, content_id: str, updates: Dict[str, Any],
                      updated_by: str = "system") -> bool:
        """
        Atualiza item de conteúdo.
        """

        if content_id not in self.content_items:
            return False

        current_item = self.content_items[content_id]

        if self.enable_versioning:
            # Criar nova versão
            new_metadata = current_item.metadata.create_version({
                "title": updates.get("title", current_item.metadata.title),
                "description": updates.get("description", current_item.metadata.description),
                "tags": updates.get("tags", current_item.metadata.tags),
                "created_by": updated_by
            })

            # Copiar dados ou aplicar mudanças
            new_data = updates.get("data", current_item.data)

            new_item = ContentItem(new_metadata, new_data)
            self.content_items[new_metadata.content_id] = new_item
            self._update_index(new_item)
            self._save_content_item(new_item)

        else:
            # Atualizar item existente
            if "title" in updates:
                current_item.metadata.title = updates["title"]
            if "description" in updates:
                current_item.metadata.description = updates["description"]
            if "tags" in updates:
                current_item.metadata.tags = updates["tags"]
            if "data" in updates:
                current_item.data = updates["data"]
                self._extract_technical_metadata(current_item.metadata, current_item.data)

            current_item.metadata.updated_at = datetime.now().isoformat()
            self._update_index(current_item)
            self._save_content_item(current_item)

        return True

    def delete_content(self, content_id: str) -> bool:
        """
        Remove item de conteúdo.
        """

        if content_id not in self.content_items:
            return False

        # Remover do índice
        if content_id in self.content_index:
            del self.content_index[content_id]

        # Remover item
        del self.content_items[content_id]

        # Remover arquivo físico
        content_file = self.content_storage_dir / f"{content_id}.json"
        if content_file.exists():
            content_file.unlink()

        self._save_index()
        return True

    def get_content_versions(self, content_id: str) -> List[ContentItem]:
        """
        Retorna todas as versões de um conteúdo.
        """

        versions = []

        # Encontrar versão raiz
        root_id = content_id
        current_item = self.content_items.get(content_id)
        if current_item and current_item.metadata.parent_id:
            root_id = current_item.metadata.parent_id

        # Coletar todas as versões
        for item in self.content_items.values():
            if (item.metadata.content_id == root_id or
                item.metadata.parent_id == root_id or
                (item.metadata.parent_id and item.metadata.parent_id.startswith(root_id))):
                versions.append(item)

        # Ordenar por versão
        versions.sort(key=lambda x: x.metadata.version)

        return versions

    def get_content_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do conteúdo."""

        total_items = len(self.content_items)
        type_distribution = {}

        total_size = 0
        avg_quality = 0.0
        quality_count = 0

        for item in self.content_items.values():
            # Distribuição por tipo
            media_type = item.metadata.media_type.value
            type_distribution[media_type] = type_distribution.get(media_type, 0) + 1

            # Tamanho total
            total_size += item.metadata.file_size

            # Qualidade média
            if item.metadata.quality_score > 0:
                avg_quality += item.metadata.quality_score
                quality_count += 1

        return {
            "total_items": total_items,
            "type_distribution": type_distribution,
            "total_size_mb": total_size / (1024 * 1024),
            "avg_quality_score": avg_quality / max(quality_count, 1),
            "versioned_items": sum(1 for item in self.content_items.values() if item.metadata.version > 1)
        }

    def _calculate_content_hash(self, data: Any) -> str:
        """Calcula hash do conteúdo."""
        if isinstance(data, bytes):
            return hashlib.sha256(data).hexdigest()
        elif isinstance(data, str):
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
        else:
            # Para dados estruturados, serializar como JSON
            data_str = json.dumps(data, sort_keys=True)
            return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def _extract_technical_metadata(self, metadata: ContentMetadata, data: Any) -> None:
        """Extrai metadados técnicos do conteúdo."""

        if isinstance(data, bytes):
            metadata.file_size = len(data)
            metadata.mime_type = self._detect_mime_type(data)

            # Metadados específicos por tipo
            if metadata.media_type == MediaType.IMAGE:
                self._extract_image_metadata(metadata, data)
            elif metadata.media_type == MediaType.VIDEO:
                self._extract_video_metadata(metadata, data)
            elif metadata.media_type == MediaType.AUDIO:
                self._extract_audio_metadata(metadata, data)

        elif isinstance(data, str):
            metadata.file_size = len(data.encode('utf-8'))
            metadata.encoding = 'utf-8'

            if metadata.media_type == MediaType.CODE:
                metadata.language = self._detect_programming_language(data)

        elif isinstance(data, dict) or isinstance(data, list):
            data_str = json.dumps(data)
            metadata.file_size = len(data_str.encode('utf-8'))
            metadata.mime_type = 'application/json'

    def _detect_mime_type(self, data: bytes) -> str:
        """Detecta tipo MIME dos dados."""
        # Verificação simples baseada em cabeçalhos
        if data.startswith(b'\xff\xd8'):
            return 'image/jpeg'
        elif data.startswith(b'\x89PNG'):
            return 'image/png'
        elif data.startswith(b'GIF8'):
            return 'image/gif'
        elif data.startswith(b'\x00\x00\x00'):
            return 'video/mp4'  # Simplificado
        else:
            return 'application/octet-stream'

    def _extract_image_metadata(self, metadata: ContentMetadata, data: bytes) -> None:
        """Extrai metadados de imagem."""
        # Implementação simplificada - em produção usaria PIL ou similar
        try:
            # Simular extração de dimensões
            metadata.dimensions = {"width": 1024, "height": 768}  # Valores simulados
        except Exception:
            metadata.dimensions = {}

    def _extract_video_metadata(self, metadata: ContentMetadata, data: bytes) -> None:
        """Extrai metadados de vídeo."""
        # Implementação simplificada
        metadata.duration = 30.0  # Segundos simulados
        metadata.dimensions = {"width": 1920, "height": 1080}

    def _extract_audio_metadata(self, metadata: ContentMetadata, data: bytes) -> None:
        """Extrai metadados de áudio."""
        # Implementação simplificada
        metadata.duration = 180.0  # Segundos simulados

    def _detect_programming_language(self, code: str) -> str:
        """Detecta linguagem de programação."""
        # Detecção simples baseada em padrões
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function' in code and ('var ' in code or 'const ' in code):
            return 'javascript'
        elif '#include' in code and 'int main' in code:
            return 'c++'
        elif '<?php' in code:
            return 'php'
        else:
            return 'unknown'

    def _validate_content(self, metadata: ContentMetadata, data: Any) -> bool:
        """Valida conteúdo baseado em regras de segurança e qualidade."""

        # Verificar tamanho máximo
        if metadata.file_size > self.max_content_size_mb * 1024 * 1024:
            return False

        # Validações específicas por tipo
        if metadata.media_type == MediaType.IMAGE:
            return self._validate_image_content(data)
        elif metadata.media_type == MediaType.TEXT:
            return self._validate_text_content(data)
        elif metadata.media_type == MediaType.CODE:
            return self._validate_code_content(data)

        return True

    def _validate_image_content(self, data: bytes) -> bool:
        """Valida conteúdo de imagem."""
        # Verificações básicas de segurança
        return len(data) > 100 and not data.startswith(b'<script')

    def _validate_text_content(self, data: str) -> bool:
        """Valida conteúdo de texto."""
        # Verificar tamanho razoável
        return len(data) < 1000000  # 1MB máximo

    def _validate_code_content(self, data: str) -> bool:
        """Valida conteúdo de código."""
        # Verificações básicas de segurança
        dangerous_patterns = ['eval(', 'exec(', 'system(', '__import__(']
        for pattern in dangerous_patterns:
            if pattern in data:
                return False
        return True

    def _matches_query(self, index_data: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Verifica se item corresponde à consulta."""

        for key, value in query.items():
            if key == "media_type":
                if index_data.get("media_type") != value:
                    return False
            elif key == "tags":
                item_tags = set(index_data.get("tags", []))
                query_tags = set(value) if isinstance(value, list) else {value}
                if not query_tags.issubset(item_tags):
                    return False
            elif key == "title_contains":
                if value.lower() not in index_data.get("title", "").lower():
                    return False
            elif key == "created_by":
                if index_data.get("created_by") != value:
                    return False
            elif key == "min_quality":
                if index_data.get("quality_score", 0) < value:
                    return False

        return True

    def _update_index(self, content_item: ContentItem) -> None:
        """Atualiza índice com item de conteúdo."""

        self.content_index[content_item.metadata.content_id] = {
            "media_type": content_item.metadata.media_type.value,
            "title": content_item.metadata.title,
            "description": content_item.metadata.description,
            "tags": content_item.metadata.tags,
            "created_by": content_item.metadata.created_by,
            "file_size": content_item.metadata.file_size,
            "quality_score": content_item.metadata.quality_score,
            "created_at": content_item.metadata.created_at,
            "updated_at": content_item.metadata.updated_at,
            "accessed_at": content_item.metadata.accessed_at
        }

    def _save_content_item(self, content_item: ContentItem) -> None:
        """Salva item de conteúdo em disco."""

        self.content_storage_dir.mkdir(parents=True, exist_ok=True)

        content_file = self.content_storage_dir / f"{content_item.metadata.content_id}.json"
        content_file.write_text(
            json.dumps(content_item.to_dict(), ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def _load_content(self) -> None:
        """Carrega conteúdo do disco."""

        if not self.content_storage_dir.exists():
            return

        for content_file in self.content_storage_dir.glob("*.json"):
            try:
                content_data = json.loads(content_file.read_text(encoding='utf-8'))
                content_item = ContentItem.from_dict(content_data)
                self.content_items[content_item.metadata.content_id] = content_item
                self._update_index(content_item)
            except Exception as e:
                print(f"Error loading content {content_file}: {e}")

    def _save_index(self) -> None:
        """Salva índice em disco."""

        self.content_dir.mkdir(parents=True, exist_ok=True)

        self.content_index_file.write_text(
            json.dumps(self.content_index, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
