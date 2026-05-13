import { Router } from "express";
import { db } from "@workspace/db";
import { hubAgents } from "@workspace/db";
import { eq, sql } from "drizzle-orm";

const router = Router();

router.get("/", async (_req, res) => {
  try {
    const agents = await db.select().from(hubAgents).orderBy(hubAgents.createdAt);
    res.json(agents);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch agents" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { name, behavior, promptBase = "", rarity = "Common", description, avatar } = req.body;
    const [agent] = await db.insert(hubAgents).values({ name, behavior, promptBase, rarity, description, avatar }).returning();
    res.status(201).json(agent);
  } catch (err) {
    res.status(500).json({ error: "Failed to create agent" });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [agent] = await db.select().from(hubAgents).where(eq(hubAgents.id, id));
    if (!agent) return res.status(404).json({ error: "Agent not found" });
    res.json(agent);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch agent" });
  }
});

router.patch("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { name, behavior, promptBase, rarity, description, avatar } = req.body;
    const updates: Partial<typeof hubAgents.$inferInsert> = {};
    if (name !== undefined) updates.name = name;
    if (behavior !== undefined) updates.behavior = behavior;
    if (promptBase !== undefined) updates.promptBase = promptBase;
    if (rarity !== undefined) updates.rarity = rarity;
    if (description !== undefined) updates.description = description;
    if (avatar !== undefined) updates.avatar = avatar;
    const [agent] = await db.update(hubAgents).set(updates).where(eq(hubAgents.id, id)).returning();
    if (!agent) return res.status(404).json({ error: "Agent not found" });
    res.json(agent);
  } catch (err) {
    res.status(500).json({ error: "Failed to update agent" });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    await db.delete(hubAgents).where(eq(hubAgents.id, id));
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: "Failed to delete agent" });
  }
});

router.post("/:id/run", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { prompt } = req.body;
    const [agent] = await db.select().from(hubAgents).where(eq(hubAgents.id, id));
    if (!agent) return res.status(404).json({ error: "Agent not found" });
    await db.update(hubAgents).set({ runCount: sql`${hubAgents.runCount} + 1` }).where(eq(hubAgents.id, id));
    const result = `[${agent.name}] Analyzing: "${prompt}"\n\nBehavior: ${agent.behavior}\n\nProcessing complete. Response generated based on configured prompt base and behavior directives.`;
    res.json({
      agentId: id,
      prompt,
      result,
      runAt: new Date().toISOString(),
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to run agent" });
  }
});

export default router;
