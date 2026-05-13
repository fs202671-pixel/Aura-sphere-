import { useState, useRef } from "react";
import { useStudyTopic, useAcquireSkill, getListSkillsQueryKey, getGetAiStatsQueryKey, getGetAiProfileQueryKey } from "@/lib/nexus-api";
import { useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen, Send, CheckCircle, ChevronRight, Zap, Brain,
  Github, Globe, Upload, FileCode, X, Loader2
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

type StudyMode = "topic" | "github" | "url" | "file";

const MODES: { id: StudyMode; label: string; icon: typeof Brain; desc: string }[] = [
  { id: "topic", label: "Tópico", icon: Brain, desc: "Estudar um conceito ou área de conhecimento" },
  { id: "github", label: "GitHub", icon: Github, desc: "Analisar repositório e extrair habilidades" },
  { id: "url", label: "URL / Site", icon: Globe, desc: "Analisar qualquer página ou serviço externo" },
  { id: "file", label: "Arquivo", icon: Upload, desc: "Carregar código ou documento para análise" },
];

const TOPIC_SUGGESTIONS = [
  "Criptografia e segurança", "React e componentes modernos", "Machine Learning básico",
  "APIs REST e GraphQL", "Docker e containers", "Algoritmos e estruturas de dados",
  "TypeScript avançado", "Banco de dados PostgreSQL",
];

export default function Study() {
  const [mode, setMode] = useState<StudyMode>("topic");
  const [topic, setTopic] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [externalUrl, setExternalUrl] = useState("");
  const [filter, setFilter] = useState("");
  const [result, setResult] = useState<any>(null);
  const [acquiredIds, setAcquiredIds] = useState<Set<number>>(new Set());
  const [fileContent, setFileContent] = useState<string>("");
  const [fileName, setFileName] = useState<string>("");
  const fileRef = useRef<HTMLInputElement>(null);
  const studyMut = useStudyTopic();
  const acquireMut = useAcquireSkill();
  const qc = useQueryClient();
  const { toast } = useToast();

  const getStudyTopic = () => {
    switch (mode) {
      case "github": return githubUrl.trim();
      case "url": return externalUrl.trim();
      case "file": return fileContent ? `Arquivo: ${fileName}\n\n${fileContent}` : "";
      default: return topic.trim();
    }
  };

  const getStudyFilter = () => {
    switch (mode) {
      case "github": return `Analise o repositório GitHub: ${githubUrl}. Extraia as principais tecnologias, padrões de código, arquitetura e boas práticas como habilidades. ${filter || ""}`;
      case "url": return `Analise o conteúdo de: ${externalUrl}. Extraia conceitos, tecnologias e práticas como habilidades. ${filter || ""}`;
      case "file": return `Analise este código/arquivo e extraia habilidades de programação e boas práticas. ${filter || ""}`;
      default: return filter || null;
    }
  };

  const isValid = () => {
    switch (mode) {
      case "github": return githubUrl.trim().length > 0;
      case "url": return externalUrl.trim().length > 0;
      case "file": return fileContent.length > 0;
      default: return topic.trim().length > 0;
    }
  };

  const handleStudy = async () => {
    if (!isValid()) return;
    setResult(null);
    setAcquiredIds(new Set());
    const t = getStudyTopic();
    const f = getStudyFilter();
    const res = await studyMut.mutateAsync({ data: { topic: t, filter: f as any } });
    setResult(res);
  };

  const handleAcquire = async (id: number) => {
    await acquireMut.mutateAsync({ id });
    setAcquiredIds(prev => new Set([...prev, id]));
    qc.invalidateQueries({ queryKey: getListSkillsQueryKey() });
    qc.invalidateQueries({ queryKey: getGetAiStatsQueryKey() });
    qc.invalidateQueries({ queryKey: getGetAiProfileQueryKey() });
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 200 * 1024) {
      toast({ title: "Arquivo muito grande", description: "Máximo 200KB.", variant: "destructive" });
      return;
    }
    const reader = new FileReader();
    reader.onload = (ev) => {
      setFileContent(ev.target?.result as string);
      setFileName(file.name);
      toast({ title: "Arquivo carregado!", description: file.name });
    };
    reader.readAsText(file);
    e.target.value = "";
  };

  const getPlaceholder = () => {
    switch (mode) {
      case "github": return "https://github.com/usuario/repositorio";
      case "url": return "https://nextjs.org, https://lovable.dev, ...";
      case "file": return "Clique em 'Carregar Arquivo' acima";
      default: return "Ex: Criptografia, React Hooks, Machine Learning...";
    }
  };

  const getLoadingMessages = () => {
    switch (mode) {
      case "github": return ["Clonando repositório...", "Analisando estrutura...", "Extraindo padrões..."];
      case "url": return ["Acessando URL...", "Analisando conteúdo...", "Mapeando conceitos..."];
      case "file": return ["Lendo arquivo...", "Analisando código...", "Estruturando habilidades..."];
      default: return ["Mapeando conceitos fundamentais...", "Extraindo princípios-chave...", "Estruturando habilidades..."];
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <p className="text-[10px] font-mono uppercase tracking-[0.3em] text-primary/60 mb-1">// Módulo de Aprendizagem</p>
        <h1 className="text-2xl font-black uppercase tracking-widest">Estudar</h1>
        <p className="text-sm text-muted-foreground mt-1">A IA analisa e propõe habilidades baseadas no que você estuda.</p>
      </motion.div>

      {/* Mode selector */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.05 }}
        className="grid grid-cols-2 sm:grid-cols-4 gap-2"
      >
        {MODES.map(m => (
          <motion.button
            key={m.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => { setMode(m.id); setResult(null); }}
            className={cn(
              "flex flex-col items-center gap-1.5 p-3 rounded-xl border text-center transition-all",
              mode === m.id
                ? "bg-primary/10 border-primary/40 text-primary"
                : "bg-card/30 border-border/30 text-muted-foreground hover:border-border/60 hover:text-foreground"
            )}
          >
            <m.icon className="w-5 h-5" />
            <span className="text-xs font-bold">{m.label}</span>
            <span className="text-[10px] leading-tight opacity-70 hidden sm:block">{m.desc}</span>
          </motion.button>
        ))}
      </motion.div>

      {/* Study form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-xl border border-primary/20 bg-card/60 backdrop-blur-sm p-5 relative space-y-4"
      >
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

        <AnimatePresence mode="wait">
          {/* Topic mode */}
          {mode === "topic" && (
            <motion.div key="topic" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} className="space-y-3">
              <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <Brain className="w-3 h-3" /> Tópico para Estudar
              </label>
              <input
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleStudy()}
                placeholder={getPlaceholder()}
                className="w-full rounded-xl bg-black/40 border border-border/50 text-sm px-4 py-3 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50 transition-colors font-mono"
              />
              {/* Suggestions */}
              <div className="flex flex-wrap gap-1.5">
                {TOPIC_SUGGESTIONS.map(s => (
                  <button
                    key={s}
                    onClick={() => setTopic(s)}
                    className="px-2.5 py-1 rounded-full bg-card/40 border border-border/20 text-[10px] text-muted-foreground hover:text-foreground hover:border-border/50 transition-all"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {/* GitHub mode */}
          {mode === "github" && (
            <motion.div key="github" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} className="space-y-3">
              <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <Github className="w-3 h-3" /> URL do Repositório GitHub
              </label>
              <input
                type="text"
                value={githubUrl}
                onChange={e => setGithubUrl(e.target.value)}
                onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleStudy()}
                placeholder="https://github.com/usuario/repositorio"
                className="w-full rounded-xl bg-black/40 border border-border/50 text-sm px-4 py-3 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50 transition-colors font-mono"
              />
              <div className="flex flex-wrap gap-1.5">
                {[
                  "https://github.com/facebook/react",
                  "https://github.com/vercel/next.js",
                  "https://github.com/tailwindlabs/tailwindcss",
                ].map(u => (
                  <button
                    key={u}
                    onClick={() => setGithubUrl(u)}
                    className="px-2.5 py-1 rounded-full bg-card/40 border border-border/20 text-[10px] text-muted-foreground hover:text-foreground hover:border-border/50 transition-all font-mono truncate max-w-[200px]"
                  >
                    {u.replace("https://github.com/", "")}
                  </button>
                ))}
              </div>
              <div className="p-3 rounded-lg bg-primary/5 border border-primary/10 text-xs text-muted-foreground">
                💡 A IA vai analisar o repositório, identificar tecnologias, padrões de código e boas práticas, e convertê-las em habilidades para sua IA.
              </div>
            </motion.div>
          )}

          {/* URL mode */}
          {mode === "url" && (
            <motion.div key="url" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} className="space-y-3">
              <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <Globe className="w-3 h-3" /> URL ou Serviço para Analisar
              </label>
              <input
                type="text"
                value={externalUrl}
                onChange={e => setExternalUrl(e.target.value)}
                onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleStudy()}
                placeholder="https://docs.react.dev, https://www.typescriptlang.org..."
                className="w-full rounded-xl bg-black/40 border border-border/50 text-sm px-4 py-3 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50 transition-colors font-mono"
              />
            </motion.div>
          )}

          {/* File mode */}
          {mode === "file" && (
            <motion.div key="file" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} className="space-y-3">
              <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <Upload className="w-3 h-3" /> Arquivo de Código ou Documento
              </label>
              <input
                ref={fileRef}
                type="file"
                accept=".js,.ts,.tsx,.jsx,.py,.html,.css,.json,.md,.txt,.yaml,.yml,.sql,.rs,.go,.java,.cpp,.c"
                className="hidden"
                onChange={handleFileUpload}
              />
              {fileContent ? (
                <div className="flex items-center gap-3 p-3 rounded-xl bg-primary/5 border border-primary/20">
                  <FileCode className="w-5 h-5 text-primary flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{fileName}</p>
                    <p className="text-xs text-muted-foreground">{(fileContent.length / 1024).toFixed(1)}KB carregado</p>
                  </div>
                  <button onClick={() => { setFileContent(""); setFileName(""); }} className="text-muted-foreground hover:text-foreground">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => fileRef.current?.click()}
                  className="w-full py-8 border-2 border-dashed border-border/40 rounded-xl text-sm text-muted-foreground hover:border-primary/40 hover:text-primary transition-all flex flex-col items-center gap-2"
                >
                  <Upload className="w-6 h-6" />
                  Clique para selecionar um arquivo
                  <span className="text-[10px]">JS, TS, PY, HTML, CSS, JSON, MD, SQL...</span>
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Filter (always visible) */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
            Filtro / Foco <span className="text-muted-foreground/50 normal-case font-normal">(opcional)</span>
          </label>
          <input
            type="text"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="Ex: apenas fundamentos, foco em segurança, excluir design..."
            className="w-full rounded-xl bg-black/40 border border-border/50 text-sm px-4 py-3 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50 transition-colors font-mono"
          />
        </div>

        <button
          onClick={handleStudy}
          disabled={!isValid() || studyMut.isPending}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_hsl(var(--primary)/0.3)] hover:shadow-[0_0_30px_hsl(var(--primary)/0.5)]"
        >
          <Send className="h-4 w-4" />
          {studyMut.isPending ? "Analisando..." : "Iniciar Estudo"}
        </button>
      </motion.div>

      {/* Loading state */}
      <AnimatePresence>
        {studyMut.isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="rounded-xl border border-border/30 bg-card/40 p-8 flex flex-col items-center gap-4"
          >
            <div className="relative">
              <div className="h-16 w-16 rounded-full border-2 border-primary/20 animate-spin border-t-primary" />
              {mode === "github" ? <Github className="absolute inset-0 m-auto h-6 w-6 text-primary" /> : <Brain className="absolute inset-0 m-auto h-6 w-6 text-primary" />}
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-primary">Processando conhecimento...</p>
              <p className="text-xs text-muted-foreground mt-1 font-mono">
                {mode === "github" ? `Analisando ${githubUrl.replace("https://github.com/", "")}` :
                 mode === "url" ? `Analisando ${externalUrl.slice(0, 40)}` :
                 mode === "file" ? `Lendo ${fileName}` : `Analisando "${topic}"`}
              </p>
            </div>
            {getLoadingMessages().map((msg, i) => (
              <motion.p
                key={i}
                className="text-xs text-muted-foreground/50 font-mono"
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.5 }}
              >
                {msg}
              </motion.p>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {result && !studyMut.isPending && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-5"
          >
            {/* Summary */}
            <div className="rounded-xl border border-border/50 bg-card/60 p-5">
              <h3 className="text-xs font-semibold uppercase tracking-widest text-primary mb-3 flex items-center gap-2">
                <BookOpen className="h-3 w-3" /> Análise de Estudo
                {mode === "github" && <span className="text-muted-foreground font-normal normal-case">— {githubUrl.replace("https://github.com/", "")}</span>}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{result.summary}</p>
            </div>

            {/* Proposed skills */}
            {result.proposedSkills?.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                  {result.proposedSkills.length} Habilidades Propostas — Autorize para Adquirir
                </h3>
                <div className="space-y-3">
                  {result.proposedSkills.map((skill: any, i: number) => {
                    const isAcquired = acquiredIds.has(skill.id);
                    return (
                      <motion.div
                        key={skill.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.08 }}
                        className={cn(
                          "rounded-xl border p-5 flex items-start gap-4 transition-all",
                          isAcquired ? "border-green-500/40 bg-green-500/5" : "border-border/50 bg-card/60"
                        )}
                        style={!isAcquired ? { borderColor: `${skill.color}30` } : {}}
                      >
                        <div className="h-12 w-12 rounded-xl flex items-center justify-center text-xl font-bold flex-shrink-0 border"
                          style={{ backgroundColor: `${skill.color}15`, borderColor: `${skill.color}40`, color: skill.color }}>
                          {skill.name?.charAt(0)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <h4 className="font-semibold text-sm">{skill.name}</h4>
                            <span className="text-[10px] px-2 py-0.5 rounded-full border" style={{ borderColor: `${skill.color}40`, color: skill.color }}>{skill.category}</span>
                            <span className="text-[10px] text-green-400 font-mono">+{skill.xpValue} XP</span>
                          </div>
                          <p className="text-xs text-muted-foreground mb-2 leading-relaxed">{skill.description}</p>
                          {skill.principles?.length > 0 && (
                            <ul className="space-y-0.5">
                              {skill.principles.map((p: string, j: number) => (
                                <li key={j} className="flex items-center gap-1 text-xs text-muted-foreground">
                                  <ChevronRight className="h-3 w-3 text-primary/50 flex-shrink-0" />
                                  {p}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                        <div className="flex-shrink-0">
                          {isAcquired ? (
                            <div className="flex items-center gap-1 text-green-400 text-sm">
                              <CheckCircle className="h-5 w-5" />
                              <span className="text-xs">Adquirida</span>
                            </div>
                          ) : (
                            <button
                              onClick={() => handleAcquire(skill.id)}
                              disabled={acquireMut.isPending}
                              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-xs font-medium hover:opacity-90 transition-opacity disabled:opacity-50 shadow-[0_0_15px_hsl(var(--primary)/0.3)]"
                            >
                              <Zap className="h-3 w-3" />
                              Autorizar
                            </button>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
                {result.proposedSkills.every((_: any, i: number) => acquiredIds.has(result.proposedSkills[i].id)) && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-4 p-4 rounded-xl border border-green-500/30 bg-green-500/5 text-center"
                  >
                    <CheckCircle className="w-6 h-6 text-green-400 mx-auto mb-1" />
                    <p className="text-sm text-green-400 font-medium">Todas as habilidades adquiridas!</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Continue estudando para expandir seu conhecimento.</p>
                  </motion.div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
