"""
Bee Worker - Abelha Trabalhadora
===============================

Agente executor de tarefas.
Características:
- Execução especializada de tarefas
- Relatório de progresso
- Adaptação baseada em feedback
- Colaboração com outros workers
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from memory.collective import CollectiveMemory
from core.security import SecurityManager
from core.sandbox import SandboxManager

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskResult:
    """Resultado de uma tarefa executada"""
    task_id: str
    status: TaskStatus
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_time: float
    quality_score: float
    timestamp: float

class BeeWorker:
    """
    Abelha trabalhadora - executa tarefas atribuídas

    Funcionalidades:
    - Receber tarefas do coordinator
    - Executar tarefas de forma segura
    - Reportar progresso e resultados
    - Aprender com feedback
    """

    def __init__(self, worker_id: Optional[str] = None, capabilities: Optional[List[str]] = None):
        self.worker_id = worker_id or f"worker_{int(time.time())}"
        self.capabilities = capabilities or ["general"]
        self.memory = CollectiveMemory()
        self.security = SecurityManager()
        self.sandbox = SandboxManager()

        # Estado atual
        self.current_task: Optional[Dict[str, Any]] = None
        self.task_start_time: Optional[float] = None
        self.active = False

        # Estatísticas de performance
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.average_execution_time = 0.0
        self.performance_score = 1.0

        # Handlers de tarefas por tipo
        self.task_handlers: Dict[str, Callable] = {
            "structure_analysis": self._handle_structure_analysis,
            "code_analysis": self._handle_code_analysis,
            "pattern_validation": self._handle_pattern_validation,
            "general": self._handle_general_task
        }

        logger.info(f"BeeWorker {self.worker_id} initialized with capabilities: {self.capabilities}")

    async def start_working(self):
        """Inicia o ciclo de trabalho"""
        self.active = True
        logger.info(f"BeeWorker {self.worker_id} started working")

        while self.active:
            try:
                # Verificar se há tarefas disponíveis
                task = await self._get_next_task()

                if task:
                    # Executar tarefa
                    result = await self._execute_task(task)

                    # Reportar resultado
                    await self._report_result(result)

                    # Atualizar estatísticas
                    self._update_performance(result)

                else:
                    # Aguardar antes de verificar novamente
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"BeeWorker {self.worker_id} error: {e}")
                await asyncio.sleep(5)

    async def _get_next_task(self) -> Optional[Dict[str, Any]]:
        """
        Busca próxima tarefa disponível

        Returns:
            Próxima tarefa ou None
        """
        # Buscar tarefas atribuídas a este worker
        tasks = await self.memory.get_worker_tasks(self.worker_id)

        # Pegar primeira tarefa pendente
        for task in tasks:
            if task.get('status') == 'assigned':
                return task

        return None

    async def _execute_task(self, task: Dict[str, Any]) -> TaskResult:
        """
        Executa uma tarefa

        Args:
            task: Dados da tarefa

        Returns:
            Resultado da execução
        """
        task_id = task['id']
        task_type = task.get('type', 'general')

        self.current_task = task
        self.task_start_time = time.time()

        logger.info(f"BeeWorker {self.worker_id} executing task {task_id} ({task_type})")

        try:
            # Marcar tarefa como em progresso
            await self.memory.update_task_status(task_id, 'in_progress')

            # Executar tarefa em sandbox
            result_data = await self.sandbox.execute_in_sandbox(
                self._execute_task_logic,
                task
            )

            # Calcular qualidade do resultado
            quality_score = self._assess_result_quality(result_data)

            execution_time = time.time() - self.task_start_time

            result = TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                result_data=result_data,
                error_message=None,
                execution_time=execution_time,
                quality_score=quality_score,
                timestamp=time.time()
            )

        except Exception as e:
            execution_time = time.time() - (self.task_start_time or time.time())

            result = TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                result_data=None,
                error_message=str(e),
                execution_time=execution_time,
                quality_score=0.0,
                timestamp=time.time()
            )

            logger.error(f"BeeWorker {self.worker_id} failed task {task_id}: {e}")

        finally:
            self.current_task = None
            self.task_start_time = None

        return result

    async def _execute_task_logic(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lógica de execução da tarefa

        Args:
            task: Dados da tarefa

        Returns:
            Resultado da execução
        """
        task_type = task.get('type', 'general')
        task_data = task.get('data', {})

        # Encontrar handler apropriado
        handler = self.task_handlers.get(task_type, self._handle_general_task)

        # Executar handler
        return await handler(task_data)

    async def _handle_structure_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para análise de estrutura"""
        findings = data.get('findings', [])

        # Analisar estrutura dos achados
        analysis = {
            'structure_type': self._classify_structure(findings),
            'complexity_score': self._calculate_complexity(findings),
            'recommendations': self._generate_structure_recommendations(findings),
            'risk_assessment': self._assess_structure_risks(findings)
        }

        return {
            'task_type': 'structure_analysis',
            'analysis': analysis,
            'processed_at': time.time()
        }

    async def _handle_code_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para análise de código"""
        findings = data.get('code_findings', [])

        # Analisar código
        analysis = {
            'code_quality': self._assess_code_quality(findings),
            'patterns_identified': self._identify_code_patterns(findings),
            'improvement_suggestions': self._suggest_code_improvements(findings),
            'security_issues': self._check_security_issues(findings)
        }

        return {
            'task_type': 'code_analysis',
            'analysis': analysis,
            'processed_at': time.time()
        }

    async def _handle_pattern_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para validação de padrões"""
        findings = data.get('pattern_findings', [])

        # Validar padrões
        validation = {
            'patterns_valid': self._validate_patterns(findings),
            'consistency_score': self._check_pattern_consistency(findings),
            'violations': self._identify_pattern_violations(findings),
            'recommendations': self._suggest_pattern_improvements(findings)
        }

        return {
            'task_type': 'pattern_validation',
            'validation': validation,
            'processed_at': time.time()
        }

    async def _handle_general_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para tarefas gerais"""
        # Processamento genérico
        return {
            'task_type': 'general',
            'processed_data': data,
            'summary': f"Processed {len(data)} data items",
            'processed_at': time.time()
        }

    def _classify_structure(self, findings: List[Dict[str, Any]]) -> str:
        """Classifica tipo de estrutura"""
        # TODO: Implementar classificação real
        return "unknown"

    def _calculate_complexity(self, findings: List[Dict[str, Any]]) -> float:
        """Calcula complexidade da estrutura"""
        # TODO: Implementar cálculo real
        return 0.5

    def _generate_structure_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações para estrutura"""
        # TODO: Implementar recomendações reais
        return ["Review structure for optimization opportunities"]

    def _assess_structure_risks(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia riscos da estrutura"""
        # TODO: Implementar avaliação real
        return {"risk_level": "low", "issues": []}

    def _assess_code_quality(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia qualidade do código"""
        # TODO: Implementar avaliação real
        return {"score": 0.7, "metrics": {}}

    def _identify_code_patterns(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Identifica padrões no código"""
        # TODO: Implementar identificação real
        return []

    def _suggest_code_improvements(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Sugere melhorias no código"""
        # TODO: Implementar sugestões reais
        return ["Consider refactoring for better readability"]

    def _check_security_issues(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verifica problemas de segurança"""
        # TODO: Implementar verificação real
        return []

    def _validate_patterns(self, findings: List[Dict[str, Any]]) -> bool:
        """Valida padrões encontrados"""
        # TODO: Implementar validação real
        return True

    def _check_pattern_consistency(self, findings: List[Dict[str, Any]]) -> float:
        """Verifica consistência de padrões"""
        # TODO: Implementar verificação real
        return 0.8

    def _identify_pattern_violations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Identifica violações de padrões"""
        # TODO: Implementar identificação real
        return []

    def _suggest_pattern_improvements(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Sugere melhorias nos padrões"""
        # TODO: Implementar sugestões reais
        return []

    def _assess_result_quality(self, result_data: Dict[str, Any]) -> float:
        """Avalia qualidade do resultado"""
        # TODO: Implementar avaliação real baseada em métricas
        return 0.8

    async def _report_result(self, result: TaskResult):
        """
        Reporta resultado da tarefa

        Args:
            result: Resultado a reportar
        """
        # Criar relatório
        report = {
            'task_id': result.task_id,
            'worker_id': self.worker_id,
            'status': result.status.value,
            'result_data': result.result_data,
            'error_message': result.error_message,
            'execution_time': result.execution_time,
            'quality_score': result.quality_score,
            'timestamp': result.timestamp
        }

        # Armazenar na memória coletiva
        await self.memory.store_task_result(report)

        # Atualizar status da tarefa
        await self.memory.update_task_status(result.task_id, result.status.value)

        logger.info(f"BeeWorker {self.worker_id} reported result for task {result.task_id}")

    def _update_performance(self, result: TaskResult):
        """Atualiza estatísticas de performance"""
        if result.status == TaskStatus.COMPLETED:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1

        # Atualizar tempo médio de execução
        total_time = self.average_execution_time * (self.tasks_completed + self.tasks_failed - 1)
        total_time += result.execution_time
        self.average_execution_time = total_time / (self.tasks_completed + self.tasks_failed)

        # Atualizar score de performance baseado na qualidade
        self.performance_score = (self.performance_score + result.quality_score) / 2

    async def get_worker_status(self) -> Dict[str, Any]:
        """Retorna status do worker"""
        return {
            'worker_id': self.worker_id,
            'capabilities': self.capabilities,
            'active': self.active,
            'current_task': self.current_task['id'] if self.current_task else None,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'average_execution_time': self.average_execution_time,
            'performance_score': self.performance_score
        }

    def stop_working(self):
        """Para o trabalho"""
        self.active = False
        logger.info(f"BeeWorker {self.worker_id} stopped working")