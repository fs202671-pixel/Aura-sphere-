"""
Core Validator - Validador de Integridade do Sistema

Responsável por verificar a integridade do core e validar operações críticas.
"""

import hashlib
import os
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import json

from .immutable import IMMUTABLE_RULES, validate_rule_compliance
from .permissions import PermissionLevel, permission_manager

class CoreValidator:
    """Validador de integridade e conformidade do core"""

    # Arquivos críticos que devem existir e não serem modificados
    CORE_FILES = {
        "core/__init__.py",
        "core/immutable.py",
        "core/permissions.py",
        "core/validator.py"
    }

    # Hash esperado dos arquivos do core (deve ser atualizado quando houver mudanças legítimas)
    EXPECTED_HASHES = {
        # Estes hashes devem ser gerados após implementação final
        # Por enquanto, aceitamos qualquer hash válido
    }

    def __init__(self):
        self.validation_history: List[Dict[str, Any]] = []
        self.last_validation = None

    def validate_core_integrity(self) -> Dict[str, Any]:
        """
        Valida a integridade completa do core

        Returns:
            Dict com resultado da validação
        """

        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {},
            "violations": []
        }

        # 1. Verificar se todos os arquivos existem
        files_exist = self._check_core_files_exist()
        results["checks"]["files_exist"] = files_exist

        # 2. Calcular e verificar hashes
        hash_check = self._validate_file_hashes()
        results["checks"]["file_hashes"] = hash_check

        # 3. Verificar sintaxe dos arquivos Python
        syntax_check = self._validate_python_syntax()
        results["checks"]["python_syntax"] = syntax_check

        # 4. Verificar imports e dependências
        import_check = self._validate_imports()
        results["checks"]["imports"] = import_check

        # Determinar status geral
        all_passed = all(result["status"] == "passed" for result in [
            files_exist, hash_check, syntax_check, import_check
        ])

        results["overall_status"] = "passed" if all_passed else "failed"

        # Coletar violações
        for check_name, check_result in results["checks"].items():
            if check_result["status"] == "failed":
                results["violations"].append({
                    "check": check_name,
                    "details": check_result.get("details", "Unknown error")
                })

        # Registrar no histórico
        self.validation_history.append(results)
        self.last_validation = results

        # Manter apenas últimas 50 validações
        if len(self.validation_history) > 50:
            self.validation_history = self.validation_history[-50:]

        return results

    def _check_core_files_exist(self) -> Dict[str, Any]:
        """Verifica se todos os arquivos do core existem"""
        missing_files = []
        existing_files = []

        for file_path in self.CORE_FILES:
            if os.path.exists(file_path):
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)

        return {
            "status": "passed" if not missing_files else "failed",
            "existing_files": existing_files,
            "missing_files": missing_files,
            "details": f"Missing: {missing_files}" if missing_files else "All files present"
        }

    def _validate_file_hashes(self) -> Dict[str, Any]:
        """Valida hashes SHA256 dos arquivos do core"""
        violations = []

        for file_path in self.CORE_FILES:
            if not os.path.exists(file_path):
                continue

            current_hash = self._calculate_file_hash(file_path)
            expected_hash = self.EXPECTED_HASHES.get(file_path)

            if expected_hash and current_hash != expected_hash:
                violations.append({
                    "file": file_path,
                    "expected": expected_hash,
                    "current": current_hash
                })

        return {
            "status": "passed" if not violations else "failed",
            "violations": violations,
            "details": f"Hash violations: {len(violations)}" if violations else "All hashes valid"
        }

    def _validate_python_syntax(self) -> Dict[str, Any]:
        """Valida sintaxe Python dos arquivos do core"""
        syntax_errors = []

        for file_path in self.CORE_FILES:
            if not file_path.endswith('.py') or not os.path.exists(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
            except SyntaxError as e:
                syntax_errors.append({
                    "file": file_path,
                    "error": str(e),
                    "line": e.lineno
                })
            except Exception as e:
                syntax_errors.append({
                    "file": file_path,
                    "error": f"Unexpected error: {str(e)}"
                })

        return {
            "status": "passed" if not syntax_errors else "failed",
            "syntax_errors": syntax_errors,
            "details": f"Syntax errors: {len(syntax_errors)}" if syntax_errors else "Syntax valid"
        }

    def _validate_imports(self) -> Dict[str, Any]:
        """Valida se os imports do core funcionam"""
        import_errors = []

        # Tentar importar cada módulo do core
        modules_to_test = [
            ("core", "core"),
            ("core.immutable", "core.immutable"),
            ("core.permissions", "core.permissions")
        ]

        for module_name, module_path in modules_to_test:
            try:
                __import__(module_name)
            except ImportError as e:
                import_errors.append({
                    "module": module_name,
                    "error": str(e)
                })
            except Exception as e:
                import_errors.append({
                    "module": module_name,
                    "error": f"Unexpected error: {str(e)}"
                })

        return {
            "status": "passed" if not import_errors else "failed",
            "import_errors": import_errors,
            "details": f"Import errors: {len(import_errors)}" if import_errors else "Imports valid"
        }

    def validate_operation(self, user_id: str, operation: str,
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida uma operação crítica contra regras imutáveis e permissões

        Args:
            user_id: ID do usuário executando a operação
            operation: Nome da operação
            context: Contexto da operação

        Returns:
            Dict com resultado da validação
        """

        results = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "validations": {},
            "approved": False
        }

        # 1. Validar contra regras imutáveis
        rule_validation = validate_rule_compliance(operation, context)
        results["validations"]["immutable_rules"] = rule_validation

        # 2. Verificar permissões
        required_level = self._get_required_permission_level(operation)
        permission_check = permission_manager.check_permission(
            user_id, required_level, operation
        )
        results["validations"]["permissions"] = permission_check

        # 3. Verificações específicas da operação
        specific_checks = self._validate_operation_specifics(operation, context)
        results["validations"]["specific"] = specific_checks

        # Determinar se operação é aprovada
        all_validations_passed = all(
            validation.get("compliant", validation.get("allowed", validation.get("status") == "passed"))
            for validation in results["validations"].values()
        )

        results["approved"] = all_validations_passed

        # Log da validação
        self._log_validation(results)

        return results

    def _get_required_permission_level(self, operation: str) -> PermissionLevel:
        """Determina o nível de permissão necessário para uma operação"""

        # Operações críticas requerem nível máximo
        critical_ops = [
            "modify_core", "delete_system_files", "override_security",
            "grant_admin_permissions", "disable_security"
        ]

        if any(op in operation for op in critical_ops):
            return PermissionLevel.LEVEL_4_PRODUCTION_EVOLUTION  # Nunca deve ser usado

        # Operações de produção
        production_ops = [
            "deploy_to_production", "modify_production_code",
            "restart_production_services"
        ]

        if any(op in operation for op in production_ops):
            return PermissionLevel.LEVEL_3_SANDBOX_EVOLUTION

        # Operações com confirmação
        confirmed_ops = [
            "execute_system_command", "modify_files",
            "install_packages", "restart_services"
        ]

        if any(op in operation for op in confirmed_ops):
            return PermissionLevel.LEVEL_2_EXECUTE_CONFIRMED

        # Operações de sandbox
        sandbox_ops = [
            "execute_code_sandbox", "run_sandbox", "sandbox_execute"
        ]

        if any(op in operation for op in sandbox_ops):
            return PermissionLevel.LEVEL_2_EXECUTE_CONFIRMED

    def _validate_operation_specifics(self, operation: str,
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Valificações específicas por tipo de operação"""

        # Implementar validações específicas conforme necessário
        # Por enquanto, retorna sempre válido
        return {
            "status": "passed",
            "details": "No specific validations implemented yet"
        }

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula hash SHA256 de um arquivo"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
        except Exception:
            return "error_calculating_hash"

        return hasher.hexdigest()

    def _log_validation(self, validation_result: Dict[str, Any]) -> None:
        """Registra validação no histórico"""
        # Adicionar ao histórico de validações
        pass  # Implementar se necessário

    def get_validation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna histórico de validações"""
        return self.validation_history[-limit:]

# ========== INSTÂNCIA GLOBAL ==========

core_validator = CoreValidator()

# ========== FUNÇÕES DE CONVENIÊNCIA ==========

def validate_system_integrity() -> bool:
    """Valida integridade completa do sistema"""
    result = core_validator.validate_core_integrity()
    return result["overall_status"] == "passed"

def validate_operation(user_id: str, operation: str,
                      context: Optional[Dict[str, Any]] = None) -> bool:
    """Valida se uma operação pode ser executada"""
    context = context or {}
    result = core_validator.validate_operation(user_id, operation, context)
    return result["approved"]