import { useState } from "react";
import { useListItems, ItemType, ItemRarity } from "@workspace/api-client-react";
import { ItemCard } from "@/components/ui-rpg";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const tipoLabels: Record<string, string> = {
  design: "Design",
  theme: "Fragmento",
  agent: "Entidade",
  skill: "Protocolo",
  project: "Missão",
  component: "Componente",
};

const raridadeLabels: Record<string, string> = {
  Common: "Comum",
  Rare: "Raro",
  Epic: "Épico",
  Legendary: "Lendário",
};

export default function Library() {
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [rarityFilter, setRarityFilter] = useState<string>("all");

  const { data: items, isLoading } = useListItems({
    type: typeFilter !== "all" ? typeFilter as any : undefined,
    rarity: rarityFilter !== "all" ? rarityFilter as any : undefined,
  });

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8">
      <div className="flex flex-col gap-3 md:flex-row md:justify-between md:items-center">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl md:text-3xl font-bold font-mono uppercase tracking-widest text-foreground">
            Arsenal
          </h1>
          <p className="text-muted-foreground text-sm">Coleção completa de artefatos CAOS.</p>
        </div>

        <div className="flex gap-2 w-full md:w-auto">
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="flex-1 md:w-[140px] bg-card border-border font-mono text-xs uppercase tracking-wider">
              <SelectValue placeholder="Todos os tipos" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os tipos</SelectItem>
              {Object.values(ItemType).map(t => (
                <SelectItem key={t} value={t}>{tipoLabels[t] ?? t}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={rarityFilter} onValueChange={setRarityFilter}>
            <SelectTrigger className="flex-1 md:w-[140px] bg-card border-border font-mono text-xs uppercase tracking-wider">
              <SelectValue placeholder="Raridade" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toda raridade</SelectItem>
              {Object.values(ItemRarity).map(r => (
                <SelectItem key={r} value={r}>{raridadeLabels[r] ?? r}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-lg bg-card" />
          ))}
        </div>
      ) : items && items.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-6">
          {items.map(item => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <div className="h-56 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest text-sm">Nenhum artefato encontrado.</p>
        </div>
      )}
    </div>
  );
}
