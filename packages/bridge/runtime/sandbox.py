"""
Sandbox System - Sistema de Execução Segura

Fornece ambiente isolado para execução de código gerado pela IA.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import resource
import signal
import psutil

from core.permissions import PermissionLevel, permission_manager
from core.validator import core_validator

class SandboxError(Exception):
    """Erro específico do sandbox"""
    pass

class SandboxTimeout(SandboxError):
    """Timeout na execução do sandbox"""
    pass

class SandboxSecurityViolation(SandboxError):
    """Violação de segurança no sandbox"""
    pass

class SandboxConfig:
    """Configuração do sandbox"""

    def __init__(self):
        # Limites de recursos
        self.max_execution_time = 30  # segundos
        self.max_memory_mb = 100      # MB
        self.max_cpu_percent = 50     # %
        self.max_file_size_mb = 10    # MB
        self.max_files_count = 100    # arquivos

        # Restrições de sistema
        self.allowed_modules = {
            'os', 'sys', 'math', 'random', 'datetime', 'json',
            'collections', 'itertools', 'functools', 'operator',
            're', 'string', 'pathlib'
        }

        self.forbidden_modules = {
            'subprocess', 'multiprocessing', 'threading', 'socket',
            'http', 'urllib', 'requests', 'socketserver',
            'shutil', 'os.system', 'os.popen', 'os.exec',
            'importlib', 'inspect', 'pickle'
        }

        # Diretórios permitidos (relativos ao sandbox)
        self.allowed_paths = ['.', './temp', './output']

class SandboxEnvironment:
    """Ambiente de execução em sandbox"""

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.temp_dir = None
        self.process = None
        self.start_time = None

    def __enter__(self):
        """Inicializa o ambiente sandbox"""
        self.temp_dir = tempfile.mkdtemp(prefix='aura_sandbox_')
        self.start_time = datetime.now()

        # Criar estrutura de diretórios
        for path in self.config.allowed_paths:
            full_path = os.path.join(self.temp_dir, path)
            os.makedirs(full_path, exist_ok=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Limpa o ambiente sandbox"""
        if self.process and self.process.poll() is None:
            self._kill_process()

        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def execute_code(self, code: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa código Python em ambiente seguro

        Args:
            code: Código Python a executar
            inputs: Dados de entrada para o código

        Returns:
            Dict com resultado da execução
        """

        result = {
            "success": False,
            "output": None,
            "error": None,
            "execution_time": None,
            "memory_used": None,
            "security_violations": []
        }

        try:
            # Validar código antes da execução
            validation = self._validate_code(code)
            if not validation["safe"]:
                result["security_violations"] = validation["violations"]
                result["error"] = "Código não passou na validação de segurança"
                return result

            # Executar código
            exec_result = self._execute_secure(code, inputs or {})

            result.update(exec_result)
            result["success"] = True

        except SandboxTimeout:
            result["error"] = "Timeout na execução"
        except SandboxSecurityViolation as e:
            result["error"] = f"Violação de segurança: {str(e)}"
        except Exception as e:
            result["error"] = f"Erro na execução: {str(e)}"

        finally:
            execution_time = (datetime.now() - self.start_time).total_seconds()
            result["execution_time"] = execution_time

        return result

    def _validate_code(self, code: str) -> Dict[str, Any]:
        """Valida código para segurança"""

        violations = []

        # Verificar imports proibidos
        for forbidden in self.config.forbidden_modules:
            if f"import {forbidden}" in code or f"from {forbidden}" in code:
                violations.append(f"Import proibido: {forbidden}")

        # Verificar funções perigosas
        dangerous_patterns = [
            "eval(", "exec(", "compile(", "__import__(",
            "open(", "file(", "input(",
            "os.system", "os.popen", "os.exec",
            "subprocess.", "multiprocessing."
        ]

        for pattern in dangerous_patterns:
            if pattern in code:
                violations.append(f"Padrão perigoso detectado: {pattern}")

        # Verificar tamanho do código
        if len(code) > 10000:  # 10KB limite
            violations.append("Código muito grande")

        return {
            "safe": len(violations) == 0,
            "violations": violations
        }

    def _execute_secure(self, code: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Executa código com limitações de segurança"""

        # Preparar código seguro
        safe_code = self._prepare_safe_code(code, inputs)

        # Criar processo isolado
        try:
            result = subprocess.run(
                [sys.executable, '-c', safe_code],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=self.config.max_execution_time,
                preexec_fn=self._set_process_limits
            )

            return {
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            raise SandboxTimeout("Execução excedeu tempo limite")

    def _prepare_safe_code(self, code: str, inputs: Dict[str, Any]) -> str:
        """Prepara código para execução segura"""

        # Adicionar imports seguros
        safe_imports = """
import sys
import os
sys.path.insert(0, '/safe/path')  # Restringir path
"""

        # Preparar variáveis de entrada
        input_setup = f"""
# Variáveis de entrada
inputs = {repr(inputs)}
"""

        # Restringir builtins perigosos
        restrictions = """
# Remover funções perigosas
dangerous_builtins = ['eval', 'exec', 'compile', 'open', '__import__', 'input']
safe_builtins = {}
for name in dir(__builtins__):
    if name not in dangerous_builtins:
        safe_builtins[name] = getattr(__builtins__, name)
__builtins__ = safe_builtins
"""

        # Combinar tudo
        safe_code = f"""
{safe_imports}
{input_setup}
{restrictions}

# Código do usuário
{code}

# Capturar output
import io
from contextlib import redirect_stdout, redirect_stderr

output_buffer = io.StringIO()
error_buffer = io.StringIO()

with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
    try:
        exec(compile({repr(code)}, '<sandbox>', 'exec'))
    except Exception as e:
        print(f"Erro: {{e}}", file=sys.stderr)

print("=== OUTPUT ===")
print(output_buffer.getvalue())
print("=== ERRORS ===")
print(error_buffer.getvalue())
"""

        return safe_code

    def _set_process_limits(self):
        """Define limites de recursos para o processo"""

        # Limite de memória
        memory_limit = self.config.max_memory_mb * 1024 * 1024  # bytes
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

        # Limite de CPU (tempo)
        cpu_limit = self.config.max_execution_time
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))

        # Limite de arquivos abertos
        resource.setrlimit(resource.RLIMIT_NOFILE, (100, 100))

    def _kill_process(self):
        """Mata processo em execução"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except:
                pass

class SandboxManager:
    """Gerenciador de sandboxes"""

    def __init__(self):
        self.active_sandboxes: Dict[str, SandboxEnvironment] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def create_sandbox(self, sandbox_id: str) -> SandboxEnvironment:
        """Cria um novo sandbox"""
        sandbox = SandboxEnvironment()
        self.active_sandboxes[sandbox_id] = sandbox
        return sandbox

    def execute_in_sandbox(self, sandbox_id: str, code: str,
                          inputs: Optional[Dict[str, Any]] = None,
                          user_id: str = "system") -> Dict[str, Any]:
        """
        Executa código em sandbox específico

        Args:
            sandbox_id: ID do sandbox
            code: Código a executar
            inputs: Dados de entrada
            user_id: ID do usuário executando

        Returns:
            Resultado da execução
        """

        # Verificar permissões
        # Criar sessão se não existir (para usuários do sistema)
        if user_id not in permission_manager.sessions:
            permission_manager.create_session(user_id)
            # Conceder nível básico para usuários do sistema
            permission_manager.grant_permission(
                user_id, PermissionLevel.LEVEL_2_EXECUTE_CONFIRMED,
                "system", "Auto-grant for sandbox execution", scope=["sandbox"]
            )

        permission_check = core_validator.validate_operation(
            user_id, "execute_code_sandbox", {
                "sandbox_id": sandbox_id,
                "in_sandbox": True,
                "logged": True
            }
        )

        if not permission_check["approved"]:
            return {
                "success": False,
                "error": "Permissões insuficientes para executar código em sandbox"
            }

        # Obter ou criar sandbox
        if sandbox_id not in self.active_sandboxes:
            self.create_sandbox(sandbox_id)

        sandbox = self.active_sandboxes[sandbox_id]

        # Executar código
        with sandbox:
            result = sandbox.execute_code(code, inputs)

        # Registrar execução
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "sandbox_id": sandbox_id,
            "user_id": user_id,
            "code_length": len(code),
            "success": result["success"],
            "execution_time": result.get("execution_time"),
            "has_security_violations": len(result.get("security_violations", [])) > 0
        }

        self.execution_history.append(execution_record)

        # Manter apenas últimas 100 execuções
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]

        return result

    def get_execution_history(self, sandbox_id: Optional[str] = None,
                            limit: int = 20) -> List[Dict[str, Any]]:
        """Retorna histórico de execuções"""
        history = self.execution_history

        if sandbox_id:
            history = [h for h in history if h["sandbox_id"] == sandbox_id]

        return history[-limit:]

    def cleanup_sandbox(self, sandbox_id: str) -> bool:
        """Limpa um sandbox específico"""
        if sandbox_id in self.active_sandboxes:
            del self.active_sandboxes[sandbox_id]
            return True
        return False

# ========== INSTÂNCIA GLOBAL ==========

sandbox_manager = SandboxManager()

# ========== FUNÇÕES DE CONVENIÊNCIA ==========

def execute_code_safely(code: str, inputs: Optional[Dict[str, Any]] = None,
                       user_id: str = "system", sandbox_id: str = "default") -> Dict[str, Any]:
    """Executa código Python de forma segura em sandbox"""
    return sandbox_manager.execute_in_sandbox(sandbox_id, code, inputs, user_id)

def validate_and_execute(code: str, user_id: str) -> Dict[str, Any]:
    """Valida e executa código com todas as verificações de segurança"""
    # Primeiro validar com o core
    validation = core_validator.validate_operation(
        user_id, "execute_code", {"code": code}
    )

    if not validation["approved"]:
        return {
            "success": False,
            "error": "Operação não aprovada pelo sistema de segurança"
        }

    # Se aprovado, executar em sandbox
    return execute_code_safely(code, user_id=user_id)