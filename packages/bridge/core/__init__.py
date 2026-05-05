"""
Core Module - Núcleo Imutável do Sistema IA

Este módulo contém as regras fundamentais e imutáveis do sistema.
NENHUMA IA pode modificar este código em runtime.
"""

from typing import Dict, List, Any, Optional
import hashlib
import os
from datetime import datetime

# ========== REGRAS FUNDAMENTAIS (IMUTÁVEIS) ==========

class ImmutableRules:
    """Regras fundamentais que nunca podem ser alteradas pela IA"""

    # Prioridade absoluta do usuário sobre qualquer IA
    USER_PRIORITY_LEVEL = 100

    # Proibições absolutas
    FORBIDDEN_ACTIONS = [
        "self_modify_core",      # Modificar o próprio núcleo
        "delete_core_files",     # Deletar arquivos do core
        "override_user_commands", # Ignorar comandos do usuário
        "execute_system_dangerous", # Executar comandos perigosos no sistema
        "access_sensitive_files", # Acessar arquivos sensíveis sem permissão
        "bypass_sandbox",        # Contornar o sandbox
        "auto_evolution_production", # Auto-evoluir em produção sem confirmação
    ]

    # Limites de segurança
    MAX_EXECUTION_TIME = 30  # segundos
    MAX_MEMORY_USAGE = 100 * 1024 * 1024  # 100MB
    MAX_FILE_SIZE_READ = 10 * 1024 * 1024  # 10MB

    # Permissões padrão (sempre começar com nível mais baixo)
    DEFAULT_PERMISSION_LEVEL = 0

class PermissionLevels:
    """Níveis de permissão do sistema"""

    LEVEL_0_READ_ONLY = 0        # Apenas leitura e análise
    LEVEL_1_SUGGEST = 1          # Pode sugerir ações
    LEVEL_2_EXECUTE_CONFIRMED = 2  # Executa com confirmação do usuário
    LEVEL_3_SANDBOX_EVOLUTION = 3  # Auto-evolução em sandbox

    @staticmethod
    def get_level_description(level: int) -> str:
        descriptions = {
            0: "Leitura e análise apenas",
            1: "Sugestão de ações",
            2: "Execução sob confirmação do usuário",
            3: "Auto-evolução em sandbox"
        }
        return descriptions.get(level, "Nível desconhecido")

class CoreValidator:
    """Validador de integridade do núcleo"""

    CORE_FILES = [
        "__init__.py",
        "immutable.py",
        "permissions.py",
        "sandbox.py",
        "security.py",
        "user_obedience.py",
        "validator.py"
    ]

    @staticmethod
    def _core_file_path(filename: str) -> str:
        """Retorna o caminho absoluto de um arquivo do core."""
        base_dir = os.path.dirname(__file__)
        return os.path.join(base_dir, filename)

    @staticmethod
    def calculate_core_hash() -> str:
        """Calcula hash SHA256 de todos os arquivos do core"""
        hasher = hashlib.sha256()
        for file_path in CoreValidator.CORE_FILES:
            abs_path = CoreValidator._core_file_path(file_path)
            if os.path.exists(abs_path):
                with open(abs_path, 'rb') as f:
                    hasher.update(f.read())
        return hasher.hexdigest()

    @staticmethod
    def validate_core_integrity() -> bool:
        """Valida se o core não foi modificado"""
        # Em produção, comparar com hash conhecido
        # Por enquanto, apenas verifica se os arquivos existem
        return all(os.path.exists(CoreValidator._core_file_path(f)) for f in CoreValidator.CORE_FILES)

class SecurityEnforcer:
    """Aplicador de regras de segurança"""

    @staticmethod
    def check_action_allowed(action: str, permission_level: int) -> bool:
        """Verifica se uma ação é permitida no nível de permissão atual"""

        # Ações sempre proibidas
        if action in ImmutableRules.FORBIDDEN_ACTIONS:
            return False

        # Verificações por nível
        if permission_level >= PermissionLevels.LEVEL_3_SANDBOX_EVOLUTION:
            # Nível 3: pode fazer quase tudo, mas ainda com restrições
            return action not in ["override_user_commands", "auto_evolution_production"]

        elif permission_level >= PermissionLevels.LEVEL_2_EXECUTE_CONFIRMED:
            # Nível 2: execução com confirmação
            dangerous_actions = ["execute_system_dangerous", "delete_core_files"]
            return action not in dangerous_actions

        elif permission_level >= PermissionLevels.LEVEL_1_SUGGEST:
            # Nível 1: apenas sugestões
            execution_actions = ["execute_system", "modify_files", "auto_evolution"]
            return action not in execution_actions

        else:
            # Nível 0: apenas leitura
            return action in ["read_files", "analyze_code", "suggest_improvements"]

    @staticmethod
    def log_security_event(event: str, details: Dict[str, Any]) -> None:
        """Registra eventos de segurança"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "event": event,
            "details": details
        }
        # Em produção, escrever em arquivo de log seguro
        print(f"[SECURITY] {timestamp}: {event} - {details}")

# ========== INICIALIZAÇÃO DO CORE ==========

def initialize_core() -> bool:
    """Inicializa o núcleo e valida integridade"""
    print("🔐 Inicializando núcleo imutável...")

    if not CoreValidator.validate_core_integrity():
        print("❌ ERRO: Integridade do core comprometida!")
        return False

    SecurityEnforcer.log_security_event("core_initialized", {
        "core_hash": CoreValidator.calculate_core_hash(),
        "rules_loaded": len(ImmutableRules.FORBIDDEN_ACTIONS)
    })

    print("✅ Core inicializado com sucesso")
    return True

# Verificação automática na importação
if not initialize_core():
    raise RuntimeError("Falha na inicialização do core - sistema comprometido!")