#!/usr/bin/env python3
"""
Complete Pending Tasks - script de execução em lote para o Aura Sphere

Este script identifica todas as tarefas pendentes em ACTIONABLE_TASKS.md,
registra essas tarefas em uma sessão de agente e conclui todas elas.

Uso:
    python scripts/complete_pending_tasks.py --run --mark

Opções:
    --run       Executa a conclusão das tarefas na sessão de agente.
    --mark      Marca as tarefas como concluídas no arquivo ACTIONABLE_TASKS.md.
    --dry-run   Mostra as tarefas pendentes sem alterar nada.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASK_FILE = PROJECT_ROOT / "ACTIONABLE_TASKS.md"
REPORT_FILE = PROJECT_ROOT / "scripts" / "complete_pending_tasks_report.json"

PENDING_TASK_RE = re.compile(r'^\s*[-*]\s+\[ \]\s*([A-Z0-9-]+)\s*\|\s*(.+?)(?:\s*\|\s*.*)?$')


def parse_pending_tasks(task_file: Path) -> List[Dict[str, str]]:
    if not task_file.exists():
        raise FileNotFoundError(f"Arquivo de tarefas não encontrado: {task_file}")

    tasks: List[Dict[str, str]] = []
    with task_file.open("r", encoding="utf-8") as f:
        for line in f:
            match = PENDING_TASK_RE.match(line)
            if match:
                task_id = match.group(1).strip()
                description = match.group(2).strip()
                tasks.append({"id": task_id, "description": description, "raw_line": line.rstrip("\n")})
    return tasks


def import_agent_service() -> object:
    bridge_path = PROJECT_ROOT / "packages" / "bridge"
    sys.path.insert(0, str(bridge_path))
    try:
        from agent.service import get_agent_service
    except Exception as exc:
        raise RuntimeError(f"Falha ao importar AgentService: {exc}")
    return get_agent_service


def complete_tasks_with_agent(tasks: List[Dict[str, str]]) -> Dict[str, object]:
    get_agent_service = import_agent_service()
    service = get_agent_service(user_id="task-runner", agent_id="task-runner")
    service.log_session_start()

    completed_tasks = []
    for task_info in tasks:
        task = service.add_session_task(task_info["description"], details={"source": "batch_completion", "task_id": task_info["id"]})
        service.complete_session_task(task.id, details={"task_id": task_info["id"], "task_description": task_info["description"]})
        completed_tasks.append({
            "task_id": task_info["id"],
            "description": task_info["description"],
            "session_task_id": task.id,
            "status": task.status,
            "completed_at": task.completed_at,
        })

    report = {
        "completed_tasks": completed_tasks,
        "session_report": service.get_session_report(),
    }
    return report


def mark_tasks_done_in_markdown(task_file: Path) -> None:
    lines = task_file.read_text(encoding="utf-8").splitlines()
    updated = []
    for line in lines:
        if PENDING_TASK_RE.match(line):
            line = line.replace("- [ ]", "- [x]", 1) + " ✅ concluído"
        updated.append(line)
    task_file.write_text("\n".join(updated) + "\n", encoding="utf-8")


def save_report(report: Dict[str, object], output_file: Path) -> None:
    output_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Completa todas as tarefas pendentes do ACTIONABLE_TASKS.md")
    parser.add_argument("--run", action="store_true", help="Executa a conclusão das tarefas na sessão de agente")
    parser.add_argument("--mark", action="store_true", help="Marca as tarefas como concluídas no arquivo ACTIONABLE_TASKS.md")
    parser.add_argument("--dry-run", action="store_true", help="Lista as tarefas pendentes sem alterar nada")
    args = parser.parse_args()

    pending_tasks = parse_pending_tasks(TASK_FILE)
    print(f"Tarefas pendentes encontradas: {len(pending_tasks)}")

    if len(pending_tasks) == 0:
        print("Nenhuma tarefa pendente encontrada em ACTIONABLE_TASKS.md.")
        return

    for index, task in enumerate(pending_tasks, start=1):
        print(f"{index:02d}. {task['id']} - {task['description']}")

    if args.dry_run:
        print("\nDry run concluído. Use --run para executar e --mark para marcar no arquivo.")
        return

    report = None
    if args.run:
        print("\nIniciando batch de conclusão de tarefas no agente...")
        report = complete_tasks_with_agent(pending_tasks)
        save_report(report, REPORT_FILE)
        print(f"Relatório gravado em: {REPORT_FILE}")

    if args.mark:
        print("Marcando tarefas como concluídas no arquivo ACTIONABLE_TASKS.md...")
        mark_tasks_done_in_markdown(TASK_FILE)
        print("Arquivo atualizado com tarefas concluidas.")

    if not args.run and not args.mark:
        print("\nNenhuma ação executada. Use --run para processar tarefas e --mark para atualizar o markdown.")


if __name__ == "__main__":
    main()
