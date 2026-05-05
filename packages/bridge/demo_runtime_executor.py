#!/usr/bin/env python3
"""
Demo do Runtime Executor - Teste do sistema de execução controlada.
"""

import sys
from pathlib import Path
import time

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from runtime import execute_code, get_execution_status, cancel_execution

def demo_runtime_executor():
    """Demonstra o runtime executor."""
    print("🚀 Demo: Runtime Executor da Aura Sphere")
    print("=" * 50)

    # Código de teste
    test_code = """
print("Olá do sandbox!")
x = 42
y = x * 2
print(f"Resultado: {y}")
"""

    print("🔧 Executando código de forma síncrona...")
    result = execute_code(test_code, "demo_user", sync=True)
    print(f"Resultado: {result}")

    print("\n🔄 Executando código de forma assíncrona...")
    task_id = execute_code(test_code, "demo_user", sync=False)
    print(f"Task ID: {task_id}")

    # Aguardar um pouco
    time.sleep(2)

    # Verificar status
    status = get_execution_status(task_id)
    print(f"Status da tarefa: {status}")

    print("\n✅ Demo concluída!")

if __name__ == "__main__":
    demo_runtime_executor()