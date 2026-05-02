"""
Controlled Deploy Pipeline - Validação → Sandbox → Comparação → Deploy

Este módulo implementa o pipeline completo de deploy com múltiplas
validações antes de aplicar qualquer mudança.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import subprocess
import sys


class DeployStage(Enum):
    """Estágios do pipeline de deploy."""
    VALIDATION = "validation"
    SANDBOX_TEST = "sandbox_test"
    COMPARISON = "comparison"
    USER_APPROVAL = "user_approval"
    DEPLOYMENT = "deployment"
    VERIFICATION = "verification"


class DeployStatus(Enum):
    """Status do deploy."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ControlledDeployPipeline:
    """
    Pipeline controlado de deploy com validação em múltiplas camadas.
    
    Fluxo:
    1. VALIDATION - Verifica integridade e segurança
    2. SANDBOX_TEST - Executa em ambiente isolado
    3. COMPARISON - Compara com versão anterior
    4. USER_APPROVAL - Aguarda aprovação do usuário
    5. DEPLOYMENT - Aplica mudanças
    6. VERIFICATION - Valida resultado final
    """

    def __init__(self, data_dir: Path, patch_validator, backup_manager):
        self.data_dir = data_dir
        self.patch_validator = patch_validator
        self.backup_manager = backup_manager
        self.deploys_log = data_dir / "deploys.json"
        self.sandbox_dir = data_dir / ".sandbox"
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.deploys: list = []
        self._load_deploys()

    def validate_patch(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estágio 1: VALIDATION
        Valida patch contra regras de segurança.
        """
        validation_result = {
            "stage": DeployStage.VALIDATION.value,
            "timestamp": datetime.now().isoformat(),
            "patch_id": patch.get("id"),
            "passed": True,
            "checks": []
        }

        # Usar validator externo
        is_valid, issues = self.patch_validator.validate(patch)
        
        validation_result["passed"] = is_valid
        validation_result["checks"] = issues

        return validation_result

    def sandbox_test(self, patch: Dict[str, Any],
                    test_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Estágio 2: SANDBOX_TEST
        Executa patch em ambiente isolado e valida resultado.
        """
        sandbox_result = {
            "stage": DeployStage.SANDBOX_TEST.value,
            "timestamp": datetime.now().isoformat(),
            "patch_id": patch.get("id"),
            "success": False,
            "error": None,
            "output": None
        }

        try:
            # Criar diretório sandbox isolado
            sandbox_path = self.sandbox_dir / f"test_{patch.get('id')}"
            sandbox_path.mkdir(parents=True, exist_ok=True)

            # Aplicar patch em cópia isolada
            for file_changes in patch.get("changes", []):
                file_path = sandbox_path / file_changes["file"]
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(
                    file_changes["content"],
                    encoding='utf-8'
                )

            # Executar testes
            test_result = self._run_sandbox_tests(sandbox_path)
            
            sandbox_result["success"] = test_result["passed"]
            sandbox_result["output"] = test_result["output"]

            # Limpar sandbox após teste
            import shutil
            shutil.rmtree(sandbox_path, ignore_errors=True)

        except Exception as e:
            sandbox_result["error"] = str(e)

        return sandbox_result

    def compare_versions(self, patch: Dict[str, Any],
                        current_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Estágio 3: COMPARISON
        Compara patch com versão atual e anterior.
        """
        comparison = {
            "stage": DeployStage.COMPARISON.value,
            "timestamp": datetime.now().isoformat(),
            "patch_id": patch.get("id"),
            "diff_summary": {
                "files_changed": len(patch.get("changes", [])),
                "lines_added": 0,
                "lines_deleted": 0
            },
            "breaking_changes": [],
            "compatibility": "compatible"
        }

        # Análise simples de diferenças
        for change in patch.get("changes", []):
            old_content = change.get("old_content", "")
            new_content = change.get("content", "")
            
            # Contar linhas
            old_lines = len(old_content.split("\n"))
            new_lines = len(new_content.split("\n"))
            
            comparison["diff_summary"]["lines_added"] += max(0, new_lines - old_lines)
            comparison["diff_summary"]["lines_deleted"] += max(0, old_lines - new_lines)

        return comparison

    def prepare_for_deployment(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estágio 4: USER_APPROVAL
        Prepara tudo para deploy e aguarda aprovação.
        """
        approval_prep = {
            "stage": DeployStage.USER_APPROVAL.value,
            "timestamp": datetime.now().isoformat(),
            "patch_id": patch.get("id"),
            "backup_created": False,
            "ready_for_deploy": False
        }

        try:
            # Criar backup antes de deploy
            backup_id = self.backup_manager.create_backup(patch.get("id", "unknown"))
            approval_prep["backup_created"] = True
            approval_prep["backup_id"] = backup_id
            approval_prep["ready_for_deploy"] = True

        except Exception as e:
            approval_prep["error"] = str(e)
            approval_prep["ready_for_deploy"] = False

        return approval_prep

    def deploy(self, patch: Dict[str, Any],
              user_approval: bool = False) -> Dict[str, Any]:
        """
        Estágio 5: DEPLOYMENT
        Aplica patch após todas as validações e aprovação.
        """
        deploy_record = {
            "stage": DeployStage.DEPLOYMENT.value,
            "timestamp": datetime.now().isoformat(),
            "patch_id": patch.get("id"),
            "success": False,
            "files_deployed": [],
            "errors": []
        }

        if not user_approval:
            deploy_record["error"] = "Aguardando aprovação do usuário"
            return deploy_record

        try:
            # Aplicar mudanças
            for change in patch.get("changes", []):
                try:
                    file_path = Path(change["file"])
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(
                        change["content"],
                        encoding='utf-8'
                    )
                    deploy_record["files_deployed"].append(change["file"])
                except Exception as e:
                    deploy_record["errors"].append({
                        "file": change["file"],
                        "error": str(e)
                    })

            deploy_record["success"] = len(deploy_record["errors"]) == 0

        except Exception as e:
            deploy_record["error"] = str(e)

        self.deploys.append(deploy_record)
        self._save_deploys()

        return deploy_record

    def verify_deployment(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estágio 6: VERIFICATION
        Valida que deploy foi bem-sucedido.
        """
        verification = {
            "stage": DeployStage.VERIFICATION.value,
            "timestamp": datetime.now().isoformat(),
            "patch_id": patch.get("id"),
            "passed": True,
            "checks": []
        }

        # Verificar integridade dos arquivos
        for change in patch.get("changes", []):
            file_path = Path(change["file"])
            
            check = {
                "file": change["file"],
                "exists": file_path.exists(),
                "content_matches": False
            }

            if file_path.exists():
                current_content = file_path.read_text(encoding='utf-8')
                check["content_matches"] = current_content == change["content"]

            verification["checks"].append(check)
            verification["passed"] = verification["passed"] and check["content_matches"]

        return verification

    def run_full_pipeline(self, patch: Dict[str, Any],
                         user_approval: bool = False) -> Dict[str, Any]:
        """
        Executa o pipeline completo.
        """
        pipeline_result = {
            "patch_id": patch.get("id"),
            "started_at": datetime.now().isoformat(),
            "stages": {},
            "overall_status": DeployStatus.PENDING.value,
            "ready_to_deploy": False
        }

        # Estágio 1: Validação
        validation = self.validate_patch(patch)
        pipeline_result["stages"]["validation"] = validation

        if not validation["passed"]:
            pipeline_result["overall_status"] = DeployStatus.FAILED.value
            return pipeline_result

        # Estágio 2: Sandbox
        sandbox = self.sandbox_test(patch)
        pipeline_result["stages"]["sandbox"] = sandbox

        if not sandbox["success"]:
            pipeline_result["overall_status"] = DeployStatus.FAILED.value
            return pipeline_result

        # Estágio 3: Comparação
        comparison = self.compare_versions(patch)
        pipeline_result["stages"]["comparison"] = comparison

        # Estágio 4: Preparação para Deploy
        approval = self.prepare_for_deployment(patch)
        pipeline_result["stages"]["approval"] = approval

        if not approval["ready_for_deploy"]:
            pipeline_result["overall_status"] = DeployStatus.PENDING.value
            return pipeline_result

        pipeline_result["ready_to_deploy"] = True

        # Estágio 5: Deploy (apenas com aprovação)
        if user_approval:
            deploy = self.deploy(patch, user_approval=True)
            pipeline_result["stages"]["deployment"] = deploy

            if deploy["success"]:
                # Estágio 6: Verificação
                verification = self.verify_deployment(patch)
                pipeline_result["stages"]["verification"] = verification

                if verification["passed"]:
                    pipeline_result["overall_status"] = DeployStatus.SUCCESS.value
                else:
                    pipeline_result["overall_status"] = DeployStatus.FAILED.value
            else:
                pipeline_result["overall_status"] = DeployStatus.FAILED.value

        pipeline_result["completed_at"] = datetime.now().isoformat()

        self.deploys.append(pipeline_result)
        self._save_deploys()

        return pipeline_result

    def rollback_deployment(self, patch_id: str, backup_id: str) -> Dict[str, Any]:
        """
        Reverte deploy usando backup.
        """
        rollback_result = {
            "timestamp": datetime.now().isoformat(),
            "patch_id": patch_id,
            "backup_id": backup_id,
            "success": False
        }

        try:
            # Restaurar do backup
            restored = self.backup_manager.restore_backup(backup_id)
            rollback_result["success"] = restored
        except Exception as e:
            rollback_result["error"] = str(e)

        return rollback_result

    def _run_sandbox_tests(self, sandbox_path: Path) -> Dict[str, Any]:
        """
        Executa testes de sintaxe no sandbox.
        """
        results = {
            "passed": True,
            "output": ""
        }

        # Verificar sintaxe Python
        python_files = list(sandbox_path.glob("**/*.py"))
        for py_file in python_files:
            try:
                compile(py_file.read_text(), str(py_file), 'exec')
            except SyntaxError as e:
                results["passed"] = False
                results["output"] += f"\nSyntax error in {py_file}: {e}"

        return results

    def _load_deploys(self) -> None:
        """Carrega histórico de deploys."""
        if self.deploys_log.exists():
            try:
                self.deploys = json.loads(
                    self.deploys_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.deploys = []

    def _save_deploys(self) -> None:
        """Persiste histórico de deploys."""
        self.deploys_log.parent.mkdir(parents=True, exist_ok=True)
        self.deploys_log.write_text(
            json.dumps(self.deploys[-500:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
