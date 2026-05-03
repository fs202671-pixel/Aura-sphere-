"""
Sistema de Geração de Imagens - Versão básica com PIL

Este módulo implementa geração de imagens simples usando PIL.
Em produção, seria substituído por modelos de IA avançados.
"""

from typing import Dict, Any, Optional, Tuple, List
import hashlib
import os
from pathlib import Path
from datetime import datetime
import json
from PIL import Image, ImageDraw, ImageFont
import colorsys
import random


class ImageGenerationSystem:
    """
    Sistema básico de geração de imagens usando PIL.

    Funcionalidades:
    - Geração de imagens abstratas baseadas em prompts
    - Suporte a estilos básicos (realistic, abstract, geometric, minimalist)
    - Controle de tamanho e qualidade
    - Validação de segurança de prompts
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path("generated_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configurações
        self.max_size = (2048, 2048)  # Máximo 2048x2048
        self.default_size = (1024, 1024)
        self.supported_styles = ["realistic", "abstract", "geometric", "minimalist"]

        # Cache de prompts processados
        self.prompt_cache = {}

        # Paleta de cores seguras
        self.safe_colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
        ]

    def generate_image(self, prompt: str, style: str = "realistic",
                      size: str = "1024x1024", **kwargs) -> Dict[str, Any]:
        """
        Gera uma imagem baseada no prompt fornecido.

        Args:
            prompt: Descrição da imagem desejada
            style: Estilo da imagem (realistic, abstract, geometric, minimalist)
            size: Tamanho da imagem (formato "WxH")
            **kwargs: Parâmetros adicionais

        Returns:
            Dict com informações da imagem gerada
        """

        try:
            # Validar entrada
            validation = self._validate_prompt(prompt)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"Prompt inválido: {validation['reason']}",
                    "generated_id": None
                }

            # Processar parâmetros
            width, height = self._parse_size(size)
            style = style.lower() if style.lower() in self.supported_styles else "abstract"

            # Gerar ID único para a imagem
            prompt_hash = hashlib.md5(f"{prompt}_{style}_{size}".encode()).hexdigest()[:8]
            image_id = f"img_{int(datetime.now().timestamp())}_{prompt_hash}"

            # Gerar imagem
            image_path = self.output_dir / f"{image_id}.png"
            self._generate_image_content(prompt, style, width, height, image_path)

            # Metadados
            metadata = {
                "id": image_id,
                "prompt": prompt,
                "style": style,
                "size": f"{width}x{height}",
                "generated_at": datetime.now().isoformat(),
                "file_path": str(image_path),
                "file_size": image_path.stat().st_size if image_path.exists() else 0
            }

            # Salvar metadados
            self._save_metadata(image_id, metadata)

            return {
                "success": True,
                "image_id": image_id,
                "file_path": str(image_path),
                "metadata": metadata,
                "size": f"{width}x{height}",
                "style": style
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na geração de imagem: {str(e)}",
                "generated_id": None
            }

    def _validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Valida se o prompt é seguro e apropriado.
        """
        if not prompt or len(prompt.strip()) == 0:
            return {"valid": False, "reason": "Prompt vazio"}

        if len(prompt) > 500:
            return {"valid": False, "reason": "Prompt muito longo"}

        # Palavras proibidas (básico)
        forbidden_words = ["nsfw", "nude", "violent", "harmful", "illegal"]
        prompt_lower = prompt.lower()

        for word in forbidden_words:
            if word in prompt_lower:
                return {"valid": False, "reason": f"Conteúdo proibido detectado: {word}"}

        return {"valid": True, "reason": "Prompt válido"}

    def _parse_size(self, size_str: str) -> Tuple[int, int]:
        """
        Converte string de tamanho para tupla (width, height).
        """
        try:
            parts = size_str.split('x')
            if len(parts) != 2:
                return self.default_size

            width = min(int(parts[0]), self.max_size[0])
            height = min(int(parts[1]), self.max_size[1])

            return (max(width, 64), max(height, 64))  # Mínimo 64x64
        except:
            return self.default_size

    def _generate_image_content(self, prompt: str, style: str, width: int, height: int, output_path: Path):
        """
        Gera o conteúdo da imagem baseado no prompt e estilo.
        """

        # Criar imagem base
        if style == "realistic":
            image = self._generate_realistic_image(prompt, width, height)
        elif style == "geometric":
            image = self._generate_geometric_image(prompt, width, height)
        elif style == "minimalist":
            image = self._generate_minimalist_image(prompt, width, height)
        else:  # abstract (padrão)
            image = self._generate_abstract_image(prompt, width, height)

        # Salvar imagem
        image.save(output_path, "PNG", quality=95)

    def _generate_abstract_image(self, prompt: str, width: int, height: int) -> Image.Image:
        """
        Gera imagem abstrata baseada no prompt.
        """
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        # Extrair "cores" do prompt
        prompt_hash = hash(prompt) % 1000
        random.seed(prompt_hash)

        # Gerar formas abstratas
        for _ in range(10 + (prompt_hash % 20)):
            # Cor aleatória da paleta segura
            color = random.choice(self.safe_colors)

            # Posição e tamanho aleatórios
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(x1, min(x1 + 200, width))
            y2 = random.randint(y1, min(y1 + 200, height))

            # Desenhar forma (retângulo, círculo ou triângulo)
            shape_type = random.choice(['rect', 'circle', 'triangle'])

            if shape_type == 'rect':
                draw.rectangle([x1, y1, x2, y2], fill=color, outline=self._darken_color(color))
            elif shape_type == 'circle':
                draw.ellipse([x1, y1, x2, y2], fill=color, outline=self._darken_color(color))
            else:  # triangle
                points = [(x1, y1), (x2, y2), ((x1+x2)//2, y1-50)]
                draw.polygon(points, fill=color, outline=self._darken_color(color))

        return image

    def _generate_geometric_image(self, prompt: str, width: int, height: int) -> Image.Image:
        """
        Gera imagem com formas geométricas.
        """
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        prompt_hash = hash(prompt) % 1000
        random.seed(prompt_hash)

        # Grade geométrica
        cols = 3 + (prompt_hash % 4)
        rows = 3 + (prompt_hash % 4)

        cell_width = width // cols
        cell_height = height // rows

        for i in range(rows):
            for j in range(cols):
                color = random.choice(self.safe_colors)
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = (j + 1) * cell_width
                y2 = (i + 1) * cell_height

                # Forma baseada na posição
                if (i + j) % 3 == 0:
                    draw.rectangle([x1+10, y1+10, x2-10, y2-10], fill=color)
                elif (i + j) % 3 == 1:
                    draw.ellipse([x1+10, y1+10, x2-10, y2-10], fill=color)
                else:
                    # Triângulo
                    points = [(x1+cell_width//2, y1+10), (x1+10, y2-10), (x2-10, y2-10)]
                    draw.polygon(points, fill=color)

        return image

    def _generate_minimalist_image(self, prompt: str, width: int, height: int) -> Image.Image:
        """
        Gera imagem minimalista.
        """
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        prompt_hash = hash(prompt) % 1000
        random.seed(prompt_hash)

        # Fundo com gradiente sutil
        for y in range(height):
            r = int(255 * (1 - y/height * 0.1))
            g = int(255 * (1 - y/height * 0.1))
            b = int(255 * (1 - y/height * 0.1))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Poucos elementos
        num_elements = 2 + (prompt_hash % 3)

        for _ in range(num_elements):
            color = random.choice(self.safe_colors)
            center_x = random.randint(width//4, 3*width//4)
            center_y = random.randint(height//4, 3*height//4)
            size = random.randint(50, 150)

            # Círculo central
            draw.ellipse([center_x-size, center_y-size, center_x+size, center_y+size],
                        fill=color, outline=self._darken_color(color))

        return image

    def _generate_realistic_image(self, prompt: str, width: int, height: int) -> Image.Image:
        """
        Gera imagem "realista" simplificada (ainda abstrata, mas com tentativa de formas reconhecíveis).
        """
        image = Image.new('RGB', (width, height), color='#87CEEB')  # Céu azul
        draw = ImageDraw.Draw(image)

        prompt_hash = hash(prompt) % 1000
        random.seed(prompt_hash)

        # Tentar detectar elementos no prompt
        prompt_lower = prompt.lower()

        # Sol
        if 'sun' in prompt_lower or 'sky' in prompt_lower:
            draw.ellipse([width-150, 50, width-50, 150], fill='#FFD700')

        # Montanhas
        if 'mountain' in prompt_lower or 'hill' in prompt_lower:
            mountain_color = '#8B4513'
            points = [(0, height), (width//3, height//2), (2*width//3, height//3), (width, height)]
            draw.polygon(points, fill=mountain_color)

        # Árvore
        if 'tree' in prompt_lower or 'forest' in prompt_lower:
            tree_color = '#228B22'
            # Tronco
            draw.rectangle([width//2-20, height-200, width//2+20, height-100], fill='#8B4513')
            # Copa
            draw.ellipse([width//2-80, height-300, width//2+80, height-200], fill=tree_color)

        # Se nenhum elemento específico, gerar composição abstrata
        if not any(word in prompt_lower for word in ['sun', 'mountain', 'tree', 'sky']):
            return self._generate_abstract_image(prompt, width, height)

        return image

    def _darken_color(self, color: str) -> str:
        """
        Escurece uma cor para outline.
        """
        # Conversão simples de hex para RGB e escurecer
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, c - 50) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _save_metadata(self, image_id: str, metadata: Dict[str, Any]):
        """
        Salva metadados da imagem.
        """
        metadata_file = self.output_dir / f"{image_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def get_generated_images(self) -> List[Dict[str, Any]]:
        """
        Lista todas as imagens geradas.
        """
        images = []
        for metadata_file in self.output_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    images.append(metadata)
            except:
                continue
        return sorted(images, key=lambda x: x.get('generated_at', ''), reverse=True)
