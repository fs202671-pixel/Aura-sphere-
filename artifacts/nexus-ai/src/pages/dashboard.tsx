import { useGetAiProfile, useGetAiStats, useListNexusSkills as useListSkills, useCaosStatus } from "@/lib/nexus-api";
import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useEffect, useRef } from "react";
import {
  Cpu, Zap, Shield, Star, TrendingUp, Activity, BookOpen, Layers,
  Brain, Sword, Database, MessageSquare, RefreshCw, Wifi, WifiOff, Clock,
} from "lucide-react";
import { Link } from "wouter";
import { cn } from "@/lib/utils";

// ── Contador Animado ─────────────────────────────────────────────────────────

function AnimatedCounter({ value, className }: { value: number; className?: string }) {
  const motionVal = useMotionValue(0);
  const rounded = useTransform(motionVal, (v) => Math.round(v));
  const displayRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const controls = animate(motionVal, value, {
      duration: 1.4,
      ease: "easeOut",
    });
    return controls.stop;
  }, [value, motionVal]);

  useEffect(() => {
    return rounded.on("change", (v) => {
      if (displayRef.current) displayRef.current.textContent = String(v);
    });
  }, [rounded]);

  return <span ref={displayRef} className={className}>0</span>;
}

// ── Barra XP ─────────────────────────────────────────────────────────────────

function XpBar({ xp, xpToNext, level }: { xp: number; xpToNext: number; level: number }) {
  const total = xp + xpToNext;
  const pct = total > 0 ? (xp / total) * 100 : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>XP: {xp}</span>
        <span>Próximo nível: {xpToNext} XP</span>
      </div>
      <div className="h-2 w-full bg-black/60 rounded-full border border-border/50 overflow-hidden">
        <motion.div
          className="h-full bg-primary rounded-full shadow-[0_0_8px_hsl(var(--primary))]"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

// ── Cards de stats do perfil ──────────────────────────────────────────────────

const statCards = [
  { key: "acquiredSkills", label: "Habilidades", icon: Shield, color: "text-primary" },
  { key: "pendingSkills", label: "Pendentes", icon: BookOpen, color: "text-yellow-400" },
  { key: "fusedSkills", label: "Fundidas", icon: Zap, color: "text-purple-400" },
  { key: "totalXp", label: "XP Total", icon: Star, color: "text-green-400" },
];

// ── Configuração dos subsistemas ──────────────────────────────────────────────

const SUBSYSTEM_CONFIG = {
  "caos-nexus": {
    label: "CAOS Nexus",
    icon: Brain,
    color: "text-cyan-400",
    borderColor: "border-cyan-400/30",
    glowColor: "shadow-[0_0_20px_rgba(34,211,238,0.08)]",
    stats: [
      { key: "skills", label: "Skills", icon: Shield },
      { key: "conversations", label: "Conversas", icon: MessageSquare },
      { key: "profiles", label: "Perfis", icon: Cpu },
      { key: "activityLogs", label: "Atividades", icon: Activity },
    ],
  },
  "caos-studio": {
    label: "CAOS Studio",
    icon: Sword,
    color: "text-purple-400",
    borderColor: "border-purple-400/30",
    glowColor: "shadow-[0_0_20px_rgba(167,139,250,0.08)]",
    stats: [
      { key: "items", label: "Artefatos", icon: Layers },
      { key: "agents", label: "Entidades", icon: Cpu },
      { key: "skills", label: "Protocolos", icon: Zap },
      { key: "projects", label: "Missões", icon: Star },
    ],
  },
  "caos-shell": {
    label: "CAOS Shell",
    icon: Database,
    color: "text-green-400",
    borderColor: "border-green-400/30",
    glowColor: "shadow-[0_0_20px_rgba(74,222,128,0.08)]",
    stats: [
      { key: "skills", label: "Skills", icon: Shield },
      { key: "memories", label: "Memórias", icon: Brain },
      { key: "profiles", label: "Perfis", icon: Cpu },
    ],
  },
} as const;

// ── Card de Subsistema ────────────────────────────────────────────────────────

function SubsystemCard({
  id,
  subsystem,
  delay,
}: {
  id: keyof typeof SUBSYSTEM_CONFIG;
  subsystem: { label: string; status: string; stats: Record<string, number> };
  delay: number;
}) {
  const config = SUBSYSTEM_CONFIG[id];
  const Icon = config.icon;
  const isOnline = subsystem.status === "online";

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={cn(
        "relative rounded-sm border bg-card/60 backdrop-blur-sm p-5",
        config.borderColor,
        config.glowColor
      )}
    >
      <div className={cn("absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent to-transparent", {
        "via-cyan-400/60": id === "caos-nexus",
        "via-purple-400/60": id === "caos-studio",
        "via-green-400/60": id === "caos-shell",
      })} />

      {/* Header do card */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className={cn("h-9 w-9 rounded-sm border flex items-center justify-center bg-black/40", config.borderColor)}>
            <Icon className={cn("h-4 w-4", config.color)} />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-wide">{config.label}</p>
            <div className="flex items-center gap-1.5 mt-0.5">
              {isOnline ? (
                <Wifi className="h-3 w-3 text-green-400" />
              ) : (
                <WifiOff className="h-3 w-3 text-red-400" />
              )}
              <span className={cn("text-[10px] uppercase tracking-widest font-mono", isOnline ? "text-green-400" : "text-red-400")}>
                {isOnline ? "online" : "offline"}
              </span>
            </div>
          </div>
        </div>
        <div className={cn("h-2 w-2 rounded-full", isOnline ? "bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.8)]" : "bg-red-400")} />
      </div>

      {/* Grid de contadores */}
      <div className="grid grid-cols-2 gap-3">
        {config.stats.map((stat, i) => {
          const val = subsystem.stats[stat.key] ?? 0;
          const StatIcon = stat.icon;
          return (
            <motion.div
              key={stat.key}
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: delay + 0.1 + i * 0.07 }}
              className="rounded-sm bg-black/30 border border-border/20 p-3"
            >
              <div className="flex items-center gap-1.5 mb-2">
                <StatIcon className="h-3 w-3 text-muted-foreground" />
                <span className="text-[10px] text-muted-foreground uppercase tracking-widest">{stat.label}</span>
              </div>
              <AnimatedCounter value={val} className={cn("text-2xl font-bold font-mono", config.color)} />
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}

// ── Dashboard Principal ───────────────────────────────────────────────────────

export default function Dashboard() {
  const { data: profile, isLoading: loadingProfile } = useGetAiProfile();
  const { data: stats, isLoading: loadingStats } = useGetAiStats();
  const { data: skills } = useListSkills({ status: "acquired" });
  const { data: caosStatus, isLoading: loadingStatus, isError: statusError, dataUpdatedAt, refetch } = useCaosStatus();

  const recentSkills = skills?.slice(0, 4) || [];

  const lastUpdate = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })
    : null;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <p className="text-xs text-primary/70 uppercase tracking-widest mb-1">// Sistema Neural Ativo</p>
        <h1 className="text-3xl font-bold text-foreground tracking-tight">Dashboard</h1>
      </motion.div>

      {/* Profile card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="relative rounded-sm border border-primary/30 bg-card/80 backdrop-blur-sm p-6 shadow-[0_0_30px_hsl(var(--primary)/0.1)]"
      >
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary to-transparent" />
        {loadingProfile ? (
          <div className="h-24 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-primary" />
          </div>
        ) : profile ? (
          <div className="flex flex-col md:flex-row md:items-center gap-6">
            <div className="relative">
              <div className="h-20 w-20 rounded-sm bg-primary/10 border border-primary/40 flex items-center justify-center shadow-[0_0_20px_hsl(var(--primary)/0.3)]">
                <Cpu className="h-10 w-10 text-primary" />
              </div>
              <div className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full bg-background border border-primary/50 flex items-center justify-center text-[10px] font-bold text-primary">
                {profile.level}
              </div>
            </div>
            <div className="flex-1 space-y-3">
              <div>
                <h2 className="text-2xl font-bold tracking-wider text-primary glitch-text">{profile.name}</h2>
                <p className="text-sm text-muted-foreground">Classe: <span className="text-accent-foreground">{profile.aiClass}</span></p>
              </div>
              <p className="text-sm text-muted-foreground">{profile.description}</p>
              <XpBar xp={profile.xp} xpToNext={profile.xpToNext} level={profile.level} />
            </div>
            <div className="text-right">
              <div className="text-5xl font-bold text-primary/80">Nv.{profile.level}</div>
              <p className="text-xs text-muted-foreground mt-1">{profile.personality}</p>
            </div>
          </div>
        ) : null}
      </motion.div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <motion.div
            key={card.key}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: 0.2 + i * 0.08 }}
            className="rounded-sm border border-border/50 bg-card/60 backdrop-blur-sm p-4 hover:border-primary/30 transition-colors group"
          >
            <div className="flex items-center justify-between mb-3">
              <card.icon className={cn("h-5 w-5", card.color, "group-hover:drop-shadow-[0_0_8px_currentColor] transition-all")} />
              <span className="text-[10px] text-muted-foreground uppercase tracking-widest">{card.label}</span>
            </div>
            {loadingStats ? (
              <div className="h-8 w-16 bg-muted/30 rounded animate-pulse" />
            ) : (
              <motion.div
                className={cn("text-3xl font-bold", card.color)}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 + i * 0.1 }}
              >
                {(stats as any)?.[card.key] ?? 0}
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* ── Painel Unificado CAOS ─────────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.35 }}
        className="space-y-4"
      >
        {/* Cabeçalho da seção */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-primary/70 uppercase tracking-widest mb-0.5">// Sincronizado em tempo real</p>
            <h2 className="text-lg font-bold tracking-tight flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Painel Unificado CAOS
            </h2>
          </div>
          <div className="flex items-center gap-3">
            {lastUpdate && (
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span className="font-mono">{lastUpdate}</span>
              </div>
            )}
            <button
              onClick={() => refetch()}
              disabled={loadingStatus}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-primary transition-colors disabled:opacity-40 border border-border/40 hover:border-primary/30 rounded-sm px-2.5 py-1.5"
            >
              <RefreshCw className={cn("h-3 w-3", loadingStatus && "animate-spin")} />
              Atualizar
            </button>
          </div>
        </div>

        {/* Estado de carregamento */}
        {loadingStatus && !caosStatus && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[0, 1, 2].map((i) => (
              <div key={i} className="rounded-sm border border-border/30 bg-card/40 p-5 space-y-4 animate-pulse">
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 rounded-sm bg-muted/30" />
                  <div className="space-y-1.5">
                    <div className="h-3 w-24 bg-muted/30 rounded" />
                    <div className="h-2.5 w-14 bg-muted/20 rounded" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {[0, 1, 2, 3].map((j) => (
                    <div key={j} className="rounded-sm bg-black/20 border border-border/20 p-3">
                      <div className="h-2 w-12 bg-muted/20 rounded mb-2" />
                      <div className="h-6 w-8 bg-muted/30 rounded" />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Erro ao carregar */}
        {statusError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-sm border border-red-500/30 bg-red-500/5 p-5 flex items-center gap-3"
          >
            <WifiOff className="h-5 w-5 text-red-400 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-400">Falha ao conectar com a API</p>
              <p className="text-xs text-muted-foreground mt-0.5">Verifique se o servidor está rodando e tente novamente.</p>
            </div>
          </motion.div>
        )}

        {/* Cards dos subsistemas */}
        {caosStatus && (
          <>
            {/* Banner de status geral */}
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4 }}
              className="flex items-center gap-3 rounded-sm border border-primary/20 bg-primary/5 px-4 py-2.5"
            >
              <div className="h-2 w-2 rounded-full bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.8)] animate-pulse" />
              <span className="text-xs font-mono text-muted-foreground">
                CAOS v{caosStatus.caos.version} · status:{" "}
                <span className="text-green-400">{caosStatus.caos.status}</span>
                {" · "}todos os subsistemas operacionais
              </span>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {(Object.keys(SUBSYSTEM_CONFIG) as Array<keyof typeof SUBSYSTEM_CONFIG>).map((key, i) => {
                const subsystem = caosStatus.subsystems[key];
                if (!subsystem) return null;
                return (
                  <SubsystemCard
                    key={key}
                    id={key}
                    subsystem={subsystem}
                    delay={0.45 + i * 0.1}
                  />
                );
              })}
            </div>

            {/* Totalizador geral */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.75 }}
              className="grid grid-cols-3 gap-4"
            >
              {[
                {
                  label: "Total de Skills",
                  icon: Shield,
                  color: "text-cyan-400",
                  value:
                    (caosStatus.subsystems["caos-nexus"]?.stats.skills ?? 0) +
                    (caosStatus.subsystems["caos-studio"]?.stats.skills ?? 0) +
                    (caosStatus.subsystems["caos-shell"]?.stats.skills ?? 0),
                },
                {
                  label: "Total de Memórias",
                  icon: Brain,
                  color: "text-purple-400",
                  value: caosStatus.subsystems["caos-shell"]?.stats.memories ?? 0,
                },
                {
                  label: "Total de Conversas",
                  icon: MessageSquare,
                  color: "text-green-400",
                  value: caosStatus.subsystems["caos-nexus"]?.stats.conversations ?? 0,
                },
              ].map((total, i) => {
                const TotalIcon = total.icon;
                return (
                  <motion.div
                    key={total.label}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.4, delay: 0.8 + i * 0.07 }}
                    className="rounded-sm border border-border/40 bg-black/40 p-4 flex items-center gap-4"
                  >
                    <div className={cn("h-10 w-10 rounded-sm border border-border/30 bg-black/40 flex items-center justify-center flex-shrink-0")}>
                      <TotalIcon className={cn("h-5 w-5", total.color)} />
                    </div>
                    <div>
                      <p className="text-[10px] text-muted-foreground uppercase tracking-widest mb-1">{total.label}</p>
                      <AnimatedCounter value={total.value} className={cn("text-2xl font-bold font-mono", total.color)} />
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>
          </>
        )}
      </motion.div>

      {/* Recent Skills + Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Recent acquired skills */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="rounded-sm border border-border/50 bg-card/60 backdrop-blur-sm p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Layers className="h-4 w-4" /> Habilidades Recentes
            </h3>
            <Link href="/caos/habilidades" className="text-xs text-primary hover:underline">Ver todas</Link>
          </div>
          {recentSkills.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p className="text-sm">Nenhuma habilidade adquirida.</p>
              <Link href="/caos/estudar" className="text-primary text-xs hover:underline mt-2 inline-block">Ir para Estudar</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentSkills.map((skill) => (
                <div key={skill.id} className="flex items-center gap-3 p-2 rounded-sm bg-black/30 border border-border/30">
                  <div className="h-8 w-8 rounded-sm flex items-center justify-center" style={{ backgroundColor: `${skill.color}20`, border: `1px solid ${skill.color}40` }}>
                    <span className="text-xs font-bold" style={{ color: skill.color }}>{skill.icon?.charAt(0) || "Z"}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{skill.name}</p>
                    <p className="text-xs text-muted-foreground">{skill.category}</p>
                  </div>
                  <span className="text-xs text-green-400">+{skill.xpValue} XP</span>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Activity feed */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="rounded-sm border border-border/50 bg-card/60 backdrop-blur-sm p-5"
        >
          <h3 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-2 mb-4">
            <Activity className="h-4 w-4" /> Log de Atividade
          </h3>
          {loadingStats ? (
            <div className="space-y-2">
              {[1, 2, 3].map(i => <div key={i} className="h-6 bg-muted/30 rounded animate-pulse" />)}
            </div>
          ) : (stats?.recentActivity?.length ?? 0) === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-sm">
              Nenhuma atividade registrada.
            </div>
          ) : (
            <div className="space-y-2 text-xs font-mono">
              {stats?.recentActivity?.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + i * 0.05 }}
                  className="flex items-start gap-2 text-muted-foreground"
                >
                  <span className="text-primary/50 mt-0.5">{">"}</span>
                  <span className="flex-1">{item}</span>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Quick actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="space-y-3"
      >
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Ações Rápidas</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {[
            { href: "/caos/estudar", label: "Estudar Tópico", desc: "Adicionar conhecimento à IA", icon: BookOpen, color: "text-cyan-400 border-cyan-400/20 hover:border-cyan-400/50" },
            { href: "/builder", label: "CAOS Builder", desc: "Assistente de codificação", icon: TrendingUp, color: "text-green-400 border-green-400/20 hover:border-green-400/50" },
            { href: "/professor", label: "Modo Professor", desc: "Ensino em 3 passos guiados", icon: Star, color: "text-yellow-400 border-yellow-400/20 hover:border-yellow-400/50" },
            { href: "/caos/fusao", label: "Fundir Habilidades", desc: "Combinar poderes existentes", icon: Zap, color: "text-pink-400 border-pink-400/20 hover:border-pink-400/50" },
            { href: "/seguranca", label: "Dashboard de Segurança", desc: "Formigas, Lobos e Auditoria", icon: Shield, color: "text-red-400 border-red-400/20 hover:border-red-400/50" },
            { href: "/caos/terminal", label: "Terminal IA", desc: "Sessões com histórico", icon: Activity, color: "text-purple-400 border-purple-400/20 hover:border-purple-400/50" },
          ].map((action, i) => (
            <motion.div
              key={action.href}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.7 + i * 0.05 }}
            >
              <Link href={action.href}>
                <div className={cn("rounded-sm border bg-card/40 p-4 flex items-center gap-3 cursor-pointer transition-all duration-200 hover:bg-card/80 group", action.color)}>
                  <action.icon className="h-7 w-7 flex-shrink-0 group-hover:drop-shadow-[0_0_10px_currentColor] transition-all" />
                  <div>
                    <p className="font-medium text-sm">{action.label}</p>
                    <p className="text-xs text-muted-foreground">{action.desc}</p>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
