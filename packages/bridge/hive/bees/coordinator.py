"""
Bee Coordinator - Abelha Coordenadora
====================================

Agente que organiza tarefas e coordena execução.
Características:
- Distribuição inteligente de tarefas
- Priorização baseada em impacto e risco
- Coordenação entre workers
- Otimização de recursos
"""

import asyncio
import time
import heapq
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from memory.collective import CollectiveMemory
from core.security import SecurityManager

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Tarefa a ser executada"""
    id: str
    type: str
    data: Dict[str, Any]
    priority: TaskPriority
    estimated_complexity: float
    dependencies: List[str]
    created_at: float
    deadline: Optional[float] = None

    def is_overdue(self) -> bool:
        """Verifica se a tarefa está atrasada"""
        return self.deadline is not None and time.time() > self.deadline

    def get_urgency_score(self) -> float:
        """Calcula score de urgência da tarefa"""
        base_score = self.priority.value

        if self.is_overdue():
            base_score += 2

        # Penalizar por dependências não resolvidas
        unresolved_deps = len([d for d in self.dependencies if not self._is_dependency_resolved(d)])
        base_score -= unresolved_deps * 0.5

        return max(base_score, 0)

    def _is_dependency_resolved(self, dep_id: str) -> bool:
        """Verifica se uma dependência foi resolvida"""
        # TODO: Implementar verificação real
        return False

@dataclass
class WorkerStatus:
    """Status de um worker"""
    worker_id: str
    current_task: Optional[str]
    capabilities: List[str]
    performance_score: float
    last_active: float
    task_queue_size: int

class BeeCoordinator:
    """
    Abelha coordenadora - gerencia distribuição de tarefas

    Funcionalidades:
    - Receber dados dos scouts
    - Criar e priorizar tarefas
    - Distribuir tarefas para workers
    - Monitorar progresso
    - Rebalancear carga
    """

    def __init__(self, coordinator_id: Optional[str] = None):
        self.coordinator_id = coordinator_id or f"coord_{int(time.time())}"
        self.memory = CollectiveMemory()
        self.security = SecurityManager()

        # Filas de tarefas por prioridade
        self.task_queues: Dict[TaskPriority, List[Task]] = {
            priority: [] for priority in TaskPriority
        }

        # Workers disponíveis
        self.workers: Dict[str, WorkerStatus] = {}
        self.active = False

        # Estatísticas
        self.tasks_created = 0
        self.tasks_completed = 0

        logger.info(f"BeeCoordinator {self.coordinator_id} initialized")

    async def start_coordination(self):
        """Inicia o ciclo de coordenação"""
        self.active = True
        logger.info(f"BeeCoordinator {self.coordinator_id} started coordination")

        while self.active:
            try:
                # Processar dados dos scouts
                await self._process_scout_data()

                # Distribuir tarefas para workers
                await self._distribute_tasks()

                # Monitorar progresso
                await self._monitor_progress()

                # Rebalancear carga se necessário
                await self._rebalance_load()

                # Aguardar antes do próximo ciclo
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"BeeCoordinator {self.coordinator_id} error: {e}")
                await asyncio.sleep(5)

    async def _process_scout_data(self):
        """Processa dados recebidos dos scouts"""
        # Buscar relatórios dos scouts
        scout_reports = await self.memory.get_pending_tasks()

        scout_reports = [r for r in scout_reports if r.get('type') == 'scout_report']

        for report in scout_reports:
            try:
                # Criar tarefas baseadas nos dados
                tasks = await self._create_tasks_from_report(report)

                # Adicionar tarefas às filas
                for task in tasks:
                    self._add_task_to_queue(task)

                # Marcar relatório como processado
                await self.memory.update_task_status(report['id'], 'processed')

                self.tasks_created += len(tasks)

            except Exception as e:
                logger.error(f"Failed to process scout report {report.get('id')}: {e}")

    async def _create_tasks_from_report(self, report: Dict[str, Any]) -> List[Task]:
        """
        Cria tarefas baseadas em um relatório de scout

        Args:
            report: Relatório do scout

        Returns:
            Lista de tarefas criadas
        """
        tasks = []
        processed_data = report.get('processed_data', {})
        quality_score = report.get('quality_score', 0.0)

        # Criar tarefas baseadas nos achados
        findings = processed_data.get('summary', {})

        # Tarefa de análise se há achados estruturais
        if processed_data.get('structure_findings'):
            task = Task(
                id=f"analyze_structure_{int(time.time() * 1000)}",
                type="structure_analysis",
                data={
                    'findings': processed_data['structure_findings'],
                    'source': report.get('source_ant'),
                    'quality_score': quality_score
                },
                priority=self._determine_priority('structure', quality_score),
                estimated_complexity=1.0,
                dependencies=[],
                created_at=time.time()
            )
            tasks.append(task)

        # Tarefa de análise de código se há achados de código
        if processed_data.get('code_findings'):
            task = Task(
                id=f"analyze_code_{int(time.time() * 1000)}",
                type="code_analysis",
                data={
                    'findings': processed_data['code_findings'],
                    'source': report.get('source_ant'),
                    'quality_score': quality_score
                },
                priority=self._determine_priority('code', quality_score),
                estimated_complexity=2.0,
                dependencies=[],
                created_at=time.time()
            )
            tasks.append(task)

        # Tarefa de validação de padrões
        if processed_data.get('pattern_findings'):
            task = Task(
                id=f"validate_patterns_{int(time.time() * 1000)}",
                type="pattern_validation",
                data={
                    'findings': processed_data['pattern_findings'],
                    'source': report.get('source_ant'),
                    'quality_score': quality_score
                },
                priority=self._determine_priority('patterns', quality_score),
                estimated_complexity=1.5,
                dependencies=[],
                created_at=time.time()
            )
            tasks.append(task)

        return tasks

    def _determine_priority(self, task_type: str, quality_score: float) -> TaskPriority:
        """Determina prioridade de uma tarefa"""
        if quality_score > 0.8:
            return TaskPriority.HIGH
        elif quality_score > 0.6:
            return TaskPriority.MEDIUM
        elif quality_score > 0.3:
            return TaskPriority.LOW
        else:
            return TaskPriority.LOW

    def _add_task_to_queue(self, task: Task):
        """Adiciona tarefa à fila apropriada"""
        heapq.heappush(self.task_queues[task.priority], (-task.get_urgency_score(), task))

    async def _distribute_tasks(self):
        """Distribui tarefas para workers disponíveis"""
        # Para cada prioridade (do mais alto para o mais baixo)
        for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW]:
            queue = self.task_queues[priority]

            while queue:
                # Pegar tarefa mais urgente
                _, task = heapq.heappop(queue)

                # Encontrar worker adequado
                worker_id = await self._find_suitable_worker(task)

                if worker_id:
                    # Atribuir tarefa ao worker
                    await self._assign_task_to_worker(task, worker_id)
                else:
                    # Nenhum worker disponível, voltar para fila
                    heapq.heappush(queue, (-task.get_urgency_score(), task))
                    break

    async def _find_suitable_worker(self, task: Task) -> Optional[str]:
        """
        Encontra worker adequado para a tarefa

        Args:
            task: Tarefa a ser executada

        Returns:
            ID do worker adequado ou None
        """
        best_worker = None
        best_score = -1

        for worker_id, status in self.workers.items():
            if status.current_task is not None:
                continue  # Worker ocupado

            # Verificar se worker tem capacidades necessárias
            if task.type not in status.capabilities:
                continue

            # Calcular score de adequação
            score = self._calculate_worker_score(status, task)

            if score > best_score:
                best_score = score
                best_worker = worker_id

        return best_worker

    def _calculate_worker_score(self, worker: WorkerStatus, task: Task) -> float:
        """Calcula score de adequação do worker para a tarefa"""
        score = worker.performance_score

        # Bonus por baixa carga
        if worker.task_queue_size == 0:
            score += 0.2

        # Penalizar por inatividade
        time_since_active = time.time() - worker.last_active
        if time_since_active > 300:  # 5 minutos
            score -= 0.1

        return score

    async def _assign_task_to_worker(self, task: Task, worker_id: str):
        """
        Atribui tarefa a um worker

        Args:
            task: Tarefa a atribuir
            worker_id: ID do worker
        """
        # Atualizar status do worker
        if worker_id in self.workers:
            self.workers[worker_id].current_task = task.id
            self.workers[worker_id].last_active = time.time()

        # Enviar tarefa via memória coletiva
        task_data = {
            'id': task.id,
            'type': task.type,
            'data': task.data,
            'priority': task.priority.value,
            'assigned_worker': worker_id,
            'coordinator_id': self.coordinator_id,
            'timestamp': time.time()
        }

        await self.memory.store_task(task_data)

        logger.info(f"Coordinator {self.coordinator_id} assigned task {task.id} to worker {worker_id}")

    async def _monitor_progress(self):
        """Monitora progresso das tarefas em execução"""
        # Verificar status das tarefas
        # TODO: Implementar monitoramento real

        # Atualizar estatísticas
        completed_tasks = await self._get_completed_tasks()
        self.tasks_completed = len(completed_tasks)

    async def _get_completed_tasks(self) -> List[Dict[str, Any]]:
        """Busca tarefas completadas"""
        # TODO: Implementar busca real
        return []

    async def _rebalance_load(self):
        """Rebalanceia carga entre workers se necessário"""
        # Calcular carga média
        total_load = sum(w.task_queue_size for w in self.workers.values())
        avg_load = total_load / len(self.workers) if self.workers else 0

        # Identificar workers sobrecarregados e subcarregados
        overloaded = [wid for wid, w in self.workers.items() if w.task_queue_size > avg_load + 1]
        underloaded = [wid for wid, w in self.workers.items() if w.task_queue_size < avg_load - 1]

        # Rebalancear
        for overloaded_id in overloaded:
            for underloaded_id in underloaded:
                # Transferir tarefa se possível
                # TODO: Implementar transferência real
                pass

    def register_worker(self, worker_id: str, capabilities: List[str]):
        """
        Registra um worker no sistema

        Args:
            worker_id: ID do worker
            capabilities: Capacidades do worker
        """
        self.workers[worker_id] = WorkerStatus(
            worker_id=worker_id,
            current_task=None,
            capabilities=capabilities,
            performance_score=1.0,  # Score inicial
            last_active=time.time(),
            task_queue_size=0
        )

        logger.info(f"Worker {worker_id} registered with capabilities: {capabilities}")

    def unregister_worker(self, worker_id: str):
        """Remove worker do sistema"""
        if worker_id in self.workers:
            del self.workers[worker_id]
            logger.info(f"Worker {worker_id} unregistered")

    async def get_coordinator_status(self) -> Dict[str, Any]:
        """Retorna status do coordenador"""
        total_queued = sum(len(queue) for queue in self.task_queues.values())

        return {
            'coordinator_id': self.coordinator_id,
            'active': self.active,
            'workers_count': len(self.workers),
            'tasks_created': self.tasks_created,
            'tasks_completed': self.tasks_completed,
            'tasks_queued': total_queued,
            'queue_sizes': {
                priority.name: len(queue) for priority, queue in self.task_queues.items()
            }
        }

    def stop_coordination(self):
        """Para o ciclo de coordenação"""
        self.active = False
        logger.info(f"BeeCoordinator {self.coordinator_id} stopped coordination")

    async def execute_from_exploration(self, orchestrator_task: Any, exploration_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executa tarefas baseadas nos resultados da exploração das formigas

        Args:
            orchestrator_task: Tarefa do orquestrador
            exploration_results: Resultados da exploração

        Returns:
            Lista de resultados da execução
        """
        execution_results = []

        try:
            # Processar resultados da exploração como relatórios de scout
            for result in exploration_results:
                scout_report = {
                    "id": f"scout_{int(time.time() * 1000)}_{len(execution_results)}",
                    "type": "scout_report",
                    "processed_data": {
                        "summary": result,
                        "structure_findings": result.get("findings", []),
                        "code_findings": result.get("code_findings", []),
                        "pattern_findings": result.get("patterns", [])
                    },
                    "quality_score": result.get("relevance", 0.5),
                    "source_ant": result.get("ant_id", "unknown")
                }

                # Processar relatório e criar tarefas
                tasks = await self._create_tasks_from_report(scout_report)
                execution_results.extend([{
                    "task_id": task.id,
                    "type": task.type,
                    "priority": task.priority.value,
                    "bee_id": f"bee_{self.coordinator_id}",
                    "based_on_exploration": result.get("subtask_type"),
                    "estimated_complexity": task.estimated_complexity
                } for task in tasks])

                # Adicionar tarefas às filas
                for task in tasks:
                    self._add_task_to_queue(task)

            # Tentar distribuir tarefas imediatamente
            await self._distribute_tasks()

            logger.info(f"Created {len(execution_results)} execution tasks from {len(exploration_results)} exploration results")

        except Exception as e:
            logger.error(f"Error in execute_from_exploration: {e}")
            execution_results = [{"error": str(e), "bee_id": f"bee_{self.coordinator_id}"}]

        return execution_results