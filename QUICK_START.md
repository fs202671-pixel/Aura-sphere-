# 🚀 QUICK START - Começar a Implementação em 1 Hora

## 📌 Objetivo desta Sessão
Preparar a infraestrutura para Phase 1 e criar a primeira tarefa real: **Sistema de Planejamento com Barras de Progresso**

---

## ⏱️ Cronograma (60 minutos)

- **0-5 min**: Revisar este documento
- **5-20 min**: Setup do Database
- **20-35 min**: Criar modelos ORM
- **35-50 min**: Implementar API básica
- **50-60 min**: Criar componente Frontend simples

---

## 1️⃣ DATABASE SETUP (5-10 min)

### Passo 1: Atualizar `database.py`

Adicione as novas tabelas ao arquivo `packages/bridge/database.py`:

```python
# Adicione ao final, antes de init_db()

class Plan(Base):
    """Plano de estudo/projeto com milestones"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), default="active")  # active, completed, archived
    progress = Column(Float, default=0.0)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Task(Base):
    """Tarefa dentro de um plano"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), default="pending")  # pending, in_progress, completed
    progress = Column(Float, default=0.0)  # 0-100
    priority = Column(Integer, default=5)  # 1-10
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ActionProposal(Base):
    """Ações que requerem aprovação do usuário"""
    __tablename__ = "action_proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    action_type = Column(String(64), nullable=False)  # publish, schedule, execute, etc
    description = Column(Text, nullable=False)
    parameters = Column(Text, nullable=True)  # JSON string
    status = Column(String(32), default="pending")  # pending, approved, rejected, executed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
```

Depois, remova as linhas antigas de `Conversation` se quiser consolidar, ou deixe como está.

### Passo 2: Rodar migrations

```bash
cd /workspaces/Aura-sphere-/packages/bridge

# Se tiver alembic setup:
alembic upgrade head

# Se não tiver (manual):
python -c "from database import init_db; init_db()"
```

---

## 2️⃣ BACKEND LOGIC (10-15 min)

### Passo 1: Criar `planning_service.py`

Arquivo: `/workspaces/Aura-sphere-/packages/bridge/agent/planning_service.py`

```python
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
    
    def add_task(self, plan_id: int, title: str, priority: int = 5, 
                 due_date: Optional[str] = None) -> Dict[str, Any]:
        """Adicionar tarefa a um plano"""
        with SessionLocal() as session:
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
            
            return {
                "task_id": task.id,
                "status": task.status,
                "progress": task.progress
            }
    
    def get_plan_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Dashboard completo do usuário"""
        with SessionLocal() as session:
            plans = session.query(Plan).filter(Plan.user_id == user_id).all()
            
            total_plans = len(plans)
            active_plans = len([p for p in plans if p.status == "active"])
            total_tasks = sum(len(session.query(Task).filter(Task.plan_id == p.id).all()) 
                            for p in plans)
            
            # Calcular progresso geral
            total_progress = 0
            if total_tasks > 0:
                completed_tasks = sum(
                    len(session.query(Task).filter(
                        Task.plan_id == p.id,
                        Task.status == "completed"
                    ).all())
                    for p in plans
                )
                total_progress = (completed_tasks / total_tasks * 100)
            
            return {
                "user_id": user_id,
                "total_plans": total_plans,
                "active_plans": active_plans,
                "total_tasks": total_tasks,
                "overall_progress": round(total_progress, 1),
                "plans": self.get_user_plans(user_id)
            }


# Instância global
planning_service = PlanningService()
```

### Passo 2: Adicionar ao `app.py`

Adicione as rotas ao final de `packages/bridge/app.py` (antes de `if __name__`):

```python
# === PLANNING API ===

from agent.planning_service import planning_service

@app.post("/api/v1/planning/plans")
def create_plan(
    data: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Criar novo plano de estudo/projeto"""
    user_id = current_user.get("sub", "dev-user")
    result = planning_service.create_plan(
        user_id=user_id,
        title=data.get("title"),
        description=data.get("description", "")
    )
    return result


@app.get("/api/v1/planning/plans/{user_id}")
def get_plans(
    user_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Listar planos do usuário"""
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return {"plans": planning_service.get_user_plans(user_id)}


@app.post("/api/v1/planning/tasks")
def add_task(
    data: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Adicionar tarefa a um plano"""
    plan_id = data.get("plan_id")
    title = data.get("title")
    priority = data.get("priority", 5)
    
    result = planning_service.add_task(plan_id, title, priority)
    return result


@app.patch("/api/v1/planning/tasks/{task_id}")
def update_task(
    task_id: int,
    data: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Atualizar progresso de tarefa"""
    progress = data.get("progress", 0)
    result = planning_service.update_task_progress(task_id, progress)
    return result


@app.get("/api/v1/planning/dashboard/{user_id}")
def get_dashboard(
    user_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Dashboard completo de planejamento"""
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return planning_service.get_plan_dashboard(user_id)
```

---

## 3️⃣ TESTE RÁPIDO (5 min)

```bash
cd /workspaces/Aura-sphere-/packages/bridge

# Testar se compila
python -m py_compile agent/planning_service.py app.py

# Ou testar a API diretamente:
python -c "
from agent.planning_service import planning_service

# Criar plano
result = planning_service.create_plan('test-user', 'Aprender Python')
print('✅ Plano criado:', result)

# Adicionar tarefa
task = planning_service.add_task(result['plan_id'], 'Estudar loops')
print('✅ Tarefa criada:', task)

# Ver dashboard
dashboard = planning_service.get_plan_dashboard('test-user')
print('✅ Dashboard:', dashboard)
"
```

---

## 4️⃣ FRONTEND SIMPLE (10-15 min)

Crie novo componente: `src/components/PlanningTab.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import { ChevronDown, Plus } from 'lucide-react';

export function PlanningTab() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newPlanTitle, setNewPlanTitle] = useState('');

  // Buscar planos
  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/planning/plans/dev-user');
      const data = await response.json();
      setPlans(data.plans || []);
    } catch (error) {
      console.error('Erro ao buscar planos:', error);
    }
    setLoading(false);
  };

  const handleCreatePlan = async () => {
    if (!newPlanTitle.trim()) return;

    try {
      const response = await fetch('/api/v1/planning/plans', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newPlanTitle, description: '' })
      });
      
      if (response.ok) {
        setNewPlanTitle('');
        fetchPlans(); // Recarregar
      }
    } catch (error) {
      console.error('Erro ao criar plano:', error);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold">Planejamento</h2>

      {/* Novo Plano */}
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Nome do plano (ex: Aprender React)"
          value={newPlanTitle}
          onChange={(e) => setNewPlanTitle(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleCreatePlan()}
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <button
          onClick={handleCreatePlan}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus size={20} /> Novo Plano
        </button>
      </div>

      {/* Lista de Planos */}
      {loading ? (
        <div>Carregando...</div>
      ) : (
        <div className="space-y-4">
          {plans.map((plan) => (
            <div key={plan.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-semibold text-lg">{plan.title}</h3>
                  <p className="text-sm text-gray-600">
                    {plan.completed_tasks} / {plan.task_count} tarefas
                  </p>
                </div>
                <span className={`px-3 py-1 rounded text-sm ${
                  plan.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100'
                }`}>
                  {plan.status}
                </span>
              </div>

              {/* Barra de Progresso */}
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-500"
                  style={{ width: `${plan.progress}%` }}
                />
              </div>

              <div className="flex justify-between text-sm text-gray-600 mt-2">
                <span>{plan.progress.toFixed(0)}% completo</span>
                <span>{plan.created_at ? new Date(plan.created_at).toLocaleDateString() : '-'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Integrar no App:

Edite `src/App.tsx` para incluir a aba:

```tsx
// Adicione ao estado de abas
const [activeTab, setActiveTab] = useState('dashboard');

// Na renderização, adicione:
{activeTab === 'planning' && <PlanningTab />}

// E no menu de abas:
<button onClick={() => setActiveTab('planning')}>📋 Planejamento</button>
```

---

## ✅ Validação (5 min)

```bash
# 1. Verificar syntax
cd /workspaces/Aura-sphere-/packages/bridge
python -m py_compile agent/planning_service.py app.py

# 2. Start servidor
python app.py

# 3. Testar em otra terminal
curl -X POST http://localhost:8000/api/v1/planning/plans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"title":"Aprender Python"}'

# 4. Ver resposta
# Deve retornar: {"plan_id": 1, "title": "Aprender Python", ...}
```

---

## 🎯 Próximos Passos Imediatos

1. **Frontend melhorado** (20 min)
   - Adicionar formulário para criar tarefas
   - Clicar em tarefa → editar progresso
   - Visualizar tarefas em accordion

2. **Aprovações** (30 min)
   - Tabela `ActionProposal` já existe
   - Criar `ApprovalService`
   - Adicionar abas para ações pendentes

3. **Persistência** (15 min)
   - Exportar dados para CSV
   - Backup automático local

---

## 📊 Checklist de Completude

- [ ] Database tables criadas
- [ ] `planning_service.py` implementado
- [ ] Rotas `/api/v1/planning/` funcionando
- [ ] `PlanningTab.tsx` renderizando
- [ ] Barra de progresso atualizando visualmente
- [ ] Teste end-to-end funcionando

**Tempo Total: ~60 minutos**

---

## 🆘 Troubleshooting

### Erro: "Plan not found" ao adicionar tarefa
- Verificar se plan_id está correto
- Confirmar que plano foi criado antes

### Erro: "Module not found: planning_service"
- Adicionar `sys.path.append("..")` no `app.py`
- Ou mover `planning_service.py` para `packages/bridge/`

### Progresso não atualiza no frontend
- Verificar se chamada PATCH está funcionando
- Verificar se recarrega lista após update

---

**Sucesso! Primeira fase iniciada. Próximo passo: Sistema de Aprovação de Ações 🎉**

