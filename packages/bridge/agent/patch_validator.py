"""
Validador de Patches - Verifica segurança de patches antes de aplicar.
"""

import re
from typing import Dict, List, Tuple, Any
from pathlib import Path


class PatchValidator:
    """Valida patches contra regras de segurança."""

    # Padrões perigosos que não podem estar em patches
    FORBIDDEN_PATTERNS = [
        r"__import__\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",
        r"open\s*\(",
        r"os\.system\s*\(",
        r"subprocess\.call\s*\(",
        r"rm\s+-rf",
        r"rmdir\s+.*?\/.*",
    ]

    # Arquivos críticos que não podem ser modificados
    CRITICAL_FILES = {
        "core/__init__.py",
        "core/immutable.py",
        "core/permissions.py",
        "core/validator.py",
    }

    def __init__(self):
        self.violations: List[Dict[str, Any]] = []

    def validate_patch(self, relative_path: str, new_content: str) -> Tuple[bool, List[str]]:
        """
        Valida um patch antes de aplicação.

        Returns:
            (is_safe, list_of_violations)
        """
        self.violations = []

        # Verificar arquivo crítico
        if self._is_critical_file(relative_path):
            self.violations.append(f"Não é permitido modificar arquivo crítico: {relative_path}")
            return False, [v for v in self.violations]

        # Verificar padrões perigosos
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, new_content):
                self.violations.append(f"Padrão perigoso detectado: {pattern}")

        # Verificar tamanho
        if len(new_content) > 1000000:  # 1MB
            self.violations.append("Arquivo muito grande (> 1MB)")

        # Verificar path traversal
        if ".." in relative_path or relative_path.startswith("/"):
            self.violations.append("Caminho inválido detectado")

        return len(self.violations) == 0, self.violations

    def validate_proposal(self, target_files: List[str], file_patches: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Valida uma proposta de modificação completa.

        Returns:
            (is_safe, list_of_violations)
        """
        all_violations = []

        # Validar cada arquivo
        for path, content in file_patches.items():
            safe, violations = self.validate_patch(path, content)
            if not safe:
                all_violations.extend(violations)

        # Verificar se todos os target_files têm patches
        for target in target_files:
            if target not in file_patches:
                all_violations.append(f"Alvo {target} não tem patch correspondente")

        return len(all_violations) == 0, all_violations

    def _is_critical_file(self, relative_path: str) -> bool:
        """Verifica se um arquivo é crítico."""
        for critical in self.CRITICAL_FILES:
            if relative_path.endswith(critical) or relative_path == critical:
                return True
        return False

    def compare_patch_to_core(self, relative_path: str, new_content: str,
                             core_rules_dir: Path) -> Tuple[bool, List[str]]:
        """
        Verifica se o patch viola regras do core.

        Returns:
            (is_compliant, list_of_violations)
        """
        violations = []

        # Verificar se o patch tenta modificar core
        if "core" in Path(relative_path).parts:
            violations.append("Patches não podem modificar arquivos do core")
            return False, violations

        # Verificar se o patch tenta contornar permissões
        if "PermissionLevel" in new_content and "LEVEL_4" in new_content:
            violations.append("Patches não podem elevar níveis de permissão para máximo")
            return False, violations

        return len(violations) == 0, violations


def validate_patch_safety(relative_path: str, new_content: str) -> Tuple[bool, List[str]]:
    """Função de conveniência para validação rápida."""
    validator = PatchValidator()
    return validator.validate_patch(relative_path, new_content)
