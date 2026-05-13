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
import { Plus, Bot } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  name: z.string().min(2, "Name is required"),
  rarity: z.enum(["Common", "Rare", "Epic", "Legendary"]).default("Common"),
  behavior: z.string().min(2, "Behavior required"),
  promptBase: z.string().min(10, "Base prompt required"),
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
      behavior: "helpful",
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
        toast({ title: "Agent Summoned", description: "Your new agent has dropped!" });
        setOpen(false);
        form.reset();
        refetch();
      },
      onError: (err: any) => {
        toast({ title: "Failed to summon", description: err.message, variant: "destructive" });
      }
    });
  };

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-end">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold font-mono uppercase tracking-widest text-foreground flex items-center gap-3">
            <Bot className="w-8 h-8 text-primary" /> IA Builder
          </h1>
          <p className="text-muted-foreground text-sm">Summon and configure AI companions.</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="font-mono uppercase tracking-wider">
              <Plus className="w-4 h-4 mr-2" /> Summon Agent
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle className="font-mono uppercase tracking-wider text-xl">Summon New Agent</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Agent Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Code Wizard" className="bg-background" {...field} />
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
                            {Object.values(AgentRarity).map(r => (
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
                    name="behavior"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="font-mono text-xs uppercase text-muted-foreground">Behavior</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g. strict, creative" className="bg-background" {...field} />
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
                      <FormLabel className="font-mono text-xs uppercase text-muted-foreground">System Prompt</FormLabel>
                      <FormControl>
                        <Textarea placeholder="You are a helpful assistant..." className="bg-background min-h-[100px]" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="pt-4 flex justify-end">
                  <Button type="submit" disabled={createAgent.isPending} className="w-full font-mono uppercase tracking-wider">
                    {createAgent.isPending ? "Summoning..." : "Summon Agent"}
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-48 rounded-lg bg-card" />
          ))}
        </div>
      ) : agents && agents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map(agent => (
            <div key={agent.id} className={`p-5 border rounded-md bg-card rarity-${agent.rarity} relative overflow-hidden flex flex-col h-[200px]`}>
               <div className="flex justify-between items-start mb-2">
                 <Bot className="w-6 h-6 text-muted-foreground" />
                 <RarityBadge rarity={agent.rarity} />
               </div>
               <h3 className="font-bold text-lg">{agent.name}</h3>
               <p className="text-xs text-muted-foreground font-mono mt-1 mb-2">Behavior: {agent.behavior}</p>
               <div className="flex-1" />
               <div className="text-[10px] bg-background/50 p-2 rounded border border-border/50 text-muted-foreground font-mono truncate">
                 {agent.promptBase}
               </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="h-64 border border-dashed border-border rounded-lg flex flex-col items-center justify-center bg-card/20 gap-4">
          <p className="text-muted-foreground font-mono uppercase tracking-widest">No agents summoned.</p>
        </div>
      )}
    </div>
  );
}
