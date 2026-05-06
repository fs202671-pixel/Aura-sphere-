import React, { useEffect, useState } from 'react';
import { BarChart3, CheckCircle2, Zap, Settings, Package, Layers, Smartphone, Shield, DollarSign, Palette } from 'lucide-react';
import { Dashboard } from './Dashboard';
import { PlanningTab } from './PlanningTab';
import { ActionQueue } from './ActionQueue';
import { MemoryVisualizer } from './MemoryVisualizer';
import { AbilitiesGallery } from './AbilitiesGallery';
import { SecurityDashboard } from './SecurityDashboard';
import { CostTracker } from './CostTracker';
import { ThemeBuilder } from './ThemeBuilder';
import { ThemeGallery } from './ThemeGallery';
import { getApiBase, getAuthHeaders } from '@/lib/api';

export function AIOnShellTabs() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, component: Dashboard },
    { id: 'planning', label: 'Planning', icon: CheckCircle2, component: PlanningTab },
    { id: 'actions', label: 'Ações', icon: Zap, component: ActionQueueTab },
    { id: 'abilities', label: 'Abilities', icon: Package, component: AbilitiesGallery },
    { id: 'memory', label: 'Memória', icon: Layers, component: MemoryVisualizer },
    { id: 'security', label: 'Segurança', icon: Shield, component: SecurityDashboard },
    { id: 'costs', label: 'Custos', icon: DollarSign, component: CostTracker },
    { id: 'themes', label: 'Temas', icon: Palette, component: ThemesTab },
    { id: 'device', label: 'Device', icon: Smartphone, component: DeviceTab }
  ];

  const activeTabConfig = tabs.find(t => t.id === activeTab);
  const ActiveComponent = activeTabConfig?.component;

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header */}
      <div className="bg-black/50 border-b border-slate-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg"></div>
          Aura-sphere Control Panel
        </h1>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 px-4 py-3 bg-slate-800/50 border-b border-slate-700 overflow-x-auto">
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/50'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              <Icon size={18} />
              <span className="text-sm font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto bg-gradient-to-b from-slate-800 to-slate-900">
        <div className="max-w-7xl mx-auto">
          {ActiveComponent ? <ActiveComponent /> : <div className="p-6">Componente não encontrado</div>}
        </div>
      </div>
    </div>
  );
}

function ActionQueueTab() {
  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold text-white">Fila de Ações</h2>
      <ActionQueue />
    </div>
  );
}

function ThemesTab() {
  const [activeTab, setActiveTab] = useState<'builder' | 'gallery'>('builder');

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex gap-2 px-6 py-4 bg-slate-800/50 border-b border-slate-700">
        <button
          onClick={() => setActiveTab('builder')}
          className={`px-4 py-2 rounded-lg font-semibold transition ${
            activeTab === 'builder'
              ? 'bg-purple-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Construtor de Temas
        </button>
        <button
          onClick={() => setActiveTab('gallery')}
          className={`px-4 py-2 rounded-lg font-semibold transition ${
            activeTab === 'gallery'
              ? 'bg-purple-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Galeria de Referências
        </button>
      </div>
      <div className="flex-1 overflow-auto">
        {activeTab === 'builder' ? <ThemeBuilder /> : <ThemeGallery />}
      </div>
    </div>
  );
}

function ToolsTab() {
  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold text-white">Ferramentas</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ToolCard title="AST Parser" description="Analisar estrutura de código" />
        <ToolCard title="Code Generator" description="Gerar código automaticamente" />
        <ToolCard title="Sandbox Executor" description="Executar código em sandbox" />
        <ToolCard title="Security Auditor" description="Auditar segurança" />
        <ToolCard title="Performance Analyzer" description="Analisar performance" />
        <ToolCard title="Documentation Generator" description="Gerar documentação" />
      </div>
    </div>
  );
}

function ToolCard({ title, description }) {
  return (
    <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-4 hover:border-blue-500 transition cursor-pointer">
      <h3 className="font-semibold text-white">{title}</h3>
      <p className="text-sm text-slate-300 mt-2">{description}</p>
    </div>
  );
}

function DeviceTab() {
  const [deviceProfile, setDeviceProfile] = useState<null | {
    device_type: string;
    os: string;
    os_version: string;
    architecture: string;
    storage_total_mb: number;
    storage_free_mb: number;
    ram_total_mb: number;
    ram_available_mb: number;
    cpu_cores: number;
    cpu_freq_mhz: number;
    capabilities: string[];
    health_score: number;
  }>(null);
  const [syncStatus, setSyncStatus] = useState<null | {
    status: string;
    last_sync: string;
    pending_changes: number;
  }>(null);
  const [optimization, setOptimization] = useState<null | {
    recommendations: string[];
    estimated_freed_mb: number;
  }>(null);
  const [loading, setLoading] = useState(true);
  const [optimizeLoading, setOptimizeLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = getApiBase();
  const AUTH_HEADERS = getAuthHeaders();

  useEffect(() => {
    const fetchDeviceProfile = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/device/profile`, {
          headers: AUTH_HEADERS,
        });
        if (!response.ok) {
          throw new Error(`Erro ao buscar perfil do dispositivo: ${response.statusText}`);
        }
        setDeviceProfile(await response.json());
      } catch (err) {
        setError((err as Error).message);
      }
    };

    const fetchSyncStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/device/sync/status`, {
          headers: AUTH_HEADERS,
        });
        if (!response.ok) {
          throw new Error(`Erro ao buscar status de sync: ${response.statusText}`);
        }
        setSyncStatus(await response.json());
      } catch (err) {
        setError((err as Error).message);
      }
    };

    Promise.all([fetchDeviceProfile(), fetchSyncStatus()]).finally(() => setLoading(false));
  }, [API_BASE, AUTH_HEADERS]);

  const optimizeDevice = async () => {
    setOptimizeLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1/device/optimize`, {
        method: "POST",
        headers: AUTH_HEADERS,
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error(`Erro ao otimizar dispositivo: ${response.statusText}`);
      }

      setOptimization(await response.json());
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setOptimizeLoading(false);
    }
  };

  const getStorageText = () => {
    if (!deviceProfile) return "-";
    return `${Math.round(deviceProfile.storage_free_mb / 1024)} GB / ${Math.round(deviceProfile.storage_total_mb / 1024)} GB`;
  };

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-white">Informações do Dispositivo</h2>
      {loading ? (
        <div className="rounded-3xl bg-slate-700/50 border border-slate-600 p-6 text-slate-200">Carregando dados do dispositivo…</div>
      ) : error ? (
        <div className="rounded-3xl bg-rose-700/20 border border-rose-500 p-6 text-rose-100">{error}</div>
      ) : (
        <>
          <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InfoItem label="Tipo de Dispositivo" value={deviceProfile?.device_type ?? "Desktop"} />
              <InfoItem label="Sistema Operacional" value={`${deviceProfile?.os ?? "Linux"} ${deviceProfile?.os_version ?? ""}`} />
              <InfoItem label="Arquitetura" value={deviceProfile?.architecture ?? "x86_64"} />
              <InfoItem label="Armazenamento" value={getStorageText()} />
              <InfoItem label="Memória RAM" value={`${Math.round((deviceProfile?.ram_available_mb ?? 0) / 1024)} GB / ${Math.round((deviceProfile?.ram_total_mb ?? 0) / 1024)} GB`} />
              <InfoItem label="Cores de CPU" value={deviceProfile?.cpu_cores?.toString() ?? "N/A"} />
              <InfoItem label="Frequência CPU" value={`${deviceProfile?.cpu_freq_mhz?.toFixed(0) ?? 0} MHz`} />
              <InfoItem label="Status de Saúde" value={`${deviceProfile?.health_score ?? 0}/100`} />
            </div>
          </div>

          {syncStatus && (
            <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Sincronização Offline</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <InfoItem label="Status" value={syncStatus.status} />
                <InfoItem label="Última sincronização" value={new Date(syncStatus.last_sync).toLocaleString()} />
                <InfoItem label="Alterações pendentes" value={syncStatus.pending_changes.toString()} />
              </div>
            </div>
          )}

          <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
            <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Otimização de Armazenamento</h3>
              <p className="text-slate-300 mb-4">
                Analise automaticamente o uso de arquivos temporários, caches e dados antigos para liberar espaço.
              </p>
              {optimization ? (
                <div className="space-y-3">
                  <p className="text-slate-200">Economia estimada: <strong>{Math.round(optimization.estimated_freed_mb / 1024)} GB</strong></p>
                  <ul className="list-disc list-inside text-slate-300 space-y-2">
                    {optimization.recommendations.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="text-slate-300">Clique em otimizar para receber recomendações de limpeza e liberar espaço.</p>
              )}
            </div>
            <div className="flex flex-col justify-between bg-slate-800/60 border border-slate-600 rounded-lg p-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Ações Rápidas</h3>
                <p className="text-slate-300 mb-6">Execute a análise de otimização e receba um plano prático sem sair da interface.</p>
              </div>
              <button
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
                onClick={optimizeDevice}
                disabled={optimizeLoading}
              >
                {optimizeLoading ? "Otimização em progresso…" : "Otimizar Dispositivo"}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function InfoItem({ label, value }) {
  return (
    <div className="border-b border-slate-600 pb-3">
      <label className="text-sm text-slate-400">{label}</label>
      <p className="text-lg font-semibold text-white">{value}</p>
    </div>
  );
}
