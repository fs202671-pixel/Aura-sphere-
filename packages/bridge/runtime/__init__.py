"""
Runtime Module - Camada de Execução e Controle

Esta camada gerencia a execução de código, controle de processos e isolamento.
"""

from .sandbox import SandboxManager, SandboxEnvironment, execute_code_safely

__all__ = [
    'SandboxManager',
    'SandboxEnvironment',
    'execute_code_safely'
]