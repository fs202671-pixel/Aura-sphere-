import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Shield, TrendingUp } from 'lucide-react';
import { getApiBase, getAuthHeaders } from '@/lib/api';

interface SecurityIssue {
  id: string;
  severity: string;
  description: string;
  component: string;
  resolution: string;
  reported_at: string;
  status: string;
  details: Record<string, unknown>;
}

interface SecuritySummary {
  total_issues: number;
  by_severity: Record<string, number>;
  critical_count: number;
  requires_attention: boolean;
  timestamp: string;
}

export function SecurityDashboard() {
  const [issues, setIssues] = useState<SecurityIssue[]>([]);
  const [summary, setSummary] = useState<SecuritySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [auditCode, setAuditCode] = useState('');
  const [auditing, setAuditing] = useState(false);

  const API_BASE = getApiBase();
  const AUTH_HEADERS = getAuthHeaders();

  useEffect(() => {
    const fetchIssues = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/security/issues`, { headers: AUTH_HEADERS });
        if (!response.ok) throw new Error('Failed to fetch issues');
        const data = await response.json();
        setIssues(data.issues || []);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    const fetchSummary = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/security/summary`, { headers: AUTH_HEADERS });
        if (!response.ok) throw new Error('Failed to fetch summary');
        setSummary(await response.json());
      } catch (err) {
        setError((err as Error).message);
      }
    };

    Promise.all([fetchIssues(), fetchSummary()]).finally(() => setLoading(false));
  }, [API_BASE, AUTH_HEADERS]);

  const runAudit = async () => {
    if (!auditCode.trim()) return;
    
    setAuditing(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1/security/audit`, {
        method: 'POST',
        headers: AUTH_HEADERS,
        body: JSON.stringify({
          code: auditCode,
          language: 'python',
          component: 'user_audit'
        })
      });

      if (!response.ok) throw new Error('Audit failed');
      const data = await response.json();
      
      setIssues(data.issues || []);
      setSummary(data.summary || null);
      setAuditCode('');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAuditing(false);
    }
  };

  const updateIssueStatus = async (issueId: string, newStatus: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/security/issues/${issueId}/status`, {
        method: 'PATCH',
        headers: AUTH_HEADERS,
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) throw new Error('Failed to update status');
      
      setIssues(issues.map(i => i.id === issueId ? { ...i, status: newStatus } : i));
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-50';
      case 'high': return 'text-orange-500 bg-orange-50';
      case 'medium': return 'text-yellow-500 bg-yellow-50';
      case 'low': return 'text-blue-500 bg-blue-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-white flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-500" />
          Security Dashboard
        </h2>
      </div>

      {/* Resumo de Segurança */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-slate-700 to-slate-800 border border-slate-600 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Issues</p>
                <p className="text-3xl font-bold text-white">{summary.total_issues}</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-slate-500 opacity-50" />
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-red-900/20 to-red-900/10 border border-red-600/30 rounded-lg p-6">
            <p className="text-red-400 text-sm">Critical</p>
            <p className="text-3xl font-bold text-red-400">{summary.by_severity.critical || 0}</p>
          </div>
          
          <div className="bg-gradient-to-br from-orange-900/20 to-orange-900/10 border border-orange-600/30 rounded-lg p-6">
            <p className="text-orange-400 text-sm">High</p>
            <p className="text-3xl font-bold text-orange-400">{summary.by_severity.high || 0}</p>
          </div>
          
          <div className={`bg-gradient-to-br rounded-lg p-6 border ${
            summary.requires_attention 
              ? 'from-red-900/20 to-red-900/10 border-red-600/30' 
              : 'from-green-900/20 to-green-900/10 border-green-600/30'
          }`}>
            <p className={summary.requires_attention ? 'text-red-400 text-sm' : 'text-green-400 text-sm'}>
              Status
            </p>
            <div className="flex items-center gap-2 mt-2">
              {summary.requires_attention ? (
                <>
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                  <span className="text-red-400 font-bold">Atenção Necessária</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                  <span className="text-green-400 font-bold">Seguro</span>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Ferramenta de Auditoria */}
      <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Executar Auditoria de Código</h3>
        <div className="space-y-4">
          <textarea
            value={auditCode}
            onChange={(e) => setAuditCode(e.target.value)}
            placeholder="Cole seu código Python aqui para auditoria..."
            className="w-full h-48 bg-slate-800 border border-slate-600 rounded-lg p-4 text-white placeholder:text-slate-500 font-mono text-sm"
          />
          <button
            onClick={runAudit}
            disabled={auditing || !auditCode.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white px-6 py-2 rounded-lg font-semibold transition"
          >
            {auditing ? 'Auditando...' : 'Executar Auditoria'}
          </button>
        </div>
      </div>

      {/* Lista de Issues */}
      {issues.length > 0 && (
        <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Problemas Detectados ({issues.length})</h3>
          <div className="space-y-4">
            {issues.map((issue) => (
              <div key={issue.id} className={`border-l-4 p-4 rounded ${getSeverityColor(issue.severity)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`font-semibold uppercase text-xs px-2 py-1 rounded ${getSeverityColor(issue.severity)}`}>
                        {issue.severity}
                      </span>
                      <span className="text-slate-400 text-xs">
                        {issue.component}
                      </span>
                    </div>
                    <h4 className="font-semibold text-white mb-2">{issue.description}</h4>
                    <p className="text-slate-300 text-sm mb-3">{issue.resolution}</p>
                    {issue.details?.line && (
                      <p className="text-xs text-slate-400">Line {issue.details.line}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <select
                      value={issue.status}
                      onChange={(e) => updateIssueStatus(issue.id, e.target.value)}
                      className="bg-slate-800 border border-slate-600 text-white text-xs rounded px-2 py-1"
                    >
                      <option value="open">Open</option>
                      <option value="resolved">Resolved</option>
                      <option value="ignored">Ignored</option>
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div className="text-center text-slate-300">Carregando dados de segurança...</div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-600/50 rounded-lg p-4 text-red-200">
          Erro: {error}
        </div>
      )}

      {!loading && issues.length === 0 && !error && (
        <div className="bg-green-900/30 border border-green-600/50 rounded-lg p-4 text-green-200">
          ✓ Nenhum problema de segurança detectado
        </div>
      )}
    </div>
  );
}
