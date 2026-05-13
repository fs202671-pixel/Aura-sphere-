import { useState } from "react";
import { useListProjects, useCreateProject } from "@workspace/api-client-react";
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
import { Plus, Map, Clock } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const statusLabels: Record<string, string> = {
  draft: "Rascunho",
  building: "Em Construção",
  complete: "Concluída",
  archived: "Arquivada",
};

const statusColors: Record<string, string> = {
  draft: "text-muted-foreground",
  building: "text-blue-400",
  complete: "text-green-400",
  archived: "text-muted-foreground/50",
};

const formSchema = z.object({
  name: z.string().min(2, "Nome obrigatório"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  description: z.string().optional(),
});

export default function Missions() {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();
  const { data: projects, isLoading, refetch } = useListProjects();
  const createProject = useCreateProject();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", rarity: "Common", description: "" },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createProject.mutate(
      { data: { name: values.name, rarity: values.rarity as any, description: values.description } },
      {
        onSuccess: () => {
          toast({ title: "Missão Iniciada!", description: "Nova missão registrada no sistema CAOS." });
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
    <div className="max-w-4xl mx-auto space-y-6">
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-amber-400/60 mb-1">// Studio</p>
          <h1 className="text-2xl font-black uppercase tracking-widest text-foreground flex items-center gap-2">
            <Map className="w-6 h-6 text-amber-400" /> Missões
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Projetos e objetivos do universo CAOS.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="flex-shrink-0"><Plus className="w-4 h-4 mr-1" /> Iniciar</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-widest">Nova Missão</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mt-2">
                <FormField control={form.control} name="name" render={({ field }) => (
                  <FormItem><FormLabel>Nome da Missão</FormLabel><FormControl><Input placeholder="Nome" {...field} /></FormControl><FormMessage /></FormItem>
                )} />
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
                <FormField control={form.control} name="description" render={({ field }) => (
                  <FormItem><FormLabel>Descrição (opcional)</FormLabel><FormControl><Textarea placeholder="Objetivo da missão..." rows={3} {...field} /></FormControl><FormMessage /></FormItem>
                )} />
                <Button type="submit" disabled={createProject.isPending} className="w-full">
                  {createProject.isPending ? "Iniciando..." : "Iniciar Missão"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </motion.div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-xl bg-card/40" />)}
        </div>
      ) : (projects?.length ?? 0) === 0 ? (
        <div className="text-center py-16 text-muted-foreground">
          <Map className="w-12 h-12 mx-auto mb-4 opacity-20" />
          <p className="font-medium">Nenhuma missão iniciada</p>
          <p className="text-sm mt-1">Inicie sua primeira missão CAOS.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {projects?.map((project, i) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06 }}
              className="p-4 rounded-xl bg-card/50 border border-border/40 hover:border-amber-500/30 transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Map className="w-5 h-5 text-amber-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h3 className="font-bold text-sm text-foreground truncate">{project.name}</h3>
                    <RarityBadge rarity={project.rarity} />
                    <span className={cn("text-[10px] font-mono", statusColors[project.status] ?? "text-muted-foreground")}>
                      {statusLabels[project.status] ?? project.status}
                    </span>
                  </div>
                  {project.description && (
                    <p className="text-xs text-muted-foreground line-clamp-2">{project.description}</p>
                  )}
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-[10px] font-mono text-muted-foreground/60">#{project.id.toString().padStart(4, "0")}</span>
                    <span className="flex items-center gap-1 text-[10px] text-muted-foreground/60">
                      <Clock className="w-3 h-3" />
                      {new Date(project.createdAt).toLocaleDateString("pt-BR")}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
