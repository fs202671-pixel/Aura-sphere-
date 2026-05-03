import { useEffect, useMemo, useState } from "react";
import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ParticleSphere } from "@/components/ParticleSphere";
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarProvider, SidebarSeparator, SidebarTrigger } from "@/components/ui/sidebar";
import Chat from "@/pages/Chat";
import VisualMode from "@/pages/Visual";
import { getApiBase, getAuthHeaders } from "@/lib/api";
import { speak, getVoiceConfig } from "@/lib/speech";
import type { AiMode, ChatMessage, Project, SphereState, VoiceId } from "@/lib/types";

const AI_MODES: { id: AiMode; label: string; description: string }[] = [
  { id: "Chat", label: "Chat", description: "Converse naturalmente com a IA para ideias, respostas e ações rápidas." },
  { id: "Código", label: "Código", description: "Gere, revise e aprimore código com assistência contextual." },
  { id: "Projetos", label: "Projetos", description: "Organize tarefas, cronogramas e objetivos de desenvolvimento." },
  { id: "Memória", label: "Memória", description: "Armazene e recupere informações importantes em contexto." },
  { id: "Imagem", label: "Imagem", description: "Crie imagens rápidas com prompts inteligentes." },
  { id: "Voz", label: "Voz", description: "Fale com a IA e ajuste a assistente de voz." },
  { id: "Automação", label: "Automação", description: "Defina fluxos e rotinas para automatizar tarefas." },
  { id: "Visual", label: "Visual", description: "Personalize a aparência e interface gráfica do sistema." },
  { id: "Dev Mode", label: "Dev Mode", description: "Acesse ferramentas de desenvolvedor e informações do ambiente." },
];

const DEFAULT_PROJECTS: Project[] = [
  {
    id: "proj-1",
    name: "Assistente AI ON",
    description: "Desenvolver um sistema de IA com modos adaptativos e memória contextual.",
    status: "in-progress",
    createdAt: new Date().toISOString(),
    tasks: [
      { id: "task-1", title: "Criar sidebar de modos", completed: true },
      { id: "task-2", title: "Integrar chat e memória", completed: false },
    ],
  },
];

export default function AIOnShell({
  userId,
  aiName,
  voiceId,
  onSignOut,
  onEditProfile,
}: {
  userId: string;
  aiName: string;
  voiceId: VoiceId | string;
  onSignOut: () => void;
  onEditProfile: () => void;
}) {
  const [activeMode, setActiveMode] = useState<AiMode>("Chat");
  const [projectName, setProjectName] = useState("");
  const [projectList, setProjectList] = useState<Project[]>(DEFAULT_PROJECTS);
  const [memoryQuery, setMemoryQuery] = useState("");
  const [memoryResults, setMemoryResults] = useState<(ChatMessage & { category?: string })[]>([]);
  const [imagePrompt, setImagePrompt] = useState("");
  const [imagePreview, setImagePreview] = useState<string>("");
  const [voiceText, setVoiceText] = useState("Olá, estou testando a voz da assistente.");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [flowSteps, setFlowSteps] = useState<string[]>([
    "Enviar resumo diário ao canal de equipe",
    "Criar tarefa de acompanhamento inteligente",
  ]);

  useEffect(() => {
    if (activeMode === "Voz") {
      document.title = `AI ON • Voz`;
    }
  }, [activeMode]);

  const activeModeMeta = useMemo(
    () => AI_MODES.find((mode) => mode.id === activeMode) ?? AI_MODES[0],
    [activeMode],
  );

  const addProject = () => {
    if (!projectName.trim()) return;
    setProjectList((current) => [
      {
        id: `proj-${Date.now()}`,
        name: projectName.trim(),
        description: "Projeto gerado pelo AI ON.",
        status: "pending",
        createdAt: new Date().toISOString(),
        tasks: [],
      },
      ...current,
    ]);
    setProjectName("");
  };

  const generateImage = () => {
    const prompt = imagePrompt.trim() || "Nano Banana";
    setImagePreview(`https://placehold.co/640x420/0a0d1a/ffffff?text=${encodeURIComponent(prompt)}`);
  };

  const replayVoice = () => {
    setIsSpeaking(true);
    speak(voiceText, voiceId, () => setIsSpeaking(false));
  };

  const apiBase = getApiBase();
  const authHeaders = getAuthHeaders();

  const addFlowStep = () => {
    setFlowSteps((current) => [...current, `Nova etapa criada em ${new Date().toLocaleTimeString()}`]);
  };

  const searchMemory = async () => {
    const trimmed = memoryQuery.trim();
    if (!trimmed) {
      setMemoryResults([]);
      return;
    }

    try {
      setIsSearchingMemory(true);
      const response = await fetch(
        `${apiBase}/api/v1/search?user_id=${encodeURIComponent(userId)}&q=${encodeURIComponent(trimmed)}`,
        { headers: authHeaders },
      );
      if (!response.ok) {
        throw new Error(`Search failed ${response.status}`);
      }
      const data = (await response.json()) as { results?: Array<{ id: string; role: "user" | "assistant" | "system"; content: string; category?: string }> };
      setMemoryResults(
        (data.results ?? []).map((item) => ({
          id: item.id,
          role: item.role,
          content: item.content,
          category: item.category,
        })),
      );
    } catch (error) {
      console.error("Memory search failed", error);
      setMemoryResults([]);
    } finally {
      setIsSearchingMemory(false);
    }
  };

  const copyMemoryResult = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch (error) {
      console.error("Copy failed", error);
    }
  };

  const sphereState: SphereState = activeMode === "Voz" ? "listening" : activeMode === "Chat" ? "responding" : "idle";
  const sphereShape =
    activeMode === "Imagem"
      ? "galaxy"
      : activeMode === "Código"
      ? "cube"
      : activeMode === "Projetos"
      ? "torus"
      : activeMode === "Memória"
      ? "wave"
      : activeMode === "Visual"
      ? "heart"
      : activeMode === "Automação"
      ? "question"
      : "sphere";

  const renderModeContent = () => {
    switch (activeMode) {
      case "Chat":
        return (
          <Chat
            userId={userId}
            aiName={aiName}
            voiceId={voiceId}
            onEditProfile={onEditProfile}
            onSignOut={onSignOut}
            onRequestMode={(mode) => setActiveMode(mode)}
          />
        );
      case "Código":
        return (
          <section className="space-y-4 p-6">
            <div className="space-y-2">
              <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Modo Código</p>
              <h2 className="text-2xl font-semibold">Aumente sua produtividade com geração e revisão de código.</h2>
              <p className="text-sm text-muted-foreground max-w-2xl">
                Use este espaço para criar trechos de código, refatorar estruturas e validar designs de software.
              </p>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
              <div className="space-y-3 rounded-3xl border border-border/70 bg-card p-5 shadow-sm">
                <Label htmlFor="code-prompt">Descrição do requisito</Label>
                <Textarea
                  id="code-prompt"
                  rows={10}
                  placeholder="Explique a funcionalidade ou peça o código desejado..."
                />
                <Button variant="secondary">Gerar código</Button>
              </div>
              <div className="rounded-3xl border border-border/70 bg-card p-5 shadow-sm">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <span className="text-sm font-medium">Resumo rápido</span>
                  <span className="rounded-full bg-muted px-3 py-1 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                    HTML / JS / TS
                  </span>
                </div>
                <pre className="max-h-[24rem] overflow-auto rounded-2xl bg-background p-4 text-sm text-muted-foreground">
{/* Placeholder for generated code output */}
</pre>
              </div>
            </div>
          </section>
        );
      case "Projetos":
        return (
          <section className="space-y-4 p-6">
            <div className="space-y-2">
              <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Modo Projetos</p>
              <h2 className="text-2xl font-semibold">Organize seus ciclos de desenvolvimento.</h2>
              <p className="text-sm text-muted-foreground max-w-2xl">
                Gerencie projetos com tarefas, prazos e progresso direto do AI ON.
              </p>
            </div>
            <div className="flex flex-col gap-3 rounded-3xl border border-border/70 bg-card p-5">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="space-y-2">
                  <p className="text-sm font-medium">Criar novo projeto</p>
                  <p className="text-xs text-muted-foreground">Digite o nome e pressione adicionar.</p>
                </div>
                <div className="flex flex-1 items-center gap-2">
                  <Input
                    value={projectName}
                    onChange={(event) => setProjectName(event.target.value)}
                    placeholder="Nome do projeto"
                  />
                  <Button onClick={addProject} disabled={!projectName.trim()}>
                    Adicionar
                  </Button>
                </div>
              </div>
            </div>
            <div className="grid gap-4 xl:grid-cols-2">
              {projectList.map((project) => (
                <div key={project.id} className="rounded-3xl border border-border/70 bg-background p-5 shadow-sm">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="text-lg font-semibold">{project.name}</h3>
                      <p className="text-sm text-muted-foreground">{project.description}</p>
                    </div>
                    <span className="rounded-full bg-muted px-3 py-1 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                      {project.status.replace("-", " ")}
                    </span>
                  </div>
                  <div className="mt-4 space-y-2">
                    {project.tasks.length === 0 ? (
                      <p className="text-sm text-muted-foreground">Sem tarefas definidas.</p>
                    ) : (
                      project.tasks.map((task) => (
                        <div key={task.id} className="flex items-center gap-3 rounded-2xl bg-card p-3">
                          <span className={task.completed ? "text-green-500" : "text-muted-foreground"}>
                            {task.completed ? "✓" : "○"}
                          </span>
                          <span className="text-sm">{task.title}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        );
      case "Memória":
        return (
          <section className="space-y-4 p-6">
            <div className="space-y-2">
              <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Modo Memória</p>
              <h2 className="text-2xl font-semibold">Busque e relacione informações antigas.</h2>
              <p className="text-sm text-muted-foreground max-w-2xl">
                Encontre rapidamente partes importantes das conversas e mantenha o contexto fluido.
              </p>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-3xl border border-border/70 bg-card p-5">
                <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <Label htmlFor="memory-query">Buscar memória</Label>
                  <Button variant="secondary" size="sm" onClick={searchMemory} disabled={!memoryQuery.trim()}>
                    Buscar
                  </Button>
                </div>
                <Input
                  id="memory-query"
                  value={memoryQuery}
                  onChange={(event) => setMemoryQuery(event.target.value)}
                  placeholder="Digite palavras-chave para encontrar lembranças"
                />
              </div>
              <div className="rounded-3xl border border-border/70 bg-card p-5">
                <h3 className="text-sm font-semibold">Dica</h3>
                <p className="text-sm text-muted-foreground">
                  Você pode pesquisar termos, ideias de projeto ou instruções para recuperar o contexto da IA.
                </p>
              </div>
            </div>
            <div className="grid gap-3">
              {memoryResults.map((result) => (
                <div key={result.id} className="rounded-3xl border border-border/70 bg-background p-4">
                  <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                        {result.role === "assistant" ? "IA" : result.role === "user" ? "Você" : "Sistema"}
                      </p>
                      {result.category ? (
                        <span className="mt-1 inline-flex rounded-full bg-secondary px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-secondary-foreground">
                          {result.category}
                        </span>
                      ) : null}
                    </div>
                    <Button variant="secondary" size="sm" onClick={() => copyMemoryResult(result.content)}>
                      <Copy className="mr-2 h-3.5 w-3.5" /> Copiar
                    </Button>
                  </div>
                  <p className="whitespace-pre-wrap text-sm">{result.content}</p>
                </div>
              ))}
              {memoryResults.length === 0 && memoryQuery.trim() && (
                <div className="rounded-3xl border border-border/70 bg-background p-4 text-sm text-muted-foreground">
                  Nenhum resultado encontrado. Tente palavras-chave diferentes ou refine sua busca.
                </div>
              )}
            </div>
          </section>
        );
      case "Imagem":
        return (
          <section className="space-y-4 p-6">
            <div className="space-y-2">
              <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Modo Imagem</p>
              <h2 className="text-2xl font-semibold">Crie imagens com prompts de estilo Nano Banana.</h2>
              <p className="text-sm text-muted-foreground max-w-2xl">
                Use descrições criativas para gerar proposta visual e itere rapidamente.
              </p>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1fr_0.9fr]">
              <div className="rounded-3xl border border-border/70 bg-card p-5">
                <Label htmlFor="image-prompt">Prompt de imagem</Label>
                <Textarea
                  id="image-prompt"
                  rows={6}
                  value={imagePrompt}
                  onChange={(event) => setImagePrompt(event.target.value)}
                  placeholder="Descreva a imagem que deseja gerar..."
                />
                <Button onClick={generateImage} className="mt-4">
                  Gerar imagem
                </Button>
              </div>
              <div className="rounded-3xl border border-border/70 bg-card p-5">
                <div className="aspect-[4/3] overflow-hidden rounded-3xl bg-muted">
                  {imagePreview ? (
                    <img src={imagePreview} alt="Preview de imagem" className="h-full w-full object-cover" />
                  ) : (
                    <div className="grid h-full place-items-center text-sm text-muted-foreground">
                      Preview será exibido aqui
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        );
      case "Voz":
        return (
          <section className="space-y-4 p-6">
            <div className="space-y-2">
              <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Modo Voz</p>
              <h2 className="text-2xl font-semibold">Configure e teste a fala da assistente.</h2>
              <p className="text-sm text-muted-foreground max-w-2xl">
                Ajuste a voz e ouça como a IA se comunica em voz natural.
              </p>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1fr_0.8fr]">
              <div className="rounded-3xl border border-border/70 bg-card p-5">
                <Label htmlFor="voice-text">Texto para fala</Label>
                <Textarea
                  id="voice-text"
                  rows={6}
                  value={voiceText}
                  onChange={(event) => setVoiceText(event.target.value)}
                />
                <Button onClick={replayVoice} className="mt-4" disabled={isSpeaking}>
                  {isSpeaking ? "Falando…" : "Reproduzir voz"}
                </Button>
              </div>
              <div className="rounded-3xl border border-border/70 bg-card p-5">
                <div className="space-y-3">
                  <p className="text-sm font-semibold">Voz selecionada</p>
                  <p className="text-sm text-muted-foreground">{getVoiceConfig(voiceId).label}</p>
                  <p className="text-sm text-muted-foreground">Idioma: {getVoiceConfig(voiceId).lang}</p>
                </div>
              </div>
            </div>
          </section>
        );
      case "Automação":
        return (
          <section className="space-y-4 p-6">
            <div className="space-y-2">
              <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Modo Automação</p>
              <h2 className="text-2xl font-semibold">Crie fluxos e rotinas com poucos passos.</h2>
              <p className="text-sm text-muted-foreground max-w-2xl">
                Monte tarefas encadeadas que podem ser usadas como base para automações futuras.
              </p>
            </div>
            <div className="flex flex-col gap-4 rounded-3xl border border-border/70 bg-card p-5">
              <div className="flex flex-wrap gap-3">
                {flowSteps.map((step, index) => (
                  <span key={index} className="rounded-full bg-muted px-3 py-1 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                    {step}
                  </span>
                ))}
              </div>
              <Button onClick={addFlowStep} variant="secondary">
                Adicionar etapa ao fluxo
              </Button>
            </div>
          </section>
        );
      case "Dev Mode":
        return (
          <section className="space-y-4 p-6">
            <div className="space-y-2">
              <p className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Dev Mode</p>
              <h2 className="text-2xl font-semibold">Ferramentas e visão técnica do ambiente.</h2>
              <p className="text-sm text-muted-foreground max-w-2xl">
                Acesse informações do projeto e execute verificações básicas diretamente no front-end.
              </p>
            </div>
            <div className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-3xl border border-border/70 bg-card p-5">
                <h3 className="text-sm font-semibold">Informações do app</h3>
                <dl className="mt-4 space-y-3 text-sm text-muted-foreground">
                  <div>
                    <dt className="font-medium text-foreground">Modo ativo</dt>
                    <dd>AI ON</dd>
                  </div>
                  <div>
                    <dt className="font-medium text-foreground">Versão</dt>
                    <dd>0.0.0</dd>
                  </div>
                  <div>
                    <dt className="font-medium text-foreground">Usuário</dt>
                    <dd>{userId}</dd>
                  </div>
                </dl>
              </div>
              <div className="rounded-3xl border border-border/70 bg-card p-5">
                <h3 className="text-sm font-semibold">Ações rápidas</h3>
                <div className="mt-4 flex flex-col gap-3">
                  <Button variant="secondary">Abrir console de depuração</Button>
                  <Button variant="outline">Ver logs do sistema</Button>
                </div>
              </div>
            </div>
          </section>
        );
      case "Visual":
        return (
          <VisualMode
            userId={userId}
            aiName={aiName}
            voiceId={voiceId}
          />
        );
      default:
        return null;
    }
  };

  return (
    <SidebarProvider>
      <div className="grid min-h-[100dvh] grid-cols-1 md:grid-cols-[18rem_1fr] bg-background text-foreground">
        <Sidebar side="left" className="border-r border-border/50 bg-sidebar">
          <SidebarHeader className="px-4 py-5">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">AI ON</p>
              <h1 className="text-lg font-semibold">Aura Sphere</h1>
            </div>
          </SidebarHeader>
          <SidebarSeparator />
          <SidebarContent className="px-3 py-4">
            <SidebarMenu>
              {AI_MODES.map((mode) => (
                <SidebarMenuItem key={mode.id}>
                  <SidebarMenuButton
                    onClick={() => setActiveMode(mode.id)}
                    isActive={activeMode === mode.id}
                  >
                    {mode.label}
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>
          <SidebarFooter className="px-4 py-5">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">Modo ativo</p>
              <p className="text-sm font-semibold">{activeModeMeta.label}</p>
              <p className="text-sm text-muted-foreground">{activeModeMeta.description}</p>
              <Button variant="ghost" size="sm" onClick={onEditProfile} className="mt-3 w-full">
                Editar perfil
              </Button>
              <Button variant="destructive" size="sm" onClick={onSignOut} className="w-full">
                Sair
              </Button>
            </div>
          </SidebarFooter>
        </Sidebar>
        <main className="min-h-[100dvh] overflow-hidden bg-background">{renderModeContent()}</main>
        <SidebarTrigger className="md:hidden" />
        <div className="pointer-events-none fixed inset-x-0 bottom-0 z-20 flex justify-end p-4 md:p-8">
          <div className="h-44 w-44 rounded-full bg-background/20 backdrop-blur-xl shadow-2xl shadow-black/20 ring-1 ring-white/10 md:h-56 md:w-56">
            <ParticleSphere state={sphereState} shape={sphereShape} volume={0.08} />
          </div>
        </div>
      </div>
    </SidebarProvider>
  );
}
