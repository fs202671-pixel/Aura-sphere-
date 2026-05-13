import { useListSkills, useCreateSkill, SkillRarity } from "@workspace/api-client-react";
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
import { Plus, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const raridadeLabels: Record<string, string> = {
  Common: "Comum",
  Rare: "Raro",
  Epic: "Épico",
  Legendary: "Lendário",
};

const formSchema = z.object({
  name: z.string().min(2, "Nome obrigatório"),
  category: z.string().min(2, "Categoria obrigatória"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  description: z.string().min(5, "Descrição obrigatória"),
});

export default function Skills() {
  const { data: skills, isLoading, refetch } = useListSkills();
  const createSkill = useCreateSkill();
  const [open, setOpen] = useState(false);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      category: "combate",
      rarity: "Common",
      description: "",
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createSkill.mutate({
      data: {
        name: values.name,
        rarity: values.rarity as any,
        category: values.category,
        description: values.description,
      }
    }, {
      onSuccess: () => {
        toast({ title: "Protocolo Instalado", description: "Novo protocolo carregado no sistema CAOS." });
        setOpen(false);
        form.reset();
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Falha na instalação", description: err.message, variant: "destructive" });
      }
    });
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8">
      <div className="flex justify-between items-start md:items-end gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl md:text-3xl font-bold font-mono uppercase tracking-widest text-foreground flex items-center gap-2">
            <Zap className="w-6 h-6 md:w-8 md:h-8 text-primary" /> Protocolos
          </h1>
          <p className="text-muted-foreground text-sm">Módulos instaláveis que potencializam missões e entidades.</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="font-mono uppercase tracking-wider text-xs md:text-sm shrink-0">
              <Plus className="w-4 h-4 mr-1.5" /> Instalar
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border w-[95vw] max-w-[425px] rounded-xl">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-wider text-lg">Instalar Protocolo</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Nome do Protocolo</FormLabel>
                      <FormControl>
                        <Input placeholder="ex: Leitor de Arquivos" className="bg-background" {...field} />
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
                            {Object.values(SkillRarity).map(r => (
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
                    name="category"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Categoria</FormLabel>
                        <FormControl>
                          <Input placeholder="ex: análise" className="bg-background" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Descrição</FormLabel>
                      <FormControl>
                        <Input placeholder="O que esse protocolo executa?" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button type="submit" disabled={createSkill.isPending} className="w-full font-mono uppercase tracking-wider">
                  {createSkill.isPending ? "Instalando..." : "Confirmar Instalação"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 md:gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-lg bg-card" />
          ))}
        </div>
      ) : skills && skills.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 md:gap-4">
          {skills.map(skill => (
            <div key={skill.id} className={`p-3 border rounded-md bg-card rarity-${skill.rarity} relative flex flex-col justify-between hover:-translate-y-1 transition-transform`}>
              <div className="flex justify-between items-start mb-2">
                <div className="p-1.5 rounded bg-background border border-border">
                  <Zap className="w-3.5 h-3.5 text-primary" />
                </div>
                <RarityBadge rarity={skill.rarity} />
              </div>
              <div>
                <h3 className="font-bold text-xs leading-tight">{skill.name}</h3>
                <p className="text-[10px] text-muted-foreground font-mono mt-1 uppercase tracking-wider">{skill.category}</p>
              </div>
              <div className="mt-1.5 text-[10px] text-muted-foreground line-clamp-2">
                {skill.description}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="h-56 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest text-sm">Nenhum protocolo instalado.</p>
        </div>
      )}
    </div>
  );
}
