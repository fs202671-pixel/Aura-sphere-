"""
Backup e Rollback Manager - Gerencia backups e rollback de patches.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil


class BackupManager:
    """Gerencia backups de arquivos modificados por patches."""

    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backups_file = self.backup_dir / "backups_index.json"
        self.backups: List[Dict[str, Any]] = []
        self._load_backups()

    def _load_backups(self) -> None:
        """Carrega índice de backups."""
        if self.backups_file.exists():
            try:
                self.backups = json.loads(self.backups_file.read_text(encoding='utf-8'))
            except Exception:
                self.backups = []

    def _save_backups(self) -> None:
        """Persiste índice de backups."""
        self.backups_file.write_text(json.dumps(self.backups, ensure_ascii=False, indent=2), encoding='utf-8')

    def create_backup(self, proposal_id: str, files_to_backup: Dict[str, Path]) -> Dict[str, Any]:
        """
        Cria backup de arquivos antes de aplicar patch.

        Args:
            proposal_id: ID da proposta
            files_to_backup: Dict com path_relativo -> Path absoluto

        Returns:
            Dict com informações do backup
        """
        backup_id = f"backup_{proposal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)

        backup_info = {
            "backup_id": backup_id,
            "proposal_id": proposal_id,
            "created_at": datetime.now().isoformat(),
            "files": {}
        }

        for relative_path, abs_path in files_to_backup.items():
            if abs_path.exists():
                # Criar estrutura de diretório
                backup_file_path = backup_path / relative_path
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                # Copiar arquivo
                backup_file_path.write_text(abs_path.read_text(encoding='utf-8'), encoding='utf-8')
                backup_info["files"][relative_path] = {
                    "size": backup_file_path.stat().st_size,
                    "checksum": self._calculate_checksum(backup_file_path)
                }

        self.backups.append(backup_info)
        self._save_backups()

        return backup_info

    def restore_backup(self, backup_id: str, target_dir: Path) -> bool:
        """
        Restaura arquivos de um backup.

        Args:
            backup_id: ID do backup
            target_dir: Diretório raiz onde restaurar

        Returns:
            True se restaurada com sucesso
        """
        backup = self._find_backup(backup_id)
        if not backup:
            return False

        backup_path = self.backup_dir / backup_id
        if not backup_path.exists():
            return False

        try:
            for relative_path in backup["files"].keys():
                backup_file = backup_path / relative_path
                target_file = target_dir / relative_path
                if backup_file.exists():
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    target_file.write_text(backup_file.read_text(encoding='utf-8'), encoding='utf-8')
            return True
        except Exception:
            return False

    def list_backups_for_proposal(self, proposal_id: str) -> List[Dict[str, Any]]:
        """Lista todos os backups de uma proposta."""
        return [b for b in self.backups if b["proposal_id"] == proposal_id]

    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """
        Remove backups mais antigos que o limite.

        Returns:
            Número de backups removidos
        """
        cutoff = datetime.now() - timedelta(days=keep_days)
        removed = 0

        for backup in self.backups[:]:
            try:
                created = datetime.fromisoformat(backup["created_at"])
                if created < cutoff:
                    # Remover pasta de backup
                    backup_path = self.backup_dir / backup["backup_id"]
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    # Remover do índice
                    self.backups.remove(backup)
                    removed += 1
            except Exception:
                continue

        if removed > 0:
            self._save_backups()

        return removed

    def _find_backup(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Encontra backup por ID."""
        for backup in self.backups:
            if backup["backup_id"] == backup_id:
                return backup
        return None

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum simples de um arquivo."""
        import hashlib
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Retorna informações de um backup."""
        return self._find_backup(backup_id)

    def keep_n_latest_backups(self, proposal_id: str, n: int = 3) -> int:
        """
        Mantém apenas os N backups mais recentes de uma proposta.

        Returns:
            Número de backups removidos
        """
        proposal_backups = self.list_backups_for_proposal(proposal_id)
        # Ordenar por data descrescente
        proposal_backups.sort(key=lambda b: b["created_at"], reverse=True)

        removed = 0
        for backup in proposal_backups[n:]:
            backup_path = self.backup_dir / backup["backup_id"]
            if backup_path.exists():
                shutil.rmtree(backup_path)
            if backup in self.backups:
                self.backups.remove(backup)
            removed += 1

        if removed > 0:
            self._save_backups()

        return removed
