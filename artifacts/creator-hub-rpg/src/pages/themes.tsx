import { useListThemes, useCreateTheme, ThemeRarity } from "@workspace/api-client-react";
import { ItemCard, RarityBadge } from "@/components/ui-rpg";
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
import { Plus, Palette } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  name: z.string().min(2, "Name is required"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  layoutStyle: z.string().min(2, "Layout style required"),
  colors: z.string().min(2, "Colors required"),
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
      layoutStyle: "modern",
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
        toast({ title: "Theme Forged successfully", description: "Your new theme has dropped!" });
        setOpen(false);
        form.reset();
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Failed to forge theme", description: err.message, variant: "destructive" });
      }
    });
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-end">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold font-mono uppercase tracking-widest text-foreground flex items-center gap-3">
            <Palette className="w-8 h-8 text-primary" /> Theme Engine
          </h1>
          <p className="text-muted-foreground text-sm">Forge visual styles to equip on your projects.</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="font-mono uppercase tracking-wider">
              <Plus className="w-4 h-4 mr-2" /> Forge Theme
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-wider text-xl">Forge New Theme</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Theme Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Abyssal Void" className="bg-background" {...field} />
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
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Rarity</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger className="bg-background">
                            <SelectValue placeholder="Select rarity" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {Object.values(ThemeRarity).map(r => (
                            <SelectItem key={r} value={r}>{r}</SelectItem>
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
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Layout Paradigm</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. bento, masonry, standard" className="bg-background" {...field} />
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
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Color Palette (comma separated)</FormLabel>
                      <FormControl>
                        <Input placeholder="#000,#fff,#f0f0f0" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="pt-4 flex justify-end">
                  <Button type="submit" disabled={createTheme.isPending} className="w-full font-mono uppercase tracking-wider">
                    {createTheme.isPending ? "Forging..." : "Craft Theme"}
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-48 rounded-lg bg-card" />
          ))}
        </div>
      ) : themes && themes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {themes.map(theme => (
            <div key={theme.id} className={`p-4 border rounded-md bg-card rarity-${theme.rarity} relative overflow-hidden group`}>
               <div className="flex justify-between items-start mb-4">
                 <div className="flex gap-2">
                   {theme.colors.slice(0,3).map((c, i) => (
                     <div key={i} className="w-4 h-4 rounded-full border border-border" style={{ backgroundColor: c }} />
                   ))}
                 </div>
                 <RarityBadge rarity={theme.rarity} />
               </div>
               <h3 className="font-bold text-lg">{theme.name}</h3>
               <p className="text-xs text-muted-foreground font-mono mt-1">Layout: {theme.layoutStyle}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="h-64 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest">No themes forged.</p>
        </div>
      )}
    </div>
  );
}
