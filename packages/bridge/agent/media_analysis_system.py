"""
Sistema de Análise de Mídia - Análise multimodal básica

Este módulo implementa análise básica de imagens e vídeos usando PIL e bibliotecas padrão.
Em produção, seria substituído por modelos de IA avançados.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
import statistics
from PIL import Image, ImageStat
import colorsys
import math


class MediaAnalysisSystem:
    """
    Sistema básico de análise de mídia multimodal.

    Funcionalidades:
    - Análise de imagens (cores, composição, qualidade)
    - Detecção básica de objetos e padrões
    - Análise de vídeo (se suportado)
    - Geração de descrições textuais
    - Classificação de conteúdo
    - Detecção de anomalias visuais
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("media_analysis_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Configurações
        self.supported_image_formats = ['PNG', 'JPEG', 'JPG', 'BMP', 'TIFF', 'GIF']
        self.max_image_size = 4096
        self.analysis_timeout = 30  # segundos

        # Paletas de cores conhecidas para classificação
        self.color_palettes = {
            'warm': ['#FF6B6B', '#FFD93D', '#FF8E53', '#FF6B9D'],
            'cool': ['#4ECDC4', '#45B7D1', '#96CEB4', '#6C5CE7'],
            'neutral': ['#636E72', '#B2BEC3', '#DFE6E9', '#2D3436'],
            'nature': ['#00B894', '#00CEC9', '#55A3FF', '#A29BFE']
        }

    def analyze_media(self, media_path: str, analysis_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analisa mídia (imagem ou vídeo).

        Args:
            media_path: Caminho para o arquivo de mídia
            analysis_types: Tipos de análise a realizar

        Returns:
            Dict com resultados da análise
        """

        try:
            # Validar arquivo
            validation = self._validate_media_file(media_path)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["reason"],
                    "media_type": validation.get("media_type"),
                    "analysis": {}
                }

            media_type = validation["media_type"]

            # Tipos de análise padrão
            if analysis_types is None:
                if media_type == "image":
                    analysis_types = ["basic", "colors", "composition", "quality"]
                else:
                    analysis_types = ["basic", "content"]

            # Realizar análises
            analysis_results = {}

            if media_type == "image":
                analysis_results = self._analyze_image(media_path, analysis_types)
            elif media_type == "video":
                analysis_results = self._analyze_video(media_path, analysis_types)

            # Metadados gerais
            metadata = {
                "media_path": media_path,
                "media_type": media_type,
                "file_size": Path(media_path).stat().st_size,
                "analyzed_at": datetime.now().isoformat(),
                "analysis_types": analysis_types
            }

            return {
                "success": True,
                "media_type": media_type,
                "analysis": analysis_results,
                "metadata": metadata
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise de mídia: {str(e)}",
                "media_type": "unknown",
                "analysis": {}
            }

    def _validate_media_file(self, media_path: str) -> Dict[str, Any]:
        """
        Valida se o arquivo de mídia é suportado.
        """
        path = Path(media_path)

        if not path.exists():
            return {"valid": False, "reason": "Arquivo não encontrado", "media_type": "unknown"}

        if not path.is_file():
            return {"valid": False, "reason": "Caminho não é um arquivo", "media_type": "unknown"}

        # Tentar identificar tipo
        try:
            # Verificar se é imagem
            with Image.open(media_path) as img:
                if img.format in self.supported_image_formats:
                    # Verificar tamanho
                    if img.size[0] > self.max_image_size or img.size[1] > self.max_image_size:
                        return {"valid": False, "reason": f"Imagem muito grande (máx: {self.max_image_size}x{self.max_image_size})", "media_type": "image"}

                    return {"valid": True, "reason": "Arquivo válido", "media_type": "image"}

        except Exception:
            pass

        # Verificar extensões de vídeo (básico)
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        if path.suffix.lower() in video_extensions:
            return {"valid": True, "reason": "Arquivo de vídeo identificado", "media_type": "video"}

        return {"valid": False, "reason": "Formato de mídia não suportado", "media_type": "unknown"}

    def _analyze_image(self, image_path: str, analysis_types: List[str]) -> Dict[str, Any]:
        """
        Analisa uma imagem.
        """
        results = {}

        with Image.open(image_path) as img:
            # Análise básica
            if "basic" in analysis_types:
                results["basic"] = self._analyze_basic_properties(img)

            # Análise de cores
            if "colors" in analysis_types:
                results["colors"] = self._analyze_colors(img)

            # Análise de composição
            if "composition" in analysis_types:
                results["composition"] = self._analyze_composition(img)

            # Análise de qualidade
            if "quality" in analysis_types:
                results["quality"] = self._analyze_quality(img)

            # Detecção de objetos (básica)
            if "objects" in analysis_types:
                results["objects"] = self._detect_basic_objects(img)

            # Classificação de estilo
            if "style" in analysis_types:
                results["style"] = self._classify_style(img)

        return results

    def _analyze_basic_properties(self, img: Image.Image) -> Dict[str, Any]:
        """
        Analisa propriedades básicas da imagem.
        """
        stat = ImageStat.Stat(img)

        return {
            "dimensions": img.size,
            "mode": img.mode,
            "format": img.format,
            "has_alpha": img.mode == 'RGBA' or img.mode == 'LA',
            "aspect_ratio": img.size[0] / img.size[1] if img.size[1] > 0 else 0,
            "total_pixels": img.size[0] * img.size[1],
            "mean_color": stat.mean,
            "median_color": stat.median,
            "std_dev": stat.stddev
        }

    def _analyze_colors(self, img: Image.Image) -> Dict[str, Any]:
        """
        Analisa paleta de cores da imagem.
        """
        # Converter para RGB se necessário
        if img.mode != 'RGB':
            img_rgb = img.convert('RGB')
        else:
            img_rgb = img

        # Obter cores dominantes (simplificado)
        colors = img_rgb.getcolors(maxcolors=256)
        if not colors:
            return {"dominant_colors": [], "color_distribution": {}}

        # Ordenar por frequência
        colors.sort(key=lambda x: x[0], reverse=True)
        dominant_colors = colors[:10]

        # Classificar paleta
        palette_classification = self._classify_color_palette(dominant_colors)

        return {
            "dominant_colors": [{"color": color, "count": count} for count, color in dominant_colors],
            "total_colors": len(colors),
            "palette_type": palette_classification,
            "brightness_distribution": self._analyze_brightness_distribution(img_rgb),
            "saturation_distribution": self._analyze_saturation_distribution(img_rgb)
        }

    def _analyze_composition(self, img: Image.Image) -> Dict[str, Any]:
        """
        Analisa composição da imagem.
        """
        width, height = img.size

        # Dividir em regiões
        regions = {
            "top_left": (0, 0, width//2, height//2),
            "top_right": (width//2, 0, width, height//2),
            "bottom_left": (0, height//2, width//2, height),
            "bottom_right": (width//2, height//2, width, height)
        }

        region_analysis = {}
        for region_name, bbox in regions.items():
            region_img = img.crop(bbox)
            region_stat = ImageStat.Stat(region_img)
            region_analysis[region_name] = {
                "brightness": statistics.mean(region_stat.mean) / 255,
                "contrast": self._calculate_contrast(region_img),
                "detail_level": self._calculate_detail_level(region_img)
            }

        # Regra dos terços
        thirds_h = [width//3, 2*width//3]
        thirds_v = [height//3, 2*height//3]

        return {
            "regions": region_analysis,
            "rule_of_thirds_lines": {"horizontal": thirds_h, "vertical": thirds_v},
            "balance_score": self._calculate_balance_score(region_analysis),
            "symmetry_score": self._calculate_symmetry_score(img)
        }

    def _analyze_quality(self, img: Image.Image) -> Dict[str, Any]:
        """
        Analisa qualidade da imagem.
        """
        # Nitidez (simplificada)
        sharpness = self._calculate_sharpness(img)

        # Ruído (simplificado)
        noise_level = self._estimate_noise(img)

        # Compressão (se aplicável)
        compression_artifacts = self._detect_compression_artifacts(img)

        # Resolução efetiva
        effective_resolution = self._calculate_effective_resolution(img)

        quality_score = self._calculate_overall_quality(sharpness, noise_level, compression_artifacts)

        return {
            "sharpness": sharpness,
            "noise_level": noise_level,
            "compression_artifacts": compression_artifacts,
            "effective_resolution": effective_resolution,
            "overall_quality_score": quality_score,
            "quality_rating": self._quality_score_to_rating(quality_score)
        }

    def _detect_basic_objects(self, img: Image.Image) -> Dict[str, Any]:
        """
        Detecção básica de objetos (muito simplificada).
        """
        # Esta é uma implementação muito básica
        # Em produção, usaria modelos de IA reais

        width, height = img.size

        # Detectar formas simples baseadas em pixels
        img_gray = img.convert('L')
        pixels = list(img_gray.getdata())

        # Estatísticas básicas
        mean_brightness = statistics.mean(pixels)
        std_brightness = statistics.stdev(pixels) if len(pixels) > 1 else 0

        # Classificação simples baseada em padrões
        objects_detected = []

        if std_brightness > 50:  # Imagem com contraste
            if width > height:
                objects_detected.append({"type": "landscape", "confidence": 0.6})
            else:
                objects_detected.append({"type": "portrait", "confidence": 0.6})

        if mean_brightness < 100:
            objects_detected.append({"type": "dark_scene", "confidence": 0.7})
        elif mean_brightness > 200:
            objects_detected.append({"type": "bright_scene", "confidence": 0.7})

        return {
            "objects_detected": objects_detected,
            "detection_method": "basic_statistical_analysis",
            "confidence_threshold": 0.5
        }

    def _classify_style(self, img: Image.Image) -> Dict[str, Any]:
        """
        Classifica o estilo da imagem.
        """
        # Análise baseada em características visuais
        colors_analysis = self._analyze_colors(img)
        composition_analysis = self._analyze_composition(img)

        # Lógica simplificada de classificação
        styles = []

        # Verificar se é minimalista
        if len(colors_analysis.get("dominant_colors", [])) <= 3:
            styles.append({"style": "minimalist", "confidence": 0.8})

        # Verificar se é abstrato
        balance_score = composition_analysis.get("balance_score", 0.5)
        if balance_score < 0.3:
            styles.append({"style": "abstract", "confidence": 0.7})

        # Verificar se é realista (simplificado)
        quality_score = self._analyze_quality(img).get("overall_quality_score", 0.5)
        if quality_score > 0.7:
            styles.append({"style": "realistic", "confidence": 0.6})

        return {
            "detected_styles": styles,
            "primary_style": styles[0]["style"] if styles else "unknown",
            "classification_method": "feature_based_analysis"
        }

    def _analyze_video(self, video_path: str, analysis_types: List[str]) -> Dict[str, Any]:
        """
        Analisa um vídeo (implementação básica).
        """
        # Esta é uma implementação muito básica
        # Em produção, seria necessário FFmpeg ou bibliotecas de vídeo

        path = Path(video_path)

        return {
            "basic": {
                "file_size": path.stat().st_size,
                "extension": path.suffix,
                "estimated_duration": "unknown",  # Requer biblioteca de vídeo
                "codec": "unknown"  # Requer biblioteca de vídeo
            },
            "note": "Video analysis requires additional libraries (FFmpeg, OpenCV)",
            "supported_analysis": ["basic"]
        }

    # Métodos auxiliares para cálculos

    def _classify_color_palette(self, dominant_colors: List[Tuple[int, Tuple]]) -> str:
        """Classifica a paleta de cores dominante."""
        if not dominant_colors:
            return "unknown"

        # Lógica simplificada
        warm_count = 0
        cool_count = 0

        for _, color in dominant_colors[:5]:
            h, s, v = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
            if 0 <= h <= 0.1 or 0.9 <= h <= 1.0:  # Vermelho/amarelo
                warm_count += 1
            elif 0.4 <= h <= 0.7:  # Azul/verde
                cool_count += 1

        if warm_count > cool_count:
            return "warm"
        elif cool_count > warm_count:
            return "cool"
        else:
            return "neutral"

    def _analyze_brightness_distribution(self, img: Image.Image) -> Dict[str, float]:
        """Analisa distribuição de brilho."""
        gray_img = img.convert('L')
        pixels = list(gray_img.getdata())

        return {
            "mean": statistics.mean(pixels) / 255,
            "median": statistics.median(pixels) / 255,
            "std_dev": statistics.stdev(pixels) / 255 if len(pixels) > 1 else 0,
            "min": min(pixels) / 255,
            "max": max(pixels) / 255
        }

    def _analyze_saturation_distribution(self, img: Image.Image) -> Dict[str, float]:
        """Analisa distribuição de saturação."""
        hsv_img = img.convert('HSV')
        pixels = list(hsv_img.getdata())

        saturations = [pixel[1] for pixel in pixels]

        return {
            "mean": statistics.mean(saturations) / 255,
            "median": statistics.median(saturations) / 255,
            "std_dev": statistics.stdev(saturations) / 255 if len(saturations) > 1 else 0,
            "min": min(saturations) / 255,
            "max": max(saturations) / 255
        }

    def _calculate_contrast(self, img: Image.Image) -> float:
        """Calcula contraste da imagem."""
        gray_img = img.convert('L')
        pixels = list(gray_img.getdata())

        if not pixels:
            return 0

        mean = statistics.mean(pixels)
        variance = statistics.variance(pixels) if len(pixels) > 1 else 0

        return math.sqrt(variance) / 255  # Normalizado

    def _calculate_detail_level(self, img: Image.Image) -> float:
        """Calcula nível de detalhe (simplificado)."""
        gray_img = img.convert('L')

        # Calcular variação local
        width, height = gray_img.size
        total_variation = 0
        count = 0

        for y in range(1, height):
            for x in range(1, width):
                center = gray_img.getpixel((x, y))
                neighbors = [
                    gray_img.getpixel((x-1, y)),
                    gray_img.getpixel((x+1, y)),
                    gray_img.getpixel((x, y-1)),
                    gray_img.getpixel((x, y+1))
                ]
                variation = sum(abs(center - neighbor) for neighbor in neighbors) / 4
                total_variation += variation
                count += 1

        return total_variation / count / 255 if count > 0 else 0

    def _calculate_balance_score(self, region_analysis: Dict) -> float:
        """Calcula score de balanceamento."""
        brightness_values = [region["brightness"] for region in region_analysis.values()]
        return 1 - (statistics.stdev(brightness_values) if len(brightness_values) > 1 else 0)

    def _calculate_symmetry_score(self, img: Image.Image) -> float:
        """Calcula score de simetria (simplificado)."""
        width, height = img.size
        gray_img = img.convert('L')

        symmetry_score = 0
        comparisons = 0

        # Comparar pixels simétricos horizontalmente
        for y in range(height):
            for x in range(width // 2):
                left_pixel = gray_img.getpixel((x, y))
                right_pixel = gray_img.getpixel((width - 1 - x, y))
                symmetry_score += 1 - abs(left_pixel - right_pixel) / 255
                comparisons += 1

        return symmetry_score / comparisons if comparisons > 0 else 0

    def _calculate_sharpness(self, img: Image.Image) -> float:
        """Calcula nitidez da imagem."""
        gray_img = img.convert('L')

        # Usar filtro de Laplace para detectar edges
        edges = gray_img.filter(ImageFilter.FIND_EDGES)
        edge_pixels = list(edges.getdata())

        # Calcular variância dos pixels de edge
        mean_edge = statistics.mean(edge_pixels)
        variance = statistics.variance(edge_pixels) if len(edge_pixels) > 1 else 0

        return variance / (mean_edge + 1)  # Evitar divisão por zero

    def _estimate_noise(self, img: Image.Image) -> float:
        """Estima nível de ruído (simplificado)."""
        gray_img = img.convert('L')

        # Calcular diferença entre pixels adjacentes
        width, height = gray_img.size
        noise_sum = 0
        count = 0

        for y in range(1, height):
            for x in range(1, width):
                pixel = gray_img.getpixel((x, y))
                neighbors = [
                    gray_img.getpixel((x-1, y)),
                    gray_img.getpixel((x+1, y)),
                    gray_img.getpixel((x, y-1)),
                    gray_img.getpixel((x, y+1))
                ]
                avg_neighbor = statistics.mean(neighbors)
                noise_sum += abs(pixel - avg_neighbor)
                count += 1

        return noise_sum / count / 255 if count > 0 else 0

    def _detect_compression_artifacts(self, img: Image.Image) -> float:
        """Detecta artefatos de compressão (simplificado)."""
        # Esta é uma detecção muito básica
        # Em produção, seria necessário análise mais sofisticada

        if img.format == 'JPEG':
            # JPEG sempre tem algum artefato
            return 0.3
        elif img.format == 'PNG':
            # PNG lossless, menos artefatos
            return 0.1
        else:
            return 0.2

    def _calculate_effective_resolution(self, img: Image.Image) -> float:
        """Calcula resolução efetiva."""
        width, height = img.size
        pixel_count = width * height

        # Fator baseado na qualidade percebida
        quality_factor = self._calculate_sharpness(img) / 1000  # Normalizar

        return pixel_count * (0.5 + quality_factor)

    def _calculate_overall_quality(self, sharpness: float, noise: float, artifacts: float) -> float:
        """Calcula score geral de qualidade."""
        # Fórmula simplificada
        quality = (sharpness / 1000) * 0.5 + (1 - noise) * 0.3 + (1 - artifacts) * 0.2
        return max(0, min(1, quality))

    def _quality_score_to_rating(self, score: float) -> str:
        """Converte score para rating textual."""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        elif score >= 0.2:
            return "poor"
        else:
            return "very_poor"
