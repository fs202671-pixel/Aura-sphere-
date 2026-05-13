import { useGetAiProfile, useGetAiStats, useListNexusSkills as useListSkills } from "@/lib/nexus-api";
import { motion } from "framer-motion";
import { Cpu, Zap, Shield, Star, TrendingUp, Activity, BookOpen, Layers } from "lucide-react";
import { Link } from "wouter";
import { cn } from "@/lib/utils";

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

const statCards = [
  { key: "acquiredSkills", label: "Habilidades", icon: Shield, color: "text-primary" },
  { key: "pendingSkills", label: "Pendentes", icon: BookOpen, color: "text-yellow-400" },
  { key: "fusedSkills", label: "Fundidas", icon: Zap, color: "text-purple-400" },
  { key: "totalXp", label: "XP Total", icon: Star, color: "text-green-400" },
];

export default function Dashboard() {
  const { data: profile, isLoading: loadingProfile } = useGetAiProfile();
  const { data: stats, isLoading: loadingStats } = useGetAiStats();
  const { data: skills } = useListSkills({ status: "acquired" });

  const recentSkills = skills?.slice(0, 4) || [];

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
