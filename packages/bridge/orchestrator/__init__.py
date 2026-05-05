"""
Módulo Orchestrator - Coordenação Central da Inteligência Coletiva

Este módulo implementa o orquestrador central que coordena os agentes
da inteligência coletiva: formigas (exploradores), abelhas (executores)
e lobos (defensores).

O orquestrador não executa tarefas diretamente - apenas coordena e
consolida resultados dos agentes especializados.
"""

from .central_orchestrator import CentralOrchestrator, OrchestratorResult, get_central_orchestrator

__version__ = "0.1.0"
__all__ = [
    "CentralOrchestrator",
    "OrchestratorResult",
    "get_central_orchestrator",
]