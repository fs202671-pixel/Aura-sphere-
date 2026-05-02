"""
Recovery Manager - Gerencia recuperação total do sistema.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class RecoveryManager:
    """Gerencia recuperação do sistema em caso de falha crítica."""

    def __init__(self, repo_root: Path, data_dir: Path):
        self.repo_root = repo_root
        self.data_dir = data_dir
        self.recovery_dir = data_dir / "recovery"
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_log = self.recovery_dir / "recovery_log.json"

    def create_system_snapshot(self) -> Dict[str, Any]:
        """
        Cria snapshot do estado atual do sistema.

        Returns:
            Dict com informações do snapshot
        """
        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        snapshot_dir = self.recovery_dir / snapshot_id

        try:
            # Copiar arquivos críticos
            critical_paths = [
                "packages/bridge/core",
                "packages/bridge/agent",
                "packages/bridge/data"
            ]

            snapshot_dir.mkdir(parents=True, exist_ok=True)
            for path_str in critical_paths:
                source = self.repo_root / path_str
                dest = snapshot_dir / path_str
                if source.exists():
                    if source.is_dir():
                        shutil.copytree(source, dest, dirs_exist_ok=True)
                    else:
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, dest)

            snapshot_info = {
                "snapshot_id": snapshot_id,
                "created_at": datetime.now().isoformat(),
                "components": critical_paths,
                "size_mb": self._get_dir_size_mb(snapshot_dir),
                "status": "complete"
            }

            self._log_recovery_event("snapshot_created", snapshot_info)
            return snapshot_info

        except Exception as e:
            error_info = {
                "snapshot_id": snapshot_id,
                "error": str(e),
                "status": "failed"
            }
            self._log_recovery_event("snapshot_failed", error_info)
            return error_info

    def restore_from_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Restaura sistema de um snapshot.

        Returns:
            Dict com resultado da restauração
        """
        snapshot_dir = self.recovery_dir / snapshot_id
        if not snapshot_dir.exists():
            return {
                "status": "failed",
                "error": f"Snapshot {snapshot_id} não encontrado"
            }

        try:
            # Restaurar arquivos
            for component_dir in snapshot_dir.iterdir():
                if component_dir.is_dir():
                    dest = self.repo_root / component_dir.relative_to(snapshot_dir)
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(component_dir, dest)

            result = {
                "status": "success",
                "snapshot_id": snapshot_id,
                "restored_at": datetime.now().isoformat()
            }

            self._log_recovery_event("restore_completed", result)
            return result

        except Exception as e:
            error_result = {
                "status": "failed",
                "snapshot_id": snapshot_id,
                "error": str(e)
            }
            self._log_recovery_event("restore_failed", error_result)
            return error_result

    def restore_clean_core(self) -> Dict[str, Any]:
        """
        Restaura core imutável para estado limpo.

        Returns:
            Dict com status da restauração
        """
        core_dir = self.repo_root / "packages/bridge/core"
        core_backup_source = self.recovery_dir / "clean_core_backup"

        if not core_backup_source.exists():
            return {
                "status": "failed",
                "error": "Backup limpo do core não encontrado"
            }

        try:
            if core_dir.exists():
                shutil.rmtree(core_dir)
            shutil.copytree(core_backup_source, core_dir)

            return {
                "status": "success",
                "component": "core",
                "restored_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    def reset_agent_to_defaults(self) -> Dict[str, Any]:
        """
        Reseta agente para configuração padrão.

        Returns:
            Dict com status do reset
        """
        agent_defaults = {
            "offline_mode": True,
            "permission_level": 0,
            "safe_mode": False,
            "data_cleared_at": datetime.now().isoformat()
        }

        try:
            # Limpar propostas de modificação
            proposals_file = self.data_dir / "modification_proposals.json"
            if proposals_file.exists():
                proposals_file.unlink()

            # Limpar patches
            patch_dir = self.data_dir / "patches"
            if patch_dir.exists():
                shutil.rmtree(patch_dir)
                patch_dir.mkdir(parents=True, exist_ok=True)

            # Limpar memória de evolução
            evolution_dir = self.data_dir / "versions"
            if evolution_dir.exists():
                shutil.rmtree(evolution_dir)
                evolution_dir.mkdir(parents=True, exist_ok=True)

            result = {
                "status": "success",
                "reset_at": datetime.now().isoformat(),
                "defaults": agent_defaults
            }

            self._log_recovery_event("agent_reset", result)
            return result

        except Exception as e:
            error_result = {
                "status": "failed",
                "error": str(e)
            }
            self._log_recovery_event("agent_reset_failed", error_result)
            return error_result

    def perform_full_recovery(self, snapshot_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa recuperação completa do sistema.

        Returns:
            Dict com resultado da recuperação
        """
        recovery_steps = []

        # 1. Restaurar core limpo
        step1 = self.restore_clean_core()
        recovery_steps.append({"step": "restore_clean_core", "result": step1})

        # 2. Restaurar snapshot se especificado
        if snapshot_id:
            step2 = self.restore_from_snapshot(snapshot_id)
            recovery_steps.append({"step": "restore_snapshot", "result": step2})

        # 3. Reset do agente
        step3 = self.reset_agent_to_defaults()
        recovery_steps.append({"step": "reset_agent", "result": step3})

        overall_success = all(step["result"].get("status") != "failed" for step in recovery_steps)

        result = {
            "status": "success" if overall_success else "partial",
            "recovered_at": datetime.now().isoformat(),
            "steps": recovery_steps
        }

        self._log_recovery_event("full_recovery", result)
        return result

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """Lista todos os snapshots disponíveis."""
        snapshots = []
        for snapshot_dir in self.recovery_dir.iterdir():
            if snapshot_dir.is_dir() and snapshot_dir.name.startswith("snapshot_"):
                snapshots.append({
                    "snapshot_id": snapshot_dir.name,
                    "size_mb": self._get_dir_size_mb(snapshot_dir),
                    "created_at": self._extract_timestamp(snapshot_dir.name)
                })
        return sorted(snapshots, key=lambda x: x["created_at"], reverse=True)

    def get_recovery_status(self) -> Dict[str, Any]:
        """Retorna status de recuperação do sistema."""
        snapshots = self.list_snapshots()
        log_entries = self._load_recovery_log()

        return {
            "snapshots_available": len(snapshots),
            "last_snapshot": snapshots[0] if snapshots else None,
            "recent_recovery_events": log_entries[-10:] if log_entries else [],
            "recovery_enabled": True
        }

    def _get_dir_size_mb(self, dir_path: Path) -> float:
        """Calcula tamanho de diretório em MB."""
        total_size = 0
        for path in dir_path.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
        return total_size / (1024 * 1024)

    def _extract_timestamp(self, snapshot_name: str) -> str:
        """Extrai timestamp do nome do snapshot."""
        parts = snapshot_name.split("_")
        if len(parts) >= 3:
            return f"{parts[1]} {parts[2]}"
        return snapshot_name

    def _log_recovery_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Registra evento de recuperação."""
        entries = self._load_recovery_log()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        entries.append(entry)
        self.recovery_log.write_text(json.dumps(entries[-100:], ensure_ascii=False, indent=2), encoding='utf-8')

    def _load_recovery_log(self) -> List[Dict[str, Any]]:
        """Carrega log de recuperação."""
        if self.recovery_log.exists():
            try:
                return json.loads(self.recovery_log.read_text(encoding='utf-8'))
            except Exception:
                return []
        return []
