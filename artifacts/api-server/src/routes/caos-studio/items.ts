import { Router } from "express";
import { db } from "@workspace/db";
import { hubItems } from "@workspace/db";
import { eq } from "drizzle-orm";

const router = Router();

router.get("/", async (req, res) => {
  try {
    const { type, rarity } = req.query;
    let items = await db.select().from(hubItems).orderBy(hubItems.createdAt);
    if (type) items = items.filter((i) => i.type === type);
    if (rarity) items = items.filter((i) => i.rarity === rarity);
    res.json(items);
  } catch {
    res.status(500).json({ error: "Falha ao buscar artefatos" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { name, type, rarity = "Common", tags = [], previewUrl, description, metadata } = req.body;
    const [item] = await db.insert(hubItems).values({ name, type, rarity, tags, previewUrl, description, metadata }).returning();
    res.status(201).json(item);
  } catch {
    res.status(500).json({ error: "Falha ao criar artefato" });
  }
});

router.get("/stats", async (_req, res) => {
  try {
    const items = await db.select().from(hubItems);
    const byType: Record<string, number> = {};
    const byRarity: Record<string, number> = {};
    for (const item of items) {
      byType[item.type] = (byType[item.type] || 0) + 1;
      byRarity[item.rarity] = (byRarity[item.rarity] || 0) + 1;
    }
    const recentDrops = [...items]
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 5);
    res.json({ total: items.length, byType, byRarity, legendaryCount: byRarity["Legendary"] || 0, recentDrops });
  } catch {
    res.status(500).json({ error: "Falha ao buscar estatísticas" });
  }
});

router.get("/recent", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit as string) || 10;
    const items = await db.select().from(hubItems).orderBy(hubItems.createdAt);
    const sorted = items
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, limit);
    res.json(sorted);
  } catch {
    res.status(500).json({ error: "Falha ao buscar artefatos recentes" });
  }
});

// ── Fusão de Artefatos ─────────────────────────────────────────────────────

const RARITY_ORDER = ["Common", "Rare", "Epic", "Legendary"] as const;

router.post("/fusao", async (req, res) => {
  try {
    const { itemAId, itemBId } = req.body as { itemAId: number; itemBId: number };

    if (!itemAId || !itemBId) {
      return res.status(400).json({ error: "Informe os dois artefatos para fundir." });
    }
    if (itemAId === itemBId) {
      return res.status(400).json({ error: "Selecione dois artefatos distintos para fundir." });
    }

    const [itemA] = await db.select().from(hubItems).where(eq(hubItems.id, itemAId));
    const [itemB] = await db.select().from(hubItems).where(eq(hubItems.id, itemBId));

    if (!itemA || !itemB) {
      return res.status(404).json({ error: "Um ou ambos os artefatos não foram encontrados." });
    }

    // Raridade resultante: um nível acima do maior input (teto em Lendário)
    const idxA = RARITY_ORDER.indexOf(itemA.rarity as any);
    const idxB = RARITY_ORDER.indexOf(itemB.rarity as any);
    const maxIdx = Math.max(idxA >= 0 ? idxA : 0, idxB >= 0 ? idxB : 0);
    const fusedIdx = Math.min(maxIdx + 1, RARITY_ORDER.length - 1);
    const fusedRarity = RARITY_ORDER[fusedIdx];

    // Tipo vem do artefato de raridade mais alta; empate = itemA
    const fusedType = idxA >= idxB ? itemA.type : itemB.type;

    // Valores padrão (fallback sem IA)
    let fusedName = `${itemA.name} × ${itemB.name}`;
    let fusedDescription =
      `Fusão de "${itemA.name}" e "${itemB.name}". ` +
      `O CAOS absorveu a essência de ambos e manifestou uma nova forma ${fusedRarity === "Legendary" ? "lendária" : "elevada"}.`;
    let fusedTags = [...new Set([...(itemA.tags ?? []), ...(itemB.tags ?? [])])].slice(0, 8);

    // Tentativa de geração com IA
    try {
      const mod = await import("@workspace/integrations-openai-ai-server");
      const openai = mod.openai;
      const prompt =
        `Você é o CAOS, um sistema RPG de IA criativa em português. Dois artefatos foram fundidos:\n` +
        `- A: "${itemA.name}" (${itemA.type}, ${itemA.rarity}) — ${itemA.description ?? "sem lore"}\n` +
        `- B: "${itemB.name}" (${itemB.type}, ${itemB.rarity}) — ${itemB.description ?? "sem lore"}\n` +
        `Resultado: artefato ${fusedRarity}. Responda SOMENTE com JSON:\n` +
        `{"name":"<nome criativo em pt-BR>","description":"<lore épico 1-2 frases em pt-BR>","tags":["<tag1>","<tag2>","<tag3>"]}`;

      const completion = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        max_completion_tokens: 200,
        messages: [{ role: "user", content: prompt }],
      });

      const raw = completion.choices[0]?.message?.content?.trim() ?? "";
      const cleaned = raw.replace(/^```(?:json)?\s*/i, "").replace(/```\s*$/, "").trim();
      const parsed = JSON.parse(cleaned);
      if (typeof parsed.name === "string" && parsed.name) fusedName = parsed.name;
      if (typeof parsed.description === "string" && parsed.description) fusedDescription = parsed.description;
      if (Array.isArray(parsed.tags)) fusedTags = (parsed.tags as string[]).slice(0, 8);
    } catch {
      // silently fallback to template
    }

    const [fusedItem] = await db
      .insert(hubItems)
      .values({
        name: fusedName,
        type: fusedType,
        rarity: fusedRarity,
        tags: fusedTags,
        description: fusedDescription,
        metadata: {
          fusedFrom: [itemAId, itemBId],
          fusedAt: new Date().toISOString(),
          originNames: [itemA.name, itemB.name],
        },
      })
      .returning();

    res.status(201).json(fusedItem);
  } catch (err) {
    res.status(500).json({ error: "Falha na fusão de artefatos." });
  }
});

// ── CRUD individual ────────────────────────────────────────────────────────

router.get("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [item] = await db.select().from(hubItems).where(eq(hubItems.id, id));
    if (!item) return res.status(404).json({ error: "Artefato não encontrado" });
    res.json(item);
  } catch {
    res.status(500).json({ error: "Falha ao buscar artefato" });
  }
});

router.patch("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { name, rarity, tags, previewUrl, description, metadata } = req.body;
    const updates: Partial<typeof hubItems.$inferInsert> = {};
    if (name !== undefined) updates.name = name;
    if (rarity !== undefined) updates.rarity = rarity;
    if (tags !== undefined) updates.tags = tags;
    if (previewUrl !== undefined) updates.previewUrl = previewUrl;
    if (description !== undefined) updates.description = description;
    if (metadata !== undefined) updates.metadata = metadata;
    const [item] = await db.update(hubItems).set(updates).where(eq(hubItems.id, id)).returning();
    if (!item) return res.status(404).json({ error: "Artefato não encontrado" });
    res.json(item);
  } catch {
    res.status(500).json({ error: "Falha ao atualizar artefato" });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    await db.delete(hubItems).where(eq(hubItems.id, id));
    res.status(204).send();
  } catch {
    res.status(500).json({ error: "Falha ao destruir artefato" });
  }
});

router.post("/:id/clone", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [original] = await db.select().from(hubItems).where(eq(hubItems.id, id));
    if (!original) return res.status(404).json({ error: "Artefato não encontrado" });
    const [cloned] = await db
      .insert(hubItems)
      .values({
        name: `${original.name} (Clone)`,
        type: original.type,
        rarity: original.rarity,
        tags: original.tags,
        previewUrl: original.previewUrl,
        description: original.description,
        metadata: original.metadata,
      })
      .returning();
    res.status(201).json(cloned);
  } catch {
    res.status(500).json({ error: "Falha ao clonar artefato" });
  }
});

export default router;
