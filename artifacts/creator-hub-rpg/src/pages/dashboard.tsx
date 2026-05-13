import { useGetItemStats, useGetRecentItems } from "@workspace/api-client-react";
import { ItemCard } from "@/components/ui-rpg";
import { Skeleton } from "@/components/ui/skeleton";
import { Link } from "wouter";
import { Package, Sparkles, Zap, Shield, Sword, Crown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useGetItemStats();
  const { data: recentItems, isLoading: recentLoading } = useGetRecentItems({ limit: 4 });

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl md:text-3xl font-bold font-mono uppercase tracking-widest text-foreground">
          Central CAOS
        </h1>
        <p className="text-muted-foreground text-sm">Painel de controle do seu inventário criativo.</p>
      </div>

      {statsLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 md:h-32 rounded-lg bg-card" />
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          <Card className="bg-card/50 border-border backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-1 pt-3 px-4">
              <CardTitle className="text-xs font-medium text-muted-foreground">Total</CardTitle>
              <Package className="w-3.5 h-3.5 text-muted-foreground" />
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl md:text-3xl font-bold text-foreground font-mono">{stats.total}</div>
              <p className="text-[10px] text-muted-foreground mt-0.5">artefatos</p>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-amber-500/30 backdrop-blur-sm shadow-[0_0_15px_rgba(245,158,11,0.1)]">
            <CardHeader className="flex flex-row items-center justify-between pb-1 pt-3 px-4">
              <CardTitle className="text-xs font-medium text-amber-500">Lendários</CardTitle>
              <Crown className="w-3.5 h-3.5 text-amber-500" />
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl md:text-3xl font-bold text-amber-500 font-mono">{stats.legendaryCount}</div>
              <p className="text-[10px] text-amber-500/60 mt-0.5">drops</p>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-purple-500/30 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-1 pt-3 px-4">
              <CardTitle className="text-xs font-medium text-purple-400">Épicos</CardTitle>
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl md:text-3xl font-bold text-purple-400 font-mono">
                {stats.byRarity?.Epic || 0}
              </div>
              <p className="text-[10px] text-purple-400/60 mt-0.5">itens</p>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-blue-500/30 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-1 pt-3 px-4">
              <CardTitle className="text-xs font-medium text-blue-400">Raros</CardTitle>
              <Shield className="w-3.5 h-3.5 text-blue-400" />
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="text-2xl md:text-3xl font-bold text-blue-400 font-mono">
                {stats.byRarity?.Rare || 0}
              </div>
              <p className="text-[10px] text-blue-400/60 mt-0.5">itens</p>
            </CardContent>
          </Card>
        </div>
      ) : null}

      <div className="space-y-3 md:space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base md:text-xl font-bold font-mono uppercase tracking-wider">Drops Recentes</h2>
          <Link href="/arsenal" className="text-xs text-primary hover:text-primary/80 transition-colors uppercase tracking-widest font-mono">
            Ver Arsenal →
          </Link>
        </div>

        {recentLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-44 rounded-lg bg-card" />
            ))}
          </div>
        ) : recentItems && recentItems.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            {recentItems.map(item => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
        ) : (
          <div className="h-36 border border-dashed border-border rounded-lg flex items-center justify-center bg-card/20">
            <p className="text-muted-foreground text-sm font-mono uppercase tracking-widest">Nenhum drop ainda.</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-6 pt-2">
        <Link href="/fragmentos" className="group">
          <div className="p-4 md:p-6 border border-border bg-card/30 rounded-lg hover:bg-card/80 hover:border-primary/50 transition-all cursor-pointer">
            <Zap className="w-6 h-6 md:w-8 md:h-8 text-primary mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-bold text-base mb-1">Forjar Fragmento</h3>
            <p className="text-xs text-muted-foreground">Crie estilos visuais poderosos para seu arsenal.</p>
          </div>
        </Link>
        <Link href="/entidades" className="group">
          <div className="p-4 md:p-6 border border-border bg-card/30 rounded-lg hover:bg-card/80 hover:border-primary/50 transition-all cursor-pointer">
            <Sword className="w-6 h-6 md:w-8 md:h-8 text-primary mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-bold text-base mb-1">Invocar Entidade</h3>
            <p className="text-xs text-muted-foreground">Crie IAs companheiras para executar suas ordens.</p>
          </div>
        </Link>
        <Link href="/missoes" className="group">
          <div className="p-4 md:p-6 border border-border bg-card/30 rounded-lg hover:bg-card/80 hover:border-primary/50 transition-all cursor-pointer">
            <Package className="w-6 h-6 md:w-8 md:h-8 text-primary mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-bold text-base mb-1">Iniciar Missão</h3>
            <p className="text-xs text-muted-foreground">Combine artefatos em drops épicos finais.</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
