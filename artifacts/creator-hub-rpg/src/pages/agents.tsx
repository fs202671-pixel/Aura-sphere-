import { useListAgents, useCreateAgent, AgentRarity } from "@workspace/api-client-react";
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
import { useState } from "react";
import { Plus, Cpu } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const raridadeLabels: Record<string, string> = {
  Common: "Comum",
  Rare: "Raro",
  Epic: "Épico",
  Legendary: "Lendário",
};

const formSchema = z.object({
  name: z.string().min(2, "Nome obrigatório"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  behavior: z.string().min(2, "Comportamento obrigatório"),
  promptBase: z.string().min(10, "Prompt base obrigatório"),
  description: z.string().optional(),
});

export default function Agents() {
  const { data: agents, isLoading, refetch } = useListAgents();
  const createAgent = useCreateAgent();
  const [open, setOpen] = useState(false);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      rarity: "Common",
      behavior: "assistente",
      promptBase: "",
      description: "",
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createAgent.mutate({
      data: {
        name: values.name,
        rarity: values.rarity as any,
        behavior: values.behavior,
        promptBase: values.promptBase,
        description: values.description,
      }
    }, {
      onSuccess: () => {
        toast({ title: "Entidade Invocada", description: "Nova entidade CAOS adicionada ao sistema." });
        setOpen(false);
        form.reset();
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Falha na invocação", description: err.message, variant: "destructive" });
      }
    });
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8">
      <div className="flex justify-between items-start md:items-end gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl md:text-3xl font-bold font-mono uppercase tracking-widest text-foreground flex items-center gap-2">
            <Cpu className="w-6 h-6 md:w-8 md:h-8 text-primary" /> Entidades
          </h1>
          <p className="text-muted-foreground text-sm">Invoque e configure IAs companheiras do CAOS.</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="font-mono uppercase tracking-wider text-xs md:text-sm shrink-0">
              <Plus className="w-4 h-4 mr-1.5" /> Invocar
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border w-[95vw] max-w-[500px] rounded-xl">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-wider text-lg">Invocar Nova Entidade</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Nome da Entidade</FormLabel>
                      <FormControl>
                        <Input placeholder="ex: Sentinela do Código" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-2 gap-3">
                  <FormField
                    control={form.control}
                    name="rarity"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Raridade</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger className="bg-background">
                              <SelectValue placeholder="Selecionar" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {Object.values(AgentRarity).map(r => (
                              <SelectItem key={r} value={r}>{raridadeLabels[r] ?? r}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="behavior"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Comportamento</FormLabel>
                        <FormControl>
                          <Input placeholder="ex: analítico, criativo" className="bg-background" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="promptBase"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Prompt Base</FormLabel>
                      <FormControl>
                        <Textarea placeholder="Você é uma entidade CAOS que..." className="bg-background min-h-[90px]" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button type="submit" disabled={createAgent.isPending} className="w-full font-mono uppercase tracking-wider">
                  {createAgent.isPending ? "Invocando..." : "Confirmar Invocação"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-lg bg-card" />
          ))}
        </div>
      ) : agents && agents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map(agent => (
            <div key={agent.id} className={`p-4 border rounded-md bg-card rarity-${agent.rarity} relative overflow-hidden flex flex-col min-h-[160px]`}>
              <div className="flex justify-between items-start mb-2">
                <Cpu className="w-5 h-5 text-muted-foreground" />
                <RarityBadge rarity={agent.rarity} />
              </div>
              <h3 className="font-bold text-base">{agent.name}</h3>
              <p className="text-xs text-muted-foreground font-mono mt-1 mb-2">Modo: {agent.behavior}</p>
              <div className="flex-1" />
              <div className="text-[10px] bg-background/50 p-2 rounded border border-border/50 text-muted-foreground font-mono truncate">
                {agent.promptBase}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="h-56 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest text-sm">Nenhuma entidade invocada.</p>
        </div>
      )}
    </div>
  );
}
