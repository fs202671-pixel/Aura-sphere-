from typing import Dict, Optional

from .curriculum_manager import CurriculumManager
from .evaluation_engine import EvaluationEngine
from .session_manager import SessionManager
from .student_model import StudentModel
from .teaching_engine import TeachingEngine


class LearningController:
    """Controlador do modo de ensino sob demanda."""

    def __init__(self, persistence_base: Optional[str] = None):
        self.student_model = StudentModel(persistence_path=persistence_base)
        self.curriculum_manager = CurriculumManager()
        self.teaching_engine = TeachingEngine(self.student_model, self.curriculum_manager)
        self.evaluation_engine = EvaluationEngine(self.student_model, self.curriculum_manager)
        self.session_manager = SessionManager(persistence_path=persistence_base)

    def start_learning(self, topic: str) -> Dict[str, str]:
        """Ativa o modo de ensino para o tema solicitado."""
        self.session_manager.start_session(topic)
        profile = self.student_model.get_topic_profile(topic)
        plan = self.curriculum_manager.generate_plan(topic, profile.get("level", 1))
        self.student_model.set_active_plan(topic, plan)
        self.session_manager.add_session_entry(f"Sessão iniciada para {topic}")
        explanation = self.teaching_engine.teach(topic)
        return {
            "status": "started",
            "topic": topic,
            "learning_mode": True,
            "initial_lesson": explanation,
        }

    def teach(self, topic: str) -> Dict[str, str]:
        """Ensina o tópico atual se o modo de ensino estiver ativo."""
        if not self.session_manager.learning_mode:
            return {"status": "inactive", "message": "O modo de ensino não está ativo."}
        if topic.strip().lower() != (self.session_manager.current_topic or "").lower():
            return {"status": "error", "message": "Tópico diferente do tópico de aprendizagem ativo."}

        lesson = self.teaching_engine.teach(topic)
        self.session_manager.add_session_entry(f"Ensino aplicado: {lesson['lesson']}")
        return {"status": "teaching", **lesson}

    def evaluate(self, topic: str, user_input: str) -> Dict[str, str]:
        """Avalia a resposta do usuário e atualiza o progresso."""
        if not self.session_manager.learning_mode:
            return {"status": "inactive", "message": "O modo de ensino não está ativo."}
        if topic.strip().lower() != (self.session_manager.current_topic or "").lower():
            return {"status": "error", "message": "Tópico diferente do tópico de aprendizagem ativo."}

        result = self.evaluation_engine.evaluate(topic, user_input)
        self.session_manager.add_session_entry(f"Avaliação realizada: {result['outcome']}")
        return result

    def progress(self, topic: str) -> Dict[str, str]:
        """Retorna o progresso atual do usuário no tema."""
        if topic.strip().lower() != (self.session_manager.current_topic or "").lower():
            return {"status": "error", "message": "Tópico não corresponde à sessão ativa."}
        progress = self.student_model.get_progress(topic)
        return {"status": "progress", **progress}

    def stop_learning(self) -> Dict[str, str]:
        """Encerra o modo de ensino."""
        if not self.session_manager.learning_mode:
            return {"status": "inactive", "message": "O modo de ensino já está inativo."}
        topic = self.session_manager.current_topic
        self.session_manager.stop_session()
        self.session_manager.add_session_entry("Sessão finalizada")
        return {"status": "stopped", "topic": topic or "unknown", "learning_mode": False}

    def is_learning_active(self) -> bool:
        return self.session_manager.learning_mode


def example_usage() -> None:
    controller = LearningController()
    print(controller.start_learning("inglês"))
    print(controller.teach("inglês"))
    print(controller.evaluate("inglês", "Eu aprendi a saudar e usar frases simples."))
    print(controller.progress("inglês"))
    print(controller.stop_learning())


if __name__ == "__main__":
    example_usage()
