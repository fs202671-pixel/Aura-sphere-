import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield, AlertTriangle, CheckCircle, XCircle, Activity,
  Eye, Lock, Unlock, RefreshCw, Bug, Clock,
  Info, AlertOctagon, Users
} from "lucide-react";
import { cn } from "@/lib/utils";

const BASE = import.meta.env.BASE_URL?.replace(/\/$/, "") || "";

interface LobosStatus {
  blockedIps: { ip: string; blockUntil: number; offenses: number; retryInSec: number }[];
  trackedIps: number;
  trackedUsers: number;
}

interface SecurityIssue {
  id: number;
  type: "suspicious" | "blocked" | "warning" | "info";
  title: string;
  description: string;
  severity: "low" | "medium" | "high";
  ip?: string | null;
  pattern?: string | null;
  createdAt: string;
  resolved: boolean;
}

interface AuditEntry {
  id: number;
  action: string;
  ip: string;
  route?: string | null;
  method?: string | null;
  createdAt: string;
  severity: "low" | "medium" | "high";
  pattern?: string | null;
}

interface FormigasPattern {
  id: string;
  name: string;
  description: string;
  severity: "low" | "medium" | "high";
  count: number;
  status: "ativo" | "normal";
}

interface FormigasStatus {
  active: boolean;
  patternsMonitored: number;
  alertsLast24h: number;
  autoBlocks: number;
  patterns: FormigasPattern[];
}

interface AbelhasStatus {
  score: number;
  reactionsToday: number;
  quarantinedCount: number;
  activeQuarantine: { ip: string; reason: string; retryInSec: number }[];
}

const SEVERITY_COLOR = {
  low: "text-green-400 bg-green-400/10 border-green-400/20",
  medium: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
  high: "text-red-400 bg-red-400/10 border-red-400/20",
};

const ISSUE_TYPE_ICON = {
  suspicious: AlertTriangle,
  blocked: XCircle,
  warning: AlertOctagon,
  info: Info,
};

const ISSUE_TYPE_COLOR = {
  suspicious: "text-yellow-400 border-yellow-400/20 bg-yellow-400/5",
  blocked: "text-red-400 border-red-400/20 bg-red-400/5",
  warning: "text-orange-400 border-orange-400/20 bg-orange-400/5",
  info: "text-blue-400 border-blue-400/20 bg-blue-400/5",
};

export default function Security() {
  const [lobosStatus, setLobosStatus] = useState<LobosStatus | null>(null);
  const [issues, setIssues] = useState<SecurityIssue[]>([]);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [formigasStatus, setFormigasStatus] = useState<FormigasStatus | null>(null);
  const [abelhasStatus, setAbelhasStatus] = useState<AbelhasStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "formigas" | "audit" | "lobos">("overview");
  const [refreshing, setRefreshing] = useState(false);

  const score = abelhasStatus?.score ?? 100;

  const fetchAll = useCallback(async () => {
    await Promise.allSettled([
      fetch(`${BASE}/api/security/lobos/status`)
        .then(r => r.ok ? r.json() : null)
        .then(d => d && setLobosStatus(d))
        .catch(() => {}),

      fetch(`${BASE}/v1/security/issues`)
        .then(r => r.ok ? r.json() : null)
        .then(d => d?.issues && setIssues(d.issues))
        .catch(() => {}),

      fetch(`${BASE}/api/security/audit-log?limit=50`)
        .then(r => r.ok ? r.json() : null)
        .then(d => d?.logs && setAuditLog(d.logs))
        .catch(() => {}),

      fetch(`${BASE}/api/security/formigas/status`)
        .then(r => r.ok ? r.json() : null)
        .then(d => d && setFormigasStatus(d))
        .catch(() => {}),

      fetch(`${BASE}/api/security/abelhas/status`)
        .then(r => r.ok ? r.json() : null)
        .then(d => d && setAbelhasStatus(d))
        .catch(() => {}),
    ]);
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 30_000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const refresh = async () => {
    setRefreshing(true);
    await fetchAll();
    setTimeout(() => setRefreshing(false), 800);
  };

  const resolveIssue = async (id: number) => {
    setIssues(prev => prev.map(i => i.id === id ? { ...i, resolved: true } : i));
    try {
      await fetch(`${BASE}/v1/security/issues/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resolved: true }),
      });
    } catch {}
  };

  const openIssues = issues.filter(i => !i.resolved);
  const resolvedIssues = issues.filter(i => i.resolved);

  const tabs = [
    { id: "overview" as const, label: "Visão Geral", icon: Shield },
    { id: "formigas" as const, label: "Formigas", icon: Bug },
    { id: "audit" as const, label: "Audit Log", icon: Activity },
    { id: "lobos" as const, label: "Lobos", icon: Lock },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
        <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-primary/60 mb-1">// Módulo de Segurança</p>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black uppercase tracking-widest">Segurança</h1>
            <p className="text-sm text-muted-foreground mt-1">Monitoramento em tempo real — Lobos · Formigas · Abelhas</p>
          </div>
          <button
            onClick={refresh}
            className={cn(
              "p-2.5 rounded-lg border border-border/40 text-muted-foreground hover:text-foreground transition-all",
              refreshing && "animate-spin"
            )}
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </motion.div>

      {/* Score card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        className="relative rounded-xl border border-primary/20 bg-card/60 p-6 overflow-hidden"
      >
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
          <div className="relative">
            <svg className="w-24 h-24 -rotate-90">
              <circle cx="48" cy="48" r="38" className="fill-none stroke-border/30" strokeWidth="6" />
              <motion.circle
                cx="48" cy="48" r="38"
                className="fill-none stroke-primary"
                strokeWidth="6"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 38}`}
                initial={{ strokeDashoffset: 2 * Math.PI * 38 }}
                animate={{ strokeDashoffset: 2 * Math.PI * 38 * (1 - score / 100) }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                style={{ filter: "drop-shadow(0 0 6px hsl(var(--primary)))" }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <span className="text-2xl font-black text-primary">{score}</span>
                <span className="text-xs text-muted-foreground block">/100</span>
              </div>
            </div>
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-foreground">Score de Segurança</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              {score >= 90 ? "Sistema em excelentes condições" : score >= 70 ? "Sistema em boas condições" : "Atenção requerida"} — monitoramento ativo
            </p>
            <div className="flex flex-wrap gap-2 mt-3">
              {[
                { label: `${openIssues.length} abertos`, color: openIssues.length > 0 ? "text-yellow-400 bg-yellow-400/10 border-yellow-400/20" : "text-green-400 bg-green-400/10 border-green-400/20" },
                { label: `${lobosStatus?.trackedIps ?? 0} IPs rastreados`, color: "text-blue-400 bg-blue-400/10 border-blue-400/20" },
                { label: `${lobosStatus?.blockedIps?.length ?? 0} bloqueados`, color: "text-red-400 bg-red-400/10 border-red-400/20" },
                { label: `${abelhasStatus?.reactionsToday ?? 0} reações hoje`, color: "text-purple-400 bg-purple-400/10 border-purple-400/20" },
              ].map(b => (
                <span key={b.label} className={cn("px-2 py-1 rounded-full text-xs border font-medium", b.color)}>
                  {b.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-card/40 rounded-xl border border-border/30">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg text-xs font-medium transition-all",
              activeTab === tab.id
                ? "bg-primary/10 text-primary border border-primary/20"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <tab.icon className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab content */}
      <AnimatePresence mode="wait">
        {activeTab === "overview" && (
          <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: "Problemas Abertos", value: openIssues.length, icon: AlertTriangle, color: "text-yellow-400" },
                { label: "Resolvidos", value: resolvedIssues.length, icon: CheckCircle, color: "text-green-400" },
                { label: "IPs Bloqueados", value: lobosStatus?.blockedIps?.length ?? 0, icon: XCircle, color: "text-red-400" },
                { label: "Usuários Rastreados", value: lobosStatus?.trackedUsers ?? 0, icon: Users, color: "text-blue-400" },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.08 }}
                  className="p-4 rounded-xl border border-border/30 bg-card/40"
                >
                  <stat.icon className={cn("w-5 h-5 mb-2", stat.color)} />
                  <div className={cn("text-2xl font-bold", stat.color)}>{stat.value}</div>
                  <p className="text-xs text-muted-foreground mt-0.5">{stat.label}</p>
                </motion.div>
              ))}
            </div>

            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-yellow-400" /> Problemas Ativos ({openIssues.length})
              </h3>
              {loading ? (
                <div className="text-center py-8 text-muted-foreground text-sm">Carregando...</div>
              ) : openIssues.length === 0 ? (
                <div className="text-center py-8 rounded-xl border border-green-500/20 bg-green-500/5">
                  <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                  <p className="text-sm text-green-400 font-medium">Nenhum problema ativo</p>
                  <p className="text-xs text-muted-foreground mt-1">Todos os sistemas operando normalmente</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {openIssues.map(issue => {
                    const IssueIcon = ISSUE_TYPE_ICON[issue.type] ?? Info;
                    return (
                      <motion.div
                        key={issue.id}
                        layout
                        className={cn("p-4 rounded-xl border flex items-start gap-3", ISSUE_TYPE_COLOR[issue.type])}
                      >
                        <IssueIcon className="w-5 h-5 flex-shrink-0 mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium">{issue.title}</p>
                          <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{issue.description}</p>
                          <p className="text-[10px] text-muted-foreground/60 mt-1 font-mono">
                            <Clock className="inline w-3 h-3 mr-1" />
                            {new Date(issue.createdAt).toLocaleTimeString("pt-BR")}
                          </p>
                        </div>
                        <button
                          onClick={() => resolveIssue(issue.id)}
                          className="flex-shrink-0 px-2.5 py-1 rounded-lg bg-black/20 border border-white/10 text-xs font-medium hover:bg-black/40 transition-colors"
                        >
                          Resolver
                        </button>
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </div>
          </motion.div>
        )}

        {activeTab === "formigas" && (
          <motion.div key="formigas" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">
            <div className="p-5 rounded-xl border border-primary/20 bg-card/60">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                  <Bug className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-bold text-foreground">Sistema Formigas</h3>
                  <p className="text-xs text-muted-foreground">Detecção de padrões suspeitos e anomalias</p>
                </div>
                <div className="ml-auto flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-xs text-green-400 font-mono">Ativo</span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { label: "Padrões Monitorados", value: formigasStatus?.patternsMonitored ?? 0, icon: Eye, color: "text-blue-400" },
                  { label: "Alertas nas últimas 24h", value: formigasStatus?.alertsLast24h ?? 0, icon: AlertTriangle, color: "text-yellow-400" },
                  { label: "Bloqueios automáticos", value: formigasStatus?.autoBlocks ?? 0, icon: Lock, color: "text-red-400" },
                ].map(stat => (
                  <div key={stat.label} className="p-3 rounded-lg bg-black/20 border border-border/20">
                    <stat.icon className={cn("w-4 h-4 mb-2", stat.color)} />
                    <div className={cn("text-xl font-bold", stat.color)}>{stat.value}</div>
                    <p className="text-xs text-muted-foreground">{stat.label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">Padrões Monitorados</h3>
              <div className="space-y-2">
                {(formigasStatus?.patterns ?? []).map((p, i) => (
                  <motion.div
                    key={p.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.07 }}
                    className="flex items-center gap-3 p-3.5 rounded-xl border border-border/30 bg-card/40"
                  >
                    <div className={cn(
                      "w-2 h-2 rounded-full flex-shrink-0",
                      p.status === "ativo" ? "bg-red-400 animate-pulse" : "bg-green-400"
                    )} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{p.name}</p>
                      <p className="text-xs text-muted-foreground">{p.description}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {p.count > 0 && (
                        <span className="px-2 py-0.5 rounded-full bg-red-400/10 border border-red-400/20 text-red-400 text-xs font-bold">
                          {p.count}
                        </span>
                      )}
                      <span className={cn(
                        "text-xs px-2 py-0.5 rounded-full border font-medium",
                        p.status === "ativo"
                          ? "text-red-400 border-red-400/30 bg-red-400/10"
                          : "text-green-400 border-green-400/30 bg-green-400/10"
                      )}>
                        {p.status}
                      </span>
                    </div>
                  </motion.div>
                ))}
                {!formigasStatus && (
                  <div className="text-center py-6 text-muted-foreground text-sm">Carregando padrões...</div>
                )}
              </div>
            </div>

            {/* Abelhas quarantine */}
            {abelhasStatus && abelhasStatus.activeQuarantine.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-widest text-purple-400 mb-3 flex items-center gap-2">
                  <Shield className="w-3.5 h-3.5" /> Quarentena Abelhas ({abelhasStatus.quarantinedCount})
                </h3>
                <div className="space-y-2">
                  {abelhasStatus.activeQuarantine.map((q, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 rounded-lg border border-purple-500/20 bg-purple-500/5">
                      <Shield className="w-4 h-4 text-purple-400 flex-shrink-0" />
                      <span className="font-mono text-sm text-foreground flex-1">{q.ip}</span>
                      <span className="text-xs text-muted-foreground truncate max-w-32">{q.reason}</span>
                      <span className="text-xs text-purple-400 font-mono">{q.retryInSec}s</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === "audit" && (
          <motion.div key="audit" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Activity className="w-3.5 h-3.5" /> Registro de Auditoria ({auditLog.length} entradas)
            </h3>
            {auditLog.length === 0 ? (
              <div className="text-center py-10 text-muted-foreground text-sm">
                {loading ? "Carregando..." : "Nenhuma entrada no log ainda. O sistema registrará eventos conforme requisições chegam."}
              </div>
            ) : (
              <div className="space-y-1.5">
                {auditLog.map((entry, i) => (
                  <motion.div
                    key={entry.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: Math.min(i * 0.03, 0.5) }}
                    className="flex items-center gap-3 p-3 rounded-lg border border-border/20 bg-card/30 hover:bg-card/50 transition-colors"
                  >
                    <span className={cn(
                      "flex-shrink-0 px-2 py-0.5 rounded text-[10px] font-bold border uppercase",
                      SEVERITY_COLOR[entry.severity as keyof typeof SEVERITY_COLOR] ?? SEVERITY_COLOR.low
                    )}>
                      {entry.severity}
                    </span>
                    <span className="flex-1 text-sm text-foreground/80 font-mono text-xs truncate">{entry.action}</span>
                    <span className="text-[10px] text-muted-foreground/50 font-mono flex-shrink-0">{entry.ip}</span>
                    <span className="text-[10px] text-muted-foreground/40 font-mono flex-shrink-0 hidden sm:block">
                      {new Date(entry.createdAt).toLocaleTimeString("pt-BR")}
                    </span>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {activeTab === "lobos" && (
          <motion.div key="lobos" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">
            <div className="p-5 rounded-xl border border-primary/20 bg-card/60">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                  <Lock className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-bold">Sistema Lobos</h3>
                  <p className="text-xs text-muted-foreground">Rate limiting inteligente com bloqueio progressivo</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
                {[
                  { label: "IPs Rastreados", value: lobosStatus?.trackedIps ?? 0, icon: Eye },
                  { label: "Usuários Rastreados", value: lobosStatus?.trackedUsers ?? 0, icon: Users },
                  { label: "IPs Bloqueados", value: lobosStatus?.blockedIps?.length ?? 0, icon: XCircle },
                ].map(stat => (
                  <div key={stat.label} className="p-3 rounded-lg bg-black/20 border border-border/20 text-center">
                    <stat.icon className="w-4 h-4 mx-auto mb-1 text-primary" />
                    <div className="text-2xl font-bold text-foreground">{stat.value}</div>
                    <p className="text-xs text-muted-foreground">{stat.label}</p>
                  </div>
                ))}
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Limites Configurados</h4>
                {[
                  { name: "lobosChat (Chat/IA)", ipLimit: "30/min", userLimit: "100/min", color: "text-red-400" },
                  { name: "lobosApi (API Geral)", ipLimit: "60/min", userLimit: "200/min", color: "text-yellow-400" },
                  { name: "lobosStrict (Ações Sensíveis)", ipLimit: "10/min", userLimit: "30/min", color: "text-orange-400" },
                ].map(l => (
                  <div key={l.name} className="flex items-center justify-between p-3 rounded-lg border border-border/20 bg-black/10">
                    <span className={cn("text-sm font-mono font-medium", l.color)}>{l.name}</span>
                    <div className="flex gap-3 text-xs text-muted-foreground">
                      <span>IP: {l.ipLimit}</span>
                      <span>Auth: {l.userLimit}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {lobosStatus?.blockedIps && lobosStatus.blockedIps.length > 0 ? (
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-widest text-red-400 mb-3 flex items-center gap-2">
                  <XCircle className="w-3.5 h-3.5" /> IPs Bloqueados
                </h3>
                <div className="space-y-2">
                  {lobosStatus.blockedIps.map((ip, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 rounded-lg border border-red-500/20 bg-red-500/5">
                      <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                      <span className="font-mono text-sm text-foreground flex-1">{ip.ip}</span>
                      <span className="text-xs text-muted-foreground">{ip.offenses} violações</span>
                      <span className="text-xs text-red-400 font-mono">{ip.retryInSec}s</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-6 rounded-xl border border-green-500/20 bg-green-500/5">
                <Unlock className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <p className="text-sm text-green-400">Nenhum IP bloqueado no momento</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
