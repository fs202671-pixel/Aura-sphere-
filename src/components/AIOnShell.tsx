import { useEffect, useState } from "react";
import { ParticleSphere } from "@/components/ParticleSphere";
import { LoadingScreen } from "@/components/LoadingScreen";
import { PlanningTab } from "@/components/PlanningTab";
import { MiniOverlay } from "@/components/MiniOverlay";
import { SidebarControls } from "@/components/SidebarControls";
import Chat from "@/pages/Chat";
import VisualMode from "@/pages/Visual";
import { speak } from "@/lib/speech";
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
  const [isMinimized, setIsMinimized] = useState(false);
  const [hasWelcomed, setHasWelcomed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showInitialPresentation, setShowInitialPresentation] = useState(true);

  // Tela de carregamento finalizada
  const handleLoadingComplete = () => {
    setIsLoading(false);
    // Mostrar apresentação da esfera por 3 segundos
    setTimeout(() => {
      setShowInitialPresentation(false);
      setHasWelcomed(true);
    }, 3000);
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
      case "Planejamento":
        return <PlanningTab />;
      case "Visual":
        return <VisualMode />;
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
    <div className="h-screen w-screen bg-black flex">
      {/* Sidebar lateral */}
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

      {/* Conteúdo principal - só o conteúdo, sem controles */}
      <div className="flex-1 bg-gradient-to-br from-gray-900 via-black to-gray-900 overflow-hidden">
        {renderModeContent()}
      </div>
    </div>
  );
}
