"""
Orquestrador Central - Coordenação da Inteligência Coletiva

Este módulo implementa o orquestrador central que coordena as operações
entre formigas (exploradores), abelhas (executores) e lobos (defensores).

Fluxo típico:
1. Recebe comando do usuário
2. Divide em subtarefas
3. Envia formigas para exploração
4. Coordena abelhas para execução
5. Ativa lobos se detectar risco
6. Consolida resultados
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pathlib import Path

from agent.logging import audit_logger, log_agent_action, LogEvent, LogLevel
from colony.ants.coordinator import AntCoordinator
from hive.bees.coordinator import BeeCoordinator
from wolves.sentinel import WolfSentinel
from agent.memory import MemoryStore
from core.user_obedience import UserObedienceManager


class TaskType(Enum):
    """Tipos de tarefas que o orquestrador pode coordenar"""
    EXPLORATION = "exploration"      # Exploração e descoberta
    EXECUTION = "execution"          # Execução estruturada
    ANALYSIS = "analysis"           # Análise de dados/código
    VALIDATION = "validation"       # Validação e testes
    DEFENSE = "defense"             # Resposta a incidentes


class TaskPriority(Enum):
    """Prioridades das tarefas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class OrchestratorTask:
    """Tarefa coordenada pelo orquestrador"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: TaskType = TaskType.EXECUTION
    priority: TaskPriority = TaskPriority.MEDIUM
    description: str = ""
    user_command: str = ""
    subtasks: List[Dict[str, Any]] = field(default_factory=list)
    assigned_agents: Dict[str, List[str]] = field(default_factory=dict)  # agent_type -> agent_ids
    results: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, exploring, executing, validating, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    risk_level: str = "low"  # low, medium, high, critical
    consolidated_result: Optional[Dict[str, Any]] = None


@dataclass
class OrchestratorResult:
    """Resultado consolidado de uma tarefa orquestrada"""
    task_id: str
    success: bool
    result: Dict[str, Any]
    agent_contributions: Dict[str, List[Dict[str, Any]]]
    risk_assessment: Dict[str, Any]
    execution_time: float
    consolidated_summary: str


class CentralOrchestrator:
    """
    Orquestrador Central da Inteligência Coletiva

    Coordena operações entre:
    - Formigas (colony/ants): exploração e descoberta
    - Abelhas (hive/bees): execução estruturada
    - Lobos (wolves): defesa e resposta a incidentes
    """

    def __init__(self):
        self.memory = MemoryStore()
        self.ant_coordinator = AntCoordinator()
        self.bee_coordinator = BeeCoordinator()
        self.wolf_sentinel = WolfSentinel()
        self.user_obedience = UserObedienceManager()
        self.active_tasks: Dict[str, OrchestratorTask] = {}
        self.task_history: List[OrchestratorTask] = []

    async def process_user_command(self, command: str, user_id: str = "system") -> OrchestratorResult:
        """
        Processa um comando do usuário através da inteligência coletiva

        Args:
            command: Comando do usuário
            user_id: ID do usuário (para auditoria)

        Returns:
            Resultado consolidado da execução
        """
        # Verificar obediência ao usuário
        obedience_check = await self.user_obedience.validate_command(command)
        if not obedience_check["allowed"]:
            await audit_logger.log_event(
                LogEvent(
                    event_type="orchestrator_command_rejected",
                    level=LogLevel.WARNING,
                    message=f"Comando rejeitado por violação de obediência: {command}",
                    details={"command": command, "reason": obedience_check["reason"]}
                )
            )
            return OrchestratorResult(
                task_id="rejected",
                success=False,
                result={"error": "Comando rejeitado", "reason": obedience_check["reason"]},
                agent_contributions={},
                risk_assessment={"level": "high", "reason": "Violação de obediência"},
                execution_time=0.0,
                consolidated_summary=f"Comando rejeitado: {obedience_check['reason']}"
            )

        # Criar tarefa orquestrada
        task = OrchestratorTask(
            type=self._classify_command_type(command),
            priority=self._assess_command_priority(command),
            description=f"Processamento coletivo do comando: {command}",
            user_command=command
        )

        self.active_tasks[task.id] = task
        start_time = datetime.now()

        try:
            # Fase 1: Dividir tarefa em subtarefas
            subtasks = await self._divide_into_subtasks(command, task.type)
            task.subtasks = subtasks

            # Fase 2: Enviar formigas para exploração
            exploration_results = await self._coordinate_exploration(task)

            # Fase 3: Avaliar riscos com lobos
            risk_assessment = await self._assess_risks(task, exploration_results)
            task.risk_level = risk_assessment["level"]

            # Fase 4: Coordenar abelhas para execução (se risco aceitável)
            if risk_assessment["level"] in ["low", "medium"]:
                execution_results = await self._coordinate_execution(task, exploration_results)
            else:
                # Ativar lobos para contenção se risco alto
                await self._activate_defense(task, risk_assessment)
                execution_results = {"error": "Execução bloqueada por alto risco"}

            # Fase 5: Consolidar resultados
            consolidated = await self._consolidate_results(task, exploration_results, execution_results, risk_assessment)

            task.status = "completed"
            task.completed_at = datetime.now()
            task.consolidated_result = consolidated

            execution_time = (datetime.now() - start_time).total_seconds()

            result = OrchestratorResult(
                task_id=task.id,
                success=consolidated["success"],
                result=consolidated["result"],
                agent_contributions={
                    "ants": exploration_results,
                    "bees": execution_results if isinstance(execution_results, list) else [],
                    "wolves": risk_assessment
                },
                risk_assessment=risk_assessment,
                execution_time=execution_time,
                consolidated_summary=consolidated["summary"]
            )

            # Registrar na memória e auditoria
            await self._record_task_completion(task, result)

            return result

        except Exception as e:
            task.status = "failed"
            task.completed_at = datetime.now()

            await audit_logger.log_event(
                LogEvent(
                    event_type="orchestrator_task_failed",
                    level=LogLevel.ERROR,
                    message=f"Tarefa orquestrada falhou: {str(e)}",
                    details={"task_id": task.id, "error": str(e)}
                )
            )

            return OrchestratorResult(
                task_id=task.id,
                success=False,
                result={"error": str(e)},
                agent_contributions={},
                risk_assessment={"level": "unknown", "error": str(e)},
                execution_time=(datetime.now() - start_time).total_seconds(),
                consolidated_summary=f"Falha na orquestração: {str(e)}"
            )

    def _classify_command_type(self, command: str) -> TaskType:
        """Classifica o tipo de comando"""
        command_lower = command.lower()

        if any(word in command_lower for word in ["explore", "search", "find", "discover"]):
            return TaskType.EXPLORATION
        elif any(word in command_lower for word in ["execute", "run", "implement", "create"]):
            return TaskType.EXECUTION
        elif any(word in command_lower for word in ["analyze", "review", "check", "validate"]):
            return TaskType.ANALYSIS
        elif any(word in command_lower for word in ["test", "verify", "confirm"]):
            return TaskType.VALIDATION
        else:
            return TaskType.EXECUTION  # default

    def _assess_command_priority(self, command: str) -> TaskPriority:
        """Avalia a prioridade do comando"""
        command_lower = command.lower()

        if any(word in command_lower for word in ["critical", "urgent", "emergency", "security"]):
            return TaskPriority.CRITICAL
        elif any(word in command_lower for word in ["important", "high", "priority"]):
            return TaskPriority.HIGH
        elif any(word in command_lower for word in ["medium", "normal"]):
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.MEDIUM  # default

    async def _divide_into_subtasks(self, command: str, task_type: TaskType) -> List[Dict[str, Any]]:
        """Divide o comando em subtarefas apropriadas"""
        # Análise simples - pode ser expandida com IA
        subtasks = []

        if task_type == TaskType.EXPLORATION:
            subtasks = [
                {"type": "search_repositories", "description": "Buscar informações em repositórios"},
                {"type": "analyze_patterns", "description": "Analisar padrões e tendências"},
                {"type": "gather_intelligence", "description": "Coletar dados relevantes"}
            ]
        elif task_type == TaskType.EXECUTION:
            subtasks = [
                {"type": "plan_execution", "description": "Planejar execução estruturada"},
                {"type": "coordinate_resources", "description": "Coordenar recursos necessários"},
                {"type": "execute_steps", "description": "Executar passos planejados"}
            ]
        elif task_type == TaskType.ANALYSIS:
            subtasks = [
                {"type": "collect_data", "description": "Coletar dados para análise"},
                {"type": "analyze_content", "description": "Analisar conteúdo coletado"},
                {"type": "generate_insights", "description": "Gerar insights e recomendações"}
            ]
        elif task_type == TaskType.VALIDATION:
            subtasks = [
                {"type": "setup_tests", "description": "Configurar testes de validação"},
                {"type": "run_validations", "description": "Executar validações"},
                {"type": "verify_results", "description": "Verificar e confirmar resultados"}
            ]

        return subtasks

    async def _coordinate_exploration(self, task: OrchestratorTask) -> List[Dict[str, Any]]:
        """Coordena formigas para exploração"""
        exploration_results = []

        try:
            # Enviar formigas para explorar cada subtarefa
            for subtask in task.subtasks:
                ant_results = await self.ant_coordinator.explore_subtask(subtask, task.user_command)
                exploration_results.extend(ant_results)

            task.assigned_agents["ants"] = [r.get("ant_id", "unknown") for r in exploration_results]

        except Exception as e:
            await audit_logger.log_event(
                LogEvent(
                    event_type="orchestrator_exploration_failed",
                    level=LogLevel.ERROR,
                    message=f"Falha na exploração: {str(e)}",
                    details={"task_id": task.id, "error": str(e)}
                )
            )

        return exploration_results

    async def _assess_risks(self, task: OrchestratorTask, exploration_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia riscos com lobos sentinelas"""
        try:
            risk_assessment = await self.wolf_sentinel.assess_task_risk(task, exploration_results)
            task.assigned_agents["wolves"] = ["sentinel"]
            return risk_assessment
        except Exception as e:
            await audit_logger.log_event(
                LogEvent(
                    event_type="orchestrator_risk_assessment_failed",
                    level=LogLevel.ERROR,
                    message=f"Falha na avaliação de risco: {str(e)}",
                    details={"task_id": task.id, "error": str(e)}
                )
            )
            return {"level": "unknown", "error": str(e)}

    async def _coordinate_execution(self, task: OrchestratorTask, exploration_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Coordena abelhas para execução"""
        execution_results = []

        try:
            # Coordenar abelhas para executar baseado nos resultados da exploração
            bee_results = await self.bee_coordinator.execute_from_exploration(task, exploration_results)
            execution_results = bee_results

            task.assigned_agents["bees"] = [r.get("bee_id", "unknown") for r in execution_results if isinstance(r, dict)]

        except Exception as e:
            await audit_logger.log_event(
                LogEvent(
                    event_type="orchestrator_execution_failed",
                    level=LogLevel.ERROR,
                    message=f"Falha na execução: {str(e)}",
                    details={"task_id": task.id, "error": str(e)}
                )
            )

        return execution_results

    async def _activate_defense(self, task: OrchestratorTask, risk_assessment: Dict[str, Any]):
        """Ativa lobos para defesa se risco alto"""
        try:
            await self.wolf_sentinel.activate_defense_measures(task, risk_assessment)

            await audit_logger.log_event(
                LogEvent(
                    event_type="orchestrator_defense_activated",
                    level=LogLevel.WARNING,
                    message=f"Defesa ativada para tarefa de alto risco: {task.id}",
                    details={"task_id": task.id, "risk_level": risk_assessment["level"]}
                )
            )

        except Exception as e:
            await audit_logger.log_event(
                LogEvent(
                    event_type="orchestrator_defense_activation_failed",
                    level=LogLevel.ERROR,
                    message=f"Falha ao ativar defesa: {str(e)}",
                    details={"task_id": task.id, "error": str(e)}
                )
            )

    async def _consolidate_results(self, task: OrchestratorTask,
                                 exploration_results: List[Dict[str, Any]],
                                 execution_results: Any,
                                 risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida resultados de todos os agentes"""
        try:
            # Lógica simples de consolidação - pode ser expandida
            success = risk_assessment["level"] in ["low", "medium"] and not isinstance(execution_results, dict)

            consolidated = {
                "success": success,
                "result": execution_results if success else {"error": "Execução não realizada devido a riscos"},
                "exploration_insights": len(exploration_results),
                "execution_steps": len(execution_results) if isinstance(execution_results, list) else 0,
                "risk_level": risk_assessment["level"],
                "summary": self._generate_summary(task, exploration_results, execution_results, risk_assessment)
            }

            return consolidated

        except Exception as e:
            return {
                "success": False,
                "result": {"error": f"Falha na consolidação: {str(e)}"},
                "summary": f"Erro na consolidação dos resultados: {str(e)}"
            }

    def _generate_summary(self, task: OrchestratorTask,
                         exploration_results: List[Dict[str, Any]],
                         execution_results: Any,
                         risk_assessment: Dict[str, Any]) -> str:
        """Gera resumo consolidado da tarefa"""
        summary_parts = [
            f"Tarefa {task.type.value} processada",
            f"Nível de risco: {risk_assessment['level']}",
            f"Resultados de exploração: {len(exploration_results)}",
        ]

        if isinstance(execution_results, list):
            summary_parts.append(f"Passos executados: {len(execution_results)}")
        else:
            summary_parts.append("Execução não realizada")

        return ". ".join(summary_parts)

    async def _record_task_completion(self, task: OrchestratorTask, result: OrchestratorResult):
        """Registra conclusão da tarefa na memória e auditoria"""
        # Registrar na memória
        memory_entry = {
            "type": "orchestrator_task",
            "task_id": task.id,
            "command": task.user_command,
            "result": result.result,
            "risk_level": result.risk_assessment["level"],
            "execution_time": result.execution_time,
            "timestamp": datetime.now().isoformat()
        }

        await self.memory.store("orchestrator_history", memory_entry)

        # Registrar auditoria
        await audit_logger.log_event(
            LogEvent(
                event_type="orchestrator_task_completed",
                level=LogLevel.INFO,
                message=f"Tarefa orquestrada concluída: {task.id}",
                details={
                    "task_id": task.id,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "risk_level": result.risk_assessment["level"]
                }
            )
        )

        # Mover para histórico
        self.task_history.append(task)
        if task.id in self.active_tasks:
            del self.active_tasks[task.id]

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de uma tarefa"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "id": task.id,
                "status": task.status,
                "type": task.type.value,
                "priority": task.priority.value,
                "risk_level": task.risk_level,
                "created_at": task.created_at.isoformat(),
                "subtasks_count": len(task.subtasks)
            }

        # Verificar histórico
        for task in self.task_history[-10:]:  # últimos 10
            if task.id == task_id:
                return {
                    "id": task.id,
                    "status": task.status,
                    "type": task.type.value,
                    "priority": task.priority.value,
                    "risk_level": task.risk_level,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "subtasks_count": len(task.subtasks)
                }

        return None

    async def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Retorna lista de tarefas ativas"""
        return [
            {
                "id": task.id,
                "status": task.status,
                "type": task.type.value,
                "priority": task.priority.value,
                "description": task.description,
                "created_at": task.created_at.isoformat()
            }
            for task in self.active_tasks.values()
        ]


# Instância global do orquestrador
_orchestrator_instance = None

def get_central_orchestrator() -> CentralOrchestrator:
    """Retorna instância singleton do orquestrador central"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = CentralOrchestrator()
    return _orchestrator_instance