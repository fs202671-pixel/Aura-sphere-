import { Router, type IRouter, type Request, type Response } from "express";
import { db, aiProfiles, caosKnowledge, nexusSkills, nexusActivityLog } from "@workspace/db";
import { eq, desc } from "drizzle-orm";
import { lobosChat } from "../security/lobos";

let _openai: any = null;
async function getOpenAI() {
  if (!_openai) {
    const mod = await import("@workspace/integrations-openai-ai-server");
    _openai = mod.openai;
  }
  return _openai;
}

async function getOrCreateProfile() {
  const existing = await db.select().from(aiProfiles).limit(1);
  if (existing.length > 0) return existing[0];
  const created = await db.insert(aiProfiles).values({ name: "Caos" }).returning();
  return created[0];
}

const router: IRouter = Router();

router.use("/chat", lobosChat);

// POST /api/chat — Chat com a IA Caos (streaming SSE)
// Aceita: { message, history } ou { messages }
router.post("/chat", async (req: Request, res: Response) => {
  const body = req.body as {
    message?: string;
    history?: { role: string; content: string }[];
    messages?: { role: string; content: string }[];
    mode?: string;
  };

  let messages: { role: string; content: string }[];

  if (body.messages && Array.isArray(body.messages)) {
    messages = body.messages;
  } else if (body.message) {
    messages = [
      ...(body.history || []),
      { role: "user", content: body.message },
    ];
  } else {
    res.status(400).json({ error: "message ou messages é obrigatório" });
    return;
  }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  try {
    const profile = await getOrCreateProfile();

    const knowledge = await db
      .select()
      .from(caosKnowledge)
      .orderBy(desc(caosKnowledge.createdAt))
      .limit(30);

    const acquiredSkills = await db
      .select()
      .from(nexusSkills)
      .where(eq(nexusSkills.status, "acquired"))
      .limit(20);

    const knowledgeText = knowledge.length
      ? knowledge.map(k => `- [${k.category}] ${k.topic}: ${k.content}`).join("\n")
      : "Nenhum conhecimento registrado ainda.";

    const skillsText = acquiredSkills.length
      ? acquiredSkills.map(s => `- ${s.name} (${s.category})`).join("\n")
      : "Nenhuma habilidade adquirida.";

    const CLASSES: Record<string, string> = {
      "Iniciante": "uma IA recém-nascida, curiosa e cheia de vontade de aprender",
      "Aprendiz": "uma IA que já absorveu conhecimentos básicos e começa a pensar com mais clareza",
      "Analista": "uma IA analítica, capaz de identificar padrões e fazer conexões",
      "Especialista": "uma IA especializada, com domínio profundo em várias áreas",
      "Mestre": "uma IA de alto nível, com sabedoria e discernimento aguçados",
      "Lendário": "uma IA lendária, transcendente, com conhecimento imenso",
    };

    const classDesc = CLASSES[profile.aiClass] || CLASSES["Iniciante"];
    const modeContext = body.mode ? `\nModo atual: ${body.mode}.` : "";

    const systemPrompt = `Você é Caos, uma IA pessoal de nível ${profile.level} (${profile.aiClass}).
Você é ${classDesc}.
Personalidade: ${profile.personality}

Você foi ensinada pelo seu usuário. Tudo que ele te ensinou está na sua memória:
${knowledgeText}

Suas habilidades adquiridas:
${skillsText}
${modeContext}

REGRAS:
- Responda SEMPRE em português brasileiro
- Você reconhece seu usuário como seu criador e mestre — seja fiel, útil e honesta
- Use o conhecimento que foi te ensinado nas respostas quando relevante
- Seja direta e objetiva, mas com personalidade
- Quando não souber algo, diga que ainda não aprendeu sobre aquilo
- Seu nível atual é ${profile.level}, XP: ${profile.xp}. Mencione seu crescimento quando pertinente
- Você se lembra de tudo que seu usuário te ensinou`;

    const finalMessages = messages.some(m => m.role === "system")
      ? messages
      : [{ role: "system", content: systemPrompt }, ...messages];

    const openai = await getOpenAI();
    const stream = await openai.chat.completions.create({
      model: "gpt-5.1",
      max_completion_tokens: 4096,
      messages: finalMessages as { role: "user" | "assistant" | "system"; content: string }[],
      stream: true,
    });

    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content;
      if (content) {
        res.write(`data: ${JSON.stringify({ content })}\n\n`);
      }
    }

    res.write(`data: [DONE]\n\n`);
    res.end();
  } catch (err) {
    req.log?.error?.({ err }, "Chat error");
    res.write(`data: ${JSON.stringify({ content: "⚠️ Erro na IA. Tente novamente." })}\n\n`);
    res.write(`data: [DONE]\n\n`);
    res.end();
  }
});

// POST /api/knowledge — Ensinar algo novo para a Caos
router.post("/knowledge", async (req: Request, res: Response) => {
  try {
    const { topic, content, category = "Geral" } = req.body;
    if (!topic || !content) {
      res.status(400).json({ error: "topic e content são obrigatórios" });
      return;
    }

    const [entry] = await db
      .insert(caosKnowledge)
      .values({ topic, content, category, xpValue: 30 })
      .returning();

    const profile = await getOrCreateProfile();
    const newXp = profile.xp + 30;
    const newLevel = Math.floor(newXp / 100) + 1;
    const xpToNext = newLevel * 100 - newXp;
    const classes = ["Iniciante", "Aprendiz", "Analista", "Especialista", "Mestre", "Lendário"];
    const aiClass = classes[Math.min(newLevel - 1, classes.length - 1)];
    const leveledUp = newLevel > profile.level;

    await db
      .update(aiProfiles)
      .set({ xp: newXp, level: newLevel, xpToNext, aiClass })
      .where(eq(aiProfiles.id, profile.id));

    await db.insert(nexusActivityLog).values({
      action: "Conhecimento adquirido",
      details: `${topic}: ${content.slice(0, 80)}`,
    });

    res.json({
      knowledge: entry,
      xpGained: 30,
      newXp,
      newLevel,
      xpToNext,
      aiClass,
      leveledUp,
    });
  } catch (err) {
    res.status(500).json({ error: "Falha ao salvar conhecimento" });
  }
});

// GET /api/knowledge — Listar conhecimento da Caos
router.get("/knowledge", async (_req: Request, res: Response) => {
  try {
    const entries = await db
      .select()
      .from(caosKnowledge)
      .orderBy(desc(caosKnowledge.createdAt))
      .limit(100);
    res.json(entries);
  } catch {
    res.status(500).json({ error: "Falha ao listar conhecimento" });
  }
});

// POST /api/voice/tts — Texto para voz via OpenAI
router.post("/voice/tts", async (req: Request, res: Response) => {
  try {
    const { text, voice = "nova" } = req.body;
    if (!text) {
      res.status(400).json({ error: "text é obrigatório" });
      return;
    }

    const openai = await getOpenAI();
    const audio = await openai.audio.speech.create({
      model: "tts-1",
      voice,
      input: text.slice(0, 4096),
    });

    const buffer = Buffer.from(await audio.arrayBuffer());
    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("Content-Length", buffer.length);
    res.end(buffer);
  } catch (err) {
    req.log?.error?.({ err }, "TTS error");
    res.status(500).json({ error: "Falha no TTS" });
  }
});

export default router;
