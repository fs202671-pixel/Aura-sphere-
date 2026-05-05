"""Módulo de aprendizagem adaptativa sob demanda."""

from .learning_controller import LearningController
from .student_model import StudentModel
from .curriculum_manager import CurriculumManager
from .teaching_engine import TeachingEngine
from .evaluation_engine import EvaluationEngine
from .session_manager import SessionManager

__all__ = [
    "LearningController",
    "StudentModel",
    "CurriculumManager",
    "TeachingEngine",
    "EvaluationEngine",
    "SessionManager",
]
