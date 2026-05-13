import { useState } from "react";
import { useListAgents, useCreateAgent } from "@workspace/api-client-react";
import { RarityBadge } from "@/components/ui-rpg";
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
import { Plus, Cpu } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const formSchema = z.object({
  name: z.string().min(2, "Nome obrigatório"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  behavior: z.string().min(2, "Comportamento obrigatório"),
  promptBase: z.string().min(10, "Prompt base obrigatório"),
  description: z.string().optional(),
});

const rarityColors: Record<string, string> = {
  Common: "border-gray-500/40",
  Rare: "border-blue-500/40",
  Epic: "border-purple-500/40",
  Legendary: "border-amber-500/50 shadow-[0_0_20px_rgba(245,158,11,0.15)]",
};

export default function Agents() {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();
  const { data: agents, isLoading, refetch } = useListAgents();
  const createAgent = useCreateAgent();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", rarity: "Common", behavior: "assistente", promptBase: "", description: "" },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createAgent.mutate(
      { data: { name: values.name, rarity: values.rarity as any, behavior: values.behavior, promptBase: values.promptBase, description: values.description } },
      {
        onSuccess: () => {
          toast({ title: "Entidade Invocada!", description: "Nova entidade adicionada ao sistema." });
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

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-primary/60 mb-1">// Studio</p>
          <h1 className="text-2xl font-black uppercase tracking-widest text-foreground flex items-center gap-2">
            <Cpu className="w-6 h-6 text-primary" /> Entidades
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Invoque e configure IAs companheiras.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="flex-shrink-0"><Plus className="w-4 h-4 mr-1" /> Invocar</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-widest">Nova Entidade</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mt-2">
                <FormField control={form.control} name="name" render={({ field }) => (
                  <FormItem><FormLabel>Nome</FormLabel><FormControl><Input placeholder="Nome da entidade" {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <div className="grid grid-cols-2 gap-3">
                  <FormField control={form.control} name="rarity" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Raridade</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          {["Common", "Rare", "Epic", "Legendary"].map((r) => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="behavior" render={({ field }) => (
                    <FormItem><FormLabel>Comportamento</FormLabel><FormControl><Input placeholder="assistente" {...field} /></FormControl><FormMessage /></FormItem>
                  )} />
                </div>
                <FormField control={form.control} name="promptBase" render={({ field }) => (
                  <FormItem><FormLabel>Prompt Base</FormLabel><FormControl><Textarea placeholder="Instruções base da entidade..." rows={3} {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <FormField control={form.control} name="description" render={({ field }) => (
                  <FormItem><FormLabel>Descrição (opcional)</FormLabel><FormControl><Input placeholder="Descrição..." {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <Button type="submit" disabled={createAgent.isPending} className="w-full">
                  {createAgent.isPending ? "Invocando..." : "Invocar Entidade"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </motion.div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-40 rounded-xl bg-card/40" />)}
        </div>
      ) : (agents?.length ?? 0) === 0 ? (
        <div className="text-center py-16 text-muted-foreground">
          <Cpu className="w-12 h-12 mx-auto mb-4 opacity-20" />
          <p className="font-medium">Nenhuma entidade invocada</p>
          <p className="text-sm mt-1">Crie sua primeira entidade IA.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents?.map((agent, i) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className={cn("p-5 rounded-xl bg-card/50 border transition-all", rarityColors[agent.rarity] ?? "border-border/40")}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center">
                  <Cpu className="w-5 h-5 text-primary" />
                </div>
                <RarityBadge rarity={agent.rarity} />
              </div>
              <h3 className="font-bold text-sm text-foreground mb-1">{agent.name}</h3>
              {agent.description && <p className="text-xs text-muted-foreground mb-2 line-clamp-2">{agent.description}</p>}
              <div className="flex items-center gap-2 mt-3 pt-2 border-t border-border/30">
                <span className="text-[10px] font-mono text-muted-foreground">#{agent.id.toString().padStart(4, "0")}</span>
                <span className="text-[10px] text-muted-foreground">·</span>
                <span className="text-[10px] text-muted-foreground truncate">{agent.behavior}</span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
