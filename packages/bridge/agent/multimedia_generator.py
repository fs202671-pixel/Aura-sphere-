"""
Módulo de Geração de Imagens e Vídeos - Geração segura de conteúdo multimídia

Este módulo implementa geração de imagens e vídeos com filtros
de segurança rigorosos e validação de conteúdo.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import hashlib
import re
import base64
from io import BytesIO


class ContentType(Enum):
    """Tipos de conteúdo gerável."""
    IMAGE = "image"
    VIDEO = "video"
    ANIMATION = "animation"
    ICON = "icon"


class GenerationSafety(Enum):
    """Níveis de segurança para geração."""
    SAFE = "safe"              # Conteúdo completamente seguro
    MODERATE = "moderate"       # Conteúdo moderado, supervisionado
    RESTRICTED = "restricted"   # Conteúdo restrito, requer aprovação
    BLOCKED = "blocked"         # Conteúdo bloqueado


class ContentFilter:
    """
    Filtro de conteúdo para geração multimídia.
    """

    def __init__(self):
        self.blocked_keywords = {
            # Conteúdo violento
            "violence", "blood", "death", "kill", "murder", "weapon", "gun", "knife",

            # Conteúdo adulto
            "nude", "naked", "sex", "porn", "adult", "erotic",

            # Conteúdo discriminatório
            "hate", "racist", "discrimination", "offensive",

            # Conteúdo perigoso
            "explosive", "bomb", "drug", "illegal", "harmful",

            # Personagens protegidos
            "celebrity", "famous", "real person"
        }

        self.moderated_keywords = {
            "dark", "scary", "horror", "monster", "ghost",
            "military", "war", "fight", "battle"
        }

    def analyze_content(self, prompt: str, metadata: Dict[str, Any] = None) -> GenerationSafety:
        """
        Analisa prompt e determina nível de segurança.
        """

        prompt_lower = prompt.lower()
        metadata = metadata or {}

        # Verificar palavras bloqueadas
        for keyword in self.blocked_keywords:
            if keyword in prompt_lower:
                return GenerationSafety.BLOCKED

        # Verificar palavras moderadas
        for keyword in self.moderated_keywords:
            if keyword in prompt_lower:
                return GenerationSafety.RESTRICTED

        # Verificar metadados suspeitos
        if metadata.get("suspicious_flags", 0) > 0:
            return GenerationSafety.RESTRICTED

        return GenerationSafety.SAFE

    def validate_generated_content(self, content_data: bytes,
                                  content_type: ContentType) -> Tuple[bool, str]:
        """
        Valida conteúdo gerado para segurança.
        """

        try:
            # Análise básica de segurança do conteúdo
            if content_type == ContentType.IMAGE:
                return self._validate_image_content(content_data)
            elif content_type == ContentType.VIDEO:
                return self._validate_video_content(content_data)
            else:
                return True, "Content type validation not implemented"

        except Exception as e:
            return False, f"Content validation failed: {e}"

    def _validate_image_content(self, image_data: bytes) -> Tuple[bool, str]:
        """Valida conteúdo de imagem."""
        # Implementação simplificada - em produção usaria análise real de imagem
        try:
            # Verificar tamanho mínimo/máximo
            if len(image_data) < 100:  # Muito pequeno
                return False, "Image too small"

            if len(image_data) > 10 * 1024 * 1024:  # Maior que 10MB
                return False, "Image too large"

            # Verificar cabeçalho de imagem
            if not image_data.startswith(b'\xff\xd8'):  # JPEG
                if not image_data.startswith(b'\x89PNG'):  # PNG
                    return False, "Invalid image format"

            return True, "Image validation passed"

        except Exception as e:
            return False, f"Image validation error: {e}"

    def _validate_video_content(self, video_data: bytes) -> Tuple[bool, str]:
        """Valida conteúdo de vídeo."""
        # Implementação simplificada
        try:
            if len(video_data) < 1000:  # Muito pequeno
                return False, "Video too small"

            if len(video_data) > 100 * 1024 * 1024:  # Maior que 100MB
                return False, "Video too large"

            return True, "Video validation passed"

        except Exception as e:
            return False, f"Video validation error: {e}"


class GenerationRequest:
    """
    Representa uma solicitação de geração de conteúdo.
    """

    def __init__(self, content_type: ContentType, prompt: str,
                 parameters: Dict[str, Any], requested_by: str):
        self.content_type = content_type
        self.prompt = prompt
        self.parameters = parameters
        self.requested_by = requested_by
        self.request_id = f"gen_{int(datetime.now().timestamp())}_{hash(prompt) % 10000}"

        # Status e resultados
        self.status = "pending"  # pending, processing, completed, failed, blocked
        self.safety_level = None
        self.generated_content = None
        self.content_hash = None
        self.error_message = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None

    def approve_request(self) -> None:
        """Aprova solicitação restrita."""
        self.status = "approved"

    def block_request(self, reason: str) -> None:
        """Bloqueia solicitação."""
        self.status = "blocked"
        self.error_message = reason

    def complete_generation(self, content_data: bytes) -> None:
        """Completa geração com sucesso."""
        self.status = "completed"
        self.generated_content = base64.b64encode(content_data).decode('utf-8')
        self.content_hash = hashlib.sha256(content_data).hexdigest()
        self.completed_at = datetime.now().isoformat()

    def fail_generation(self, error: str) -> None:
        """Falha na geração."""
        self.status = "failed"
        self.error_message = error
        self.completed_at = datetime.now().isoformat()


class MultimediaGenerator:
    """
    Gerador seguro de conteúdo multimídia.

    Funcionalidades:
    - Geração de imagens e vídeos com filtros de segurança
    - Validação rigorosa de conteúdo
    - Controle de qualidade
    - Histórico e auditoria completos
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.generator_dir = data_dir / "multimedia_generator"
        self.generator_dir.mkdir(parents=True, exist_ok=True)

        self.requests_file = self.generator_dir / "generation_requests.json"
        self.content_dir = self.generator_dir / "generated_content"
        self.content_dir.mkdir(exist_ok=True)

        self.requests: Dict[str, GenerationRequest] = {}
        self.content_filter = ContentFilter()

        # Configurações
        self.max_requests_per_hour = 10
        self.max_content_size_mb = 50
        self.require_approval_for_restricted = True

        self._load_state()

    async def request_generation(self, content_type: ContentType, prompt: str,
                                parameters: Dict[str, Any] = None,
                                requested_by: str = "system") -> Tuple[str, GenerationSafety]:
        """
        Solicita geração de conteúdo multimídia.
        """

        parameters = parameters or {}

        # Verificar limites de taxa
        if not self._check_rate_limits(requested_by):
            raise ValueError("Rate limit exceeded")

        # Analisar segurança do prompt
        safety_level = self.content_filter.analyze_content(prompt, parameters)

        if safety_level == GenerationSafety.BLOCKED:
            raise ValueError("Content blocked by safety filter")

        # Criar solicitação
        request = GenerationRequest(
            content_type=content_type,
            prompt=prompt,
            parameters=parameters,
            requested_by=requested_by
        )

        request.safety_level = safety_level

        # Se requer aprovação, marcar como pendente
        if safety_level == GenerationSafety.RESTRICTED and self.require_approval_for_restricted:
            request.status = "pending_approval"
        else:
            request.status = "approved"

        self.requests[request.request_id] = request
        self._save_state()

        return request.request_id, safety_level

    async def approve_generation(self, request_id: str, approved_by: str) -> bool:
        """
        Aprova uma solicitação de geração pendente.
        """

        if request_id not in self.requests:
            return False

        request = self.requests[request_id]

        if request.status != "pending_approval":
            return False

        request.approve_request()
        self._save_state()

        return True

    async def generate_content(self, request_id: str) -> Optional[bytes]:
        """
        Gera conteúdo para uma solicitação aprovada.
        """

        if request_id not in self.requests:
            return None

        request = self.requests[request_id]

        if request.status not in ["approved", "processing"]:
            return None

        try:
            request.status = "processing"
            self._save_state()

            # Gerar conteúdo baseado no tipo
            if request.content_type == ContentType.IMAGE:
                content_data = await self._generate_image(request)
            elif request.content_type == ContentType.VIDEO:
                content_data = await self._generate_video(request)
            elif request.content_type == ContentType.ANIMATION:
                content_data = await self._generate_animation(request)
            elif request.content_type == ContentType.ICON:
                content_data = await self._generate_icon(request)
            else:
                raise ValueError(f"Unsupported content type: {request.content_type}")

            # Validar conteúdo gerado
            is_valid, validation_message = self.content_filter.validate_generated_content(
                content_data, request.content_type
            )

            if not is_valid:
                request.fail_generation(f"Content validation failed: {validation_message}")
                self._save_state()
                return None

            # Salvar conteúdo
            await self._save_generated_content(request_id, content_data)

            # Completar solicitação
            request.complete_generation(content_data)
            self._save_state()

            return content_data

        except Exception as e:
            request.fail_generation(str(e))
            self._save_state()
            return None

    async def _generate_image(self, request: GenerationRequest) -> bytes:
        """Gera imagem (implementação simulada)."""
        # Em produção, isso se conectaria a um serviço de geração de imagens
        # Como Stable Diffusion, DALL-E, etc.

        # Simulação: gerar uma imagem JPEG simples
        import struct

        # Cabeçalho JPEG mínimo
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x10\x00\x10\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00'

        # Dados de imagem simulados
        width, height = request.parameters.get("width", 64), request.parameters.get("height", 64)
        image_data = b'A' * (width * height * 3)  # Dados RGB simulados

        return jpeg_header + image_data + b'\xff\xd9'

    async def _generate_video(self, request: GenerationRequest) -> bytes:
        """Gera vídeo (implementação simulada)."""
        # Simulação básica - em produção seria muito mais complexo
        video_data = b'VIDEO_DATA_' + request.prompt.encode('utf-8')[:100]
        return video_data

    async def _generate_animation(self, request: GenerationRequest) -> bytes:
        """Gera animação (implementação simulada)."""
        # Simulação de GIF
        gif_data = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        return gif_data

    async def _generate_icon(self, request: GenerationRequest) -> bytes:
        """Gera ícone (implementação simulada)."""
        # Simulação de PNG pequeno
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xff\x61\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        return png_data

    async def _save_generated_content(self, request_id: str, content_data: bytes) -> None:
        """Salva conteúdo gerado."""
        content_file = self.content_dir / f"{request_id}.bin"
        content_file.write_bytes(content_data)

    def get_generation_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de uma solicitação de geração."""

        if request_id not in self.requests:
            return None

        request = self.requests[request_id]

        return {
            "request_id": request.request_id,
            "content_type": request.content_type.value,
            "status": request.status,
            "safety_level": request.safety_level.value if request.safety_level else None,
            "created_at": request.created_at,
            "completed_at": request.completed_at,
            "error_message": request.error_message,
            "content_hash": request.content_hash
        }

    def get_generated_content(self, request_id: str) -> Optional[bytes]:
        """Retorna conteúdo gerado."""

        if request_id not in self.requests:
            return None

        request = self.requests[request_id]

        if request.status != "completed" or not request.generated_content:
            return None

        # Decodificar do base64
        try:
            return base64.b64decode(request.generated_content)
        except Exception:
            return None

    def get_generation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de geração."""

        total_requests = len(self.requests)
        completed_requests = sum(1 for r in self.requests.values() if r.status == "completed")
        blocked_requests = sum(1 for r in self.requests.values() if r.status == "blocked")
        failed_requests = sum(1 for r in self.requests.values() if r.status == "failed")

        return {
            "total_requests": total_requests,
            "completed_requests": completed_requests,
            "blocked_requests": blocked_requests,
            "failed_requests": failed_requests,
            "success_rate": completed_requests / max(total_requests, 1),
            "block_rate": blocked_requests / max(total_requests, 1)
        }

    def _check_rate_limits(self, requested_by: str) -> bool:
        """Verifica limites de taxa."""

        # Contar solicitações na última hora
        current_time = datetime.now().timestamp()
        one_hour_ago = current_time - 3600

        recent_requests = sum(1 for r in self.requests.values()
                             if r.requested_by == requested_by and
                             datetime.fromisoformat(r.created_at).timestamp() > one_hour_ago)

        return recent_requests < self.max_requests_per_hour

    def _load_state(self) -> None:
        """Carrega estado do gerador."""

        if self.requests_file.exists():
            try:
                requests_data = json.loads(self.requests_file.read_text(encoding='utf-8'))

                for req_data in requests_data:
                    # Recriar objeto GenerationRequest
                    request = GenerationRequest(
                        content_type=ContentType(req_data["content_type"]),
                        prompt=req_data["prompt"],
                        parameters=req_data["parameters"],
                        requested_by=req_data["requested_by"]
                    )

                    # Restaurar estado
                    request.request_id = req_data["request_id"]
                    request.status = req_data["status"]
                    request.safety_level = GenerationSafety(req_data["safety_level"]) if req_data.get("safety_level") else None
                    request.generated_content = req_data.get("generated_content")
                    request.content_hash = req_data.get("content_hash")
                    request.error_message = req_data.get("error_message")
                    request.created_at = req_data["created_at"]
                    request.completed_at = req_data.get("completed_at")

                    self.requests[request.request_id] = request

            except Exception:
                self.requests = {}

    def _save_state(self) -> None:
        """Persiste estado do gerador."""

        self.generator_dir.mkdir(parents=True, exist_ok=True)

        # Serializar solicitações
        requests_data = []
        for request in self.requests.values():
            requests_data.append({
                "request_id": request.request_id,
                "content_type": request.content_type.value,
                "prompt": request.prompt,
                "parameters": request.parameters,
                "requested_by": request.requested_by,
                "status": request.status,
                "safety_level": request.safety_level.value if request.safety_level else None,
                "generated_content": request.generated_content,
                "content_hash": request.content_hash,
                "error_message": request.error_message,
                "created_at": request.created_at,
                "completed_at": request.completed_at
            })

        self.requests_file.write_text(
            json.dumps(requests_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
