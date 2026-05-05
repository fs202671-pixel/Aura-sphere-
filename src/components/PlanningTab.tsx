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