import { useListThemes, useCreateTheme, ThemeRarity } from "@workspace/api-client-react";
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
import { Plus, Layers } from "lucide-react";
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
  layoutStyle: z.string().min(2, "Estilo de layout obrigatório"),
  colors: z.string().min(2, "Cores obrigatórias"),
});

export default function Themes() {
  const { data: themes, isLoading, refetch } = useListThemes();
  const createTheme = useCreateTheme();
  const [open, setOpen] = useState(false);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      rarity: "Common",
      layoutStyle: "moderno",
      colors: "#000000,#ffffff",
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createTheme.mutate({
      data: {
        name: values.name,
        rarity: values.rarity as any,
        layoutStyle: values.layoutStyle,
        colors: values.colors.split(",").map(c => c.trim()),
      }
    }, {
      onSuccess: () => {
        toast({ title: "Fragmento Forjado", description: "Novo fragmento visual adicionado ao arsenal." });
        setOpen(false);
        form.reset();
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Falha ao forjar", description: err.message, variant: "destructive" });
      }
    });
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8">
      <div className="flex justify-between items-start md:items-end gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl md:text-3xl font-bold font-mono uppercase tracking-widest text-foreground flex items-center gap-2">
            <Layers className="w-6 h-6 md:w-8 md:h-8 text-primary" /> Fragmentos
          </h1>
          <p className="text-muted-foreground text-sm">Forje estilos visuais para equipar em suas missões.</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="font-mono uppercase tracking-wider text-xs md:text-sm shrink-0">
              <Plus className="w-4 h-4 mr-1.5" /> Forjar
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border w-[95vw] max-w-[425px] rounded-xl">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-wider text-lg">Forjar Fragmento</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Nome do Fragmento</FormLabel>
                      <FormControl>
                        <Input placeholder="ex: Vazio Abissal" className="bg-background" {...field} />
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
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Raridade</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger className="bg-background">
                            <SelectValue placeholder="Selecionar" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {Object.values(ThemeRarity).map(r => (
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
                  name="layoutStyle"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Paradigma de Layout</FormLabel>
                      <FormControl>
                        <Input placeholder="ex: bento, grade, padrão" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="colors"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Paleta de Cores (separadas por vírgula)</FormLabel>
                      <FormControl>
                        <Input placeholder="#000,#fff,#f0f0f0" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button type="submit" disabled={createTheme.isPending} className="w-full font-mono uppercase tracking-wider">
                  {createTheme.isPending ? "Forjando..." : "Confirmar Forja"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-lg bg-card" />
          ))}
        </div>
      ) : themes && themes.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-6">
          {themes.map(theme => (
            <div key={theme.id} className={`p-4 border rounded-md bg-card rarity-${theme.rarity} relative overflow-hidden group`}>
              <div className="flex justify-between items-start mb-3">
                <div className="flex gap-1.5">
                  {theme.colors.slice(0, 3).map((c, i) => (
                    <div key={i} className="w-4 h-4 rounded-full border border-border" style={{ backgroundColor: c }} />
                  ))}
                </div>
                <RarityBadge rarity={theme.rarity} />
              </div>
              <h3 className="font-bold text-sm">{theme.name}</h3>
              <p className="text-[10px] text-muted-foreground font-mono mt-1 uppercase tracking-wider">Layout: {theme.layoutStyle}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="h-56 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest text-sm">Nenhum fragmento forjado.</p>
        </div>
      )}
    </div>
  );
}
