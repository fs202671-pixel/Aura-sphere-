import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send, Mic, MicOff, Volume2, VolumeX, Trash2,
  Wifi, WifiOff, Bot, User as UserIcon, Copy, Check,
  Zap, Code2, Brain, FolderOpen, ImageIcon, Cpu, BookOpen,
  ChevronDown, Star, TrendingUp, RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

const BASE_URL = import.meta.env.BASE_URL?.replace(/\/$/, "") || "";
const MESSAGES_KEY = "caos_shell_v3_messages";

type AiMode = "Chat" | "Código" | "Projetos" | "Ensinar" | "Imagem" | "Dev";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  streaming?: boolean;
  mode?: AiMode;
};

type Profile = {
  name: string;
  level: number;
  xp: number;
  xpToNext: number;
  aiClass: string;
};

const MODES: { id: AiMode; label: string; icon: React.ElementType; color: string; desc: string }[] = [
  { id: "Chat",     label: "Chat",    icon: Bot,       color: "text-violet-400", desc: "Conversa geral com Caos" },
  { id: "Código",   label: "Código",  icon: Code2,     color: "text-cyan-400",   desc: "Gerar e revisar código" },
  { id: "Projetos", label: "Projetos",icon: FolderOpen,color: "text-green-400",  desc: "Planejar e organizar" },
  { id: "Ensinar",  label: "Ensinar", icon: BookOpen,  color: "text-amber-400",  desc: "Ensinar algo novo à Caos (+XP)" },
  { id: "Imagem",   label: "Imagem",  icon: ImageIcon, color: "text-orange-400", desc: "Criar com prompts visuais" },
  { id: "Dev",      label: "Dev",     icon: Cpu,       color: "text-red-400",    desc: "Ferramentas de desenvolvedor" },
];

const MODE_SYSTEM: Record<AiMode, string> = {
  Chat:     "",
  Código:   "Você está no modo Código. Responda com foco técnico, use blocos de código markdown e seja preciso.",
  Projetos: "Você está no modo Projetos. Ajude a planejar, criar tarefas e estruturar projetos com clareza.",
  Ensinar:  "Você está no modo Ensinar. O usuário vai te passar um conhecimento. Confirme que você aprendeu e agradeça com entusiasmo.",
  Imagem:   "Você está no modo Imagem. Crie prompts visuais detalhados e criativos para geração de imagens com IA.",
  Dev:      "Você está no modo Dev. Forneça informações técnicas detalhadas sobre o ambiente e sistema.",
};

const SUGGESTIONS: Record<AiMode, string[]> = {
  Chat:     ["O que você sabe fazer?", "Me dê uma dica de hoje", "Quem é você, Caos?"],
  Código:   ["Crie uma função em TypeScript", "Revise este código", "Explique async/await"],
  Projetos: ["Crie um plano de projeto", "Liste as prioridades de hoje", "Organize meu backlog"],
  Ensinar:  ["Meu nome é...", "Eu gosto de...", "Aprenda sobre: programação em Python"],
  Imagem:   ["Paisagem futurista neon", "Personagem guerreiro RPG", "Logo minimalista tech"],
  Dev:      ["Status do sistema", "Liste as rotas da API", "O que está rodando?"],
};

async function playTTS(text: string): Promise<void> {
  try {
    const resp = await fetch(`${BASE_URL}/api/voice/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text.slice(0, 500), voice: "nova" }),
    });
    if (!resp.ok) return;
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
    audio.onended = () => URL.revokeObjectURL(url);
  } catch { /* silent */ }
}

async function teachCaos(topic: string, content: string, category = "Geral") {
  const resp = await fetch(`${BASE_URL}/api/knowledge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, content, category }),
  });
  if (!resp.ok) throw new Error("Falha ao ensinar");
  return resp.json();
}

function useCaosProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);

  const reload = useCallback(async () => {
    try {
      const r = await fetch(`${BASE_URL}/api/ai/profile`);
      if (r.ok) setProfile(await r.json());
    } catch { /* silent */ }
  }, []);

  useEffect(() => { reload(); }, [reload]);
  return { profile, reload };
}

function useChat(mode: AiMode) {
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const raw = localStorage.getItem(MESSAGES_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch { return []; }
  });
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const messagesRef = useRef(messages);
  messagesRef.current = messages;

  const save = useCallback((msgs: Message[]) => {
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(msgs.slice(-200)));
  }, []);

  const send = useCallback(async (content: string): Promise<string | null> => {
    if (!content.trim() || isStreaming) return null;

    const userMsg: Message = {
      id: `u_${Date.now()}`,
      role: "user",
      content: content.trim(),
      timestamp: Date.now(),
      mode,
    };

    setMessages(prev => { const n = [...prev, userMsg]; save(n); return n; });
    setIsStreaming(true);
    abortRef.current = new AbortController();

    const aId = `a_${Date.now()}`;
    let aContent = "";

    setMessages(prev => [
      ...prev,
      { id: aId, role: "assistant" as const, content: "", timestamp: Date.now(), streaming: true, mode },
    ]);

    try {
      const history = messagesRef.current.slice(-14).map(m => ({ role: m.role, content: m.content }));
      const modeSystem = MODE_SYSTEM[mode];
      const finalHistory = modeSystem
        ? [{ role: "system", content: modeSystem }, ...history]
        : history;

      const response = await fetch(`${BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content.trim(), history: finalHistory, mode }),
        signal: abortRef.current.signal,
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!response.body) throw new Error("Sem body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        for (const line of chunk.split("\n")) {
          if (!line.startsWith("data: ")) continue;
          const data = line.slice(6).trim();
          if (data === "[DONE]") break;
          try {
            const parsed = JSON.parse(data);
            const delta = parsed.choices?.[0]?.delta?.content ?? parsed.content ?? "";
            if (delta) {
              aContent += delta;
              setMessages(prev => prev.map(m => m.id === aId ? { ...m, content: aContent } : m));
            }
          } catch { /* ignore */ }
        }
      }

      setMessages(prev => {
        const n = prev.map(m => m.id === aId ? { ...m, streaming: false } : m);
        save(n);
        return n;
      });
      return aContent;
    } catch (err: unknown) {
      if ((err as Error)?.name === "AbortError") return null;
      const errMsg = "⚠️ Erro ao conectar com Caos. Verifique se o servidor está ativo.";
      setMessages(prev => {
        const n = prev.map(m => m.id === aId ? { ...m, content: errMsg, streaming: false } : m);
        save(n);
        return n;
      });
      return null;
    } finally {
      setIsStreaming(false);
    }
  }, [isStreaming, mode, save]);

  const stop = useCallback(() => { abortRef.current?.abort(); }, []);
  const clear = useCallback(() => {
    setMessages([]);
    localStorage.removeItem(MESSAGES_KEY);
  }, []);

  return { messages, isStreaming, send, stop, clear };
}

function ModeSelector({ active, onSelect }: { active: AiMode; onSelect: (m: AiMode) => void }) {
  const [open, setOpen] = useState(false);
  const current = MODES.find(m => m.id === active)!;
  const Icon = current.icon;

  useEffect(() => {
    if (!open) return;
    const close = () => setOpen(false);
    document.addEventListener("click", close, { once: true });
    return () => document.removeEventListener("click", close);
  }, [open]);

  return (
    <div className="relative" onClick={e => e.stopPropagation()}>
      <button
        onClick={() => setOpen(!open)}
        className={cn(
          "flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-border/40 bg-card/60 text-xs transition-all hover:border-border",
          current.color
        )}
      >
        <Icon className="w-3.5 h-3.5" />
        <span className="font-medium hidden sm:inline">{current.label}</span>
        <ChevronDown className={cn("w-3 h-3 transition-transform", open && "rotate-180")} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute bottom-full mb-2 left-0 z-50 w-64 rounded-xl border border-border/50 bg-background/95 backdrop-blur-xl shadow-2xl overflow-hidden"
          >
            {MODES.map(m => {
              const MIcon = m.icon;
              return (
                <button
                  key={m.id}
                  onClick={() => { onSelect(m.id); setOpen(false); }}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2.5 hover:bg-card/60 transition-colors text-left",
                    m.id === active && "bg-card/40"
                  )}
                >
                  <MIcon className={cn("w-4 h-4 flex-shrink-0", m.color)} />
                  <div className="flex-1 min-w-0">
                    <p className={cn("text-xs font-medium", m.color)}>{m.label}</p>
                    <p className="text-[10px] text-muted-foreground truncate">{m.desc}</p>
                  </div>
                  {m.id === active && <Zap className="w-3 h-3 text-primary ml-auto flex-shrink-0" />}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function XPBar({ profile }: { profile: Profile }) {
  const pct = Math.min(100, Math.round((profile.xp % 100) / 1));
  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1">
        <Star className="w-3 h-3 text-amber-400" />
        <span className="text-[10px] font-bold text-amber-400">Nv.{profile.level}</span>
      </div>
      <div className="w-16 h-1.5 bg-border/40 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-amber-400 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
      <span className="text-[9px] text-muted-foreground font-mono">{profile.xp}xp</span>
    </div>
  );
}

function MessageBubble({ msg }: { msg: Message }) {
  const [copied, setCopied] = useState(false);
  const isUser = msg.role === "user";
  const modeInfo = msg.mode ? MODES.find(m => m.id === msg.mode) : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn("flex gap-2.5", isUser ? "flex-row-reverse" : "flex-row")}
    >
      <div className={cn(
        "flex-shrink-0 w-7 h-7 rounded-xl border flex items-center justify-center mt-0.5",
        isUser ? "bg-primary/20 border-primary/30" : "bg-card border-border/50"
      )}>
        {isUser
          ? <UserIcon className="w-3.5 h-3.5 text-primary" />
          : <Bot className="w-3.5 h-3.5 text-violet-400" />}
      </div>

      <div className={cn("group flex-1 max-w-[85%] md:max-w-[75%]", isUser && "flex flex-col items-end")}>
        <div className={cn(
          "relative rounded-2xl px-4 py-3 text-sm leading-relaxed",
          isUser
            ? "bg-primary/15 border border-primary/20 text-foreground rounded-tr-sm"
            : "bg-card/60 border border-border/30 text-foreground rounded-tl-sm"
        )}>
          {msg.streaming && !msg.content && (
            <div className="flex gap-1.5 py-1">
              {[0, 1, 2].map(i => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-violet-400/60"
                  animate={{ scale: [1, 1.5, 1], opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15 }}
                />
              ))}
            </div>
          )}
          <p className="whitespace-pre-wrap break-words">{msg.content}</p>
          {msg.streaming && (
            <motion.span
              className="inline-block w-0.5 h-4 bg-violet-400/80 ml-0.5 align-middle"
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 0.7, repeat: Infinity }}
            />
          )}
        </div>

        <div className={cn("flex items-center gap-2 mt-1", isUser ? "justify-end" : "justify-start")}>
          {modeInfo && (
            <span className={cn("text-[9px] font-mono flex items-center gap-0.5", modeInfo.color)}>
              <modeInfo.icon className="w-2.5 h-2.5" />
              {modeInfo.label}
            </span>
          )}
          <span className="text-[10px] text-muted-foreground/60">
            {new Date(msg.timestamp).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
          </span>
          {!msg.streaming && (
            <button
              onClick={() => { navigator.clipboard.writeText(msg.content); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
              className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-foreground"
            >
              {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

function LevelUpToast({ levelData, onClose }: { levelData: { newLevel: number; aiClass: string }; onClose: () => void }) {
  useEffect(() => {
    const t = setTimeout(onClose, 4000);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.8, y: -20 }}
      className="fixed bottom-32 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-3 rounded-2xl bg-amber-500/20 border border-amber-400/50 backdrop-blur-xl shadow-2xl"
    >
      <TrendingUp className="w-5 h-5 text-amber-400" />
      <div>
        <p className="text-sm font-bold text-amber-400">🎉 Subiu de nível!</p>
        <p className="text-xs text-amber-300">Caos agora é <strong>{levelData.aiClass}</strong> — Nível {levelData.newLevel}</p>
      </div>
    </motion.div>
  );
}

export default function Shell() {
  const [mode, setMode] = useState<AiMode>("Chat");
  const [input, setInput] = useState("");
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [levelUp, setLevelUp] = useState<{ newLevel: number; aiClass: string } | null>(null);

  const { profile, reload: reloadProfile } = useCaosProfile();
  const { messages, isStreaming, send, stop, clear } = useChat(mode);
  const { toast } = useToast();

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const on = () => setIsOnline(true);
    const off = () => setIsOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); };
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || isStreaming) return;
    const text = input.trim();
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    if (mode === "Ensinar") {
      const colonIdx = text.indexOf(":");
      const topic = colonIdx > 0 ? text.slice(0, colonIdx).trim() : text.split(" ").slice(0, 4).join(" ");
      const content = colonIdx > 0 ? text.slice(colonIdx + 1).trim() : text;

      try {
        const result = await teachCaos(topic, content);
        if (result.leveledUp) {
          setLevelUp({ newLevel: result.newLevel, aiClass: result.aiClass });
        }
        await reloadProfile();
        toast({ title: `✅ Caos aprendeu! +${result.xpGained}xp`, description: `Nível ${result.newLevel} — ${result.aiClass}` });
      } catch {
        toast({ title: "Erro ao ensinar", variant: "destructive" });
      }

      const reply = await send(text);
      if (reply && ttsEnabled) playTTS(reply);
    } else {
      const reply = await send(text);
      if (reply && ttsEnabled) playTTS(reply);
    }
  }, [input, isStreaming, mode, send, ttsEnabled, toast, reloadProfile]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  };

  // Voz estilo Alexa: grava, auto-envia quando para de falar
  const toggleVoice = useCallback(() => {
    if (isListening) {
      recognitionRef.current?.abort();
      setIsListening(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      toast({ title: "Voz não suportada", description: "Use Chrome ou Edge para reconhecimento de voz.", variant: "destructive" });
      return;
    }

    const rec = new SpeechRecognition();
    rec.lang = "pt-BR";
    rec.continuous = false;
    rec.interimResults = true;

    recognitionRef.current = rec;
    setIsListening(true);

    let final = "";
    rec.onresult = (e: any) => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript;
        else interim = e.results[i][0].transcript;
      }
      setInput(final + interim);
    };

    rec.onend = () => {
      setIsListening(false);
      if (final.trim()) {
        setInput(final.trim());
        setTimeout(() => {
          handleSend();
        }, 100);
      }
    };

    rec.onerror = () => setIsListening(false);
    rec.start();
  }, [isListening, toast, handleSend]);

  const currentMode = MODES.find(m => m.id === mode)!;

  return (
    <div className="fixed inset-0 md:relative md:inset-auto md:h-full flex flex-col bg-background overflow-hidden">
      {/* Level Up Toast */}
      <AnimatePresence>
        {levelUp && <LevelUpToast levelData={levelUp} onClose={() => setLevelUp(null)} />}
      </AnimatePresence>

      {/* Header */}
      <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="flex items-center gap-2.5">
          <div className="relative w-8 h-8 rounded-xl bg-violet-500/20 border border-violet-500/30 flex items-center justify-center">
            <Bot className="w-4 h-4 text-violet-400" />
            <div className={cn(
              "absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-background",
              isOnline ? "bg-green-500" : "bg-gray-500"
            )} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-foreground">Caos</h1>
              {profile && (
                <span className="text-[9px] px-1.5 py-0.5 rounded-md bg-amber-400/10 text-amber-400 border border-amber-400/20 font-mono">
                  {profile.aiClass}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1.5">
              {isOnline
                ? <><Wifi className="w-2.5 h-2.5 text-green-400" /><span className="text-[9px] text-green-400 font-mono">Online</span></>
                : <><WifiOff className="w-2.5 h-2.5 text-gray-400" /><span className="text-[9px] text-gray-400 font-mono">Offline</span></>}
              {profile && <XPBar profile={profile} />}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setTtsEnabled(!ttsEnabled)}
            className={cn(
              "p-2 rounded-lg border transition-colors",
              ttsEnabled ? "border-violet-500/40 text-violet-400 bg-violet-500/10" : "border-border/40 text-muted-foreground hover:border-border"
            )}
            title={ttsEnabled ? "Desligar voz" : "Ligar voz da Caos"}
          >
            {ttsEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
          <button
            onClick={() => { clear(); toast({ title: "Conversa limpa." }); }}
            className="p-2 rounded-lg border border-border/40 text-muted-foreground hover:border-border transition-colors"
            title="Limpar conversa"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center h-full text-center gap-5 py-16"
          >
            <div className="relative">
              <div className="w-20 h-20 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                <Bot className="w-10 h-10 text-violet-400/60" />
              </div>
              <motion.div
                className="absolute inset-0 rounded-2xl border border-violet-500/30"
                animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
                transition={{ duration: 3, repeat: Infinity }}
              />
            </div>
            <div>
              <h2 className="text-lg font-bold text-foreground mb-1">Caos pronta</h2>
              {profile && (
                <p className="text-xs text-amber-400 font-mono mb-1">
                  Nível {profile.level} · {profile.aiClass} · {profile.xp}xp
                </p>
              )}
              <p className="text-sm text-muted-foreground max-w-xs">
                {mode === "Ensinar"
                  ? 'Me ensine algo! Ex: "Meu nome é João: meu nome é João e eu moro em SP"'
                  : "Fale comigo ou use o microfone — falo português e reconheço sua voz."}
              </p>
            </div>
            <div className="grid grid-cols-1 gap-2 w-full max-w-xs">
              {SUGGESTIONS[mode].map(s => (
                <button
                  key={s}
                  onClick={() => setInput(s)}
                  className="px-4 py-2 text-xs rounded-xl border border-border/40 text-muted-foreground hover:border-primary/30 hover:text-foreground bg-card/40 transition-all text-left"
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence initial={false}>
          {messages.map(msg => <MessageBubble key={msg.id} msg={msg} />)}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t border-border/40 bg-background/80 backdrop-blur-xl px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
        {mode === "Ensinar" && (
          <div className="mb-2 px-3 py-1.5 rounded-lg bg-amber-400/10 border border-amber-400/20 text-xs text-amber-400 font-mono">
            📚 Modo Ensinar — Formato: "tópico: conteúdo" ou apenas escreva o que quer me ensinar
          </div>
        )}

        <div className="flex items-end gap-2 max-w-4xl mx-auto">
          <ModeSelector active={mode} onSelect={setMode} />

          <div className="flex-1 flex items-end gap-2 rounded-2xl border border-border/50 bg-card/40 px-3 py-2 focus-within:border-violet-500/40 transition-colors">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder={
                isListening ? "🎤 Ouvindo... fale agora" :
                mode === "Ensinar" ? "Me ensine algo novo..." :
                `Mensagem para Caos...`
              }
              rows={1}
              className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground/40 resize-none outline-none min-h-[24px] max-h-[160px]"
            />
            <button
              onClick={toggleVoice}
              className={cn(
                "flex-shrink-0 p-1.5 rounded-lg transition-all",
                isListening
                  ? "text-red-400 bg-red-400/10 animate-pulse"
                  : "text-muted-foreground hover:text-violet-400"
              )}
              title={isListening ? "Parar (auto-envia ao terminar)" : "Falar (envia ao terminar)"}
            >
              {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
            </button>
          </div>

          <button
            onClick={isStreaming ? stop : handleSend}
            disabled={!isStreaming && !input.trim()}
            className={cn(
              "flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all",
              isStreaming
                ? "bg-red-500/20 border border-red-500/40 text-red-400 hover:bg-red-500/30"
                : input.trim()
                  ? "bg-violet-500/20 border border-violet-500/40 text-violet-400 hover:bg-violet-500/30 shadow-[0_0_15px_hsl(270,60%,50%/0.2)]"
                  : "bg-card/40 border border-border/30 text-muted-foreground/30 cursor-not-allowed"
            )}
          >
            {isStreaming
              ? <RefreshCw className="w-4 h-4 animate-spin" />
              : <Send className="w-4 h-4" />}
          </button>
        </div>

        <AnimatePresence>
          {isListening && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-2 justify-center mt-2"
            >
              <div className="flex gap-0.5 items-end h-5">
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-1 bg-red-400 rounded-full"
                    animate={{ height: [4, 16, 4] }}
                    transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.1 }}
                  />
                ))}
              </div>
              <span className="text-xs text-red-400 font-mono">Ouvindo... (envia ao parar de falar)</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
