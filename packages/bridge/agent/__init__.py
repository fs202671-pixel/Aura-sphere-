"""
Módulo Agent - Sistema de Agentes Seguros

Este módulo implementa a arquitetura de agentes da Aura Sphere,
com foco em segurança, auditoria e controle de permissões.
"""

from typing import TYPE_CHECKING

from .logging import (
    AuditLogger,
    SecurityAuditor,
    LogEvent,
    LogLevel,
    audit_logger,
    security_auditor,
    log_agent_action,
    log_security_event,
    log_llm_call,
    get_audit_summary
)
if TYPE_CHECKING:
    from .service import AgentService, SessionTask, SessionState

from .tools import ToolRegistry
from .memory import MemoryStore
from .evolution import EvolutionManager
from .supervisor import AgentSupervisor
from .advanced_quality_evaluator import AdvancedQualityEvaluator, QualityEvolutionTracker
from .advanced_anomaly_detector import (
    BehavioralAnomalyDetector,
    AnomalyType,
    AnomalySeverity,
)
from .learning.learning_controller import LearningController
from .offline_scheduler import OfflineEvolutionScheduler
from .alternative_code_generator import AlternativeCodeGenerator


def __getattr__(name: str):
    if name in {"AgentService", "SessionTask", "SessionState", "get_agent_service"}:
        from .service import AgentService, SessionTask, SessionState, get_agent_service as _get_agent_service
        if name == "get_agent_service":
            return _get_agent_service
        return {
            "AgentService": AgentService,
            "SessionTask": SessionTask,
            "SessionState": SessionState,
        }[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    return [
        "AuditLogger",
        "SecurityAuditor",
        "LogEvent",
        "LogLevel",
        "audit_logger",
        "security_auditor",
        "log_agent_action",
        "log_security_event",
        "log_llm_call",
        "get_audit_summary",
        "get_agent_service",
        "ToolRegistry",
        "MemoryStore",
        "EvolutionManager",
        "AgentSupervisor",
        "AdvancedQualityEvaluator",
        "QualityEvolutionTracker",
        "BehavioralAnomalyDetector",
        "AnomalyType",
        "AnomalySeverity",
    "LearningController",
    "OfflineEvolutionScheduler",
    "AlternativeCodeGenerator",
    "SessionState",

    # Tooling
    "ToolRegistry",
    "MemoryStore",
    "EvolutionManager",
    "AgentSupervisor",
    "AdvancedQualityEvaluator",
    "QualityEvolutionTracker",

    # Enums
    "LogEvent",
    "LogLevel",

    # Instâncias globais
    "audit_logger",
    "security_auditor",

    # Funções de conveniência
    "log_agent_action",
    "log_security_event",
    "log_llm_call",
    "get_audit_summary",
    "get_agent_service",
]