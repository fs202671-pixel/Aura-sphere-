import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import {
  aiProfiles,
  nexusSkills,
  nexusConversations,
  nexusMessages,
  nexusActivityLog,
} from "@workspace/db";
import { eq, desc, sql } from "drizzle-orm";

function parseId(param: string): number { return parseInt(param, 10); }

let _openai: any = null;
async function getOpenAI() {
  if (!_openai) {
    try {
      const mod = await import("@workspace/integrations-openai-ai-server");
      _openai = mod.openai;
    } catch {
      throw new Error("OpenAI integration not provisioned");
    }
  }
  return _openai;
}
const UpdateAiProfileBody = { parse: (b: any) => b };
const CreateConversationBody = { parse: (b: any) => b };
const SendMessageBody = { parse: (b: any) => b };
const CreateSkillBody = { parse: (b: any) => b };
const UpdateSkillBody = { parse: (b: any) => b };
const StudyTopicBody = { parse: (b: any) => b };
const FuseSkillsBody = { parse: (b: any) => b };
const IdParams = { parse: (b: { id: number }) => b };

const router: IRouter = Router();

async function getOrCreateProfile() {
  const existing = await db.select().from(aiProfiles).limit(1);
  if (existing.length > 0) return existing[0];
  const created = await db.insert(aiProfiles).values({}).returning();
  return created[0];
}

async function addActivity(action: string, details?: string) {
  await db.insert(nexusActivityLog).values({ action, details });
}

async function recalculateLevel(profileId: number) {
  const profile = await db.select().from(aiProfiles).where(eq(aiProfiles.id, profileId)).limit(1);
  if (!profile[0]) return;
  const acquiredSkills = await db.select().from(nexusSkills).where(eq(nexusSkills.status, "acquired"));
  const totalXp = acquiredSkills.reduce((sum, s) => sum + s.xpValue, 0);
  const level = Math.floor(totalXp / 100) + 1;
  const xpToNext = (level * 100) - totalXp;
  const classes = ["Iniciante", "Aprendiz", "Analista", "Especialista", "Mestre", "Lendário"];
  const aiClass = classes[Math.min(level - 1, classes.length - 1)];
  await db.update(aiProfiles).set({ xp: totalXp, level, xpToNext, aiClass }).where(eq(aiProfiles.id, profileId));
}

// GET /api/ai/profile
router.get("/ai/profile", async (_req, res) => {
  try {
    const profile = await getOrCreateProfile();
    res.json(profile);
  } catch (e) {
    res.status(500).json({ error: "Failed to get profile" });
  }
});

// PATCH /api/ai/profile
router.patch("/ai/profile", async (req, res) => {
  try {
    const body = UpdateAiProfileBody.parse(req.body);
    const profile = await getOrCreateProfile();
    const updated = await db.update(aiProfiles).set(body).where(eq(aiProfiles.id, profile.id)).returning();
    res.json(updated[0]);
  } catch (e) {
    res.status(400).json({ error: "Invalid request" });
  }
});

// GET /api/ai/stats
router.get("/ai/stats", async (_req, res) => {
  try {
    const profile = await getOrCreateProfile();
    const allSkills = await db.select().from(nexusSkills);
    const acquired = allSkills.filter(s => s.status === "acquired").length;
    const pending = allSkills.filter(s => s.status === "pending").length;
    const fused = allSkills.filter(s => s.status === "fused").length;
    const recentActivity = await db.select().from(nexusActivityLog).orderBy(desc(nexusActivityLog.createdAt)).limit(10);
    res.json({
      totalSkills: allSkills.length,
      acquiredSkills: acquired,
      pendingSkills: pending,
      fusedSkills: fused,
      totalXp: profile.xp,
      level: profile.level,
      recentActivity: recentActivity.map(a => a.action + (a.details ? `: ${a.details}` : "")),
    });
  } catch (e) {
    res.status(500).json({ error: "Failed to get stats" });
  }
});

// GET /api/ai/conversations
router.get("/ai/conversations", async (_req, res) => {
  try {
    const convos = await db.select().from(nexusConversations).orderBy(desc(nexusConversations.updatedAt));
    res.json(convos);
  } catch (e) {
    res.status(500).json({ error: "Failed to list conversations" });
  }
});

// POST /api/ai/conversations
router.post("/ai/conversations", async (req, res) => {
  try {
    const body = CreateConversationBody.parse(req.body);
    const created = await db.insert(nexusConversations).values(body).returning();
    res.status(201).json(created[0]);
  } catch (e) {
    res.status(400).json({ error: "Invalid request" });
  }
});

// GET /api/ai/conversations/:id/messages
router.get("/ai/conversations/:id/messages", async (req, res) => {
  try {
    const { id } = IdParams.parse({ id: Number(req.params.id) });
    const msgs = await db.select().from(nexusMessages).where(eq(nexusMessages.conversationId, id)).orderBy(nexusMessages.createdAt);
    res.json(msgs);
  } catch (e) {
    res.status(400).json({ error: "Invalid request" });
  }
});

// POST /api/ai/conversations/:id/messages (SSE)
router.post("/ai/conversations/:id/messages", async (req, res) => {
  try {
    const { id } = IdParams.parse({ id: Number(req.params.id) });
    const body = SendMessageBody.parse(req.body);

    // Save user message
    await db.insert(nexusMessages).values({ conversationId: id, role: "user", content: body.content });

    // Build context: get profile, skills, history
    const profile = await getOrCreateProfile();
    const acquiredSkills = await db.select().from(nexusSkills).where(eq(nexusSkills.status, "acquired")).limit(20);
    const history = await db.select().from(nexusMessages).where(eq(nexusMessages.conversationId, id)).orderBy(nexusMessages.createdAt);

    const skillsSummary = acquiredSkills.map(s => `${s.name} (${s.category}): ${s.description}`).join("\n");
    const systemPrompt = `Você é ${profile.name}, uma IA de nível ${profile.level} com classe "${profile.aiClass}".
Personalidade: ${profile.personality}
Descrição: ${profile.description}

Habilidades adquiridas:
${skillsSummary || "Nenhuma habilidade adquirida ainda."}

Responda sempre em português. Você é uma IA que está evoluindo e aprendendo. Use seu conhecimento das habilidades adquiridas quando relevante. Seja útil, perspicaz e fiel à sua personalidade.`;

    const messages: { role: "system" | "user" | "assistant"; content: string }[] = [
      { role: "system", content: systemPrompt },
      ...history.slice(-20).map(m => ({ role: m.role as "user" | "assistant", content: m.content })),
    ];

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    let fullResponse = "";
    const openai = await getOpenAI();
    const stream = await openai.chat.completions.create({
      model: "gpt-5.1",
      max_completion_tokens: 8192,
      messages,
      stream: true,
    });

    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content;
      if (content) {
        fullResponse += content;
        res.write(`data: ${JSON.stringify({ content })}\n\n`);
      }
    }

    await db.insert(nexusMessages).values({ conversationId: id, role: "assistant", content: fullResponse });
    await db.update(nexusConversations).set({ updatedAt: new Date() }).where(eq(nexusConversations.id, id));

    res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
    res.end();
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: "Failed to send message" });
  }
});

// GET /api/skills
router.get("/skills", async (req, res) => {
  try {
    const category = req.query.category as string | undefined;
    const status = req.query.status as string | undefined;
    let query = db.select().from(nexusSkills);
    const allSkills = await query.orderBy(desc(nexusSkills.createdAt));
    let filtered = allSkills;
    if (category) filtered = filtered.filter(s => s.category === category);
    if (status) filtered = filtered.filter(s => s.status === status);
    res.json(filtered);
  } catch (e) {
    res.status(500).json({ error: "Failed to list skills" });
  }
});

// POST /api/skills
router.post("/skills", async (req, res) => {
  try {
    const body = CreateSkillBody.parse(req.body);
    const created = await db.insert(nexusSkills).values({
      ...body,
      status: "acquired",
      xpValue: 50,
      principles: [],
    }).returning();
    await addActivity("Habilidade criada", body.name);
    res.status(201).json(created[0]);
  } catch (e) {
    res.status(400).json({ error: "Invalid request" });
  }
});

// GET /api/skills/categories
router.get("/skills/categories", async (_req, res) => {
  try {
    const allSkills = await db.select().from(nexusSkills);
    const categoryMap: Record<string, { count: number; icon: string; color: string }> = {};
    const categoryMeta: Record<string, { icon: string; color: string }> = {
      "Hacking": { icon: "Terminal", color: "#ef4444" },
      "Criptografia": { icon: "Lock", color: "#8b5cf6" },
      "Análise": { icon: "Search", color: "#3b82f6" },
      "Redes": { icon: "Network", color: "#06b6d4" },
      "IA": { icon: "Brain", color: "#f59e0b" },
      "Programação": { icon: "Code", color: "#10b981" },
      "Segurança": { icon: "Shield", color: "#f97316" },
      "Fusão": { icon: "Zap", color: "#ec4899" },
      "Geral": { icon: "Star", color: "#6366f1" },
    };
    for (const skill of allSkills) {
      if (!categoryMap[skill.category]) {
        const meta = categoryMeta[skill.category] || { icon: "Star", color: "#6366f1" };
        categoryMap[skill.category] = { count: 0, ...meta };
      }
      categoryMap[skill.category].count++;
    }
    const result = Object.entries(categoryMap).map(([name, data]) => ({ name, ...data }));
    res.json(result);
  } catch (e) {
    res.status(500).json({ error: "Failed to get categories" });
  }
});

// GET /api/skills/:id
router.get("/skills/:id", async (req, res) => {
  try {
    const { id } = IdParams.parse({ id: Number(req.params.id) });
    const skill = await db.select().from(nexusSkills).where(eq(nexusSkills.id, id)).limit(1);
    if (!skill[0]) return res.status(404).json({ error: "Skill not found" });
    res.json(skill[0]);
  } catch (e) {
    res.status(400).json({ error: "Invalid request" });
  }
});

// PATCH /api/skills/:id
router.patch("/skills/:id", async (req, res) => {
  try {
    const { id } = IdParams.parse({ id: Number(req.params.id) });
    const body = UpdateSkillBody.parse(req.body);
    const updated = await db.update(nexusSkills).set(body).where(eq(nexusSkills.id, id)).returning();
    if (!updated[0]) return res.status(404).json({ error: "Skill not found" });
    res.json(updated[0]);
  } catch (e) {
    res.status(400).json({ error: "Invalid request" });
  }
});

// DELETE /api/skills/:id
router.delete("/skills/:id", async (req, res) => {
  try {
    const { id } = IdParams.parse({ id: Number(req.params.id) });
    await db.delete(nexusSkills).where(eq(nexusSkills.id, id));
    res.status(204).end();
  } catch (e) {
    res.status(400).json({ error: "Invalid request" });
  }
});

// POST /api/skills/study
router.post("/skills/study", async (req, res) => {
  try {
    const body = StudyTopicBody.parse(req.body);
    const profile = await getOrCreateProfile();

    const systemPrompt = `Você é ${profile.name}, uma IA de nível ${profile.level}.
Você está estudando um novo tópico para propor habilidades ao seu usuário.
Responda APENAS com JSON válido, sem markdown, sem explicações extras.`;

    const userPrompt = `Estude este tópico e proponha 3 habilidades para adquirir:
Tópico: "${body.topic}"
${body.filter ? `Foco: ${body.filter}` : ""}

Retorne um JSON com este formato EXATO:
{
  "summary": "Resumo do que foi estudado em 2-3 frases",
  "skills": [
    {
      "name": "Nome da Habilidade",
      "category": "Categoria (Hacking/Criptografia/Análise/Redes/IA/Programação/Segurança/Geral)",
      "description": "Descrição detalhada do que essa habilidade permite fazer",
      "level": 1,
      "xpValue": 50,
      "icon": "Terminal",
      "color": "#ef4444",
      "principles": ["Princípio 1", "Princípio 2", "Princípio 3"]
    }
  ]
}`;

    const openai = await getOpenAI();
    const response = await openai.chat.completions.create({
      model: "gpt-5.1",
      max_completion_tokens: 2000,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
    });

    const raw = response.choices[0]?.message?.content ?? "{}";
    let parsed: { summary: string; skills: any[] };
    try {
      parsed = JSON.parse(raw);
    } catch {
      parsed = { summary: "Estudo concluído.", skills: [] };
    }

    const proposedSkills = [];
    for (const s of parsed.skills || []) {
      const created = await db.insert(nexusSkills).values({
        name: s.name,
        category: s.category || "Geral",
        description: s.description,
        level: s.level || 1,
        status: "pending",
        xpValue: s.xpValue || 50,
        icon: s.icon || "Zap",
        color: s.color || "#6366f1",
        principles: s.principles || [],
        studySource: body.topic,
      }).returning();
      proposedSkills.push(created[0]);
    }

    await addActivity("Estudo realizado", body.topic);

    res.json({
      summary: parsed.summary,
      proposedSkills,
    });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: "Failed to study topic" });
  }
});

// POST /api/skills/:id/acquire
router.post("/skills/:id/acquire", async (req, res) => {
  try {
    const { id } = IdParams.parse({ id: Number(req.params.id) });
    const updated = await db.update(nexusSkills).set({ status: "acquired" }).where(eq(nexusSkills.id, id)).returning();
    if (!updated[0]) return res.status(404).json({ error: "Skill not found" });

    const profile = await getOrCreateProfile();
    await recalculateLevel(profile.id);
    await addActivity("Habilidade adquirida", updated[0].name);

    const finalSkill = await db.select().from(nexusSkills).where(eq(nexusSkills.id, id)).limit(1);
    res.json(finalSkill[0]);
  } catch (e) {
    res.status(400).json({ error: "Invalid request" });
  }
});

// POST /api/skills/fuse
router.post("/skills/fuse", async (req, res) => {
  try {
    const body = FuseSkillsBody.parse(req.body);
    const sourceSkills = await db.select().from(nexusSkills).where(sql`${nexusSkills.id} = ANY(${body.skillIds}::int[])`);

    if (sourceSkills.length < 2) return res.status(400).json({ error: "Need at least 2 skills to fuse" });

    const profile = await getOrCreateProfile();

    const systemPrompt = `Você é ${profile.name}, uma IA de nível ${profile.level}.
Você está fundindo habilidades para criar uma nova e poderosa combinação.
Responda APENAS com JSON válido.`;

    const userPrompt = `Funda estas habilidades em uma nova:
${sourceSkills.map(s => `- ${s.name}: ${s.description}`).join("\n")}
${body.fusionName ? `Nome desejado: "${body.fusionName}"` : ""}

Retorne um JSON com este formato EXATO:
{
  "name": "Nome da Habilidade Fundida",
  "category": "Categoria",
  "description": "Descrição da habilidade combinada",
  "xpValue": 150,
  "icon": "Zap",
  "color": "#ec4899",
  "principles": ["Princípio combinado 1", "Princípio combinado 2"],
  "fusionDescription": "Explicação de como essas habilidades se combinaram e o que criaram"
}`;

    const openai = await getOpenAI();
    const response = await openai.chat.completions.create({
      model: "gpt-5.1",
      max_completion_tokens: 1000,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
    });

    const raw = response.choices[0]?.message?.content ?? "{}";
    let parsed: any;
    try {
      parsed = JSON.parse(raw);
    } catch {
      parsed = { name: "Fusão Desconhecida", category: "Fusão", description: "Uma poderosa fusão de habilidades.", xpValue: 150 };
    }

    const fusedSkill = await db.insert(nexusSkills).values({
      name: parsed.name || body.fusionName || "Habilidade Fundida",
      category: parsed.category || "Fusão",
      description: parsed.description || "Uma poderosa combinação de habilidades.",
      level: Math.max(...sourceSkills.map(s => s.level)) + 1,
      status: "fused",
      xpValue: parsed.xpValue || 150,
      icon: parsed.icon || "Zap",
      color: parsed.color || "#ec4899",
      principles: parsed.principles || [],
      parentSkillIds: body.skillIds,
    }).returning();

    const fpProfile = await getOrCreateProfile();
    await recalculateLevel(fpProfile.id);
    await addActivity("Fusão realizada", `${sourceSkills.map(s => s.name).join(" + ")} → ${fusedSkill[0].name}`);

    res.json({
      fusedSkill: fusedSkill[0],
      description: parsed.fusionDescription || "Habilidades fundidas com sucesso.",
    });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: "Failed to fuse skills" });
  }
});

export default router;
