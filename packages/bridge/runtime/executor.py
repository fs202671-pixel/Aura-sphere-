"""
Runtime Executor - Executor Controlado de Código

Implementa execução segura de código gerado pela IA com controle de processos,
sandbox e permissões dinâmicas.
"""

import asyncio
import subprocess
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import psutil
import signal
import os

from core.permissions import PermissionLevel, permission_manager
from core.validator import core_validator
from .sandbox import sandbox_manager, SandboxConfig


class ExecutionStatus(Enum):
    """Status de execução"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ExecutionTask:
    """Tarefa de execução"""
    task_id: str
    code: str
    user_id: str
    permission_level: PermissionLevel
    sandbox_config: Optional[SandboxConfig] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    process_id: Optional[int] = None
    thread: Optional[threading.Thread] = None


class ProcessController:
    """Controla processos de execução"""

    def __init__(self):
        self.active_processes: Dict[str, psutil.Process] = {}
        self.resource_limits = {
            'cpu_percent': 50.0,
            'memory_mb': 200,
            'max_processes': 10
        }

    def start_process_monitor(self, task: ExecutionTask) -> None:
        """Inicia monitoramento de processo"""
        if task.process_id:
            try:
                process = psutil.Process(task.process_id)
                self.active_processes[task.task_id] = process
            except psutil.NoSuchProcess:
                pass

    def check_process_limits(self, task: ExecutionTask) -> Dict[str, Any]:
        """Verifica limites de recursos do processo"""
        if task.task_id not in self.active_processes:
            return {"within_limits": True}

        process = self.active_processes[task.task_id]

        try:
            cpu_percent = process.cpu_percent(interval=1.0)
            memory_mb = process.memory_info().rss / 1024 / 1024

            violations = []
            if cpu_percent > self.resource_limits['cpu_percent']:
                violations.append(f"CPU usage: {cpu_percent:.1f}% > {self.resource_limits['cpu_percent']}%")

            if memory_mb > self.resource_limits['memory_mb']:
                violations.append(f"Memory usage: {memory_mb:.1f}MB > {self.resource_limits['memory_mb']}MB")

            return {
                "within_limits": len(violations) == 0,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "violations": violations
            }

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"within_limits": True, "error": "Process not accessible"}

    def kill_process(self, task_id: str) -> bool:
        """Mata processo associado à tarefa"""
        if task_id in self.active_processes:
            process = self.active_processes[task_id]
            try:
                process.terminate()
                process.wait(timeout=5)
                del self.active_processes[task_id]
                return True
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                try:
                    process.kill()
                    del self.active_processes[task_id]
                    return True
                except psutil.NoSuchProcess:
                    pass
        return False

    def cleanup_inactive_processes(self) -> int:
        """Limpa processos inativos"""
        to_remove = []
        for task_id, process in self.active_processes.items():
            if not process.is_running():
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.active_processes[task_id]

        return len(to_remove)


class DynamicPermissionSystem:
    """Sistema de permissões dinâmicas por ação"""

    def __init__(self):
        self.action_permissions: Dict[str, Dict[str, Any]] = {
            "execute_code": {
                "required_level": PermissionLevel.LEVEL_2_EXECUTE_CONFIRMED,
                "requires_confirmation": True,
                "allowed_in_sandbox": True
            },
            "file_operation": {
                "required_level": PermissionLevel.LEVEL_1_SUGGEST,
                "requires_confirmation": True,
                "allowed_in_sandbox": False
            },
            "network_access": {
                "required_level": PermissionLevel.LEVEL_3_SANDBOX_EVOLUTION,
                "requires_confirmation": True,
                "allowed_in_sandbox": True
            },
            "system_command": {
                "required_level": PermissionLevel.LEVEL_4_PRODUCTION_EVOLUTION,  # Nunca permitir
                "requires_confirmation": True,
                "allowed_in_sandbox": False
            }
        }

    def check_action_permission(self, user_id: str, action: str,
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Verifica permissão para uma ação específica"""
        if action not in self.action_permissions:
            return {
                "approved": False,
                "reason": f"Ação '{action}' não reconhecida"
            }

        action_config = self.action_permissions[action]
        context = context or {}

        # Verificar nível de permissão
        user_level = permission_manager.get_user_level(user_id)
        if user_level.value < action_config["required_level"].value:
            return {
                "approved": False,
                "reason": f"Nível de permissão insuficiente. Necessário: {action_config['required_level'].name}"
            }

        # Verificar contexto de sandbox
        if not context.get("in_sandbox", False) and not action_config["allowed_in_sandbox"]:
            return {
                "approved": False,
                "reason": f"Ação '{action}' só permitida em sandbox"
            }

        # Verificar confirmação necessária
        if action_config["requires_confirmation"] and not context.get("user_confirmed", False):
            return {
                "approved": False,
                "reason": "Confirmação do usuário necessária",
                "requires_confirmation": True
            }

        return {
            "approved": True,
            "action_config": action_config
        }


class TaskQueue:
    """Fila de execução de tarefas"""

    def __init__(self):
        self.queue: List[ExecutionTask] = []
        self.completed_tasks: List[ExecutionTask] = []
        self.max_concurrent = 3
        self.active_tasks: Dict[str, ExecutionTask] = {}
        self.lock = threading.Lock()

    def add_task(self, task: ExecutionTask) -> None:
        """Adiciona tarefa à fila"""
        with self.lock:
            self.queue.append(task)

    def get_next_task(self) -> Optional[ExecutionTask]:
        """Obtém próxima tarefa da fila"""
        with self.lock:
            if len(self.active_tasks) >= self.max_concurrent:
                return None

            if not self.queue:
                return None

            task = self.queue.pop(0)
            self.active_tasks[task.task_id] = task
            return task

    def complete_task(self, task: ExecutionTask) -> None:
        """Marca tarefa como completa"""
        with self.lock:
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.completed_tasks.append(task)

            # Manter apenas últimas 100 tarefas completadas
            if len(self.completed_tasks) > 100:
                self.completed_tasks = self.completed_tasks[-100:]

    def cancel_task(self, task_id: str) -> bool:
        """Cancela tarefa"""
        with self.lock:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = ExecutionStatus.CANCELLED
                task.completed_at = datetime.now()
                self.complete_task(task)
                return True

            # Remover da fila se ainda não iniciou
            for i, task in enumerate(self.queue):
                if task.task_id == i:
                    self.queue.pop(i)
                    task.status = ExecutionStatus.CANCELLED
                    self.completed_tasks.append(task)
                    return True

        return False

    def get_queue_status(self) -> Dict[str, Any]:
        """Retorna status da fila"""
        with self.lock:
            return {
                "queued": len(self.queue),
                "active": len(self.active_tasks),
                "completed_recent": len(self.completed_tasks),
                "max_concurrent": self.max_concurrent
            }


class RuntimeExecutor:
    """Executor principal do runtime"""

    def __init__(self):
        self.process_controller = ProcessController()
        self.dynamic_permissions = DynamicPermissionSystem()
        self.task_queue = TaskQueue()
        self.task_counter = 0

    def execute_code_async(self, code: str, user_id: str,
                          inputs: Dict[str, Any] = None,
                          sandbox_config: SandboxConfig = None) -> str:
        """Executa código de forma assíncrona"""
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1

        # Garantir sessão do usuário
        if user_id not in permission_manager.sessions:
            permission_manager.create_session(user_id)
            permission_manager.grant_permission(
                user_id, PermissionLevel.LEVEL_2_EXECUTE_CONFIRMED,
                "system", "Auto-grant for runtime async execution", duration_minutes=30,
                scope=["sandbox"]
            )

        # Verificar permissões
        permission_check = self.dynamic_permissions.check_action_permission(
            user_id, "execute_code", {"in_sandbox": True, "user_confirmed": True}
        )

        if not permission_check["approved"]:
            raise PermissionError(permission_check["reason"])

        # Criar tarefa
        task = ExecutionTask(
            task_id=task_id,
            code=code,
            user_id=user_id,
            permission_level=permission_manager.get_user_level(user_id),
            sandbox_config=sandbox_config,
            inputs=inputs or {}
        )

        # Adicionar à fila
        self.task_queue.add_task(task)

        # Iniciar processamento se possível
        self._process_queue()

        return task_id

    def execute_code_sync(self, code: str, user_id: str,
                         inputs: Dict[str, Any] = None,
                         timeout: int = 30) -> Dict[str, Any]:
        """Executa código de forma síncrona"""
        # Garantir sessão do usuário
        if user_id not in permission_manager.sessions:
            permission_manager.create_session(user_id)
            permission_manager.grant_permission(
                user_id, PermissionLevel.LEVEL_2_EXECUTE_CONFIRMED,
                "system", "Auto-grant for runtime sync execution", duration_minutes=30,
                scope=["sandbox"]
            )

        # Verificar permissões
        permission_check = self.dynamic_permissions.check_action_permission(
            user_id, "execute_code", {"in_sandbox": True, "user_confirmed": True}
        )

        if not permission_check["approved"]:
            return {
                "success": False,
                "error": permission_check["reason"]
            }

        # Executar em sandbox
        result = sandbox_manager.execute_in_sandbox(
            f"sync_{user_id}", code, inputs, user_id
        )

        return result

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status de tarefa"""
        # Verificar tarefas ativas
        if task_id in self.task_queue.active_tasks:
            task = self.task_queue.active_tasks[task_id]
            return {
                "task_id": task.task_id,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None
            }

        # Verificar tarefas completadas
        for task in self.task_queue.completed_tasks:
            if task.task_id == task_id:
                return {
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "result": task.result,
                    "error": task.error
                }

        return None

    def cancel_task(self, task_id: str, user_id: str) -> bool:
        """Cancela tarefa"""
        # Verificar permissões
        permission_check = self.dynamic_permissions.check_action_permission(
            user_id, "execute_code", {"in_sandbox": True}
        )

        if not permission_check["approved"]:
            return False

        return self.task_queue.cancel_task(task_id)

    def _process_queue(self) -> None:
        """Processa fila de tarefas"""
        while True:
            task = self.task_queue.get_next_task()
            if not task:
                break

            # Executar tarefa em thread separada
            thread = threading.Thread(target=self._execute_task, args=(task,))
            task.thread = thread
            task.status = ExecutionStatus.RUNNING
            task.started_at = datetime.now()
            thread.start()

    def _execute_task(self, task: ExecutionTask) -> None:
        """Executa tarefa individual"""
        try:
            # Executar em sandbox
            result = sandbox_manager.execute_in_sandbox(
                f"task_{task.task_id}", task.code, task.inputs, task.user_id
            )

            # Atualizar tarefa
            task.result = result
            task.status = ExecutionStatus.COMPLETED if result.get("success") else ExecutionStatus.FAILED
            task.error = result.get("error")

        except Exception as e:
            task.status = ExecutionStatus.FAILED
            task.error = str(e)

        finally:
            task.completed_at = datetime.now()
            self.task_queue.complete_task(task)

    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status geral do sistema de execução"""
        return {
            "process_controller": {
                "active_processes": len(self.process_controller.active_processes)
            },
            "task_queue": self.task_queue.get_queue_status(),
            "permissions": {
                "total_actions": len(self.dynamic_permissions.action_permissions)
            }
        }


# ========== INSTÂNCIA GLOBAL ==========

runtime_executor = RuntimeExecutor()

# ========== FUNÇÕES DE CONVENIÊNCIA ==========

def execute_code(code: str, user_id: str, sync: bool = True,
                inputs: Dict[str, Any] = None, timeout: int = 30) -> Any:
    """Executa código Python de forma segura"""
    if sync:
        return runtime_executor.execute_code_sync(code, user_id, inputs, timeout)
    else:
        return runtime_executor.execute_code_async(code, user_id, inputs)

def get_execution_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Obtém status de execução assíncrona"""
    return runtime_executor.get_task_status(task_id)

def cancel_execution(task_id: str, user_id: str) -> bool:
    """Cancela execução assíncrona"""
    return runtime_executor.cancel_task(task_id, user_id)