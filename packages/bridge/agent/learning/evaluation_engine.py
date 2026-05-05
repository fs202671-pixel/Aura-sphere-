import re
from enum import Enum
from typing import Dict, List, Optional

from .student_model import StudentModel
from .curriculum_manager import CurriculumManager


class EvaluationOutcome(Enum):
    CORRETA = "correta"
    PARCIAL = "parcial"
    ERRADA = "errada"


class EvaluationEngine:
    """Avalia respostas e ajusta o perfil do aluno."""

    def __init__(self, student_model: StudentModel, curriculum_manager: CurriculumManager):
        self.student_model = student_model
        self.curriculum_manager = curriculum_manager

    def evaluate(self, topic: str, user_input: str) -> Dict[str, str]:
        profile = self.student_model.get_topic_profile(topic)
        plan = profile.get("active_plan") or self.curriculum_manager.generate_plan(topic, profile.get("level", 1))
        progress = profile.get("correct", 0) + profile.get("incorrect", 0)
        step = self.curriculum_manager.get_current_step(plan, progress)
        expected_keywords = step.get("goals", [])

        result = self._assess_response(user_input, expected_keywords)
        feedback = self._build_feedback(result, expected_keywords)

        self.student_model.update_performance(
            topic,
            correct=(result == EvaluationOutcome.CORRETA),
            feedback=f"Avaliação: {result.value} - {feedback}",
            weaknesses=[] if result == EvaluationOutcome.CORRETA else [expected_keywords[0] if expected_keywords else "compreensão"]
        )

        return {
            "topic": topic,
            "outcome": result.value,
            "feedback": feedback,
            "current_level": str(profile.get("level", 1)),
        }

    def _assess_response(self, user_input: str, expected_keywords: List[str]) -> EvaluationOutcome:
        normalized = user_input.lower()
        matches = sum(1 for keyword in expected_keywords if re.search(re.escape(keyword.lower()), normalized))
        if matches >= len(expected_keywords) * 0.6:
            return EvaluationOutcome.CORRETA
        if matches >= 1:
            return EvaluationOutcome.PARCIAL
        return EvaluationOutcome.ERRADA

    def _build_feedback(self, result: EvaluationOutcome, expected_keywords: List[str]) -> str:
        if result == EvaluationOutcome.CORRETA:
            return "Muito bem! Sua resposta cobre os pontos principais." 
        if result == EvaluationOutcome.PARCIAL:
            return (
                "Você está no caminho certo, mas ainda precisa desenvolver alguns pontos. "
                f"Tente focar em: {', '.join(expected_keywords[:2])}."
            )
        return (
            "A resposta está incompleta. Vamos revisar a ideia principal e tentar novamente. "
            f"Preste atenção em: {', '.join(expected_keywords[:2])}."
        )
