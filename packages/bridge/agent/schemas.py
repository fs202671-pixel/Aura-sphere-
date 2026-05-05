"""Definições de esquemas de dados para o agente."""

from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class AgentProfile:
    user_id: str
    agent_id: str
    ai_name: str
    voice_id: Optional[str] = None
    onboarded: bool = False


@dataclass
class AgentTask:
    id: str
    description: str
    status: str = "pending"
    created_at: str = ""
    completed_at: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class AgentSession:
    user_id: str
    agent_id: str
    tasks: List[AgentTask]
    last_active: str
