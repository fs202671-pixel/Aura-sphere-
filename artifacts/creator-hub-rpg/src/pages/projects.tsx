import { useListProjects, useCreateProject, ProjectRarity } from "@workspace/api-client-react";
import { RarityBadge } from "@/components/ui-rpg";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useState } from "react";
import { Plus, Map } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const raridadeLabels: Record<string, string> = {
  Common: "Comum",
  Rare: "Raro",
  Epic: "Épico",
  Legendary: "Lendário",
};

const statusLabels: Record<string, string> = {
  draft: "Rascunho",
  building: "Construindo",
  complete: "Concluída",
  archived: "Arquivada",
};

const formSchema = z.object({
  name: z.string().min(2, "Nome obrigatório"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  description: z.string().optional(),
});

export default function Projects() {
  const { data: projects, isLoading, refetch } = useListProjects();
  const createProject = useCreateProject();
  const [open, setOpen] = useState(false);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      rarity: "Common",
      description: "",
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createProject.mutate({
      data: {
        name: values.name,
        rarity: values.rarity as any,
        description: values.description,
      }
    }, {
      onSuccess: () => {
        toast({ title: "Missão Iniciada", description: "Nova missão CAOS registrada no sistema." });
        setOpen(false);
        form.reset();
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Falha ao iniciar", description: err.message, variant: "destructive" });
      }
    });
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8">
      <div className="flex justify-between items-start md:items-end gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl md:text-3xl font-bold font-mono uppercase tracking-widest text-foreground flex items-center gap-2">
            <Map className="w-6 h-6 md:w-8 md:h-8 text-primary" /> Missões
          </h1>
          <p className="text-muted-foreground text-sm">Combine artefatos em drops épicos finais.</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="font-mono uppercase tracking-wider text-xs md:text-sm shrink-0">
              <Plus className="w-4 h-4 mr-1.5" /> Nova Missão
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border w-[95vw] max-w-[425px] rounded-xl">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-wider text-lg">Iniciar Nova Missão</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Nome da Missão</FormLabel>
                      <FormControl>
                        <Input placeholder="ex: Operação Nexus V2" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="rarity"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Raridade Alvo</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger className="bg-background">
                            <SelectValue placeholder="Selecionar" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {Object.values(ProjectRarity).map(r => (
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
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Objetivo</FormLabel>
                      <FormControl>
                        <Input placeholder="Qual é o objetivo desta missão?" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button type="submit" disabled={createProject.isPending} className="w-full font-mono uppercase tracking-wider">
                  {createProject.isPending ? "Iniciando..." : "Confirmar Missão"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full rounded-lg bg-card" />
          ))}
        </div>
      ) : projects && projects.length > 0 ? (
        <div className="space-y-3">
          {projects.map(project => (
            <div key={project.id} className={`p-4 md:p-6 border rounded-md bg-card rarity-${project.rarity} relative`}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <h3 className="font-bold text-base">{project.name}</h3>
                    <RarityBadge rarity={project.rarity} />
                    <span className="px-2 py-0.5 text-[10px] uppercase font-bold rounded-sm border bg-background text-muted-foreground">
                      {statusLabels[project.status] ?? project.status}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{project.description || "Sem descrição definida."}</p>
                </div>

                <div className="flex flex-col md:flex-row items-end md:items-center gap-3 shrink-0">
                  <div className="hidden md:flex gap-4">
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] text-muted-foreground font-mono uppercase">Entidades</span>
                      <span className="font-mono text-sm">{project.agentIds?.length || 0}</span>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] text-muted-foreground font-mono uppercase">Protocolos</span>
                      <span className="font-mono text-sm">{project.skillIds?.length || 0}</span>
                    </div>
                  </div>
                  <Button variant="outline" className="font-mono uppercase tracking-widest text-xs h-8 px-3">
                    Acessar
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="h-56 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest text-sm">Nenhuma missão ativa.</p>
        </div>
      )}
    </div>
  );
}
