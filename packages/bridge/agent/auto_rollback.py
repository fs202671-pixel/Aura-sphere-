"""
Sistema de Rollback Automático - Mantém versões funcionais

Este módulo implementa rollback automático quando versões
da IA não atendem aos critérios de qualidade ou segurança.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import shutil


class RollbackTrigger(Enum):
    """Gatilhos para rollback automático."""
    QUALITY_THRESHOLD = "quality_threshold"
    SECURITY_VIOLATION = "security_violation"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    STABILITY_ISSUES = "stability_issues"
    USER_REPORTED_ISSUES = "user_reported_issues"
    MANUAL_TRIGGER = "manual_trigger"


class AutoRollbackManager:
    """
    Gerencia rollback automático para manter sistema funcional.

    Funcionalidades:
    - Monitora qualidade da versão atual
    - Mantém N versões anteriores funcionais
    - Executa rollback automático quando necessário
    - Restaura versão estável automaticamente
    - Log completo de rollbacks
    """

    def __init__(self, data_dir: Path, evolution_manager, quality_metrics):
        self.data_dir = data_dir
        self.rollback_dir = data_dir / "auto_rollback"
        self.rollback_dir.mkdir(parents=True, exist_ok=True)

        self.evolution_manager = evolution_manager
        self.quality_metrics = quality_metrics

        self.rollback_log = self.rollback_dir / "rollback_history.json"
        self.stable_versions_log = self.rollback_dir / "stable_versions.json"

        self.rollback_history: List[Dict] = []
        self.stable_versions: List[str] = []

        self.min_versions_to_keep = 3
        self.quality_threshold = 0.7
        self.max_consecutive_failures = 3

        self._load_state()

    def check_and_rollback_if_needed(self) -> Dict[str, Any]:
        """
        Verifica se rollback é necessário e executa se apropriado.
        """

        check_result = {
            "timestamp": datetime.now().isoformat(),
            "rollback_needed": False,
            "rollback_reason": None,
            "current_version": None,
            "target_version": None,
            "rollback_executed": False
        }

        # Obter versão atual
        current_version = self.evolution_manager.get_current_version()
        if not current_version:
            check_result["error"] = "No current version found"
            return check_result

        check_result["current_version"] = current_version.version_id

        # Verificar triggers de rollback
        rollback_trigger = self._check_rollback_triggers(current_version)

        if rollback_trigger:
            check_result["rollback_needed"] = True
            check_result["rollback_reason"] = rollback_trigger.value

            # Encontrar versão estável para rollback
            target_version = self._find_stable_version()
            if target_version:
                check_result["target_version"] = target_version

                # Executar rollback
                rollback_success = self._execute_rollback(current_version.version_id, target_version)
                check_result["rollback_executed"] = rollback_success

                if rollback_success:
                    self._log_rollback(check_result)

        return check_result

    def _check_rollback_triggers(self, current_version: Any) -> Optional[RollbackTrigger]:
        """
        Verifica se algum trigger de rollback foi ativado.
        """

        # 1. Verificar threshold de qualidade
        if not self.quality_metrics.meets_quality_threshold(self.quality_threshold):
            return RollbackTrigger.QUALITY_THRESHOLD

        # 2. Verificar violações de segurança recentes
        recent_violations = self.quality_metrics.get_metrics_history(
            metric_type=self.quality_metrics.MetricType.SECURITY_VIOLATIONS,
            limit=10
        )

        if len(recent_violations) > 0:
            return RollbackTrigger.SECURITY_VIOLATION

        # 3. Verificar degradação de performance
        performance_history = self.quality_metrics.get_metrics_history(
            metric_type=self.quality_metrics.MetricType.EXECUTION_TIME,
            limit=20
        )

        if self._detect_performance_degradation(performance_history):
            return RollbackTrigger.PERFORMANCE_DEGRADATION

        # 4. Verificar falhas consecutivas
        recent_errors = self.quality_metrics.get_metrics_history(
            metric_type=self.quality_metrics.MetricType.ERROR_RATE,
            limit=10
        )

        if len([e for e in recent_errors if e["value"] > 0]) >= self.max_consecutive_failures:
            return RollbackTrigger.STABILITY_ISSUES

        return None

    def _detect_performance_degradation(self, performance_history: List[Dict]) -> bool:
        """
        Detecta degradação significativa de performance.
        """

        if len(performance_history) < 10:
            return False

        # Calcular média dos últimos 5 vs anteriores
        recent_times = [m["value"] for m in performance_history[-5:]]
        older_times = [m["value"] for m in performance_history[-10:-5]]

        if not recent_times or not older_times:
            return False

        recent_avg = sum(recent_times) / len(recent_times)
        older_avg = sum(older_times) / len(older_times)

        # Se degradação > 50%, considerar problema
        degradation = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0

        return degradation > 0.5

    def _find_stable_version(self) -> Optional[str]:
        """
        Encontra a versão mais estável disponível para rollback.
        """

        # Primeiro tentar versões marcadas como estáveis
        for version_id in reversed(self.stable_versions):
            version = self.evolution_manager.get_version(version_id)
            if version and self._is_version_stable(version):
                return version_id

        # Se não há versões estáveis marcadas, procurar nas versões do evolution manager
        all_versions = self.evolution_manager.get_all_versions()
        stable_candidates = []

        for version in all_versions:
            if self._is_version_stable(version):
                stable_candidates.append(version)

        if stable_candidates:
            # Retornar a versão mais recente que seja estável
            stable_candidates.sort(key=lambda v: v.get("created_at", ""), reverse=True)
            return stable_candidates[0]["version_id"]

        return None

    def _is_version_stable(self, version: Dict) -> bool:
        """
        Verifica se uma versão é considerada estável.
        """

        # Verificar score de qualidade
        quality_score = version.get("metrics", {}).get("overall_score", 0.0)
        if quality_score < self.quality_threshold:
            return False

        # Verificar se não teve violações críticas
        security_score = version.get("metrics", {}).get("security", 1.0)
        if security_score < 0.8:
            return False

        # Verificar se foi testada adequadamente
        test_coverage = version.get("metadata", {}).get("test_coverage", 0.0)
        if test_coverage < 0.7:
            return False

        return True

    def _execute_rollback(self, from_version: str, to_version: str) -> bool:
        """
        Executa o rollback para uma versão específica.
        """

        try:
            # Registrar rollback no evolution manager
            self.evolution_manager.rollback_to_version(to_version)

            # Atualizar versões estáveis
            self._update_stable_versions(to_version)

            return True

        except Exception as e:
            # Log do erro de rollback
            self._log_rollback_error(from_version, to_version, str(e))
            return False

    def mark_version_as_stable(self, version_id: str) -> bool:
        """
        Marca uma versão como estável para futuros rollbacks.
        """

        if version_id not in self.stable_versions:
            self.stable_versions.append(version_id)

            # Manter apenas as últimas N versões estáveis
            if len(self.stable_versions) > self.min_versions_to_keep:
                self.stable_versions = self.stable_versions[-self.min_versions_to_keep:]

            self._save_state()
            return True

        return False

    def get_rollback_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de rollbacks."""
        return self.rollback_history[-limit:]

    def get_stable_versions(self) -> List[str]:
        """Retorna lista de versões consideradas estáveis."""
        return self.stable_versions.copy()

    def force_rollback(self, target_version: str, reason: str = "manual") -> Dict[str, Any]:
        """
        Força rollback manual para uma versão específica.
        """

        result = {
            "timestamp": datetime.now().isoformat(),
            "target_version": target_version,
            "reason": reason,
            "success": False
        }

        current_version = self.evolution_manager.get_current_version()
        if current_version:
            result["from_version"] = current_version.version_id
            result["success"] = self._execute_rollback(current_version.version_id, target_version)

            if result["success"]:
                result["rollback_reason"] = RollbackTrigger.MANUAL_TRIGGER.value
                self._log_rollback(result)

        return result

    def _update_stable_versions(self, new_stable_version: str) -> None:
        """
        Atualiza lista de versões estáveis após rollback.
        """

        if new_stable_version not in self.stable_versions:
            self.stable_versions.append(new_stable_version)

        # Remover versões que não são mais atuais se necessário
        # Manter apenas as mais recentes e estáveis

    def _log_rollback(self, rollback_info: Dict) -> None:
        """Registra rollback no histórico."""

        rollback_entry = {
            "timestamp": datetime.now().isoformat(),
            **rollback_info
        }

        self.rollback_history.append(rollback_entry)
        self._save_state()

    def _log_rollback_error(self, from_version: str, to_version: str, error: str) -> None:
        """Registra erro de rollback."""

        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "rollback_error",
            "from_version": from_version,
            "to_version": to_version,
            "error": error
        }

        self.rollback_history.append(error_entry)
        self._save_state()

    def _load_state(self) -> None:
        """Carrega estado do rollback manager."""

        if self.rollback_log.exists():
            try:
                self.rollback_history = json.loads(
                    self.rollback_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.rollback_history = []

        if self.stable_versions_log.exists():
            try:
                self.stable_versions = json.loads(
                    self.stable_versions_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.stable_versions = []

    def _save_state(self) -> None:
        """Persiste estado do rollback manager."""

        self.rollback_dir.mkdir(parents=True, exist_ok=True)

        self.rollback_log.write_text(
            json.dumps(self.rollback_history[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        self.stable_versions_log.write_text(
            json.dumps(self.stable_versions, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
