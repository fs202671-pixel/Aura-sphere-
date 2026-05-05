"""Agente principal do Aura Sphere - ponto de entrada do agente."""

from .service import get_agent_service
from .service import AgentService

__all__ = ["get_agent_service", "AgentService", "create_agent_service"]


def create_agent_service(user_id: str = "dev-user", agent_id: str = "aura-agent") -> AgentService:
    """Cria uma instância de serviço de agente."""
    return get_agent_service(user_id=user_id, agent_id=agent_id)


def run_agent(user_id: str = "dev-user", agent_id: str = "aura-agent") -> AgentService:
    """Inicializa o agente e retorna o serviço configurado."""
    service = create_agent_service(user_id=user_id, agent_id=agent_id)
    return service
