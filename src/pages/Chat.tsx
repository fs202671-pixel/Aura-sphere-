import { useEffect, useRef, useState } from "react";
import { Send, Mic, MicOff, LogOut, Settings, Search, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ParticleSphere } from "@/components/ParticleSphere";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChatMessage as ChatMessageCard } from "@/components/ChatMessage";
import { supabase } from "@/integrations/supabase/client";
import { getApiBase, getAuthHeaders } from "@/lib/api";
import type { AiMode, AiProvider, ChatMessage, ParticleShape, SphereState, VoiceId } from "@/lib/types";
import { createRecognition, getVoiceConfig, speak, stopSpeaking } from "@/lib/speech";
import { inferShape } from "@/lib/shapes";
import { useVoiceActivity } from "@/hooks/useVoiceActivity";
import { toast } from "sonner";

const detectModeCommand = (text: string): AiMode | undefined => {
  const normalized = text.toLowerCase().trim();
  const commands: Array<{ triggers: string[]; mode: AiMode }> = [
    { triggers: ["@chat", "/chat", "modo chat"], mode: "Chat" },
    { triggers: ["@código", "/codigo", "@codigo", "modo código", "modo code"], mode: "Código" },
    { triggers: ["@projetos", "/projetos", "modo projetos"], mode: "Projetos" },
    { triggers: ["@memória", "@memoria", "/memória", "/memoria", "modo memória"], mode: "Memória" },
    { triggers: ["@imagem", "/imagem", "modo imagem"], mode: "Imagem" },
    { triggers: ["@voz", "/voz", "modo voz"], mode: "Voz" },
    { triggers: ["@automação", "@automacao", "/automação", "/automacao", "modo automação"], mode: "Automação" },
    { triggers: ["@dev", "/dev", "modo dev", "dev mode"], mode: "Dev Mode" },
  ];

  return commands.find((command) => command.triggers.some((trigger) => normalized.startsWith(trigger)))?.mode;
};

const STATE_LABELS: Record<SphereState, string> = {
  idle: "Pronta",
  listening: "Ouvindo…",
  thinking: "Pensando…",
  responding: "Respondendo…",
};

type PromptPreset = {
  id: string;
  label: string;
  description: string;
  systemPrompt: string;
};

type MemorySearchResult = ChatMessage & { category?: string };

const AI_PROVIDER_OPTIONS: { id: AiProvider; label: string }[] = [
  { id: "lovable", label: "Lovable" },
  { id: "anthropic", label: "Anthropic / Claude" },
  { id: "openai", label: "OpenAI" },
];

const PROMPT_PRESETS: PromptPreset[] = [
  {
    id: "assistant",
    label: "Assistente",
    description: "Responda de forma clara, curta e útil em português.",
    systemPrompt: "Você é um assistente útil e educado. Responda de forma clara e objetiva em português.",
  },
  {
    id: "developer",
    label: "Desenvolvedor",
    description: "Foque em código, explicações técnicas e exemplos.",
    systemPrompt: "Você é um experiente desenvolvedor que ajuda com código, debugging e explicações técnicas.",
  },
  {
    id: "brainstorm",
    label: "Criativo",
    description: "Faça brainstorming e gere ideias para projetos.",
    systemPrompt: "Você é um assistente criativo que propõe ideias de projetos, sugestões e soluções inovadoras.",
  },
  {
    id: "memory",
    label: "Memória",
    description: "Mantenha contexto e lembre-se de preferências do usuário.",
    systemPrompt: "Você mantém o contexto e lembra preferências do usuário ao responder, usando o histórico para personalizar a resposta.",
  },
];

const API_BASE = getApiBase();
const AUTH_HEADERS = getAuthHeaders();

export default function Chat({
  userId,
  aiName,
  voiceId,
  onSignOut,
  onEditProfile,
  onRequestMode,
}: {
  userId: string;
  aiName: string;
  voiceId: VoiceId | string;
  onSignOut: () => void;
  onEditProfile: () => void;
  onRequestMode?: (mode: AiMode) => void;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState<AiProvider>("lovable");
  const [presetId, setPresetId] = useState<string>(PROMPT_PRESETS[0].id);
  const [state, setState] = useState<SphereState>("idle");
  const [shape, setShape] = useState<ParticleShape>("sphere");
  const [recording, setRecording] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<MemorySearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [memoryEnabled, setMemoryEnabled] = useState(true);
  const recognitionRef = useRef<ReturnType<typeof createRecognition> | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const lang = getVoiceConfig(voiceId).lang;

  // Live mic volume — drives particle vibration. Active only while recording.
  const { volume: micVolume, active: micActive } = useVoiceActivity(recording);

  // While the AI speaks (state === "responding"), simulate a soft volume so
  // the particles also "speak". Otherwise use the live mic volume.
  const [ttsPulse, setTtsPulse] = useState(0);
  useEffect(() => {
    if (state !== "responding") {
      setTtsPulse(0);
      return;
    }
    let raf = 0;
    const start = performance.now();
    const loop = () => {
      const t = (performance.now() - start) / 1000;
      // pseudo-speech envelope
      const v =
        0.18 +
        Math.abs(Math.sin(t * 6.2)) * 0.18 +
        Math.abs(Math.sin(t * 2.7 + 1.3)) * 0.12;
      setTtsPulse(Math.min(0.6, v));
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [state]);

  const liveVolume = recording ? micVolume : ttsPulse;

  // Auto-switch to "listening" while the user actually speaks into the mic.
  useEffect(() => {
    if (recording && micActive && state !== "listening") {
      setState("listening");
    }
  }, [recording, micActive, state]);

  // Load history
  useEffect(() => {
    supabase
      .from("chat_messages")
      .select("id, role, content")
      .eq("user_id", userId)
      .order("created_at", { ascending: true })
      .limit(100)
      .then(({ data }) => {
        if (data) setMessages(data.map((m) => ({ id: m.id, role: (m.role as 'user' | 'assistant'), content: m.content })));
      });
  }, [userId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, state]);

  // Update particle shape based on conversation context
  useEffect(() => {
    if (messages.length === 0) {
      setShape("sphere");
      return;
    }
    const last = messages[messages.length - 1];
    // Prefer assistant content if available, otherwise the user's latest message
    const text =
      last.role === "assistant"
        ? last.content
        : messages.slice().reverse().find((m) => m.role === "assistant")?.content || last.content;
    setShape(inferShape(text));
  }, [messages]);

  const persist = async (msg: ChatMessage) => {
    const { error } = await supabase
      .from("chat_messages")
      .insert({ user_id: userId, role: msg.role, content: msg.content });
    if (error) {
      console.error("Persist error", error);
      toast.error("Não foi possível salvar a mensagem.");
    }
  };

  const saveMemory = async (msg: ChatMessage, category: string = "chat") => {
    try {
      await fetch(`${API_BASE}/api/v1/memory`, {
        method: "POST",
        headers: AUTH_HEADERS,
        body: JSON.stringify({
          user_id: userId,
          role: msg.role,
          content: msg.content,
          category,
        }),
      });
    } catch (e) {
      console.warn("Memory save failed", e);
    }
  };

  const searchMemoryEntries = async (query: string): Promise<MemorySearchResult[]> => {
    const trimmed = query.trim();
    if (!trimmed) return [];

    const response = await fetch(
      `${API_BASE}/api/v1/search?user_id=${encodeURIComponent(userId)}&q=${encodeURIComponent(trimmed)}`,
      {
        headers: AUTH_HEADERS,
      },
    );

    if (!response.ok) {
      throw new Error(`Search request failed: ${response.status}`);
    }

    const result = (await response.json()) as {
      results?: Array<{ id: string; role: "user" | "assistant" | "system"; content: string; category: string }>;
    };

    return (result.results ?? []).map((item) => ({
      id: item.id,
      role: item.role,
      content: item.content,
      category: item.category,
    }));
  };

  const searchMessages = async (query = searchQuery) => {
    const trimmed = query.trim();
    if (!trimmed) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      const results = await searchMemoryEntries(trimmed);
      setSearchResults(results);
    } catch (error) {
      console.error("Search error", error);
      toast.error("Erro ao buscar na conversa. Usando fallback local.");
      const { data, error: supabaseError } = await supabase
        .from("chat_messages")
        .select("id, role, content")
        .ilike("content", `%${trimmed}%`)
        .eq("user_id", userId)
        .order("created_at", { ascending: false })
        .limit(20);

      if (supabaseError) {
        console.error("Fallback search error", supabaseError);
      }
      setSearchResults(data ?? []);
    } finally {
      setSearching(false);
    }
  };

  const clearChat = async () => {
    const { error } = await supabase.from("chat_messages").delete().eq("user_id", userId);
    if (error) {
      console.error("Clear chat error", error);
      toast.error("Não foi possível limpar a conversa.");
      return;
    }

    setMessages([]);
    setSearchResults([]);
    setSearchQuery("");
    toast.success("Conversa limpa com sucesso.");
  };

  const copyToClipboard = async (text: string) => {
    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
      } else {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
      }
      toast.success("Mensagem copiada para a área de transferência.");
    } catch (error) {
      console.error("Copy error", error);
      toast.error("Não foi possível copiar a mensagem.");
    }
  };

  const sendText = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    stopSpeaking();

    const requestedMode = detectModeCommand(trimmed);
    if (requestedMode) {
      onRequestMode?.(requestedMode);
      setInput("");
      setState("idle");
      return;
    }

    const userMsg: ChatMessage = { role: "user", content: trimmed };
    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    persist(userMsg);
    saveMemory(userMsg, "user");

    setState("thinking");

    try {
        const selectedPreset = PROMPT_PRESETS.find((preset) => preset.id === presetId);
      const systemMessage = selectedPreset
        ? { role: "system" as const, content: selectedPreset.systemPrompt }
        : null;

      const memoryEntries = memoryEnabled ? await searchMemoryEntries(trimmed) : [];
      const memoryMessage = memoryEntries.length
        ? {
            role: "system" as const,
            content:
              "Use as memórias relevantes abaixo para responder de forma mais contextualizada:\n" +
              memoryEntries
                .slice(0, 3)
                .map((item, index) =>
                  `${index + 1}. [${item.role}] ${item.category ?? "chat"}: ${item.content}`,
                )
                .join("\n"),
          }
        : null;

      const messagesForApi = [systemMessage, memoryMessage].filter(Boolean) as ChatMessage[];
      const payloadMessages = messagesForApi.length > 0 ? [...messagesForApi, ...next] : next;

      const url = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/chat`;
      const resp = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
        },
        body: JSON.stringify({
          aiName,
          provider,
          messages: payloadMessages.map(({ role, content }) => ({ role, content })),
        }),
      });

      if (!resp.ok || !resp.body) {
        if (resp.status === 429) toast.error("Limite de uso atingido. Tente novamente em instantes.");
        else if (resp.status === 402) toast.error("Créditos de IA esgotados.");
        else toast.error("Erro ao falar com a IA");
        setState("idle");
        return;
      }

      setState("responding");
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      let assistantText = "";
      let added = false;
      let done = false;

      const upsert = (chunk: string) => {
        assistantText += chunk;
        setMessages((prev) => {
          if (!added) {
            added = true;
            return [...prev, { role: "assistant", content: assistantText }];
          }
          const copy = prev.slice();
          copy[copy.length - 1] = { ...copy[copy.length - 1], content: assistantText };
          return copy;
        });
      };

      while (!done) {
        const { done: d, value } = await reader.read();
        if (d) break;
        buf += decoder.decode(value, { stream: true });
        let nl: number;
        while ((nl = buf.indexOf("\n")) !== -1) {
          let line = buf.slice(0, nl);
          buf = buf.slice(nl + 1);
          if (line.endsWith("\r")) line = line.slice(0, -1);
          if (!line || line.startsWith(":") || !line.startsWith("data: ")) continue;
          const json = line.slice(6).trim();
          if (json === "[DONE]") {
            done = true;
            break;
          }
          try {
            const parsed = JSON.parse(json);
            const content = parsed.choices?.[0]?.delta?.content as string | undefined;
            if (content) upsert(content);
          } catch {
            buf = line + "\n" + buf;
            break;
          }
        }
      }

      if (assistantText) {
        const assistantMsg = { role: "assistant", content: assistantText };
        await persist(assistantMsg);
        await saveMemory(assistantMsg, "assistant");
        speak(assistantText, voiceId, () => setState("idle"));
      } else {
        setState("idle");
      }
    } catch (e) {
      console.error(e);
      toast.error("Erro de conexão");
      setState("idle");
    }
  };

  const startRecording = () => {
    const rec = createRecognition(lang);
    if (!rec) {
      toast.error("Reconhecimento de voz não suportado neste navegador. Use Chrome/Edge.");
      return;
    }
    let finalText = "";
    rec.onresult = (e: SpeechRecognitionEvent) => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) finalText += r[0].transcript;
        else interim += r[0].transcript;
      }
      setInput((finalText + interim).trim());
    };
    rec.onerror = (e: SpeechRecognitionErrorEvent) => {
      console.error("STT error", e);
      if (e.error === "not-allowed") toast.error("Permissão de microfone negada");
      setRecording(false);
      setState("idle");
    };
    rec.onend = () => {
      setRecording(false);
      const text = finalText.trim() || (input || "").trim();
      if (text) {
        setState("thinking");
        sendText(text);
      } else {
        setState("idle");
      }
    };
    recognitionRef.current = rec;
    setRecording(true);
    setState("listening");
    try {
      rec.start();
    } catch (e) {
      console.error(e);
      setRecording(false);
      setState("idle");
    }
  };

  const stopRecording = () => {
    recognitionRef.current?.stop();
  };

  const onMicClick = () => {
    if (recording) stopRecording();
    else startRecording();
  };

  return (
    <main className="min-h-[100dvh] flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-border/50 backdrop-blur-sm">
        <div>
          <h1 className="text-base font-semibold tracking-tight">{aiName}</h1>
          <p className="text-xs text-muted-foreground">{STATE_LABELS[state]}</p>
        </div>
        <div className="flex gap-1">
          <Button variant="ghost" size="icon" onClick={onEditProfile} aria-label="Configurações">
            <Settings className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" onClick={onSignOut} aria-label="Sair">
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </header>

      <section className="px-4 py-3 border-b border-border/50 bg-background/80 backdrop-blur-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs uppercase tracking-[0.25em] text-muted-foreground">Provedor</span>
            <div className="w-full max-w-xs">
              <Select value={provider} onValueChange={(value) => setProvider(value as AiProvider)}>
                <SelectTrigger className="w-full h-10">
                  <SelectValue placeholder="Selecionar" />
                </SelectTrigger>
                <SelectContent>
                  {AI_PROVIDER_OPTIONS.map((option) => (
                    <SelectItem key={option.id} value={option.id}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">Usando: {AI_PROVIDER_OPTIONS.find((option) => option.id === provider)?.label}</p>
        </div>
      </section>

      <section className="border-b border-border/50 px-4 py-3 bg-background/80 backdrop-blur-sm">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            searchMessages(searchQuery);
          }}
          className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="flex flex-1 gap-2">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Buscar na conversa"
              className="h-12 text-base"
              disabled={searching}
            />
            <Button
              type="submit"
              variant="secondary"
              size="icon"
              disabled={!searchQuery.trim() || searching}
              aria-label="Buscar"
            >
              <Search className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-12"
              onClick={() => searchMessages(searchQuery)}
              disabled={!searchQuery.trim() || searching}
            >
              {searching ? "Buscando…" : "Buscar"}
            </Button>
            <Button
              type="button"
              variant="destructive"
              size="sm"
              className="h-12"
              onClick={clearChat}
            >
              <Trash2 className="mr-2 h-4 w-4" />Limpar conversa
            </Button>
          </div>
        </form>

        {searchResults.length > 0 ? (
          <div className="mt-4 space-y-3">
            <p className="text-sm font-medium">Resultados da busca</p>
            <div className="grid gap-2">
              {searchResults.map((result) => (
                <div key={result.id} className="rounded-2xl border border-border/70 bg-card p-3 text-sm">
                  <p className="text-xs text-muted-foreground uppercase tracking-[0.2em] mb-1">
                    {result.role === "assistant" ? "Assistente" : "Você"}
                  </p>
                  <p className="whitespace-pre-wrap">{result.content}</p>
                </div>
              ))}
            </div>
          </div>
        ) : searchQuery.trim() && !searching ? (
          <div className="mt-4 rounded-2xl border border-border/70 bg-card p-3 text-sm text-muted-foreground">
            Nenhum resultado encontrado para <strong>{searchQuery}</strong>.
          </div>
        ) : null}
      </section>

      <section className="border-b border-border/50 px-4 py-3 bg-background/80 backdrop-blur-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">Preset de prompt</p>
              <p className="text-sm text-muted-foreground">Escolha um estilo de resposta rápido.</p>
            </div>
            <div className="w-full max-w-xs">
              <Select value={presetId} onValueChange={(value) => setPresetId(value)}>
                <SelectTrigger className="w-full h-10">
                  <SelectValue placeholder="Selecionar preset" />
                </SelectTrigger>
                <SelectContent>
                  {PROMPT_PRESETS.map((preset) => (
                    <SelectItem key={preset.id} value={preset.id}>
                      <div className="flex flex-col text-left">
                        <span>{preset.label}</span>
                        <span className="text-xs text-muted-foreground">{preset.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-xs text-muted-foreground">Preset ativo: {PROMPT_PRESETS.find((preset) => preset.id === presetId)?.label}</div>
            <Button
              type="button"
              variant={memoryEnabled ? "secondary" : "outline"}
              size="sm"
              className="h-10"
              onClick={() => setMemoryEnabled((prev) => !prev)}
            >
              Memória {memoryEnabled ? "ativa" : "inativa"}
            </Button>
          </div>
        </div>
      </section>

      {/* Sphere */}
      <section className="relative flex flex-col items-center justify-center px-4 pt-2 pb-1">
        <div className="w-full max-w-sm aspect-square max-h-[42vh]">
          <ParticleSphere state={state} shape={shape} volume={liveVolume} />
        </div>
        <div
          className={`mt-1 text-xs uppercase tracking-[0.25em] font-medium animate-fade-in ${
            state === "idle" ? "text-muted-foreground" : "text-primary animate-pulse-ring"
          }`}
        >
          {STATE_LABELS[state]}
        </div>
      </section>

      {/* Messages */}
      <section
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-3 space-y-3"
        aria-live="polite"
      >
        {messages.length === 0 && (
          <p className="text-center text-sm text-muted-foreground mt-6">
            Comece uma conversa — digite ou toque no microfone.
          </p>
        )}
        {messages.map((m, i) => (
          <ChatMessageCard
            key={m.id ?? i}
            message={m}
            onCopy={() => copyToClipboard(m.content)}
          />
        ))}
      </section>

      {/* Input */}
      <footer className="px-3 pt-2 pb-[max(0.75rem,env(safe-area-inset-bottom))] border-t border-border/50 bg-background/80 backdrop-blur">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendText(input);
          }}
          className="flex items-center gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={recording ? "Ouvindo…" : "Digite uma mensagem"}
            disabled={state === "thinking"}
            className="h-12 text-base flex-1"
            inputMode="text"
          />
          <Button
            type="button"
            onClick={onMicClick}
            variant={recording ? "destructive" : "secondary"}
            size="icon"
            className="h-12 w-12 shrink-0"
            aria-label={recording ? "Parar gravação" : "Gravar voz"}
          >
            {recording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          </Button>
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || state === "thinking"}
            className="h-12 w-12 shrink-0"
            aria-label="Enviar"
          >
            <Send className="h-5 w-5" />
          </Button>
        </form>
      </footer>
    </main>
  );
}