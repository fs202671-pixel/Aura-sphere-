import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { ParticleSphere } from "@/components/ParticleSphere";
import { LoadingScreen } from "@/components/LoadingScreen";
import { PlanningTab } from "@/components/PlanningTab";
import { MiniOverlay } from "@/components/MiniOverlay";
import { SidebarControls } from "@/components/SidebarControls";
import { ModeSelector } from "@/components/ModeSelector";
import { TVMode } from "@/components/TVMode";
import { VoiceMode } from "@/components/VoiceMode";
import { VersionDashboard } from "@/components/VersionDashboard";
import { MemoryViewer } from "@/components/MemoryViewer";
import { SyncPanel } from "@/components/SyncPanel";
import { DeveloperMode } from "@/components/DeveloperMode";
import Chat from "@/pages/Chat";
import VisualMode from "@/pages/Visual";
import { speak } from "@/lib/speech";
import { useLocalAuth } from "@/hooks/useLocalAuth";
import { TourModal } from "@/components/TourModal";
import type { AiMode, SphereState, VoiceId } from "@/lib/types";

const AI_MODES: { id: AiMode; label: string; description: string }[] = [
  { id: "Chat", label: "Chat", description: "Converse naturalmente com a IA para ideias, respostas e ações rápidas." },
  { id: "Código", label: "Código", description: "Gere, revise e aprimore código com assistência contextual." },
  { id: "Planejamento", label: "Planejamento", description: "Crie planos de estudo, gerencie tarefas e acompanhe progresso com barras visuais." },
  { id: "Projetos", label: "Projetos", description: "Organize tarefas, cronogramas e objetivos de desenvolvimento." },
  { id: "Memória", label: "Memória", description: "Armazene e recupere informações importantes em contexto." },
  { id: "Imagem", label: "Imagem", description: "Crie imagens rápidas com prompts inteligentes." },
  { id: "Voz", label: "Voz", description: "Fale com a IA e ajuste a assistente de voz." },
  { id: "Automação", label: "Automação", description: "Defina fluxos e rotinas para automatizar tarefas." },
  { id: "Visual", label: "Visual", description: "Personalize a aparência e interface gráfica do sistema." },
  { id: "Dev Mode", label: "Dev Mode", description: "Acesse ferramentas de desenvolvedor e informações do ambiente." },
];

type UiMode = "standard" | "tv" | "voice" | "developer";

export default function AIOnShell({
  userId,
  aiName,
  voiceId,
  onLogout,
  onEditProfile = () => {},
}: {
  userId: string;
  aiName: string;
  voiceId: VoiceId | string;
  onLogout: () => void;
  onEditProfile?: () => void;
}) {
  const onSignOut = onLogout;
  const { isOnline } = useLocalAuth();
  const { theme, setTheme } = useTheme();
  const [activeMode, setActiveMode] = useState<AiMode>("Chat");
  const [uiMode, setUiMode] = useState<UiMode>("standard");
  const [isMinimized, setIsMinimized] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [hasWelcomed, setHasWelcomed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showInitialPresentation, setShowInitialPresentation] = useState(true);
  const [selectedMemory, setSelectedMemory] = useState<{
    id: string;
    content: string;
    category: string;
    tags: string[];
    relevance: number;
  } | null>(null);

  // Tela de carregamento finalizada
  const handleLoadingComplete = () => {
    setIsLoading(false);
    // Mostrar apresentação da esfera por 3 segundos
    setTimeout(() => {
      setShowInitialPresentation(false);
      setHasWelcomed(true);
    }, 3000);
  };

  useEffect(() => {
    if (typeof window === "undefined") return;
    const seenTour = localStorage.getItem("caos_tour_seen");
    if (!seenTour) {
      setShowTour(true);
    }
  }, []);

  const closeTour = () => {
    localStorage.setItem("caos_tour_seen", "true");
    setShowTour(false);
  };

  // Se está carregando, mostrar tela de carregamento
  if (isLoading) {
    return (
      <LoadingScreen
        aiName={aiName}
        voiceId={voiceId}
        onLoadingComplete={handleLoadingComplete}
      />
    );
  }

  // Tela de apresentação inicial
  if (showInitialPresentation) {
    return (
      <div className="h-screen w-screen bg-black flex items-center justify-center">
        <div className="text-center space-y-6">
          <ParticleSphere
            state="responding"
            shape="sphere"
            className="w-40 h-40 mx-auto"
          />
          <div className="space-y-2">
            <h1 className="text-4xl font-bold text-white">{aiName}</h1>
            <p className="text-xl text-gray-400">
              Sua assistente de IA está pronta
            </p>
          </div>
        </div>
      </div>
    );
  }

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
    if (uiMode !== "standard") {
      return (
        <div className="h-full w-full">
          {uiMode === "tv" && <TVMode />}
          {uiMode === "voice" && <VoiceMode />}
          {uiMode === "developer" && <DeveloperMode />}
        </div>
      );
    }

    switch (activeMode) {
      case "Chat":
        return (
          <Chat
            userId={userId}
            aiName={aiName}
            voiceId={voiceId}
            onEditProfile={onEditProfile}
            onSignOut={onLogout}
            onRequestMode={(mode) => setActiveMode(mode)}
            selectedMemory={selectedMemory}
            onMemoryUse={() => setSelectedMemory(null)}
          />
        );
      case "Memória":
        return (
          <div className="h-full p-6 overflow-auto">
            <MemoryViewer
              userId={userId}
              onMemorySelect={(memory) => {
                setSelectedMemory(memory);
                setActiveMode('Chat');
              }}
            />
          </div>
        );
      case "Planejamento":
        return <VisualMode userId={userId} aiName={aiName} voiceId={voiceId} />;
      case "Dev Mode":
        return (
          <div className="h-full p-6 overflow-auto">
            <VersionDashboard
              currentVersion="1.2.3"
              onVersionChange={(versionId) => {
                console.log('Mudando para versão:', versionId);
                // Integração futura: implementar mudança de versão
              }}
            />
          </div>
        );
      default:
        return (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <ParticleSphere
                state={sphereState}
                shape={sphereShape}
                className="w-32 h-32 mx-auto"
              />
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  Modo {AI_MODES.find(m => m.id === activeMode)?.label}
                </h2>
                <p className="text-gray-400 max-w-md">
                  {AI_MODES.find(m => m.id === activeMode)?.description}
                </p>
              </div>
            </div>
          </div>
        );
    }
  };

  if (isMinimized) {
    return (
      <MiniOverlay
        onClick={() => setIsMinimized(false)}
        isMinimized={isMinimized}
      />
    );
  }

  return (
    <div className="h-screen w-screen relative overflow-hidden bg-black text-white">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(124,58,237,0.22),transparent_22%),radial-gradient(circle_at_bottom_right,_rgba(59,130,246,0.18),transparent_20%)]" />
      <div className="pointer-events-none absolute left-1/2 top-0 h-[28rem] w-[28rem] -translate-x-1/2 rounded-full bg-violet-600/10 blur-3xl" />
      <div className="pointer-events-none absolute inset-x-0 top-16 h-48 bg-gradient-to-b from-slate-900/90 to-transparent" />

      <div className="relative z-10 flex min-h-screen flex-col md:flex-row">
        <div className="hidden md:flex">
          <div className="h-full">
            <SidebarControls
              activeMode={activeMode}
              onModeChange={setActiveMode}
              onMinimize={() => setIsMinimized(true)}
              onClose={onSignOut}
              aiName={aiName}
              voiceId={voiceId}
              onEditProfile={onEditProfile}
              onSignOut={onSignOut}
            />
          </div>
        </div>

        <div className="md:hidden fixed inset-x-0 bottom-0 z-50 bg-slate-900/95 border-t border-white/10 backdrop-blur-xl">
          <div className="flex justify-around items-center py-3 px-4">
            {AI_MODES.slice(0, 5).map((mode) => (
              <button
                key={mode.id}
                onClick={() => setActiveMode(mode.id)}
                aria-current={activeMode === mode.id ? 'page' : undefined}
                className={`flex flex-col items-center gap-1 rounded-2xl px-3 py-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-violet-500 ${
                  activeMode === mode.id
                    ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/20 scale-105'
                    : 'text-slate-400 hover:text-white hover:bg-white/10'
                }`}
              >
                <span className="text-xs font-medium">{mode.label}</span>
              </button>
            ))}
          </div>
        </div>

        <TourModal isOpen={showTour} onClose={closeTour} />

        <div className="flex-1 bg-gradient-to-br from-slate-950 via-slate-900 to-black overflow-hidden pb-16 md:pb-0">
          <div className="md:hidden p-4 glass-panel border border-white/10 space-y-3">
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between gap-3">
                <div className="space-y-1">
                  <h1 className="text-lg font-semibold">{aiName}</h1>
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-400">
                    {AI_MODES.find((m) => m.id === activeMode)?.label}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    aria-label="Alternar tema claro/escuro"
                    className="h-10 w-10 rounded-2xl bg-slate-800 text-gray-200 hover:bg-slate-700 transition"
                    onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                  >
                    {theme === "dark" ? "☀️" : "🌙"}
                  </button>
                  <ModeSelector value={uiMode} onChange={setUiMode} />
                </div>
              </div>
            </div>
            <SyncPanel userId={userId} isOnline={isOnline} />
          </div>

          <div className="hidden md:block px-6 py-5 glass-panel border border-white/10 mb-4">
            <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
              <div className="space-y-1">
                <p className="text-sm uppercase tracking-[0.25em] text-slate-400">Interface</p>
                <h1 className="text-2xl font-semibold">{aiName}</h1>
                <p className="text-sm text-slate-400">
                  {AI_MODES.find((m) => m.id === activeMode)?.description}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  aria-label="Abrir tour inicial"
                  className="rounded-2xl bg-slate-800 px-4 py-2 text-sm text-gray-200 hover:bg-slate-700 transition"
                  onClick={() => setShowTour(true)}
                >
                  Tour
                </button>
                <button
                  type="button"
                  aria-label="Alternar tema claro/escuro"
                  className="rounded-2xl bg-slate-800 px-4 py-2 text-sm text-gray-200 hover:bg-slate-700 transition"
                  onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                >
                  {theme === "dark" ? "Modo claro" : "Modo escuro"}
                </button>
                <ModeSelector value={uiMode} onChange={setUiMode} />
              </div>
            </div>
            <div className="mt-4">
              <SyncPanel userId={userId} isOnline={isOnline} />
            </div>
          </div>

          {renderModeContent()}
        </div>
      </div>
    </div>
  );
}
