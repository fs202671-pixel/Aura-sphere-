import { useState } from "react";
import { useListThemes, useCreateTheme } from "@workspace/api-client-react";
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
import { motion } from "framer-motion";
import { Plus, Layers } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const formSchema = z.object({
  name: z.string().min(2, "Nome obrigatório"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  layoutStyle: z.string().min(2, "Estilo obrigatório"),
  colors: z.string().min(2, "Cores obrigatórias"),
});

export default function Themes() {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();
  const { data: themes, isLoading, refetch } = useListThemes();
  const createTheme = useCreateTheme();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", rarity: "Common", layoutStyle: "moderno", colors: "#6366f1,#0ea5e9" },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    createTheme.mutate(
      { data: { name: values.name, rarity: values.rarity as any, layoutStyle: values.layoutStyle, colors: values.colors.split(",").map(c => c.trim()) } },
      {
        onSuccess: () => {
          toast({ title: "Fragmento Forjado!", description: "Novo fragmento visual criado." });
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
          <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-purple-400/60 mb-1">// Studio</p>
          <h1 className="text-2xl font-black uppercase tracking-widest text-foreground flex items-center gap-2">
            <Layers className="w-6 h-6 text-purple-400" /> Fragmentos
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Temas visuais e estilos do universo CAOS.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="flex-shrink-0"><Plus className="w-4 h-4 mr-1" /> Forjar</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-widest">Novo Fragmento</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 mt-2">
                <FormField control={form.control} name="name" render={({ field }) => (
                  <FormItem><FormLabel>Nome</FormLabel><FormControl><Input placeholder="Nome do fragmento" {...field} /></FormControl><FormMessage /></FormItem>
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
                  <FormField control={form.control} name="layoutStyle" render={({ field }) => (
                    <FormItem><FormLabel>Estilo</FormLabel><FormControl><Input placeholder="moderno" {...field} /></FormControl><FormMessage /></FormItem>
                  )} />
                </div>
                <FormField control={form.control} name="colors" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cores (separadas por vírgula)</FormLabel>
                    <FormControl><Input placeholder="#6366f1,#0ea5e9" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <Button type="submit" disabled={createTheme.isPending} className="w-full">
                  {createTheme.isPending ? "Forjando..." : "Forjar Fragmento"}
                </Button>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </motion.div>

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-36 rounded-xl bg-card/40" />)}
        </div>
      ) : (themes?.length ?? 0) === 0 ? (
        <div className="text-center py-16 text-muted-foreground">
          <Layers className="w-12 h-12 mx-auto mb-4 opacity-20" />
          <p className="font-medium">Nenhum fragmento criado</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {themes?.map((theme, i) => {
            const colors = Array.isArray(theme.colors) ? theme.colors : [];
            return (
              <motion.div
                key={theme.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.05 }}
                className="p-4 rounded-xl bg-card/50 border border-border/40 hover:border-purple-500/30 transition-all"
              >
                {colors.length > 0 && (
                  <div className="flex gap-1.5 mb-3">
                    {colors.slice(0, 4).map((c, ci) => (
                      <div key={ci} className="w-6 h-6 rounded-md border border-white/10" style={{ backgroundColor: c }} />
                    ))}
                  </div>
                )}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="font-bold text-sm text-foreground truncate flex-1">{theme.name}</h3>
                  <RarityBadge rarity={theme.rarity} />
                </div>
                <p className="text-xs text-muted-foreground">{theme.layoutStyle}</p>
                <p className="text-[10px] font-mono text-muted-foreground/50 mt-2">#{theme.id.toString().padStart(4, "0")}</p>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
