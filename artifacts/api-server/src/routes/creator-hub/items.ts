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
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch items" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { name, type, rarity = "Common", tags = [], previewUrl, description, metadata } = req.body;
    const [item] = await db.insert(hubItems).values({ name, type, rarity, tags, previewUrl, description, metadata }).returning();
    res.status(201).json(item);
  } catch (err) {
    res.status(500).json({ error: "Failed to create item" });
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
    const recentDrops = [...items].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()).slice(0, 5);
    res.json({
      total: items.length,
      byType,
      byRarity,
      legendaryCount: byRarity["Legendary"] || 0,
      recentDrops,
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch stats" });
  }
});

router.get("/recent", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit as string) || 10;
    const items = await db.select().from(hubItems).orderBy(hubItems.createdAt);
    const sorted = items.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()).slice(0, limit);
    res.json(sorted);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch recent items" });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [item] = await db.select().from(hubItems).where(eq(hubItems.id, id));
    if (!item) return res.status(404).json({ error: "Item not found" });
    res.json(item);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch item" });
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
    if (!item) return res.status(404).json({ error: "Item not found" });
    res.json(item);
  } catch (err) {
    res.status(500).json({ error: "Failed to update item" });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    await db.delete(hubItems).where(eq(hubItems.id, id));
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: "Failed to delete item" });
  }
});

router.post("/:id/clone", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [original] = await db.select().from(hubItems).where(eq(hubItems.id, id));
    if (!original) return res.status(404).json({ error: "Item not found" });
    const [cloned] = await db.insert(hubItems).values({
      name: `${original.name} (Clone)`,
      type: original.type,
      rarity: original.rarity,
      tags: original.tags,
      previewUrl: original.previewUrl,
      description: original.description,
      metadata: original.metadata,
    }).returning();
    res.status(201).json(cloned);
  } catch (err) {
    res.status(500).json({ error: "Failed to clone item" });
  }
});

export default router;
