"""
Módulo de Evolução de Estilo Criativo - Evolução adaptativa de estilos

Este módulo implementa um sistema de evolução de estilos criativos
que se adapta baseado no feedback e nas preferências do usuário.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import random
import statistics
from collections import defaultdict


class CreativeDomain(Enum):
    """Domínios criativos suportados."""
    WRITING = "writing"
    VISUAL_ART = "visual_art"
    MUSIC = "music"
    DESIGN = "design"
    CODE_STYLE = "code_style"
    PRESENTATION = "presentation"


class StyleParameter(Enum):
    """Parâmetros de estilo que podem evoluir."""
    TONE = "tone"              # Tom (formal, casual, humorístico, etc.)
    COMPLEXITY = "complexity"  # Complexidade (simples, moderado, complexo)
    LENGTH = "length"          # Comprimento (conciso, médio, detalhado)
    STRUCTURE = "structure"    # Estrutura (linear, hierárquico, modular)
    CREATIVITY = "creativity"  # Criatividade (conservador, balanceado, inovador)
    FORMALITY = "formality"    # Formalidade (informal, neutro, formal)
    DETAIL_LEVEL = "detail_level"  # Nível de detalhe
    PACE = "pace"              # Ritmo (lento, médio, rápido)


class StyleProfile:
    """
    Perfil de estilo criativo.
    """

    def __init__(self, domain: CreativeDomain, name: str = "",
                 parameters: Dict[StyleParameter, float] = None):
        self.domain = domain
        self.name = name or f"{domain.value}_style_{int(datetime.now().timestamp())}"
        self.parameters = parameters or {}

        # Inicializar parâmetros padrão se não fornecidos
        self._initialize_default_parameters()

        # Histórico de evolução
        self.evolution_history: List[Dict[str, Any]] = []
        self.feedback_history: List[Dict[str, Any]] = []

        # Métricas de performance
        self.usage_count = 0
        self.avg_satisfaction = 0.0
        self.success_rate = 0.0

        # Timestamps
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def _initialize_default_parameters(self) -> None:
        """Inicializa parâmetros padrão para o domínio."""

        defaults = {
            CreativeDomain.WRITING: {
                StyleParameter.TONE: 0.5,        # Neutro
                StyleParameter.COMPLEXITY: 0.5,   # Moderado
                StyleParameter.LENGTH: 0.5,       # Médio
                StyleParameter.CREATIVITY: 0.5,   # Balanceado
                StyleParameter.FORMALITY: 0.5,    # Neutro
                StyleParameter.DETAIL_LEVEL: 0.5  # Moderado
            },
            CreativeDomain.VISUAL_ART: {
                StyleParameter.COMPLEXITY: 0.6,   # Moderadamente complexo
                StyleParameter.CREATIVITY: 0.7,   # Inovador
                StyleParameter.DETAIL_LEVEL: 0.6  # Detalhado
            },
            CreativeDomain.CODE_STYLE: {
                StyleParameter.COMPLEXITY: 0.4,   # Simples
                StyleParameter.STRUCTURE: 0.7,    # Bem estruturado
                StyleParameter.FORMALITY: 0.6,    # Formal
                StyleParameter.DETAIL_LEVEL: 0.5  # Moderado
            }
        }

        domain_defaults = defaults.get(self.domain, {})
        for param, value in domain_defaults.items():
            if param not in self.parameters:
                self.parameters[param] = value

    def apply_feedback(self, feedback: Dict[str, Any]) -> None:
        """
        Aplica feedback para evoluir o estilo.
        """

        # Registrar feedback
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "previous_parameters": self.parameters.copy()
        }
        self.feedback_history.append(feedback_entry)

        # Extrair ajustes do feedback
        adjustments = self._extract_adjustments_from_feedback(feedback)

        # Aplicar ajustes com learning rate
        learning_rate = 0.1
        for param, adjustment in adjustments.items():
            if param in self.parameters:
                current_value = self.parameters[param]
                new_value = current_value + (adjustment * learning_rate)
                # Limitar entre 0 e 1
                self.parameters[param] = max(0.0, min(1.0, new_value))

        # Registrar evolução
        evolution_entry = {
            "timestamp": datetime.now().isoformat(),
            "adjustments": adjustments,
            "new_parameters": self.parameters.copy()
        }
        self.evolution_history.append(evolution_entry)

        # Atualizar métricas
        self._update_metrics(feedback)

        self.updated_at = datetime.now().isoformat()

    def _extract_adjustments_from_feedback(self, feedback: Dict[str, Any]) -> Dict[StyleParameter, float]:
        """
        Extrai ajustes dos parâmetros baseado no feedback.
        """

        adjustments = {}

        # Mapeamento de feedback para ajustes
        feedback_mapping = {
            "too_formal": {StyleParameter.FORMALITY: -0.2},
            "too_casual": {StyleParameter.FORMALITY: 0.2},
            "too_complex": {StyleParameter.COMPLEXITY: -0.2},
            "too_simple": {StyleParameter.COMPLEXITY: 0.2},
            "too_long": {StyleParameter.LENGTH: -0.2},
            "too_short": {StyleParameter.LENGTH: 0.2},
            "more_creative": {StyleParameter.CREATIVITY: 0.2},
            "less_creative": {StyleParameter.CREATIVITY: -0.2},
            "more_detailed": {StyleParameter.DETAIL_LEVEL: 0.2},
            "less_detailed": {StyleParameter.DETAIL_LEVEL: -0.2},
            "better_structure": {StyleParameter.STRUCTURE: 0.1},
            "faster_pace": {StyleParameter.PACE: 0.2},
            "slower_pace": {StyleParameter.PACE: -0.2}
        }

        # Processar feedback textual
        feedback_text = feedback.get("comments", "").lower()

        for keyword, param_adjustments in feedback_mapping.items():
            if keyword in feedback_text:
                for param, adjustment in param_adjustments.items():
                    adjustments[param] = adjustments.get(param, 0) + adjustment

        # Processar ratings numéricos
        satisfaction = feedback.get("satisfaction", 0.5)
        if satisfaction < 0.3:
            # Baixa satisfação - aumentar criatividade e variação
            adjustments[StyleParameter.CREATIVITY] = adjustments.get(StyleParameter.CREATIVITY, 0) + 0.1
        elif satisfaction > 0.7:
            # Alta satisfação - manter tendência atual
            pass  # Não fazer ajustes drásticos

        return adjustments

    def _update_metrics(self, feedback: Dict[str, Any]) -> None:
        """Atualiza métricas baseado no feedback."""

        self.usage_count += 1

        # Atualizar satisfação média
        satisfaction = feedback.get("satisfaction", 0.5)
        self.avg_satisfaction = ((self.avg_satisfaction * (self.usage_count - 1)) + satisfaction) / self.usage_count

        # Atualizar taxa de sucesso
        success = 1 if satisfaction >= 0.6 else 0
        self.success_rate = ((self.success_rate * (self.usage_count - 1)) + success) / self.usage_count

    def get_parameter_value(self, parameter: StyleParameter) -> float:
        """Retorna valor de parâmetro."""
        return self.parameters.get(parameter, 0.5)

    def get_style_description(self) -> str:
        """Retorna descrição textual do estilo."""

        descriptions = []

        # Descrições baseadas nos parâmetros
        tone = self.get_parameter_value(StyleParameter.TONE)
        if tone < 0.3:
            descriptions.append("conservative")
        elif tone > 0.7:
            descriptions.append("bold")
        else:
            descriptions.append("balanced")

        formality = self.get_parameter_value(StyleParameter.FORMALITY)
        if formality < 0.3:
            descriptions.append("informal")
        elif formality > 0.7:
            descriptions.append("formal")
        else:
            descriptions.append("neutral")

        complexity = self.get_parameter_value(StyleParameter.COMPLEXITY)
        if complexity < 0.3:
            descriptions.append("simple")
        elif complexity > 0.7:
            descriptions.append("complex")
        else:
            descriptions.append("moderate")

        creativity = self.get_parameter_value(StyleParameter.CREATIVITY)
        if creativity < 0.3:
            descriptions.append("practical")
        elif creativity > 0.7:
            descriptions.append("innovative")
        else:
            descriptions.append("balanced")

        return ", ".join(descriptions)


class CreativeStyleEvolution:
    """
    Sistema de evolução de estilos criativos.

    Funcionalidades:
    - Múltiplos perfis de estilo por domínio
    - Evolução baseada em feedback
    - Recomendação de estilos apropriados
    - Análise de tendências criativas
    - Backup e restauração de estilos
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.styles_dir = data_dir / "creative_styles"
        self.styles_dir.mkdir(parents=True, exist_ok=True)

        self.styles_file = self.styles_dir / "style_profiles.json"
        self.feedback_file = self.styles_dir / "style_feedback.json"

        self.style_profiles: Dict[str, StyleProfile] = {}
        self.feedback_history: List[Dict[str, Any]] = []

        # Configurações
        self.max_profiles_per_domain = 10
        self.learning_rate = 0.1
        self.feedback_retention_days = 30

        self._load_styles()

    def create_style_profile(self, domain: CreativeDomain, name: str = "",
                           base_parameters: Dict[StyleParameter, float] = None) -> str:
        """
        Cria novo perfil de estilo.
        """

        profile = StyleProfile(domain, name, base_parameters)
        self.style_profiles[profile.name] = profile

        self._save_styles()
        return profile.name

    def get_style_profile(self, profile_name: str) -> Optional[StyleProfile]:
        """Retorna perfil de estilo."""
        return self.style_profiles.get(profile_name)

    def apply_feedback_to_style(self, profile_name: str, feedback: Dict[str, Any]) -> bool:
        """
        Aplica feedback a um perfil de estilo.
        """

        profile = self.style_profiles.get(profile_name)
        if not profile:
            return False

        profile.apply_feedback(feedback)

        # Registrar feedback global
        feedback_entry = {
            "profile_name": profile_name,
            "domain": profile.domain.value,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        self.feedback_history.append(feedback_entry)

        self._save_styles()
        return True

    def recommend_style_for_task(self, domain: CreativeDomain,
                               task_description: str) -> List[Tuple[str, float]]:
        """
        Recomenda estilos apropriados para uma tarefa.
        """

        # Filtrar perfis do domínio
        domain_profiles = [(name, profile) for name, profile in self.style_profiles.items()
                          if profile.domain == domain]

        if not domain_profiles:
            return []

        recommendations = []

        for name, profile in domain_profiles:
            # Calcular adequação baseada em métricas do perfil
            suitability_score = self._calculate_task_suitability(profile, task_description)
            recommendations.append((name, suitability_score))

        # Ordenar por adequação
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:5]  # Top 5

    def _calculate_task_suitability(self, profile: StyleProfile, task_description: str) -> float:
        """
        Calcula adequação de um perfil para uma tarefa.
        """

        score = 0.0

        # Baseado na satisfação histórica
        score += profile.avg_satisfaction * 0.4

        # Baseado na taxa de sucesso
        score += profile.success_rate * 0.3

        # Baseado no uso recente (perfis usados recentemente são preferidos)
        days_since_update = (datetime.now() - datetime.fromisoformat(profile.updated_at)).days
        recency_score = max(0, 1 - (days_since_update / 30))  # Decai em 30 dias
        score += recency_score * 0.3

        # Ajustes baseados na descrição da tarefa
        task_lower = task_description.lower()

        if "creative" in task_lower or "inovative" in task_lower:
            score += profile.get_parameter_value(StyleParameter.CREATIVITY) * 0.1

        if "formal" in task_lower or "professional" in task_lower:
            score += profile.get_parameter_value(StyleParameter.FORMALITY) * 0.1

        if "simple" in task_lower or "basic" in task_lower:
            score += (1 - profile.get_parameter_value(StyleParameter.COMPLEXITY)) * 0.1

        return min(score, 1.0)

    def evolve_style_population(self) -> Dict[str, Any]:
        """
        Evolui a população de estilos através de algoritmos genéticos.
        """

        evolution_results = {
            "new_styles_created": 0,
            "styles_evolved": 0,
            "performance_improvements": {}
        }

        for domain in CreativeDomain:
            domain_profiles = [(name, profile) for name, profile in self.style_profiles.items()
                              if profile.domain == domain]

            if len(domain_profiles) < 2:
                continue  # Precisa de pelo menos 2 perfis para crossover

            # Identificar melhores performers
            sorted_profiles = sorted(domain_profiles,
                                   key=lambda x: x[1].avg_satisfaction,
                                   reverse=True)

            # Criar descendentes dos melhores
            if len(sorted_profiles) >= 2:
                parent1 = sorted_profiles[0][1]
                parent2 = sorted_profiles[1][1]

                # Crossover
                child_profile = self._create_child_style(domain, parent1, parent2)
                if child_profile:
                    self.style_profiles[child_profile.name] = child_profile
                    evolution_results["new_styles_created"] += 1

            # Mutação dos perfis existentes (baixa probabilidade)
            for name, profile in domain_profiles:
                if random.random() < 0.1:  # 10% de chance
                    self._mutate_style(profile)
                    evolution_results["styles_evolved"] += 1

        self._save_styles()
        return evolution_results

    def _create_child_style(self, domain: CreativeDomain,
                           parent1: StyleProfile, parent2: StyleProfile) -> Optional[StyleProfile]:
        """
        Cria novo estilo através de crossover de dois parentes.
        """

        child_params = {}

        # Crossover: média dos parâmetros dos parentes
        all_params = set(parent1.parameters.keys()) | set(parent2.parameters.keys())

        for param in all_params:
            val1 = parent1.parameters.get(param, 0.5)
            val2 = parent2.parameters.get(param, 0.5)
            child_params[param] = (val1 + val2) / 2

        # Adicionar pequena variação
        for param in child_params:
            child_params[param] += random.uniform(-0.1, 0.1)
            child_params[param] = max(0.0, min(1.0, child_params[param]))

        child_name = f"{domain.value}_evolved_{int(datetime.now().timestamp())}"
        return StyleProfile(domain, child_name, child_params)

    def _mutate_style(self, profile: StyleProfile) -> None:
        """
        Aplica mutação a um perfil de estilo.
        """

        # Mutar alguns parâmetros aleatoriamente
        params_to_mutate = random.sample(list(profile.parameters.keys()),
                                       k=random.randint(1, len(profile.parameters)))

        for param in params_to_mutate:
            mutation = random.uniform(-0.2, 0.2)
            profile.parameters[param] += mutation
            profile.parameters[param] = max(0.0, min(1.0, profile.parameters[param]))

        profile.updated_at = datetime.now().isoformat()

    def get_style_analytics(self) -> Dict[str, Any]:
        """Retorna análise dos estilos."""

        analytics = {
            "total_profiles": len(self.style_profiles),
            "domain_distribution": defaultdict(int),
            "avg_satisfaction_by_domain": {},
            "most_used_styles": [],
            "evolution_trends": {}
        }

        # Distribuição por domínio
        for profile in self.style_profiles.values():
            analytics["domain_distribution"][profile.domain.value] += 1

        # Satisfação média por domínio
        domain_satisfactions = defaultdict(list)
        for profile in self.style_profiles.values():
            domain_satisfactions[profile.domain].append(profile.avg_satisfaction)

        for domain, satisfactions in domain_satisfactions.items():
            analytics["avg_satisfaction_by_domain"][domain.value] = statistics.mean(satisfactions)

        # Estilos mais usados
        sorted_profiles = sorted(self.style_profiles.items(),
                               key=lambda x: x[1].usage_count,
                               reverse=True)
        analytics["most_used_styles"] = [(name, profile.usage_count)
                                       for name, profile in sorted_profiles[:5]]

        return dict(analytics)

    def export_style_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Exporta perfil de estilo para compartilhamento."""

        profile = self.style_profiles.get(profile_name)
        if not profile:
            return None

        return {
            "domain": profile.domain.value,
            "name": profile.name,
            "parameters": profile.parameters,
            "description": profile.get_style_description(),
            "metrics": {
                "usage_count": profile.usage_count,
                "avg_satisfaction": profile.avg_satisfaction,
                "success_rate": profile.success_rate
            },
            "exported_at": datetime.now().isoformat()
        }

    def import_style_profile(self, style_data: Dict[str, Any]) -> bool:
        """
        Importa perfil de estilo.
        """

        try:
            domain = CreativeDomain(style_data["domain"])
            name = style_data["name"]
            parameters = {StyleParameter(k): v for k, v in style_data["parameters"].items()}

            # Verificar se já existe
            if name in self.style_profiles:
                name = f"{name}_imported_{int(datetime.now().timestamp())}"

            profile = StyleProfile(domain, name, parameters)
            self.style_profiles[name] = profile

            self._save_styles()
            return True

        except Exception as e:
            print(f"Error importing style: {e}")
            return False

    def _load_styles(self) -> None:
        """Carrega perfis de estilo do disco."""

        if self.styles_file.exists():
            try:
                styles_data = json.loads(self.styles_file.read_text(encoding='utf-8'))

                for style_data in styles_data.get("profiles", []):
                    domain = CreativeDomain(style_data["domain"])
                    profile = StyleProfile(domain, style_data["name"], style_data["parameters"])

                    # Restaurar dados adicionais
                    profile.evolution_history = style_data.get("evolution_history", [])
                    profile.feedback_history = style_data.get("feedback_history", [])
                    profile.usage_count = style_data.get("usage_count", 0)
                    profile.avg_satisfaction = style_data.get("avg_satisfaction", 0.0)
                    profile.success_rate = style_data.get("success_rate", 0.0)
                    profile.created_at = style_data.get("created_at", profile.created_at)
                    profile.updated_at = style_data.get("updated_at", profile.updated_at)

                    self.style_profiles[profile.name] = profile

            except Exception as e:
                print(f"Error loading styles: {e}")

        # Carregar feedback
        if self.feedback_file.exists():
            try:
                self.feedback_history = json.loads(self.feedback_file.read_text(encoding='utf-8'))
            except Exception:
                self.feedback_history = []

    def _save_styles(self) -> None:
        """Salva perfis de estilo no disco."""

        self.styles_dir.mkdir(parents=True, exist_ok=True)

        # Serializar perfis
        profiles_data = []
        for profile in self.style_profiles.values():
            profiles_data.append({
                "domain": profile.domain.value,
                "name": profile.name,
                "parameters": {k.value: v for k, v in profile.parameters.items()},
                "evolution_history": profile.evolution_history,
                "feedback_history": profile.feedback_history,
                "usage_count": profile.usage_count,
                "avg_satisfaction": profile.avg_satisfaction,
                "success_rate": profile.success_rate,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at
            })

        styles_data = {
            "profiles": profiles_data,
            "last_updated": datetime.now().isoformat()
        }

        self.styles_file.write_text(
            json.dumps(styles_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Salvar feedback
        self.feedback_file.write_text(
            json.dumps(self.feedback_history[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
