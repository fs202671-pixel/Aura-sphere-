from typing import Dict, Optional

from .curriculum_manager import CurriculumManager
from .student_model import StudentModel


class TeachingEngine:
    """Responsável por explicar conteúdos e adaptar o ensino."""

    def __init__(self, student_model: StudentModel, curriculum_manager: CurriculumManager):
        self.student_model = student_model
        self.curriculum_manager = curriculum_manager

    def teach(self, topic: str) -> Dict[str, str]:
        profile = self.student_model.get_topic_profile(topic)
        plan = profile.get("active_plan")

        if plan is None:
            plan = self.curriculum_manager.generate_plan(topic, profile.get("level", 1))
            self.student_model.set_active_plan(topic, plan)

        progress = profile.get("correct", 0) + profile.get("incorrect", 0)
        step = self.curriculum_manager.get_current_step(plan, progress)
        explanation = self._explain_step(topic, step, profile.get("level", 1))
        exercise = self._build_example(step, profile.get("level", 1))

        return {
            "topic": topic,
            "level": str(profile.get("level", 1)),
            "lesson": step["title"],
            "explanation": explanation,
            "example": exercise,
        }

    def _explain_step(self, topic: str, step: Dict[str, str], level: int) -> str:
        title = step["title"]
        goals = ", ".join(step.get("goals", []))
        tone = self._adapt_language(level)
        return (
            f"Modo de ensino ativo para {topic}. {tone} Hoje vamos abordar '{title}'. "
            f"Neste trecho, você vai trabalhar: {goals}. "
            "Eu explicarei com exemplos claros e práticos, como um professor faria." 
        )

    def _build_example(self, step: Dict[str, str], level: int) -> str:
        goal = step.get("goals", ["conceito"])[0]
        if level <= 1:
            return f"Exemplo prático: vamos começar com uma explicação simples sobre {goal}."
        if level == 2:
            return f"Exemplo prático: agora vamos vivenciar {goal} com uma pequena tarefa guiada."
        return f"Exemplo prático avançado: aplique {goal} em um cenário mais complexo."

    def _adapt_language(self, level: int) -> str:
        if level == 1:
            return "Vou usar uma linguagem simples e exemplos fáceis de acompanhar."
        if level == 2:
            return "Vou manter o conteúdo claro, com exemplos mais concretos." 
        return "Vou apresentar o conteúdo com maior profundidade e relações avançadas." 

    def next_question(self, topic: str) -> str:
        profile = self.student_model.get_topic_profile(topic)
        plan = profile.get("active_plan")
        progress = profile.get("correct", 0) + profile.get("incorrect", 0)
        step = self.curriculum_manager.get_current_step(plan, progress)
        goal = step.get("goals", ["compreensão"])[0]
        return f"Pergunta de verificação: o que você entendeu sobre {goal}?" 
