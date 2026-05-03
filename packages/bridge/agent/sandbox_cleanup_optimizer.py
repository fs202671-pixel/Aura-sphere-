"""
Módulo de Limpeza e Otimização de Sandbox - Gerenciamento de ambientes de teste

Este módulo implementa limpeza automática e otimização de
ambientes sandbox para manter eficiência e segurança.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import shutil
import psutil
import asyncio
from collections import defaultdict


class CleanupTrigger(Enum):
    """Gatilhos para limpeza."""
    TIME_BASED = "time_based"          # Baseado em tempo
    SIZE_BASED = "size_based"          # Baseado em tamanho
    USAGE_BASED = "usage_based"        # Baseado em uso
    PERFORMANCE_BASED = "performance_based"  # Baseado em performance
    MANUAL = "manual"                  # Manual


class SandboxStatus(Enum):
    """Status de um sandbox."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLEANING = "cleaning"
    CLEANED = "cleaned"
    FAILED = "failed"


class SandboxMetrics:
    """
    Métricas de performance de um sandbox.
    """

    def __init__(self, sandbox_id: str):
        self.sandbox_id = sandbox_id
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()

        # Métricas de uso
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.disk_usage = 0.0
        self.network_usage = 0.0

        # Métricas de performance
        self.test_count = 0
        self.success_rate = 0.0
        self.avg_response_time = 0.0

        # Status
        self.status = SandboxStatus.ACTIVE
        self.cleanup_reason = None

    def update_usage(self, cpu: float, memory: float, disk: float, network: float) -> None:
        """Atualiza métricas de uso."""
        self.cpu_usage = cpu
        self.memory_usage = memory
        self.disk_usage = disk
        self.network_usage = network
        self.last_accessed = datetime.now()

    def record_test_result(self, success: bool, response_time: float) -> None:
        """Registra resultado de teste."""
        self.test_count += 1
        success_count = int(success)
        self.success_rate = ((self.success_rate * (self.test_count - 1)) + success_count) / self.test_count

        self.avg_response_time = ((self.avg_response_time * (self.test_count - 1)) + response_time) / self.test_count

    def should_cleanup(self, max_age_hours: int, max_inactive_hours: int,
                      max_disk_usage: float) -> Tuple[bool, str]:
        """
        Determina se o sandbox deve ser limpo.
        """

        now = datetime.now()

        # Verificar idade máxima
        age_hours = (now - self.created_at).total_seconds() / 3600
        if age_hours > max_age_hours:
            return True, f"Age exceeds limit: {age_hours:.1f}h > {max_age_hours}h"

        # Verificar inatividade
        inactive_hours = (now - self.last_accessed).total_seconds() / 3600
        if inactive_hours > max_inactive_hours:
            return True, f"Inactive for: {inactive_hours:.1f}h > {max_inactive_hours}h"

        # Verificar uso de disco
        if self.disk_usage > max_disk_usage:
            return True, f"Disk usage exceeds limit: {self.disk_usage:.2f} > {max_disk_usage}"

        # Verificar performance degradada
        if self.test_count > 10 and self.success_rate < 0.5:
            return True, f"Low success rate: {self.success_rate:.2f}"

        return False, "No cleanup needed"


class SandboxCleanupOptimizer:
    """
    Otimizador de limpeza de sandbox.

    Funcionalidades:
    - Limpeza automática baseada em regras
    - Otimização de performance
    - Monitoramento de recursos
    - Relatórios de limpeza
    - Recuperação de espaço
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.cleanup_dir = data_dir / "sandbox_cleanup"
        self.cleanup_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_file = self.cleanup_dir / "sandbox_metrics.json"
        self.cleanup_log_file = self.cleanup_dir / "cleanup_log.json"

        self.sandbox_metrics: Dict[str, SandboxMetrics] = {}
        self.cleanup_log: List[Dict[str, Any]] = []

        # Configurações de limpeza
        self.max_age_hours = 24  # Sandboxes mais velhos que isso são limpos
        self.max_inactive_hours = 6  # Sandboxes inativos por mais que isso são limpos
        self.max_disk_usage_gb = 1.0  # Limite de uso de disco por sandbox
        self.cleanup_interval_minutes = 30  # Intervalo entre limpezas automáticas

        # Estatísticas
        self.stats = {
            "total_cleanups": 0,
            "space_reclaimed_gb": 0.0,
            "avg_cleanup_time_seconds": 0.0,
            "cleanup_success_rate": 0.0
        }

        self._load_state()

    async def start_automatic_cleanup(self) -> None:
        """
        Inicia limpeza automática periódica.
        """

        while True:
            try:
                await self.perform_cleanup(CleanupTrigger.TIME_BASED)
                await asyncio.sleep(self.cleanup_interval_minutes * 60)

            except Exception as e:
                print(f"Error in automatic cleanup: {e}")
                await asyncio.sleep(300)  # Aguardar 5 minutos em caso de erro

    async def perform_cleanup(self, trigger: CleanupTrigger,
                            specific_sandboxes: List[str] = None) -> Dict[str, Any]:
        """
        Executa limpeza de sandboxes.
        """

        cleanup_start = datetime.now()
        cleanup_results = {
            "trigger": trigger.value,
            "start_time": cleanup_start.isoformat(),
            "sandboxes_processed": 0,
            "sandboxes_cleaned": 0,
            "space_reclaimed_bytes": 0,
            "errors": []
        }

        # Identificar sandboxes para limpeza
        sandboxes_to_check = specific_sandboxes or list(self.sandbox_metrics.keys())

        for sandbox_id in sandboxes_to_check:
            try:
                metrics = self.sandbox_metrics.get(sandbox_id)
                if not metrics:
                    continue

                cleanup_results["sandboxes_processed"] += 1

                # Verificar se deve limpar
                should_cleanup, reason = metrics.should_cleanup(
                    self.max_age_hours,
                    self.max_inactive_hours,
                    self.max_disk_usage_gb
                )

                if should_cleanup or trigger == CleanupTrigger.MANUAL:
                    # Executar limpeza
                    space_reclaimed = await self._cleanup_sandbox(sandbox_id, reason)

                    if space_reclaimed > 0:
                        cleanup_results["sandboxes_cleaned"] += 1
                        cleanup_results["space_reclaimed_bytes"] += space_reclaimed

                        # Atualizar métricas
                        metrics.status = SandboxStatus.CLEANED
                        metrics.cleanup_reason = reason

            except Exception as e:
                cleanup_results["errors"].append(f"Error cleaning {sandbox_id}: {e}")

        # Calcular estatísticas
        cleanup_duration = (datetime.now() - cleanup_start).total_seconds()

        # Atualizar estatísticas globais
        self.stats["total_cleanups"] += 1
        space_reclaimed_gb = cleanup_results["space_reclaimed_bytes"] / (1024**3)
        self.stats["space_reclaimed_gb"] += space_reclaimed_gb

        success_rate = cleanup_results["sandboxes_cleaned"] / max(cleanup_results["sandboxes_processed"], 1)
        self.stats["cleanup_success_rate"] = (
            (self.stats["cleanup_success_rate"] * (self.stats["total_cleanups"] - 1)) + success_rate
        ) / self.stats["total_cleanups"]

        self.stats["avg_cleanup_time_seconds"] = (
            (self.stats["avg_cleanup_time_seconds"] * (self.stats["total_cleanups"] - 1)) + cleanup_duration
        ) / self.stats["total_cleanups"]

        # Registrar limpeza
        cleanup_record = {
            "cleanup_id": f"cleanup_{int(cleanup_start.timestamp())}",
            "trigger": trigger.value,
            "results": cleanup_results,
            "duration_seconds": cleanup_duration
        }
        self.cleanup_log.append(cleanup_record)

        self._save_state()

        return cleanup_results

    async def _cleanup_sandbox(self, sandbox_id: str, reason: str) -> int:
        """
        Limpa um sandbox específico.
        """

        # Localizar diretório do sandbox
        sandbox_path = None
        for root_dir in ["advanced_evolution", "multimodal_content", "creative_styles"]:
            potential_path = self.data_dir / root_dir / "sandboxes" / f"sandbox_{sandbox_id}"
            if potential_path.exists():
                sandbox_path = potential_path
                break

        if not sandbox_path:
            return 0

        try:
            # Calcular espaço antes da limpeza
            space_before = self._calculate_directory_size(sandbox_path)

            # Remover diretório
            shutil.rmtree(sandbox_path)

            # Remover das métricas
            if sandbox_id in self.sandbox_metrics:
                del self.sandbox_metrics[sandbox_id]

            return space_before

        except Exception as e:
            print(f"Error removing sandbox {sandbox_id}: {e}")
            return 0

    def register_sandbox(self, sandbox_id: str) -> None:
        """
        Registra um novo sandbox para monitoramento.
        """

        if sandbox_id not in self.sandbox_metrics:
            self.sandbox_metrics[sandbox_id] = SandboxMetrics(sandbox_id)
            self._save_state()

    def update_sandbox_metrics(self, sandbox_id: str, cpu: float = None,
                             memory: float = None, disk: float = None,
                             network: float = None) -> None:
        """
        Atualiza métricas de um sandbox.
        """

        if sandbox_id in self.sandbox_metrics:
            metrics = self.sandbox_metrics[sandbox_id]
            metrics.update_usage(
                cpu or metrics.cpu_usage,
                memory or metrics.memory_usage,
                disk or metrics.disk_usage,
                network or metrics.network_usage
            )

    def record_sandbox_test(self, sandbox_id: str, success: bool,
                          response_time: float) -> None:
        """
        Registra resultado de teste em um sandbox.
        """

        if sandbox_id in self.sandbox_metrics:
            self.sandbox_metrics[sandbox_id].record_test_result(success, response_time)

    def get_sandbox_status(self, sandbox_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de um sandbox."""

        metrics = self.sandbox_metrics.get(sandbox_id)
        if not metrics:
            return None

        return {
            "sandbox_id": sandbox_id,
            "status": metrics.status.value,
            "created_at": metrics.created_at.isoformat(),
            "last_accessed": metrics.last_accessed.isoformat(),
            "cpu_usage": metrics.cpu_usage,
            "memory_usage": metrics.memory_usage,
            "disk_usage": metrics.disk_usage,
            "test_count": metrics.test_count,
            "success_rate": metrics.success_rate,
            "avg_response_time": metrics.avg_response_time,
            "cleanup_reason": metrics.cleanup_reason
        }

    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de limpeza."""

        active_sandboxes = sum(1 for m in self.sandbox_metrics.values()
                             if m.status == SandboxStatus.ACTIVE)
        cleaned_sandboxes = sum(1 for m in self.sandbox_metrics.values()
                              if m.status == SandboxStatus.CLEANED)

        return {
            **self.stats,
            "active_sandboxes": active_sandboxes,
            "cleaned_sandboxes": cleaned_sandboxes,
            "total_sandboxes": len(self.sandbox_metrics),
            "recent_cleanups": len(self.cleanup_log[-10:])
        }

    def optimize_cleanup_settings(self) -> Dict[str, Any]:
        """
        Otimiza configurações de limpeza baseado em dados históricos.
        """

        optimizations = {}

        # Analisar padrões de uso
        if self.cleanup_log:
            recent_cleanups = self.cleanup_log[-20:]

            # Ajustar idade máxima baseado em uso
            avg_age_hours = sum(c["results"]["sandboxes_processed"] for c in recent_cleanups) / len(recent_cleanups)
            if avg_age_hours > self.max_age_hours * 0.8:
                self.max_age_hours = int(self.max_age_hours * 1.2)
                optimizations["max_age_hours"] = f"Increased to {self.max_age_hours}h"

            # Ajustar limite de disco baseado em espaço recuperado
            total_space_reclaimed = sum(c["results"]["space_reclaimed_bytes"] for c in recent_cleanups)
            if total_space_reclaimed > 10 * 1024**3:  # 10GB
                self.max_disk_usage_gb *= 0.9  # Ser mais agressivo
                optimizations["max_disk_usage_gb"] = f"Decreased to {self.max_disk_usage_gb}GB"

        return optimizations

    async def perform_performance_optimization(self) -> Dict[str, Any]:
        """
        Executa otimizações de performance nos sandboxes ativos.
        """

        optimization_results = {
            "sandboxes_optimized": 0,
            "performance_improvements": {},
            "errors": []
        }

        for sandbox_id, metrics in self.sandbox_metrics.items():
            if metrics.status != SandboxStatus.ACTIVE:
                continue

            try:
                # Otimizações específicas
                improvements = await self._optimize_sandbox_performance(sandbox_id, metrics)

                if improvements:
                    optimization_results["sandboxes_optimized"] += 1
                    optimization_results["performance_improvements"][sandbox_id] = improvements

            except Exception as e:
                optimization_results["errors"].append(f"Error optimizing {sandbox_id}: {e}")

        return optimization_results

    async def _optimize_sandbox_performance(self, sandbox_id: str,
                                          metrics: SandboxMetrics) -> Dict[str, float]:
        """
        Otimiza performance de um sandbox específico.
        """

        improvements = {}

        # Otimização baseada em métricas
        if metrics.cpu_usage > 0.8:  # Alto uso de CPU
            improvements["cpu_reduction"] = 0.1  # Simulação de redução

        if metrics.memory_usage > 0.8:  # Alto uso de memória
            improvements["memory_reduction"] = 0.15

        if metrics.avg_response_time > 1.0:  # Resposta lenta
            improvements["response_time_improvement"] = 0.2

        # Aplicar otimizações (simulação)
        if improvements:
            await asyncio.sleep(0.1)  # Simular tempo de otimização

        return improvements

    def _calculate_directory_size(self, path: Path) -> int:
        """Calcula tamanho de um diretório."""
        total_size = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size

    def _load_state(self) -> None:
        """Carrega estado do otimizador."""

        # Carregar métricas
        if self.metrics_file.exists():
            try:
                metrics_data = json.loads(self.metrics_file.read_text(encoding='utf-8'))

                for sb_data in metrics_data.get("sandbox_metrics", []):
                    metrics = SandboxMetrics(sb_data["sandbox_id"])
                    metrics.created_at = datetime.fromisoformat(sb_data["created_at"])
                    metrics.last_accessed = datetime.fromisoformat(sb_data["last_accessed"])
                    metrics.cpu_usage = sb_data.get("cpu_usage", 0.0)
                    metrics.memory_usage = sb_data.get("memory_usage", 0.0)
                    metrics.disk_usage = sb_data.get("disk_usage", 0.0)
                    metrics.network_usage = sb_data.get("network_usage", 0.0)
                    metrics.test_count = sb_data.get("test_count", 0)
                    metrics.success_rate = sb_data.get("success_rate", 0.0)
                    metrics.avg_response_time = sb_data.get("avg_response_time", 0.0)
                    metrics.status = SandboxStatus(sb_data.get("status", "active"))
                    metrics.cleanup_reason = sb_data.get("cleanup_reason")

                    self.sandbox_metrics[metrics.sandbox_id] = metrics

                # Carregar estatísticas
                if "stats" in metrics_data:
                    self.stats.update(metrics_data["stats"])

            except Exception as e:
                print(f"Error loading cleanup state: {e}")

        # Carregar log de limpeza
        if self.cleanup_log_file.exists():
            try:
                self.cleanup_log = json.loads(self.cleanup_log_file.read_text(encoding='utf-8'))
            except Exception:
                self.cleanup_log = []

    def _save_state(self) -> None:
        """Persiste estado do otimizador."""

        self.cleanup_dir.mkdir(parents=True, exist_ok=True)

        # Serializar métricas
        metrics_data = {
            "sandbox_metrics": [],
            "stats": self.stats,
            "last_updated": datetime.now().isoformat()
        }

        for metrics in self.sandbox_metrics.values():
            metrics_data["sandbox_metrics"].append({
                "sandbox_id": metrics.sandbox_id,
                "created_at": metrics.created_at.isoformat(),
                "last_accessed": metrics.last_accessed.isoformat(),
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "disk_usage": metrics.disk_usage,
                "network_usage": metrics.network_usage,
                "test_count": metrics.test_count,
                "success_rate": metrics.success_rate,
                "avg_response_time": metrics.avg_response_time,
                "status": metrics.status.value,
                "cleanup_reason": metrics.cleanup_reason
            })

        self.metrics_file.write_text(
            json.dumps(metrics_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Salvar log de limpeza
        self.cleanup_log_file.write_text(
            json.dumps(self.cleanup_log[-100:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
