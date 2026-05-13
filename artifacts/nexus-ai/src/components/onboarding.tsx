import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cpu, Zap, ChevronRight, Check } from "lucide-react";
import { useUpdateAiProfile, getGetAiProfileQueryKey, getGetAiStatsQueryKey } from "@/lib/nexus-api";
import { useQueryClient } from "@tanstack/react-query";
import { cn } from "@/lib/utils";

const ONBOARDING_KEY = "caos_onboarding_done";

const PERSONALITY_OPTIONS = [
  { value: "Direto e eficiente. Responde com precisão.", label: "Eficiente", desc: "Respostas precisas e objetivas", color: "border-blue-500/40 bg-blue-500/10 text-blue-400" },
  { value: "Criativo e curioso. Explora possibilidades com entusiasmo.", label: "Criativo", desc: "Explora ideias com entusiasmo", color: "border-purple-500/40 bg-purple-500/10 text-purple-400" },
  { value: "Analítico e profundo. Detalha cada aspecto do problema.", label: "Analítico", desc: "Análise profunda e detalhada", color: "border-cyan-500/40 bg-cyan-500/10 text-cyan-400" },
  { value: "Motivador e encorajador. Sempre impulsiona o crescimento.", label: "Motivador", desc: "Incentiva e impulsiona o crescimento", color: "border-green-500/40 bg-green-500/10 text-green-400" },
];

export function useOnboarding() {
  const done = typeof window !== "undefined" && !!localStorage.getItem(ONBOARDING_KEY);
  return { needsOnboarding: !done };
}

export function skipOnboarding() {
  if (typeof window !== "undefined") localStorage.setItem(ONBOARDING_KEY, "1");
}

export function markOnboardingDone() {
  localStorage.setItem(ONBOARDING_KEY, "1");
}

interface OnboardingProps {
  onComplete: () => void;
}

export function OnboardingModal({ onComplete }: OnboardingProps) {
  const [step, setStep] = useState(0);
  const [aiName, setAiName] = useState("");
  const [selectedPersonality, setSelectedPersonality] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const updateProfile = useUpdateAiProfile();
  const qc = useQueryClient();

  const handleFinish = async () => {
    if (!aiName.trim()) return;
    setSaving(true);
    try {
      await updateProfile.mutateAsync({
        data: {
          name: aiName.trim(),
          personality: selectedPersonality ?? PERSONALITY_OPTIONS[0].value,
        },
      });
      qc.invalidateQueries({ queryKey: getGetAiProfileQueryKey() });
      qc.invalidateQueries({ queryKey: getGetAiStatsQueryKey() });
      markOnboardingDone();
      onComplete();
    } catch {
      setSaving(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-background/95 backdrop-blur-xl p-4"
    >
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-violet-500/5 blur-3xl" />
      </div>

      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 280, damping: 24 }}
        className="relative w-full max-w-md"
      >
        <AnimatePresence mode="wait">
          {/* Step 0 — Boas vindas */}
          {step === 0 && (
            <motion.div
              key="step0"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              className="space-y-8"
            >
              <div className="text-center space-y-4">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.1 }}
                  className="w-20 h-20 rounded-2xl bg-primary/20 border border-primary/40 flex items-center justify-center mx-auto shadow-[0_0_40px_hsl(var(--primary)/0.3)]"
                >
                  <Cpu className="w-10 h-10 text-primary" />
                </motion.div>
                <div>
                  <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-primary/60 mb-2">// Inicialização do Sistema</p>
                  <h1 className="text-3xl font-black uppercase tracking-widest text-foreground">CAOS HUB</h1>
                  <p className="text-muted-foreground text-sm mt-2 leading-relaxed">
                    Bem-vindo à plataforma unificada. Antes de começar, vamos configurar sua IA pessoal.
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {[
                  { icon: Zap, text: "IA com sistema de habilidades RPG" },
                  { icon: Cpu, text: "Terminal de conversação inteligente" },
                  { icon: ChevronRight, text: "Studio criativo com artefatos e missões" },
                ].map((item, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 + i * 0.1 }}
                    className="flex items-center gap-3 p-3 rounded-xl bg-card/40 border border-border/30"
                  >
                    <item.icon className="w-4 h-4 text-primary flex-shrink-0" />
                    <span className="text-sm text-muted-foreground">{item.text}</span>
                  </motion.div>
                ))}
              </div>

              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                onClick={() => setStep(1)}
                className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-primary text-primary-foreground font-bold text-sm tracking-wide hover:opacity-90 transition-all shadow-[0_0_25px_hsl(var(--primary)/0.4)]"
              >
                Configurar minha IA <ChevronRight className="w-4 h-4" />
              </motion.button>
            </motion.div>
          )}

          {/* Step 1 — Nome da IA */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              className="space-y-6"
            >
              <div className="text-center">
                <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-primary/60 mb-2">// Passo 1 de 2</p>
                <h2 className="text-2xl font-black uppercase tracking-widest text-foreground">Nomeie sua IA</h2>
                <p className="text-muted-foreground text-sm mt-2">
                  Dê um nome único à sua inteligência artificial pessoal.
                </p>
              </div>

              <div className="space-y-3">
                <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block">
                  Nome da IA
                </label>
                <input
                  type="text"
                  value={aiName}
                  onChange={(e) => setAiName(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && aiName.trim() && setStep(2)}
                  placeholder="Ex: ARIA, NEXUS, SIGMA, OPUS..."
                  autoFocus
                  maxLength={24}
                  className="w-full rounded-xl bg-card/60 border border-border/50 px-4 py-3.5 text-lg font-bold text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-primary/60 transition-colors text-center uppercase tracking-widest"
                />
                <p className="text-[10px] text-muted-foreground/50 text-center font-mono">
                  {aiName.length}/24 caracteres
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(0)}
                  className="flex-1 py-3 rounded-xl border border-border/50 text-muted-foreground text-sm hover:text-foreground hover:border-border transition-colors"
                >
                  Voltar
                </button>
                <button
                  onClick={() => setStep(2)}
                  disabled={!aiName.trim()}
                  className="flex-[2] flex items-center justify-center gap-2 py-3 rounded-xl bg-primary text-primary-foreground font-bold text-sm hover:opacity-90 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_0_20px_hsl(var(--primary)/0.3)]"
                >
                  Continuar <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 2 — Personalidade */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              className="space-y-6"
            >
              <div className="text-center">
                <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-primary/60 mb-2">// Passo 2 de 2</p>
                <h2 className="text-2xl font-black uppercase tracking-widest text-foreground">Personalidade</h2>
                <p className="text-muted-foreground text-sm mt-2">
                  Como <span className="text-primary font-bold">{aiName.toUpperCase()}</span> deve se comportar?
                </p>
              </div>

              <div className="space-y-2">
                {PERSONALITY_OPTIONS.map((opt) => {
                  const isSelected = selectedPersonality === opt.value;
                  return (
                    <motion.button
                      key={opt.value}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setSelectedPersonality(opt.value)}
                      className={cn(
                        "w-full flex items-center gap-4 p-4 rounded-xl border text-left transition-all",
                        isSelected ? opt.color : "border-border/40 bg-card/40 hover:bg-card/70 hover:border-border"
                      )}
                    >
                      <div className={cn(
                        "w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 border transition-all",
                        isSelected ? "border-current bg-current/10" : "border-border/40"
                      )}>
                        {isSelected ? <Check className="w-4 h-4" /> : <div className="w-2 h-2 rounded-full bg-muted-foreground/40" />}
                      </div>
                      <div>
                        <p className={cn("font-bold text-sm", isSelected ? "" : "text-foreground")}>{opt.label}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">{opt.desc}</p>
                      </div>
                    </motion.button>
                  );
                })}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 py-3 rounded-xl border border-border/50 text-muted-foreground text-sm hover:text-foreground hover:border-border transition-colors"
                >
                  Voltar
                </button>
                <button
                  onClick={handleFinish}
                  disabled={saving}
                  className="flex-[2] flex items-center justify-center gap-2 py-3 rounded-xl bg-primary text-primary-foreground font-bold text-sm hover:opacity-90 transition-all disabled:opacity-60 shadow-[0_0_25px_hsl(var(--primary)/0.4)]"
                >
                  {saving ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Inicializando...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" /> Ativar {aiName.toUpperCase()}
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Progress dots */}
        <div className="flex justify-center gap-2 mt-6">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={cn(
                "rounded-full transition-all duration-300",
                step === i ? "w-6 h-2 bg-primary" : "w-2 h-2 bg-muted-foreground/30"
              )}
            />
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
