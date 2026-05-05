import { useEffect, useState } from "react";
import { ParticleSphere } from "@/components/ParticleSphere";
import type { VoiceId } from "@/lib/types";
import { speak } from "@/lib/speech";

interface LoadingScreenProps {
  onLoadingComplete: () => void;
  aiName: string;
  voiceId: VoiceId | string;
}

export function LoadingScreen({ onLoadingComplete, aiName, voiceId }: LoadingScreenProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [phaseText, setPhaseText] = useState("Inicializando...");
  const [showPresentation, setShowPresentation] = useState(false);

  useEffect(() => {
    // Fase 1: Inicializando (2 segundos)
    const timer1 = setTimeout(() => {
      setPhaseText("Ativando sistemas");
    }, 2000);

    // Fase 2: Ativando sistemas (2 segundos)
    const timer2 = setTimeout(() => {
      setPhaseText("Conectando redes neurais");
    }, 4000);

    // Fase 3: Pronto (2 segundos)
    const timer3 = setTimeout(() => {
      setPhaseText("Pronto!");
    }, 6000);

    // Fase 4: Apresentação
    const timer4 = setTimeout(() => {
      setShowPresentation(true);
      const presentationMessage = `Olá! Sou ${aiName}, sua assistente de IA. Bem-vindo ao Aura Sphere! Estou aqui para ajudar você com planejamento, tarefas, conversas e muito mais. Vamos começar?`;
      speak(presentationMessage, voiceId, () => {
        // Após falar, aguarda 1 segundo e fecha o carregamento
        setTimeout(() => {
          setIsVisible(false);
          onLoadingComplete();
        }, 1000);
      });
    }, 8000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, [aiName, voiceId, onLoadingComplete]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black flex flex-col items-center justify-center z-50">
      {/* Esfera animada */}
      <div className="mb-12">
        <ParticleSphere
          state="idle"
          shape="sphere"
          className="w-24 h-24"
        />
      </div>

      {/* Conteúdo */}
      <div className="text-center space-y-6">
        {!showPresentation ? (
          <>
            {/* Texto de carregamento */}
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-white">{aiName}</h1>
              <p className="text-lg text-gray-300 min-h-6">{phaseText}</p>
            </div>

            {/* Indicador de progresso */}
            <div className="flex justify-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse delay-100"></div>
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse delay-200"></div>
            </div>
          </>
        ) : (
          <>
            {/* Apresentação */}
            <div className="space-y-4">
              <h1 className="text-4xl font-bold text-white">{aiName}</h1>
              <p className="text-xl text-gray-300">
                Sua assistente de IA está pronta para ajudar
              </p>
              <p className="text-sm text-gray-400 max-w-md mx-auto">
                Bem-vindo ao Aura Sphere. Estou aqui para apoiá-lo em planejamento, tarefas, conversas e muito mais.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
