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
import { Plus, FolderGit2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  name: z.string().min(2, "Name is required"),
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
        toast({ title: "Project Created", description: "Your new quest has begun!" });
        setOpen(false);
        form.reset();
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Failed to create", description: err.message, variant: "destructive" });
      }
    });
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-end">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold font-mono uppercase tracking-widest text-foreground flex items-center gap-3">
            <FolderGit2 className="w-8 h-8 text-primary" /> Project Builder
          </h1>
          <p className="text-muted-foreground text-sm">Combine items into massive epic drops.</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="font-mono uppercase tracking-wider">
              <Plus className="w-4 h-4 mr-2" /> Start Quest
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-wider text-xl">Start New Quest</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Quest/Project Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Website V2" className="bg-background" {...field} />
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
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Target Rarity</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger className="bg-background">
                            <SelectValue placeholder="Select rarity" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {Object.values(ProjectRarity).map(r => (
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
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Description</FormLabel>
                      <FormControl>
                        <Input placeholder="What is the goal?" className="bg-background" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="pt-4 flex justify-end">
                  <Button type="submit" disabled={createProject.isPending} className="w-full font-mono uppercase tracking-wider">
                    {createProject.isPending ? "Starting..." : "Begin Quest"}
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-lg bg-card" />
          ))}
        </div>
      ) : projects && projects.length > 0 ? (
        <div className="space-y-4">
          {projects.map(project => (
            <div key={project.id} className={`p-6 border rounded-md bg-card rarity-${project.rarity} relative flex items-center justify-between`}>
               <div>
                 <div className="flex items-center gap-3 mb-2">
                   <h3 className="font-bold text-xl">{project.name}</h3>
                   <RarityBadge rarity={project.rarity} />
                   <span className="px-2 py-0.5 text-[10px] uppercase font-bold rounded-sm border bg-background text-muted-foreground">
                     {project.status}
                   </span>
                 </div>
                 <p className="text-sm text-muted-foreground">{project.description || "No description provided."}</p>
               </div>
               
               <div className="flex gap-4 items-center">
                 <div className="flex flex-col items-end">
                   <span className="text-xs text-muted-foreground font-mono uppercase">Agents</span>
                   <span className="font-mono">{project.agentIds?.length || 0}</span>
                 </div>
                 <div className="flex flex-col items-end">
                   <span className="text-xs text-muted-foreground font-mono uppercase">Skills</span>
                   <span className="font-mono">{project.skillIds?.length || 0}</span>
                 </div>
                 <Button variant="outline" className="ml-4 font-mono uppercase tracking-widest text-xs">
                   Enter
                 </Button>
               </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="h-64 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest">No active quests.</p>
        </div>
      )}
    </div>
  );
}
