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
import { Plus, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  name: z.string().min(2, "Name is required"),
  category: z.string().min(2, "Category is required"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  description: z.string().min(5, "Description required"),
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
      category: "combat",
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
        toast({ title: "Skill Learned", description: "New skill added to spellbook!" });
        setOpen(false);
        form.reset();
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Failed to learn", description: err.message, variant: "destructive" });
      }
    });
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-end">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold font-mono uppercase tracking-widest text-foreground flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-primary" /> Skill System
          </h1>
          <p className="text-muted-foreground text-sm">Pluggable modules to empower your projects and agents.</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="font-mono uppercase tracking-wider">
              <Plus className="w-4 h-4 mr-2" /> Learn Skill
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-wider text-xl">Learn New Skill</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Skill Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. File Reader" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="grid grid-cols-2 gap-4">
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
                            {Object.values(SkillRarity).map(r => (
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
                    name="category"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Category</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g. utility" className="bg-background" {...field} />
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
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Description</FormLabel>
                      <FormControl>
                        <Input placeholder="What does it do?" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="pt-4 flex justify-end">
                  <Button type="submit" disabled={createSkill.isPending} className="w-full font-mono uppercase tracking-wider">
                    {createSkill.isPending ? "Learning..." : "Learn Skill"}
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-lg bg-card" />
          ))}
        </div>
      ) : skills && skills.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {skills.map(skill => (
            <div key={skill.id} className={`p-4 border rounded-md bg-card rarity-${skill.rarity} relative flex flex-col justify-between hover:-translate-y-1 transition-transform`}>
               <div className="flex justify-between items-start mb-2">
                 <div className="p-2 rounded bg-background border border-border">
                   <Sparkles className="w-4 h-4 text-primary" />
                 </div>
               </div>
               <div>
                 <h3 className="font-bold text-sm leading-tight">{skill.name}</h3>
                 <p className="text-[10px] text-muted-foreground font-mono mt-1 uppercase tracking-wider">{skill.category}</p>
               </div>
               <div className="mt-2 text-[10px] text-muted-foreground line-clamp-2">
                 {skill.description}
               </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="h-64 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest">No skills in spellbook.</p>
        </div>
      )}
    </div>
  );
}
