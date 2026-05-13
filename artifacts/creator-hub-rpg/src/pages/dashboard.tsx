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
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold font-mono uppercase tracking-widest text-foreground">Hub Command</h1>
        <p className="text-muted-foreground text-sm">Your creative inventory overview.</p>
      </div>

      {statsLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Skeleton className="h-32 rounded-lg bg-card" />
          <Skeleton className="h-32 rounded-lg bg-card" />
          <Skeleton className="h-32 rounded-lg bg-card" />
          <Skeleton className="h-32 rounded-lg bg-card" />
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-card/50 border-border backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Items</CardTitle>
              <Package className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground font-mono">{stats.total}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-card/50 border-amber-500/30 backdrop-blur-sm shadow-[0_0_15px_rgba(245,158,11,0.1)]">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-amber-500">Legendary Drops</CardTitle>
              <Crown className="w-4 h-4 text-amber-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-amber-500 font-mono">{stats.legendaryCount}</div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-purple-500/30 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-purple-400">Epic Items</CardTitle>
              <Sparkles className="w-4 h-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-400 font-mono">
                {stats.byRarity?.Epic || 0}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-blue-500/30 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-blue-400">Rare Items</CardTitle>
              <Shield className="w-4 h-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-400 font-mono">
                {stats.byRarity?.Rare || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold font-mono uppercase tracking-wider">Recent Drops</h2>
          <Link href="/library" className="text-sm text-primary hover:text-primary/80 transition-colors uppercase tracking-widest font-mono">
            View All Vault
          </Link>
        </div>
        
        {recentLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
             {Array.from({ length: 4 }).map((_, i) => (
               <Skeleton key={i} className="h-48 rounded-lg bg-card" />
             ))}
          </div>
        ) : recentItems && recentItems.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {recentItems.map(item => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
        ) : (
          <div className="h-48 border border-dashed border-border rounded-lg flex items-center justify-center bg-card/20">
            <p className="text-muted-foreground text-sm font-mono uppercase tracking-widest">No items dropped yet.</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
         <Link href="/themes" className="group">
           <div className="p-6 border border-border bg-card/30 rounded-lg hover:bg-card/80 hover:border-primary/50 transition-all cursor-pointer">
              <Zap className="w-8 h-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-lg mb-2">Forge Theme</h3>
              <p className="text-sm text-muted-foreground">Craft powerful visual styles for your arsenal.</p>
           </div>
         </Link>
         <Link href="/agents" className="group">
           <div className="p-6 border border-border bg-card/30 rounded-lg hover:bg-card/80 hover:border-primary/50 transition-all cursor-pointer">
              <Sword className="w-8 h-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-lg mb-2">Summon Agent</h3>
              <p className="text-sm text-muted-foreground">Create AI companions to do your bidding.</p>
           </div>
         </Link>
         <Link href="/projects" className="group">
           <div className="p-6 border border-border bg-card/30 rounded-lg hover:bg-card/80 hover:border-primary/50 transition-all cursor-pointer">
              <Package className="w-8 h-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-lg mb-2">Build Project</h3>
              <p className="text-sm text-muted-foreground">Combine items into an epic final product.</p>
           </div>
         </Link>
      </div>
    </div>
  );
}
