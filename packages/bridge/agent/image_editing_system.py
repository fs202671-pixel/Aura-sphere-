"""
Sistema de Edição de Imagens - Versão básica com PIL

Este módulo implementa edição de imagens usando PIL.
Suporta operações básicas de edição e filtros.
"""

from typing import Dict, Any, List, Optional, Tuple
import hashlib
from pathlib import Path
from datetime import datetime
import json
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np


class ImageEditingSystem:
    """
    Sistema básico de edição de imagens usando PIL.

    Funcionalidades:
    - Aplicação de filtros (blur, sharpen, contrast, brightness)
    - Redimensionamento e cropping
    - Rotação e flipping
    - Adição de texto e formas
    - Correção de cores básica
    - Validação de segurança das operações
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path("edited_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configurações de segurança
        self.max_image_size = 4096  # Máximo 4096x4096
        self.supported_formats = ['PNG', 'JPEG', 'JPG', 'BMP', 'TIFF']
        self.max_operations = 10  # Máximo de operações por edição

    def apply_edits(self, image_path: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aplica uma série de edições a uma imagem.

        Args:
            image_path: Caminho para a imagem original
            edits: Lista de operações de edição

        Returns:
            Dict com resultado da edição
        """

        try:
            # Validar entrada
            validation = self._validate_edit_request(image_path, edits)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["reason"],
                    "edited_path": None
                }

            # Carregar imagem
            image = Image.open(image_path)

            # Aplicar edições
            edited_image = self._apply_edit_operations(image, edits)

            # Gerar caminho de saída
            original_name = Path(image_path).stem
            edit_hash = hashlib.md5(str(edits).encode()).hexdigest()[:8]
            output_filename = f"edited_{original_name}_{edit_hash}.png"
            output_path = self.output_dir / output_filename

            # Salvar imagem editada
            edited_image.save(output_path, "PNG", quality=95)

            # Metadados
            metadata = {
                "original_path": image_path,
                "edited_path": str(output_path),
                "operations_applied": len(edits),
                "edits": edits,
                "timestamp": datetime.now().isoformat(),
                "original_size": image.size,
                "edited_size": edited_image.size
            }

            # Salvar metadados
            self._save_edit_metadata(output_path.stem, metadata)

            return {
                "success": True,
                "edited_path": str(output_path),
                "metadata": metadata,
                "operations_count": len(edits)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na edição de imagem: {str(e)}",
                "edited_path": None
            }

    def _validate_edit_request(self, image_path: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Valida a requisição de edição.
        """
        # Verificar se arquivo existe
        if not Path(image_path).exists():
            return {"valid": False, "reason": "Arquivo de imagem não encontrado"}

        # Verificar formato
        try:
            with Image.open(image_path) as img:
                if img.format not in self.supported_formats:
                    return {"valid": False, "reason": f"Formato {img.format} não suportado"}

                # Verificar tamanho
                if img.size[0] > self.max_image_size or img.size[1] > self.max_image_size:
                    return {"valid": False, "reason": f"Imagem muito grande (máx: {self.max_image_size}x{self.max_image_size})"}

        except Exception as e:
            return {"valid": False, "reason": f"Erro ao abrir imagem: {str(e)}"}

        # Verificar operações
        if not edits or len(edits) == 0:
            return {"valid": False, "reason": "Nenhuma operação de edição especificada"}

        if len(edits) > self.max_operations:
            return {"valid": False, "reason": f"Muitas operações (máx: {self.max_operations})"}

        # Validar cada operação
        supported_operations = [
            'resize', 'crop', 'rotate', 'flip', 'filter', 'brightness', 'contrast',
            'saturation', 'add_text', 'add_shape', 'blur', 'sharpen'
        ]

        for edit in edits:
            if 'operation' not in edit:
                return {"valid": False, "reason": "Operação não especificada"}

            if edit['operation'] not in supported_operations:
                return {"valid": False, "reason": f"Operação '{edit['operation']}' não suportada"}

        return {"valid": True, "reason": "Requisição válida"}

    def _apply_edit_operations(self, image: Image.Image, edits: List[Dict[str, Any]]) -> Image.Image:
        """
        Aplica as operações de edição sequencialmente.
        """
        edited_image = image.copy()

        for edit in edits:
            operation = edit['operation']
            params = edit.get('params', {})

            if operation == 'resize':
                edited_image = self._apply_resize(edited_image, params)
            elif operation == 'crop':
                edited_image = self._apply_crop(edited_image, params)
            elif operation == 'rotate':
                edited_image = self._apply_rotate(edited_image, params)
            elif operation == 'flip':
                edited_image = self._apply_flip(edited_image, params)
            elif operation == 'filter':
                edited_image = self._apply_filter(edited_image, params)
            elif operation == 'brightness':
                edited_image = self._apply_brightness(edited_image, params)
            elif operation == 'contrast':
                edited_image = self._apply_contrast(edited_image, params)
            elif operation == 'saturation':
                edited_image = self._apply_saturation(edited_image, params)
            elif operation == 'add_text':
                edited_image = self._apply_add_text(edited_image, params)
            elif operation == 'add_shape':
                edited_image = self._apply_add_shape(edited_image, params)
            elif operation == 'blur':
                edited_image = self._apply_blur(edited_image, params)
            elif operation == 'sharpen':
                edited_image = self._apply_sharpen(edited_image, params)

        return edited_image

    def _apply_resize(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Redimensiona a imagem."""
        width = params.get('width', image.size[0])
        height = params.get('height', image.size[1])
        resample = Image.LANCZOS if params.get('high_quality', True) else Image.BILINEAR
        return image.resize((width, height), resample)

    def _apply_crop(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Corta a imagem."""
        left = params.get('left', 0)
        top = params.get('top', 0)
        right = params.get('right', image.size[0])
        bottom = params.get('bottom', image.size[1])
        return image.crop((left, top, right, bottom))

    def _apply_rotate(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Rotaciona a imagem."""
        angle = params.get('angle', 0)
        expand = params.get('expand', True)
        return image.rotate(angle, expand=expand)

    def _apply_flip(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Inverte a imagem."""
        direction = params.get('direction', 'horizontal')
        if direction == 'horizontal':
            return image.transpose(Image.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            return image.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            return image

    def _apply_filter(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Aplica filtro à imagem."""
        filter_name = params.get('filter', 'blur')
        if filter_name == 'blur':
            return image.filter(ImageFilter.BLUR)
        elif filter_name == 'contour':
            return image.filter(ImageFilter.CONTOUR)
        elif filter_name == 'detail':
            return image.filter(ImageFilter.DETAIL)
        elif filter_name == 'edge_enhance':
            return image.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_name == 'emboss':
            return image.filter(ImageFilter.EMBOSS)
        elif filter_name == 'smooth':
            return image.filter(ImageFilter.SMOOTH)
        else:
            return image

    def _apply_brightness(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Ajusta brilho."""
        factor = params.get('factor', 1.0)
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    def _apply_contrast(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Ajusta contraste."""
        factor = params.get('factor', 1.0)
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    def _apply_saturation(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Ajusta saturação."""
        factor = params.get('factor', 1.0)
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)

    def _apply_add_text(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Adiciona texto à imagem."""
        text = params.get('text', '')
        position = params.get('position', (10, 10))
        color = params.get('color', 'black')
        font_size = params.get('font_size', 20)

        # Converter para RGBA se necessário
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        draw = ImageDraw.Draw(image)

        # Usar fonte padrão (PIL pode não ter fontes customizadas)
        try:
            # Tentar usar fonte padrão do sistema
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback para fonte padrão
            font = ImageFont.load_default()

        draw.text(position, text, fill=color, font=font)
        return image

    def _apply_add_shape(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Adiciona forma à imagem."""
        shape = params.get('shape', 'rectangle')
        position = params.get('position', (10, 10, 100, 100))
        color = params.get('color', 'red')
        outline = params.get('outline', None)

        # Converter para RGBA se necessário
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        draw = ImageDraw.Draw(image)

        if shape == 'rectangle':
            draw.rectangle(position, fill=color, outline=outline)
        elif shape == 'circle':
            draw.ellipse(position, fill=color, outline=outline)
        elif shape == 'line':
            start = params.get('start', (10, 10))
            end = params.get('end', (100, 100))
            draw.line([start, end], fill=color, width=params.get('width', 1))

        return image

    def _apply_blur(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Aplica desfoque."""
        radius = params.get('radius', 2)
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    def _apply_sharpen(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Aplica nitidez."""
        return image.filter(ImageFilter.UnsharpMask(
            radius=params.get('radius', 1),
            percent=params.get('percent', 150),
            threshold=params.get('threshold', 3)
        ))

    def _save_edit_metadata(self, image_id: str, metadata: Dict[str, Any]):
        """
        Salva metadados da edição.
        """
        metadata_file = self.output_dir / f"{image_id}_edit_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def get_edit_history(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Retorna histórico de edições para uma imagem.
        """
        image_name = Path(image_path).stem
        history = []

        for metadata_file in self.output_dir.glob(f"edited_{image_name}_*_edit_metadata.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    history.append(metadata)
            except:
                continue

        return sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)
