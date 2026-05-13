import { motion } from "framer-motion";
import { Link } from "wouter";
import { Shield, Cpu, Layers, Map, ChevronRight, Package } from "lucide-react";
import { useGetItemStats, useGetRecentItems } from "@workspace/api-client-react";
import { cn } from "@/lib/utils";

const sections = [
  {
    href: "/studio/arsenal",
    label: "Arsenal",
    description: "Artefatos criados e colecionados",
    icon: Shield,
    color: "text-blue-400",
    border: "border-blue-500/30",
    bg: "from-blue-500/10 to-transparent",
  },
  {
    href: "/studio/entidades",
    label: "Entidades",
    description: "IAs companheiras configuradas",
    icon: Cpu,
    color: "text-primary",
    border: "border-primary/30",
    bg: "from-primary/10 to-transparent",
  },
  {
    href: "/studio/fragmentos",
    label: "Fragmentos",
    description: "Temas visuais e estilos",
    icon: Layers,
    color: "text-purple-400",
    border: "border-purple-500/30",
    bg: "from-purple-500/10 to-transparent",
  },
  {
    href: "/studio/missoes",
    label: "Missões",
    description: "Projetos e objetivos em andamento",
    icon: Map,
    color: "text-amber-400",
    border: "border-amber-500/30",
    bg: "from-amber-500/10 to-transparent",
  },
];

export default function StudioHome() {
  const { data: stats } = useGetItemStats();
  const { data: recentItems } = useGetRecentItems({ limit: 3 });

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
        <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-amber-400/60 mb-1">// Central de Criação</p>
        <h1 className="text-2xl font-black uppercase tracking-widest text-foreground">Studio CAOS</h1>
        <p className="text-sm text-muted-foreground mt-1">Arsenal criativo gamificado com artefatos, entidades e missões.</p>
      </motion.div>

      {/* Stats */}
      {stats && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-3"
        >
          {[
            { label: "Total", value: stats.total, color: "text-foreground" },
            { label: "Lendários", value: stats.legendaryCount, color: "text-amber-400" },
            { label: "Épicos", value: (stats.byRarity as any)?.Epic ?? 0, color: "text-purple-400" },
            { label: "Raros", value: (stats.byRarity as any)?.Rare ?? 0, color: "text-blue-400" },
          ].map((s) => (
            <div key={s.label} className="rounded-xl bg-card/40 border border-border/40 p-4">
              <div className={cn("text-2xl font-black font-mono", s.color)}>{s.value}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{s.label}</div>
            </div>
          ))}
        </motion.div>
      )}

      {/* Sections */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="space-y-3"
      >
        <p className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground/60">Módulos</p>
        {sections.map((s) => (
          <Link key={s.href} href={s.href}>
            <div
              className={cn(
                "flex items-center gap-4 p-4 rounded-xl border bg-gradient-to-r backdrop-blur-sm cursor-pointer transition-all active:scale-[0.98] hover:scale-[1.01]",
                s.border, s.bg
              )}
            >
              <div className="w-11 h-11 rounded-xl bg-black/30 border border-white/10 flex items-center justify-center flex-shrink-0">
                <s.icon className={cn("w-5 h-5", s.color)} />
              </div>
              <div className="flex-1">
                <p className="font-bold text-sm text-foreground">{s.label}</p>
                <p className="text-xs text-muted-foreground">{s.description}</p>
              </div>
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            </div>
          </Link>
        ))}
      </motion.div>

      {/* Recent items */}
      {recentItems && recentItems.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="space-y-3"
        >
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground/60">Recentes</p>
            <Link href="/studio/arsenal" className="text-xs text-primary hover:underline">Ver todos</Link>
          </div>
          <div className="space-y-2">
            {recentItems.map((item) => (
              <Link key={item.id} href={`/studio/itens/${item.id}`}>
                <div className="flex items-center gap-3 p-3 rounded-xl bg-card/40 border border-border/40 hover:border-border transition-colors cursor-pointer">
                  <Package className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.name}</p>
                    <p className="text-xs text-muted-foreground">{item.type} · {item.rarity}</p>
                  </div>
                  <ChevronRight className="w-3 h-3 text-muted-foreground" />
                </div>
              </Link>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
