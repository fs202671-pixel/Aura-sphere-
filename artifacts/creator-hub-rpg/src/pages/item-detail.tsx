import { useParams } from "wouter";
import { useGetItem, useDeleteItem } from "@workspace/api-client-react";
import { RarityBadge, TypeBadge } from "@/components/ui-rpg";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Trash2, Copy, ArrowLeft } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useToast } from "@/hooks/use-toast";

export default function ItemDetail() {
  const params = useParams();
  const id = Number(params.id);
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const { data: item, isLoading } = useGetItem(id, { query: { enabled: !!id } });
  const deleteItem = useDeleteItem();

  const handleDelete = () => {
    deleteItem.mutate({ id }, {
      onSuccess: () => {
        toast({ title: "Item Destroyed", description: "The item has been removed from your inventory." });
        setLocation("/library");
      },
      onError: (err: any) => {
        toast({ title: "Failed to destroy", description: err.message, variant: "destructive" });
      }
    });
  };

  if (isLoading) {
    return (
      <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-8 w-32 bg-card" />
        <Skeleton className="h-64 w-full bg-card rounded-lg" />
      </div>
    );
  }

  if (!item) {
    return (
      <div className="p-6 md:p-8 max-w-4xl mx-auto text-center mt-20">
        <h2 className="text-2xl font-bold font-mono uppercase">Item Not Found</h2>
        <p className="text-muted-foreground mt-2">This artifact does not exist or was destroyed.</p>
        <Link href="/library">
          <Button className="mt-6 font-mono uppercase">Back to Vault</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6">
      <Link href="/library" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground font-mono uppercase tracking-wider transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Vault
      </Link>

      <div className={`border rounded-lg bg-card rarity-${item.rarity} relative overflow-hidden`}>
        {item.rarity === "Legendary" && (
          <div className="absolute inset-0 legendary-shimmer pointer-events-none opacity-20" />
        )}
        
        <div className="p-8 relative z-10">
          <div className="flex justify-between items-start mb-6">
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <TypeBadge type={item.type} />
                <RarityBadge rarity={item.rarity} />
              </div>
              <h1 className="text-4xl font-bold tracking-tight text-foreground">{item.name}</h1>
              <p className="text-sm text-muted-foreground font-mono">
                ID: {item.id.toString().padStart(4, "0")} • Forged: {new Date(item.createdAt).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="prose prose-invert max-w-none mt-8">
            <h3 className="font-mono uppercase tracking-widest text-sm text-muted-foreground mb-4">Item Lore</h3>
            <p className="text-lg leading-relaxed">{item.description || "No lore recorded for this artifact."}</p>
          </div>

          {item.tags && item.tags.length > 0 && (
            <div className="mt-8">
              <h3 className="font-mono uppercase tracking-widest text-sm text-muted-foreground mb-4">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {item.tags.map(tag => (
                  <span key={tag} className="px-2 py-1 bg-background border border-border rounded text-xs font-mono text-muted-foreground">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="mt-12 pt-6 border-t border-border flex gap-4">
            <Button variant="outline" className="font-mono uppercase tracking-wider">
              <Copy className="w-4 h-4 mr-2" /> Clone
            </Button>
            <Button variant="destructive" className="font-mono uppercase tracking-wider" onClick={handleDelete} disabled={deleteItem.isPending}>
              <Trash2 className="w-4 h-4 mr-2" /> {deleteItem.isPending ? "Destroying..." : "Destroy"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
