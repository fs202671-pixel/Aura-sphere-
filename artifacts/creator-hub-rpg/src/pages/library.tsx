import { useState } from "react";
import { useListItems, ItemType, ItemRarity, useFusaoArtefatos } from "@workspace/api-client-react";
import type { Item } from "@workspace/api-client-react";
import { ItemCard, RarityBadge, TypeBadge } from "@/components/ui-rpg";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Zap, X, Check, Loader2, ArrowRight, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";

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

const RARITY_ORDER = ["Common", "Rare", "Epic", "Legendary"];

function getResultRarity(a: string, b: string): string {
  const idxA = RARITY_ORDER.indexOf(a);
  const idxB = RARITY_ORDER.indexOf(b);
  const max = Math.max(idxA >= 0 ? idxA : 0, idxB >= 0 ? idxB : 0);
  return RARITY_ORDER[Math.min(max + 1, RARITY_ORDER.length - 1)];
}

// ── Seletor de slot para fusão ─────────────────────────────────────────────

function FusaoSlot({
  label,
  item,
  onClear,
}: {
  label: string;
  item: Item | null;
  onClear: () => void;
}) {
  return (
    <div className="flex flex-col gap-2 flex-1 min-w-0">
      <p className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground">{label}</p>
      {item ? (
        <div
          className={cn(
            "relative p-3 rounded-md bg-card border flex flex-col gap-1 group",
            `rarity-${item.rarity}`,
            item.rarity === "Rare" && "border-blue-500/50",
            item.rarity === "Epic" && "border-purple-500/50",
            item.rarity === "Legendary" && "border-amber-500/60",
          )}
        >
          <button
            onClick={onClear}
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-background/80 rounded-full p-0.5"
          >
            <X className="w-3 h-3 text-muted-foreground" />
          </button>
          <div className="flex gap-1.5 flex-wrap">
            <TypeBadge type={item.type} />
            <RarityBadge rarity={item.rarity} />
          </div>
          <p className="font-bold text-sm truncate">{item.name}</p>
          <p className="text-[10px] font-mono text-muted-foreground">#{item.id.toString().padStart(4, "0")}</p>
        </div>
      ) : (
        <div className="h-[90px] rounded-md border border-dashed border-border flex items-center justify-center bg-card/20">
          <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
            Selecione abaixo
          </p>
        </div>
      )}
    </div>
  );
}

// ── Modal de Fusão ─────────────────────────────────────────────────────────

function FusaoModal({
  open,
  onClose,
  items,
}: {
  open: boolean;
  onClose: () => void;
  items: Item[];
}) {
  const [slotA, setSlotA] = useState<Item | null>(null);
  const [slotB, setSlotB] = useState<Item | null>(null);
  const [fusedItem, setFusedItem] = useState<Item | null>(null);
  const [step, setStep] = useState<"select" | "fusing" | "result">("select");
  const fusao = useFusaoArtefatos();
  const { toast } = useToast();
  const [, setLocation] = useLocation();

  const handleClose = () => {
    setSlotA(null);
    setSlotB(null);
    setFusedItem(null);
    setStep("select");
    onClose();
  };

  const handleSelectItem = (item: Item) => {
    if (slotA?.id === item.id || slotB?.id === item.id) return;
    if (!slotA) { setSlotA(item); return; }
    if (!slotB) { setSlotB(item); return; }
  };

  const handleFundir = () => {
    if (!slotA || !slotB) return;
    setStep("fusing");
    fusao.mutate(
      { itemAId: slotA.id, itemBId: slotB.id },
      {
        onSuccess: (result) => {
          setFusedItem(result);
          setStep("result");
        },
        onError: (err) => {
          setStep("select");
          toast({ title: "Fusão falhou", description: err.message, variant: "destructive" });
        },
      }
    );
  };

  const previewRarity = slotA && slotB ? getResultRarity(slotA.rarity, slotB.rarity) : null;

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent className="bg-card border-border w-[95vw] max-w-[560px] rounded-xl overflow-hidden">
        <DialogHeader>
          <DialogTitle className="font-mono uppercase tracking-wider flex items-center gap-2 text-lg">
            <Zap className="w-5 h-5 text-amber-400" />
            Fusão de Artefatos
          </DialogTitle>
        </DialogHeader>

        {/* ── Passo 1: Seleção ── */}
        {(step === "select" || step === "fusing") && (
          <div className="space-y-5">
            {/* Slots */}
            <div className="flex items-center gap-3">
              <FusaoSlot label="Artefato A" item={slotA} onClear={() => setSlotA(null)} />
              <div className="flex flex-col items-center gap-1 shrink-0 pt-5">
                <ArrowRight className="w-4 h-4 text-muted-foreground" />
                {previewRarity && (
                  <RarityBadge rarity={previewRarity} className="text-[9px]" />
                )}
              </div>
              <FusaoSlot label="Artefato B" item={slotB} onClear={() => setSlotB(null)} />
            </div>

            {/* Botão de fundir */}
            <Button
              className="w-full font-mono uppercase tracking-wider text-sm"
              disabled={!slotA || !slotB || step === "fusing"}
              onClick={handleFundir}
            >
              {step === "fusing" ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  O CAOS está fundindo...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Fundir Artefatos
                </>
              )}
            </Button>

            <div className="border-t border-border pt-4">
              <p className="text-[10px] font-mono uppercase text-muted-foreground mb-3 tracking-wider">
                Selecione dois artefatos — clique para adicionar ao slot
              </p>
              <div className="grid grid-cols-2 gap-2 max-h-[260px] overflow-y-auto pr-1">
                {items.map((item) => {
                  const isSelected = slotA?.id === item.id || slotB?.id === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleSelectItem(item)}
                      disabled={isSelected}
                      className={cn(
                        "text-left p-2.5 rounded border transition-all flex flex-col gap-1",
                        isSelected
                          ? "opacity-40 cursor-not-allowed bg-card border-border"
                          : "bg-card/60 border-border/50 hover:border-primary/50 hover:bg-card cursor-pointer",
                        isSelected && "ring-1 ring-primary/30"
                      )}
                    >
                      {isSelected && (
                        <Check className="w-3 h-3 text-primary absolute" />
                      )}
                      <div className="flex gap-1 flex-wrap">
                        <TypeBadge type={item.type} />
                        <RarityBadge rarity={item.rarity} />
                      </div>
                      <p className="text-xs font-bold truncate">{item.name}</p>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* ── Passo 2: Resultado ── */}
        {step === "result" && fusedItem && (
          <div className="space-y-5 text-center">
            <div className="flex flex-col items-center gap-3 pt-2">
              <Sparkles className="w-10 h-10 text-amber-400 animate-pulse" />
              <p className="text-sm font-mono uppercase tracking-widest text-muted-foreground">
                Novo Artefato Manifestado
              </p>
            </div>

            <div
              className={cn(
                "p-5 rounded-lg border bg-card text-left",
                `rarity-${fusedItem.rarity}`,
                fusedItem.rarity === "Rare" && "border-blue-500/60",
                fusedItem.rarity === "Epic" && "border-purple-500/60",
                fusedItem.rarity === "Legendary" && "border-amber-500/70 shadow-[0_0_30px_rgba(245,158,11,0.25)]",
              )}
            >
              {fusedItem.rarity === "Legendary" && (
                <div className="absolute inset-0 rounded-lg legendary-shimmer pointer-events-none opacity-30" />
              )}
              <div className="relative z-10">
                <div className="flex gap-2 mb-2 flex-wrap">
                  <TypeBadge type={fusedItem.type} />
                  <RarityBadge rarity={fusedItem.rarity} />
                </div>
                <h3 className="text-xl font-bold mb-2">{fusedItem.name}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{fusedItem.description}</p>
                {fusedItem.tags && fusedItem.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-3">
                    {fusedItem.tags.map((tag) => (
                      <span key={tag} className="text-[10px] px-1.5 py-0.5 bg-background/60 border border-border/50 rounded font-mono text-muted-foreground">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex gap-2 pt-1">
              <Button
                variant="outline"
                className="flex-1 font-mono uppercase text-xs tracking-wider"
                onClick={handleClose}
              >
                Fechar
              </Button>
              <Button
                className="flex-1 font-mono uppercase text-xs tracking-wider"
                onClick={() => {
                  handleClose();
                  setLocation(`/itens/${fusedItem.id}`);
                }}
              >
                Ver Artefato
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

// ── Página principal do Arsenal ────────────────────────────────────────────

export default function Library() {
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [rarityFilter, setRarityFilter] = useState<string>("all");
  const [fusaoOpen, setFusaoOpen] = useState(false);

  const { data: items, isLoading } = useListItems({
    type: typeFilter !== "all" ? typeFilter as any : undefined,
    rarity: rarityFilter !== "all" ? rarityFilter as any : undefined,
  });

  const allItems = items ?? [];

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8">
      <div className="flex flex-col gap-3 md:flex-row md:justify-between md:items-center">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl md:text-3xl font-bold font-mono uppercase tracking-widest text-foreground">
            Arsenal
          </h1>
          <p className="text-muted-foreground text-sm">Coleção completa de artefatos CAOS.</p>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row w-full md:w-auto">
          {/* Filtros */}
          <div className="flex gap-2 flex-1 md:flex-initial">
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="flex-1 md:w-[130px] bg-card border-border font-mono text-xs uppercase tracking-wider">
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
              <SelectTrigger className="flex-1 md:w-[120px] bg-card border-border font-mono text-xs uppercase tracking-wider">
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

          {/* Botão Fundir */}
          <Button
            onClick={() => setFusaoOpen(true)}
            disabled={allItems.length < 2}
            className="font-mono uppercase tracking-wider text-xs shrink-0 bg-amber-600 hover:bg-amber-500 text-white border-amber-500"
            title={allItems.length < 2 ? "Você precisa de pelo menos 2 artefatos para fundir" : undefined}
          >
            <Zap className="w-4 h-4 mr-1.5" />
            Fundir
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-lg bg-card" />
          ))}
        </div>
      ) : allItems.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-6">
          {allItems.map(item => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <div className="h-56 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest text-sm">Nenhum artefato encontrado.</p>
        </div>
      )}

      <FusaoModal
        open={fusaoOpen}
        onClose={() => setFusaoOpen(false)}
        items={allItems}
      />
    </div>
  );
}
