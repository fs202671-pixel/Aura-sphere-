import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Mic, MicOff, Settings, User, Cpu, X, RefreshCw, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

const BASE_URL = import.meta.env.BASE_URL?.replace(/\/$/, "") || "";
const MESSAGES_KEY = "caos_shell_messages";
const USER_NAME_KEY = "caos_user_name";
const AVATAR_KEY = "caos_avatar";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  streaming?: boolean;
};

function useShellChat() {
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const raw = localStorage.getItem(MESSAGES_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const saveMessages = useCallback((msgs: Message[]) => {
    const trimmed = msgs.slice(-100);
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(trimmed));
  }, []);

  const send = useCallback(async (content: string) => {
    if (!content.trim() || isStreaming) return;

    const userMsg: Message = {
      id: `u_${Date.now()}`,
      role: "user",
      content: content.trim(),
      timestamp: Date.now(),
    };

    setMessages((prev) => {
      const next = [...prev, userMsg];
      saveMessages(next);
      return next;
    });

    setIsStreaming(true);
    abortRef.current = new AbortController();

    const assistantId = `a_${Date.now()}`;
    let assistantContent = "";

    setMessages((prev) => {
      const next = [...prev, { id: assistantId, role: "assistant" as const, content: "", timestamp: Date.now(), streaming: true }];
      return next;
    });

    try {
      const response = await fetch(`${BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: content.trim(),
          history: messages.slice(-10).map((m) => ({ role: m.role, content: m.content })),
        }),
        signal: abortRef.current.signal,
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.content) {
              assistantContent += data.content;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: assistantContent } : m
                )
              );
            }
          } catch {}
        }
      }
    } catch (err: any) {
      if (err.name === "AbortError") return;
      assistantContent = assistantContent || "Desculpe, não consegui processar sua mensagem. Verifique a conexão com a API.";
    } finally {
      setIsStreaming(false);
      setMessages((prev) => {
        const next = prev.map((m) =>
          m.id === assistantId ? { ...m, content: assistantContent, streaming: false } : m
        );
        saveMessages(next);
        return next;
      });
    }
  }, [isStreaming, messages, saveMessages]);

  const clear = useCallback(() => {
    setMessages([]);
    localStorage.removeItem(MESSAGES_KEY);
  }, []);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return { messages, send, clear, stop, isStreaming };
}

function MessageBubble({ msg, userName, avatarSrc }: { msg: Message; userName: string; avatarSrc: string | null }) {
  const isUser = msg.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn("flex gap-3 items-end", isUser && "flex-row-reverse")}
    >
      <div className="flex-shrink-0 mb-1">
        {isUser ? (
          avatarSrc ? (
            <img src={avatarSrc} alt="You" className="w-8 h-8 rounded-full object-cover border border-primary/30" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
              <User className="w-4 h-4 text-primary" />
            </div>
          )
        ) : (
          <div className="w-8 h-8 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center">
            <Cpu className="w-4 h-4 text-violet-400" />
          </div>
        )}
      </div>
      <div
        className={cn(
          "max-w-[75%] md:max-w-[65%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
          isUser
            ? "bg-primary/20 border border-primary/30 text-foreground rounded-br-sm"
            : "bg-card/80 border border-border/40 text-foreground rounded-bl-sm backdrop-blur-sm"
        )}
      >
        {msg.content || (msg.streaming && (
          <span className="flex gap-1 items-center h-4">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </span>
        ))}
      </div>
    </motion.div>
  );
}

export default function Shell() {
  const { messages, send, clear, stop, isStreaming } = useShellChat();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const { toast } = useToast();

  const [userName] = useState(() => localStorage.getItem(USER_NAME_KEY) || "Você");
  const [avatarSrc, setAvatarSrc] = useState<string | null>(() => localStorage.getItem(AVATAR_KEY));

  useEffect(() => {
    const handler = () => setAvatarSrc(localStorage.getItem(AVATAR_KEY));
    window.addEventListener("caos_avatar_changed", handler);
    return () => window.removeEventListener("caos_avatar_changed", handler);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    send(input);
    setInput("");
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed inset-0 flex flex-col bg-background md:static md:h-full pt-14 md:pt-0">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50 bg-background/80 backdrop-blur-xl flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-violet-500/20 border border-violet-500/30 flex items-center justify-center">
            <Cpu className="w-4 h-4 text-violet-400" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-foreground">CAOS Shell</h1>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[10px] text-muted-foreground font-mono">Online</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isStreaming && (
            <button
              onClick={stop}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-xs font-medium hover:bg-destructive/20 transition-colors"
            >
              <X className="w-3 h-3" /> Parar
            </button>
          )}
          <button
            onClick={() => { clear(); toast({ title: "Conversa limpa." }); }}
            className="p-2 rounded-lg border border-border/40 text-muted-foreground hover:text-foreground hover:border-border transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center h-full gap-4 text-center py-12"
          >
            <div className="w-16 h-16 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
              <MessageSquare className="w-8 h-8 text-violet-400" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-foreground">CAOS Shell</h2>
              <p className="text-sm text-muted-foreground mt-1 max-w-sm">
                Sua IA conversacional está pronta. Digite uma mensagem para começar.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center max-w-sm">
              {["Olá! O que você pode fazer?", "Me ajuda a estudar algo", "Crie um plano de projeto", "Explique inteligência artificial"].map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="px-3 py-1.5 rounded-full bg-card/60 border border-border/40 text-xs text-muted-foreground hover:text-foreground hover:border-border transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </motion.div>
        )}
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} userName={userName} avatarSrc={avatarSrc} />
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 px-4 py-3 border-t border-border/50 bg-background/80 backdrop-blur-xl pb-[max(0.75rem,env(safe-area-inset-bottom))]">
        <div className="flex items-end gap-2 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Mensagem para o CAOS..."
              rows={1}
              disabled={isStreaming}
              className={cn(
                "w-full rounded-2xl bg-card/60 border border-border/50 px-4 py-3 pr-12 text-sm text-foreground placeholder:text-muted-foreground/50",
                "focus:outline-none focus:border-primary/50 transition-colors resize-none max-h-32 backdrop-blur-sm",
                "disabled:opacity-50"
              )}
              style={{ height: "auto" }}
              onInput={(e) => {
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = Math.min(el.scrollHeight, 128) + "px";
              }}
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            className={cn(
              "flex-shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center transition-all",
              input.trim() && !isStreaming
                ? "bg-primary text-primary-foreground shadow-[0_0_15px_hsl(var(--primary)/0.4)] hover:shadow-[0_0_20px_hsl(var(--primary)/0.6)] hover:bg-primary/90"
                : "bg-card/60 border border-border/40 text-muted-foreground cursor-not-allowed"
            )}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
