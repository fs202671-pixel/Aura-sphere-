import { Router, type IRouter, type Request, type Response } from "express";
import { db, skillsTable } from "@workspace/db";
import { eq, and } from "drizzle-orm";
import { openai } from "@workspace/integrations-openai-ai-server";
import { getAuth } from "@clerk/express";

const router: IRouter = Router();

/** Returns the authenticated userId (Clerk) or a validated local/demo ID. Returns null if neither. */
function resolveUserId(req: Request): string | null {
  const auth = getAuth(req);
  if (auth?.userId) return auth.userId;
  const fromQuery = req.query?.user_id as string | undefined;
  const fromBody = (req.body as Record<string, unknown>)?.userId as string | undefined;
  const candidate = (fromQuery || fromBody || "").trim();
  // Only accept local_ or demo_ prefixed IDs for unauthenticated requests
  if (/^(local_|demo_)[a-zA-Z0-9_-]{4,}$/.test(candidate)) return candidate;
  return null;
}

// List skills for a user
router.get("/skills", async (req, res) => {
  const userId = resolveUserId(req);
  if (!userId) { res.status(400).json({ error: "user_id required" }); return; }
  try {
    const skills = await db
      .select()
      .from(skillsTable)
      .where(eq(skillsTable.userId, userId))
      .orderBy(skillsTable.createdAt);
    res.json({ skills });
  } catch (err) {
    req.log.error({ err }, "Error fetching skills");
    res.status(500).json({ error: "Internal error" });
  }
});

// AI studies a topic and streams the result
router.post("/skills/study", async (req, res) => {
  const body = req.body as { userId?: string; topic?: string; type?: "topic" | "repo" };
  const { userId, topic, type = "topic" } = body;
  if (!userId || !topic) { res.status(400).json({ error: "userId and topic required" }); return; }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const send = (data: object) => res.write(`data: ${JSON.stringify(data)}\n\n`);

  try {
    send({ type: "thinking", content: type === "repo" ? `Analisando repositório ${topic}...` : `Estudando ${topic}...` });

    const systemPrompt = type === "repo"
      ? `Você é uma IA que analisa repositórios de código e extrai habilidades aprendíveis.
Quando o usuário te dá uma URL ou nome de repositório, você:
1. Identifica os conceitos técnicos principais
2. Descreve o que pode ser aprendido
3. Cria uma habilidade estruturada no formato JSON

Responda em português brasileiro.`
      : `Você é uma IA que estuda tópicos em profundidade e cria habilidades de conhecimento.
Quando o usuário te pede para estudar um tópico, você:
1. Explica os fundamentos
2. Descreve aplicações práticas
3. Cria uma habilidade estruturada

Responda em português brasileiro.`;

    const userPrompt = type === "repo"
      ? `Analise este repositório e extraia as habilidades técnicas principais: ${topic}

Retorne um JSON com exatamente este formato:
{
  "name": "Nome da Habilidade",
  "description": "Descrição curta (1-2 frases)",
  "category": "uma dessas: programação | segurança | dados | automação | web | mobile | ai | geral",
  "icon": "um emoji relevante",
  "level": número de 1 a 5 baseado na complexidade,
  "xp": número de 100 a 500 baseado na profundidade,
  "knowledge": "Conhecimento completo sobre o tópico em markdown (pelo menos 300 palavras). Inclua: fundamentos, como funciona, exemplos práticos, casos de uso reais, técnicas avançadas."
}`
      : `Estude este tópico em profundidade: ${topic}

Retorne um JSON com exatamente este formato:
{
  "name": "Nome da Habilidade",
  "description": "Descrição curta (1-2 frases)",
  "category": "uma dessas: programação | segurança | dados | automação | web | mobile | ai | geral",
  "icon": "um emoji relevante",
  "level": número de 1 a 5 baseado na complexidade,
  "xp": número de 100 a 500 baseado na profundidade,
  "knowledge": "Conhecimento completo sobre o tópico em markdown (pelo menos 300 palavras). Inclua: fundamentos, como funciona, exemplos práticos, casos de uso reais, técnicas avançadas."
}`;

    let fullContent = "";

    const stream = await openai.chat.completions.create({
      model: "gpt-5-mini",
      max_completion_tokens: 8192,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
      stream: true,
    });

    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content;
      if (content) {
        fullContent += content;
        send({ type: "progress", content });
      }
    }

    // Parse the JSON result
    const jsonMatch = fullContent.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("No JSON in response");

    const skill = JSON.parse(jsonMatch[0]) as {
      name: string;
      description: string;
      category: string;
      icon: string;
      level: number;
      xp: number;
      knowledge: string;
    };

    send({ type: "skill", skill });
    send({ type: "done" });
    res.end();
  } catch (err) {
    req.log.error({ err }, "Error studying topic");
    send({ type: "error", message: "Erro ao estudar o tópico. Tente novamente." });
    res.end();
  }
});

// Save a confirmed skill to DB
router.post("/skills/confirm", async (req, res) => {
  const body = req.body as {
    userId?: string;
    name?: string;
    description?: string;
    category?: string;
    icon?: string;
    level?: number;
    xp?: number;
    knowledge?: string;
  };
  const { userId, name, description, category = "geral", icon = "⚡", level = 1, xp = 100, knowledge = "" } = body;
  if (!userId || !name || !description) {
    res.status(400).json({ error: "userId, name, and description required" });
    return;
  }
  try {
    const [skill] = await db
      .insert(skillsTable)
      .values({ userId, name, description, category, icon, level, xp, knowledge, status: "ready", isEquipped: false, fusionParents: [] })
      .returning();
    res.status(201).json({ skill });
  } catch (err) {
    req.log.error({ err }, "Error confirming skill");
    res.status(500).json({ error: "Internal error" });
  }
});

// Equip / unequip a skill
router.patch("/skills/:id/equip", async (req, res) => {
  const { id } = req.params;
  const body = req.body as { userId?: string; equip?: boolean };
  const { userId, equip } = body;
  if (!userId) { res.status(400).json({ error: "userId required" }); return; }
  try {
    const [skill] = await db
      .update(skillsTable)
      .set({ isEquipped: equip ?? true, status: equip ? "equipped" : "ready" })
      .where(and(eq(skillsTable.id, id), eq(skillsTable.userId, userId)))
      .returning();
    if (!skill) { res.status(404).json({ error: "Skill not found" }); return; }
    res.json({ skill });
  } catch (err) {
    req.log.error({ err }, "Error equipping skill");
    res.status(500).json({ error: "Internal error" });
  }
});

// Delete a skill
router.delete("/skills/:id", async (req, res) => {
  const { id } = req.params;
  const { user_id } = req.query;
  if (!user_id || typeof user_id !== "string") {
    res.status(400).json({ error: "user_id required" });
    return;
  }
  try {
    await db.delete(skillsTable).where(and(eq(skillsTable.id, id), eq(skillsTable.userId, user_id)));
    res.json({ success: true });
  } catch (err) {
    req.log.error({ err }, "Error deleting skill");
    res.status(500).json({ error: "Internal error" });
  }
});

// Fuse two or more skills into a new one
router.post("/skills/fuse", async (req, res) => {
  const body = req.body as { userId?: string; skillIds?: string[] };
  const { userId, skillIds } = body;
  if (!userId || !skillIds || skillIds.length < 2) {
    res.status(400).json({ error: "userId and at least 2 skillIds required" });
    return;
  }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const send = (data: object) => res.write(`data: ${JSON.stringify(data)}\n\n`);

  try {
    const skills = await db
      .select()
      .from(skillsTable)
      .where(eq(skillsTable.userId, userId));

    const toFuse = skills.filter((s) => skillIds.includes(s.id));
    if (toFuse.length < 2) {
      send({ type: "error", message: "Habilidades não encontradas." });
      res.end();
      return;
    }

    const names = toFuse.map((s) => s.name).join(" + ");
    send({ type: "thinking", content: `Fundindo ${names}...` });

    const knowledgeSummary = toFuse
      .map((s) => `## ${s.name}\n${s.knowledge.substring(0, 500)}`)
      .join("\n\n");

    const prompt = `Você é um mago da IA que funde habilidades para criar algo mais poderoso.

Aqui estão as habilidades a fundir:
${knowledgeSummary}

Crie uma nova habilidade FUSIONADA que combine os poderes de todas as anteriores em algo único e mais poderoso.
A habilidade fundida deve ter um nome criativo que reflita a fusão.

Retorne um JSON:
{
  "name": "Nome épico da fusão",
  "description": "Descrição da habilidade fundida (1-2 frases)",
  "category": "uma dessas: programação | segurança | dados | automação | web | mobile | ai | geral",
  "icon": "um emoji épico",
  "level": número de 1 a 10 (deve ser maior que os pais),
  "xp": número (soma dos XPs dos pais + 200),
  "knowledge": "Conhecimento combinado das habilidades fundidas em markdown. Explique como as duas habilidades se complementam e criam algo único e mais poderoso."
}`;

    let fullContent = "";
    const stream = await openai.chat.completions.create({
      model: "gpt-5-mini",
      max_completion_tokens: 8192,
      messages: [{ role: "user", content: prompt }],
      stream: true,
    });

    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content;
      if (content) {
        fullContent += content;
        send({ type: "progress", content });
      }
    }

    const jsonMatch = fullContent.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("No JSON");
    const fusedData = JSON.parse(jsonMatch[0]) as {
      name: string; description: string; category: string; icon: string; level: number; xp: number; knowledge: string;
    };

    send({ type: "skill", skill: { ...fusedData, fusionParents: skillIds } });
    send({ type: "done" });
    res.end();
  } catch (err) {
    req.log.error({ err }, "Error fusing skills");
    send({ type: "error", message: "Erro ao fundir habilidades." });
    res.end();
  }
});

export default router;
