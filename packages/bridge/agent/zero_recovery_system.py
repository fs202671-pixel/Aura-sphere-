"""
Sistema de Recuperação Total (Zero Recovery System)
Implementa recuperação completa do sistema em caso de falha crítica.
"""

import os
import shutil
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class RecoveryPoint:
    """Ponto de recuperação do sistema"""
    timestamp: str
    version: str
    core_hash: str
    agent_hash: str
    runtime_hash: str
    database_backup: str
    config_backup: str
    is_stable: bool = False

@dataclass
class RecoveryConfig:
    """Configuração do sistema de recuperação"""
    max_recovery_points: int = 10
    auto_recovery_enabled: bool = True
    recovery_timeout_seconds: int = 300
    backup_frequency_hours: int = 24
    critical_files: List[str] = None

    def __post_init__(self):
        if self.critical_files is None:
            self.critical_files = [
                "packages/bridge/agent/core/",
                "packages/bridge/agent/database.py",
                "packages/bridge/agent/schemas.py",
                "packages/bridge/agent/app.py",
                "supabase/migrations/",
                "SYSTEM_EVOLUTION_TASKS.md"
            ]

class ZeroRecoverySystem:
    """
    Sistema de recuperação zero - restaura sistema completamente em caso de falha crítica
    """

    def __init__(self, base_path: str = "/workspaces/Aura-sphere-"):
        self.base_path = Path(base_path)
        self.recovery_path = self.base_path / "recovery"
        self.backup_path = self.recovery_path / "backups"
        self.config_path = self.recovery_path / "recovery_config.json"

        # Criar diretórios se não existirem
        self.recovery_path.mkdir(exist_ok=True)
        self.backup_path.mkdir(exist_ok=True)

        # Configuração
        self.config = self._load_config()

        # Logger
        self.logger = logging.getLogger("ZeroRecovery")
        self.logger.setLevel(logging.INFO)

        # Estado atual
        self.current_recovery_point: Optional[RecoveryPoint] = None
        self.recovery_points: List[RecoveryPoint] = []

        # Carregar pontos de recuperação existentes
        self._load_recovery_points()

    def _load_config(self) -> RecoveryConfig:
        """Carrega configuração do sistema de recuperação"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                return RecoveryConfig(**data)
        else:
            config = RecoveryConfig()
            self._save_config(config)
            return config

    def _save_config(self, config: RecoveryConfig):
        """Salva configuração do sistema de recuperação"""
        with open(self.config_path, 'w') as f:
            json.dump(asdict(config), f, indent=2)

    def _load_recovery_points(self):
        """Carrega pontos de recuperação existentes"""
        points_file = self.recovery_path / "recovery_points.json"
        if points_file.exists():
            with open(points_file, 'r') as f:
                data = json.load(f)
                self.recovery_points = [RecoveryPoint(**point) for point in data]

    def _save_recovery_points(self):
        """Salva pontos de recuperação"""
        points_file = self.recovery_path / "recovery_points.json"
        with open(points_file, 'w') as f:
            json.dump([asdict(point) for point in self.recovery_points], f, indent=2)

    def create_recovery_point(self, version: str, is_stable: bool = False) -> RecoveryPoint:
        """
        Cria um novo ponto de recuperação
        """
        timestamp = datetime.now().isoformat()

        # Calcular hashes dos componentes
        core_hash = self._calculate_directory_hash(self.base_path / "packages/bridge/agent/core")
        agent_hash = self._calculate_directory_hash(self.base_path / "packages/bridge/agent")
        runtime_hash = self._calculate_directory_hash(self.base_path / "src")

        # Criar backup do banco
        db_backup = self._backup_database()

        # Criar backup de configurações
        config_backup = self._backup_config()

        # Criar ponto de recuperação
        recovery_point = RecoveryPoint(
            timestamp=timestamp,
            version=version,
            core_hash=core_hash,
            agent_hash=agent_hash,
            runtime_hash=runtime_hash,
            database_backup=db_backup,
            config_backup=config_backup,
            is_stable=is_stable
        )

        # Adicionar à lista
        self.recovery_points.append(recovery_point)

        # Manter apenas os mais recentes
        if len(self.recovery_points) > self.config.max_recovery_points:
            oldest = self.recovery_points.pop(0)
            self._cleanup_recovery_point(oldest)

        # Salvar
        self._save_recovery_points()

        self.logger.info(f"Ponto de recuperação criado: {version} ({timestamp})")
        return recovery_point

    def _calculate_directory_hash(self, path: Path) -> str:
        """Calcula hash de um diretório"""
        import hashlib

        if not path.exists():
            return ""

        hash_md5 = hashlib.md5()
        for file_path in sorted(path.rglob("*")):
            if file_path.is_file():
                try:
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                except:
                    pass  # Ignorar arquivos que não podem ser lidos

        return hash_md5.hexdigest()

    def _backup_database(self) -> str:
        """Faz backup do banco de dados"""
        db_path = self.base_path / "packages/bridge/agent" / "agent.db"
        if not db_path.exists():
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"database_{timestamp}.db"
        backup_path = self.backup_path / backup_name

        shutil.copy2(db_path, backup_path)
        return str(backup_path)

    def _backup_config(self) -> str:
        """Faz backup das configurações críticas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"config_{timestamp}.tar.gz"
        backup_path = self.backup_path / backup_name

        import tarfile

        with tarfile.open(backup_path, "w:gz") as tar:
            for file_path in self.config.critical_files:
                full_path = self.base_path / file_path
                if full_path.exists():
                    tar.add(full_path, arcname=file_path)

        return str(backup_path)

    def _cleanup_recovery_point(self, point: RecoveryPoint):
        """Remove arquivos de backup de um ponto de recuperação"""
        try:
            if os.path.exists(point.database_backup):
                os.remove(point.database_backup)
            if os.path.exists(point.config_backup):
                os.remove(point.config_backup)
        except Exception as e:
            self.logger.warning(f"Erro ao limpar ponto de recuperação: {e}")

    def initiate_zero_recovery(self, target_version: Optional[str] = None) -> bool:
        """
        Inicia recuperação zero do sistema
        """
        self.logger.critical("INICIANDO RECUPERAÇÃO ZERO DO SISTEMA")

        try:
            # Encontrar ponto de recuperação
            recovery_point = self._find_recovery_point(target_version)
            if not recovery_point:
                self.logger.error("Nenhum ponto de recuperação válido encontrado")
                return False

            self.logger.info(f"Usando ponto de recuperação: {recovery_point.version}")

            # Fase 1: Backup do estado atual (se possível)
            self._emergency_backup()

            # Fase 2: Limpar sistema atual
            self._clean_system()

            # Fase 3: Restaurar do ponto de recuperação
            success = self._restore_from_point(recovery_point)

            if success:
                self.logger.info("RECUPERAÇÃO ZERO CONCLUÍDA COM SUCESSO")
                return True
            else:
                self.logger.error("FALHA NA RECUPERAÇÃO ZERO")
                return False

        except Exception as e:
            self.logger.critical(f"ERRO CRÍTICO NA RECUPERAÇÃO: {e}")
            return False

    def _find_recovery_point(self, target_version: Optional[str] = None) -> Optional[RecoveryPoint]:
        """Encontra o melhor ponto de recuperação"""
        if target_version:
            # Procurar versão específica
            for point in reversed(self.recovery_points):
                if point.version == target_version:
                    return point
        else:
            # Usar o ponto estável mais recente
            for point in reversed(self.recovery_points):
                if point.is_stable:
                    return point

            # Se não há estável, usar o mais recente
            if self.recovery_points:
                return self.recovery_points[-1]

        return None

    def _emergency_backup(self):
        """Backup de emergência do estado atual"""
        try:
            emergency_path = self.recovery_path / "emergency_backup"
            emergency_path.mkdir(exist_ok=True)

            # Copiar arquivos críticos
            for file_path in self.config.critical_files:
                src = self.base_path / file_path
                dst = emergency_path / file_path
                if src.exists():
                    if src.is_file():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
                    else:
                        shutil.copytree(src, dst, dirs_exist_ok=True)

            self.logger.info("Backup de emergência criado")
        except Exception as e:
            self.logger.warning(f"Falha no backup de emergência: {e}")

    def _clean_system(self):
        """Limpa o sistema atual para recuperação"""
        self.logger.info("Limpando sistema atual...")

        # Remover arquivos do agent (exceto core)
        agent_path = self.base_path / "packages/bridge/agent"
        for item in agent_path.iterdir():
            if item.name != "core" and item.is_file():
                try:
                    if item.suffix == ".db":
                        # Não remover banco se for o único
                        continue
                    item.unlink()
                except:
                    pass

        # Limpar src (exceto arquivos essenciais)
        src_path = self.base_path / "src"
        essential_files = ["main.tsx", "App.tsx", "index.css", "App.css"]
        for item in src_path.iterdir():
            if item.is_file() and item.name not in essential_files:
                try:
                    item.unlink()
                except:
                    pass

        self.logger.info("Sistema limpo para recuperação")

    def _restore_from_point(self, point: RecoveryPoint) -> bool:
        """Restaura sistema do ponto de recuperação"""
        try:
            self.logger.info("Restaurando banco de dados...")
            if point.database_backup and os.path.exists(point.database_backup):
                db_dest = self.base_path / "packages/bridge/agent" / "agent.db"
                shutil.copy2(point.database_backup, db_dest)

            self.logger.info("Restaurando configurações...")
            if point.config_backup and os.path.exists(point.config_backup):
                import tarfile
                with tarfile.open(point.config_backup, "r:gz") as tar:
                    tar.extractall(self.base_path)

            self.logger.info("Sistema restaurado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Falha na restauração: {e}")
            return False

    def get_recovery_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de recuperação"""
        return {
            "total_recovery_points": len(self.recovery_points),
            "latest_stable": next((p for p in reversed(self.recovery_points) if p.is_stable), None),
            "latest_any": self.recovery_points[-1] if self.recovery_points else None,
            "auto_recovery_enabled": self.config.auto_recovery_enabled,
            "backup_frequency_hours": self.config.backup_frequency_hours
        }

    def mark_version_stable(self, version: str):
        """Marca uma versão como estável"""
        for point in self.recovery_points:
            if point.version == version:
                point.is_stable = True
                self._save_recovery_points()
                self.logger.info(f"Versão {version} marcada como estável")
                break

    def list_recovery_points(self) -> List[Dict[str, Any]]:
        """Lista todos os pontos de recuperação"""
        return [asdict(point) for point in self.recovery_points]

    def validate_system_integrity(self) -> Dict[str, Any]:
        """Valida integridade do sistema atual"""
        results = {
            "core_integrity": True,
            "agent_integrity": True,
            "runtime_integrity": True,
            "database_integrity": True,
            "issues": []
        }

        try:
            # Verificar core
            core_path = self.base_path / "packages/bridge/agent/core"
            if not core_path.exists():
                results["core_integrity"] = False
                results["issues"].append("Core directory missing")

            # Verificar agent
            agent_path = self.base_path / "packages/bridge/agent"
            if not (agent_path / "app.py").exists():
                results["agent_integrity"] = False
                results["issues"].append("Agent app.py missing")

            # Verificar runtime
            runtime_path = self.base_path / "src"
            if not (runtime_path / "main.tsx").exists():
                results["runtime_integrity"] = False
                results["issues"].append("Runtime main.tsx missing")

            # Verificar banco
            db_path = agent_path / "agent.db"
            if db_path.exists():
                try:
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("SELECT 1").fetchone()
                    conn.close()
                except:
                    results["database_integrity"] = False
                    results["issues"].append("Database corrupted")
            else:
                results["database_integrity"] = False
                results["issues"].append("Database missing")

        except Exception as e:
            results["issues"].append(f"Integrity check error: {e}")

        return results