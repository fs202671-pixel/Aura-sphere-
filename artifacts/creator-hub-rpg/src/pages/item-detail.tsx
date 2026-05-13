import { useParams } from "wouter";
import { useGetItem, useDeleteItem, useCloneItem } from "@workspace/api-client-react";
import { RarityBadge, TypeBadge } from "@/components/ui-rpg";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Trash2, Copy, ArrowLeft, Loader2 } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useToast } from "@/hooks/use-toast";

export default function ItemDetail() {
  const params = useParams();
  const id = Number(params.id);
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const { data: item, isLoading } = useGetItem(id, { query: { enabled: !!id } });
  const deleteItem = useDeleteItem();
  const cloneItem = useCloneItem();

  const handleDelete = () => {
    deleteItem.mutate({ id }, {
      onSuccess: () => {
        toast({ title: "Artefato Destruído", description: "O artefato foi removido do seu arsenal." });
        setLocation("/arsenal");
      },
      onError: (err: any) => {
        toast({ title: "Falha ao destruir", description: err.message, variant: "destructive" });
      }
    });
  };

  const handleClone = () => {
    cloneItem.mutate({ id }, {
      onSuccess: (cloned) => {
        toast({ title: "Artefato Clonado", description: `"${cloned.name}" adicionado ao arsenal.` });
        setLocation(`/itens/${cloned.id}`);
      },
      onError: (err: any) => {
        toast({ title: "Falha ao clonar", description: err.message, variant: "destructive" });
      }
    });
  };

  if (isLoading) {
    return (
      <div className="p-4 md:p-8 max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-8 w-32 bg-card" />
        <Skeleton className="h-64 w-full bg-card rounded-lg" />
      </div>
    );
  }

  if (!item) {
    return (
      <div className="p-4 md:p-8 max-w-4xl mx-auto text-center mt-20">
        <h2 className="text-2xl font-bold font-mono uppercase">Artefato Não Encontrado</h2>
        <p className="text-muted-foreground mt-2">Este artefato não existe ou foi destruído.</p>
        <Link href="/arsenal">
          <Button className="mt-6 font-mono uppercase">Voltar ao Arsenal</Button>
        </Link>
      </div>
    );
  }

  const isFused = Array.isArray((item.metadata as any)?.fusedFrom);

  return (
    <div className="p-4 md:p-8 max-w-4xl mx-auto space-y-6">
      <Link href="/arsenal" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground font-mono uppercase tracking-wider transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" /> Voltar ao Arsenal
      </Link>

      <div className={`border rounded-lg bg-card rarity-${item.rarity} relative overflow-hidden`}>
        {item.rarity === "Legendary" && (
          <div className="absolute inset-0 legendary-shimmer pointer-events-none opacity-20" />
        )}

        <div className="p-5 md:p-8 relative z-10">
          <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-6">
            <div className="space-y-2">
              <div className="flex items-center gap-3 flex-wrap">
                <TypeBadge type={item.type} />
                <RarityBadge rarity={item.rarity} />
                {isFused && (
                  <span className="px-2 py-0.5 text-[10px] uppercase tracking-wider font-bold rounded-sm border bg-amber-500/20 text-amber-400 border-amber-500/30">
                    ⚡ Fundido
                  </span>
                )}
              </div>
              <h1 className="text-2xl md:text-4xl font-bold tracking-tight text-foreground">{item.name}</h1>
              <p className="text-xs text-muted-foreground font-mono">
                ID: #{item.id.toString().padStart(4, "0")} · Gerado em: {new Date(item.createdAt).toLocaleDateString("pt-BR")}
              </p>
            </div>
          </div>

          <div className="mt-6 md:mt-8">
            <h3 className="font-mono uppercase tracking-widest text-xs text-muted-foreground mb-3">Lore do Artefato</h3>
            <p className="text-base leading-relaxed">{item.description || "Nenhum lore registrado para este artefato."}</p>
          </div>

          {isFused && (
            <div className="mt-6 md:mt-8">
              <h3 className="font-mono uppercase tracking-widest text-xs text-muted-foreground mb-3">Origem da Fusão</h3>
              <p className="text-sm text-muted-foreground font-mono">
                Forjado a partir de:{" "}
                {((item.metadata as any)?.originNames as string[] | undefined)?.join(" × ")
                  ?? `IDs ${((item.metadata as any)?.fusedFrom as number[])?.join(" × ")}`}
              </p>
            </div>
          )}

          {item.tags && item.tags.length > 0 && (
            <div className="mt-6 md:mt-8">
              <h3 className="font-mono uppercase tracking-widest text-xs text-muted-foreground mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {item.tags.map(tag => (
                  <span key={tag} className="px-2 py-1 bg-background border border-border rounded text-xs font-mono text-muted-foreground">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="mt-8 md:mt-12 pt-5 border-t border-border flex gap-3 flex-wrap">
            <Button
              variant="outline"
              className="font-mono uppercase tracking-wider text-xs"
              onClick={handleClone}
              disabled={cloneItem.isPending}
            >
              {cloneItem.isPending
                ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Clonando...</>
                : <><Copy className="w-4 h-4 mr-2" /> Clonar</>
              }
            </Button>
            <Button
              variant="destructive"
              className="font-mono uppercase tracking-wider text-xs"
              onClick={handleDelete}
              disabled={deleteItem.isPending}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              {deleteItem.isPending ? "Destruindo..." : "Destruir"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
