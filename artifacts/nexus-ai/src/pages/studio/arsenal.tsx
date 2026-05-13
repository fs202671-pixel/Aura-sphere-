import { useState } from "react";
import { useListItems, useCreateItem, useGetItemStats, ItemType, ItemRarity } from "@workspace/api-client-react";
import { ItemCard } from "@/components/ui-rpg";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { motion } from "framer-motion";
import { Plus, Shield, Search } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const tipoLabels: Record<string, string> = {
  design: "Design",
  theme: "Fragmento",
  agent: "Entidade",
  skill: "Protocolo",
  project: "Missão",
  component: "Componente",
};

const formSchema = z.object({
  name: z.string().min(2, "Nome obrigatório"),
  type: z.enum(["design", "theme", "agent", "skill", "project", "component"]).default("design"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  description: z.string().optional(),
});

export default function Arsenal() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<string | null>(null);
  const { toast } = useToast();

  const { data: items, isLoading, refetch } = useListItems({ type: typeFilter as any ?? undefined });
  const createItem = useCreateItem();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", type: "design", rarity: "Common", description: "" },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createItem.mutate(
      { data: { name: values.name, type: values.type as any, rarity: values.rarity as any, description: values.description } },
      {
        onSuccess: () => {
          toast({ title: "Artefato Criado!", description: "Novo artefato adicionado ao arsenal." });
          setOpen(false);
          form.reset();
          refetch();
        },
        onError: (err: any) => {
          toast({ title: "Erro", description: err.message, variant: "destructive" });
        },
      }
    );
  };

  const filtered = items?.filter((i) =>
    search ? i.name.toLowerCase().includes(search.toLowerCase()) : true
  );

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-blue-400/60 mb-1">// Studio</p>
          <h1 className="text-2xl font-black uppercase tracking-widest text-foreground flex items-center gap-2">
            <Shield className="w-6 h-6 text-blue-400" /> Arsenal
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Todos os artefatos do seu inventário criativo.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="flex-shrink-0">
              <Plus className="w-4 h-4 mr-1" /> Criar
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-widest">Novo Artefato</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mt-2">
                <FormField control={form.control} name="name" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome</FormLabel>
                    <FormControl><Input placeholder="Nome do artefato" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <div className="grid grid-cols-2 gap-3">
                  <FormField control={form.control} name="type" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tipo</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          {Object.entries(tipoLabels).map(([v, l]) => (
                            <SelectItem key={v} value={v}>{l}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="rarity" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Raridade</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          {["Common", "Rare", "Epic", "Legendary"].map((r) => (
                            <SelectItem key={r} value={r}>{r}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>
                <FormField control={form.control} name="description" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Descrição</FormLabel>
                    <FormControl><Textarea placeholder="Descrição opcional..." rows={3} {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <Button type="submit" disabled={createItem.isPending} className="w-full">
                  {createItem.isPending ? "Criando..." : "Criar Artefato"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </motion.div>

      {/* Filters */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar artefatos..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-card/40 border border-border/40 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50 transition-colors"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setTypeFilter(null)}
            className={cn("px-3 py-1.5 rounded-lg text-xs font-medium border transition-all", typeFilter === null ? "bg-primary/20 border-primary/40 text-primary" : "border-border/40 text-muted-foreground hover:text-foreground")}
          >
            Todos
          </button>
          {Object.entries(tipoLabels).map(([v, l]) => (
            <button
              key={v}
              onClick={() => setTypeFilter(v === typeFilter ? null : v)}
              className={cn("px-3 py-1.5 rounded-lg text-xs font-medium border transition-all", typeFilter === v ? "bg-primary/20 border-primary/40 text-primary" : "border-border/40 text-muted-foreground hover:text-foreground")}
            >
              {l}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-xl bg-card/40" />
          ))}
        </div>
      ) : (filtered?.length ?? 0) === 0 ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16 text-muted-foreground">
          <Shield className="w-12 h-12 mx-auto mb-4 opacity-20" />
          <p className="font-medium">Arsenal vazio</p>
          <p className="text-sm mt-1">Crie seu primeiro artefato para começar.</p>
        </motion.div>
      ) : (
        <motion.div layout className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filtered?.map((item, i) => (
            <motion.div key={item.id} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.04 }}>
              <ItemCard item={item} studioBase="/studio" />
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
