"""Serviço de planejamento com barras de progresso"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

import sys
sys.path.append("..")
from database import SessionLocal, Plan, Task


@dataclass
class PlanResponse:
    id: int
    user_id: str
    title: str
    description: str
    status: str
    progress: float
    task_count: int
    completed_tasks: int
    created_at: str


class PlanningService:
    """Gerencia planos e tarefas com progresso"""
    
    def create_plan(self, user_id: str, title: str, description: str = "") -> Dict[str, Any]:
        """Criar novo plano"""
        with SessionLocal() as session:
            plan = Plan(
                user_id=user_id,
                title=title,
                description=description,
                progress=0.0
            )
            session.add(plan)
            session.commit()
            session.refresh(plan)
            
            return {
                "plan_id": plan.id,
                "title": plan.title,
                "status": "created",
                "progress": 0.0
            }
    
    def get_user_plans(self, user_id: str) -> List[Dict[str, Any]]:
        """Obter todos os planos do usuário"""
        with SessionLocal() as session:
            plans = session.query(Plan).filter(Plan.user_id == user_id).all()
            
            result = []
            for plan in plans:
                # Recalcular progresso baseado em tarefas
                tasks = session.query(Task).filter(Task.plan_id == plan.id).all()
                completed = len([t for t in tasks if t.status == "completed"])
                total = len(tasks)
                
                progress = (completed / total * 100) if total > 0 else 0.0
                
                result.append({
                    "id": plan.id,
                    "title": plan.title,
                    "description": plan.description,
                    "status": plan.status,
                    "progress": progress,
                    "task_count": total,
                    "completed_tasks": completed,
                    "created_at": plan.created_at.isoformat() if plan.created_at else None
                })
            
            return result
    
    def _recalculate_plan_progress(self, session, plan_id: int) -> Optional[Plan]:
        """Recalcula progresso e status do plano com base nas tarefas."""
        plan = session.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            return None

        tasks = session.query(Task).filter(Task.plan_id == plan_id).all()
        completed = len([t for t in tasks if t.status == "completed"])
        total = len(tasks)

        plan.progress = (completed / total * 100) if total > 0 else 0.0
        if total > 0 and completed == total:
            plan.status = "completed"
        elif plan.status == "completed":
            plan.status = "active"

        session.commit()
        session.refresh(plan)
        return plan

    def add_task(self, plan_id: int, title: str, priority: int = 5, 
                 due_date: Optional[str] = None) -> Dict[str, Any]:
        """Adicionar tarefa a um plano"""
        with SessionLocal() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return {"error": "Plan not found"}

            due = datetime.fromisoformat(due_date) if due_date else None
            
            task = Task(
                plan_id=plan_id,
                title=title,
                priority=priority,
                due_date=due,
                status="pending",
                progress=0.0
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            self._recalculate_plan_progress(session, plan_id)
            
            return {
                "task_id": task.id,
                "title": task.title,
                "status": "pending",
                "progress": 0.0
            }
    
    def update_task_progress(self, task_id: int, progress: float) -> Dict[str, Any]:
        """Atualizar progresso de uma tarefa (0-100)"""
        with SessionLocal() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"error": "Task not found"}
            
            task.progress = min(max(progress, 0), 100)
            
            # Se progresso = 100, marcar como completed
            if task.progress == 100:
                task.status = "completed"
            elif task.status == "pending":
                task.status = "in_progress"
            
            session.commit()
            session.refresh(task)
            self._recalculate_plan_progress(session, task.plan_id)
            
            return {
                "task_id": task.id,
                "status": task.status,
                "progress": task.progress
            }
    
    def get_plan_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Dashboard completo do usuário"""
        plans = self.get_user_plans(user_id)
        
        total_plans = len(plans)
        active_plans = len([p for p in plans if p["status"] == "active"])
        total_tasks = sum(p["task_count"] for p in plans)
        
        total_progress = 0
        if total_tasks > 0:
            completed_tasks = sum(p["completed_tasks"] for p in plans)
            total_progress = (completed_tasks / total_tasks * 100)
        
        return {
            "user_id": user_id,
            "total_plans": total_plans,
            "active_plans": active_plans,
            "total_tasks": total_tasks,
            "overall_progress": round(total_progress, 1),
            "plans": plans
        }


# Instância global
planning_service = PlanningService()