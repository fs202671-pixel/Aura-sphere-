from typing import Any, Dict, List


class CurriculumManager:
    """Gera planos de estudo adaptativos para qualquer tema."""

    def __init__(self):
        self.topic_templates = self._build_templates()

    def _build_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "inglês": [
                {"title": "vocabulário básico", "goals": ["saudar", "nomes comuns", "cores"]},
                {"title": "frases importantes", "goals": ["perguntas simples", "respostas", "expressões úteis"]},
                {"title": "gramática inicial", "goals": ["present simple", "pronomes", "preposições"]},
                {"title": "conversação básica", "goals": ["diálogo curto", "perguntas pessoais", "situações cotidianas"]},
            ],
            "estilo": [
                {"title": "tipos de roupa", "goals": ["casual", "formal", "moda diária"]},
                {"title": "combinação de cores", "goals": ["paletas básicas", "contrastando tons", "acessórios"]},
                {"title": "ocasiões", "goals": ["trabalho", "eventos sociais", "lazer"]},
                {"title": "identidade visual", "goals": ["roupa pessoal", "impressão desejada", "confiança"]},
            ],
            "programação": [
                {"title": "fundamentos", "goals": ["variáveis", "tipos", "fluxo de controle"]},
                {"title": "estruturas de dados", "goals": ["listas", "dicionários", "funções"]},
                {"title": "design de código", "goals": ["modularidade", "legibilidade", "documentação"]},
                {"title": "projeto prático", "goals": ["mini-projeto", "testes", "refatoração"]},
            ],
        }

    def generate_plan(self, topic: str, level: int = 1) -> Dict[str, Any]:
        topic_key = topic.strip().lower()
        template = self.topic_templates.get(topic_key)

        if template is None:
            return self._generate_generic_plan(topic)

        return {
            "topic": topic.strip(),
            "level": level,
            "steps": template,
        }

    def _generate_generic_plan(self, topic: str) -> Dict[str, Any]:
        title = topic.strip().lower()
        return {
            "topic": topic.strip(),
            "level": 1,
            "steps": [
                {"title": f"Introdução a {title}", "goals": ["entender a finalidade", "identificar conceitos básicos"]},
                {"title": f"Princípios centrais de {title}", "goals": ["descobrir termos-chave", "comparar exemplos"]},
                {"title": f"Aplicações práticas de {title}", "goals": ["criar um pequeno exercício", "analisar resultados"]},
                {"title": f"Melhorias e próximas etapas em {title}", "goals": ["planejar progresso", "definir objetivos"]},
            ],
        }

    def get_current_step(self, plan: Dict[str, Any], progress_count: int = 0) -> Dict[str, Any]:
        steps = plan.get("steps", [])
        if not steps:
            return {"title": "Plano não disponível", "goals": []}
        index = min(progress_count, len(steps) - 1)
        return steps[index]

    def describe_plan(self, plan: Dict[str, Any]) -> str:
        lines = [f"Plano de estudo para {plan['topic']} (nível {plan['level']}):"]
        for step in plan.get("steps", []):
            goals = ", ".join(step.get("goals", []))
            lines.append(f"- {step['title']}: {goals}")
        return "\n".join(lines)
