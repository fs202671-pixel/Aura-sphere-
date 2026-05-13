import { useParams } from "wouter";
import { useGetItem, useDeleteItem, useCloneItem } from "@workspace/api-client-react";
import { RarityBadge, TypeBadge } from "@/components/ui-rpg";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Trash2, Copy, ArrowLeft, Loader2 } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useToast } from "@/hooks/use-toast";
import { motion } from "framer-motion";

export default function ItemDetail() {
  const params = useParams();
  const id = Number(params.id);
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const { data: item, isLoading } = useGetItem(id, { query: { enabled: !!id } });
  const deleteItem = useDeleteItem();
  const cloneItem = useCloneItem();

  const handleDelete = () => {
    deleteItem.mutate(
      { id },
      {
        onSuccess: () => {
          toast({ title: "Artefato Destruído", description: "O artefato foi removido do arsenal." });
          setLocation("/studio/arsenal");
        },
        onError: (err: any) => {
          toast({ title: "Falha ao destruir", description: err.message, variant: "destructive" });
        },
      }
    );
  };

  const handleClone = () => {
    cloneItem.mutate(
      { id },
      {
        onSuccess: (cloned) => {
          toast({ title: "Artefato Clonado", description: `"${cloned.name}" adicionado ao arsenal.` });
          setLocation(`/studio/itens/${cloned.id}`);
        },
        onError: (err: any) => {
          toast({ title: "Falha ao clonar", description: err.message, variant: "destructive" });
        },
      }
    );
  };

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-4">
        <Skeleton className="h-8 w-32 bg-card" />
        <Skeleton className="h-64 w-full bg-card rounded-xl" />
      </div>
    );
  }

  if (!item) {
    return (
      <div className="max-w-3xl mx-auto text-center mt-16">
        <h2 className="text-xl font-bold font-mono uppercase">Artefato Não Encontrado</h2>
        <p className="text-muted-foreground mt-2 text-sm">Este artefato não existe ou foi destruído.</p>
        <Link href="/studio/arsenal">
          <Button className="mt-6 font-mono uppercase" variant="outline">Voltar ao Arsenal</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <Link href="/studio/arsenal" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground font-mono uppercase tracking-wider transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" /> Arsenal
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6 rounded-xl bg-card border border-border/50 relative overflow-hidden"
      >
        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <TypeBadge type={item.type} />
              <RarityBadge rarity={item.rarity} />
            </div>
            <h1 className="text-2xl font-black tracking-wide text-foreground">{item.name}</h1>
            <p className="text-xs text-muted-foreground font-mono">#{item.id.toString().padStart(4, "0")} · Criado em {new Date(item.createdAt).toLocaleDateString("pt-BR")}</p>
          </div>

          <div className="flex gap-2 flex-shrink-0">
            <Button
              size="sm"
              variant="outline"
              onClick={handleClone}
              disabled={cloneItem.isPending}
            >
              {cloneItem.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Copy className="w-4 h-4" />}
              <span className="ml-1.5">Clonar</span>
            </Button>
            <Button
              size="sm"
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteItem.isPending}
            >
              {deleteItem.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
              <span className="ml-1.5">Destruir</span>
            </Button>
          </div>
        </div>

        {item.description && (
          <div className="p-4 rounded-xl bg-black/30 border border-border/30 mb-4">
            <p className="text-sm text-muted-foreground leading-relaxed">{item.description}</p>
          </div>
        )}

        {item.metadata && Object.keys(item.metadata).length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground/60">Metadados</p>
            <div className="p-3 rounded-xl bg-black/20 border border-border/20">
              <pre className="text-xs text-muted-foreground font-mono overflow-auto">
                {JSON.stringify(item.metadata, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
