import { Router } from "express";
import { db } from "@workspace/db";
import { hubSkills } from "@workspace/db";
import { eq, sql } from "drizzle-orm";

const router = Router();

router.get("/", async (req, res) => {
  try {
    const { category } = req.query;
    let skills = await db.select().from(hubSkills).orderBy(hubSkills.createdAt);
    if (category) skills = skills.filter((s) => s.category === category);
    res.json(skills);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch skills" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { name, category, description, rarity = "Common", icon, behavior } = req.body;
    const [skill] = await db.insert(hubSkills).values({ name, category, description, rarity, icon, behavior }).returning();
    res.status(201).json(skill);
  } catch (err) {
    res.status(500).json({ error: "Failed to create skill" });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [skill] = await db.select().from(hubSkills).where(eq(hubSkills.id, id));
    if (!skill) return res.status(404).json({ error: "Skill not found" });
    res.json(skill);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch skill" });
  }
});

router.patch("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { name, description, category, icon, behavior } = req.body;
    const updates: Partial<typeof hubSkills.$inferInsert> = {};
    if (name !== undefined) updates.name = name;
    if (description !== undefined) updates.description = description;
    if (category !== undefined) updates.category = category;
    if (icon !== undefined) updates.icon = icon;
    if (behavior !== undefined) updates.behavior = behavior;
    const [skill] = await db.update(hubSkills).set(updates).where(eq(hubSkills.id, id)).returning();
    if (!skill) return res.status(404).json({ error: "Skill not found" });
    res.json(skill);
  } catch (err) {
    res.status(500).json({ error: "Failed to update skill" });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    await db.delete(hubSkills).where(eq(hubSkills.id, id));
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: "Failed to delete skill" });
  }
});

router.post("/:id/plug", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { targetType, targetId } = req.body;
    const [skill] = await db.select().from(hubSkills).where(eq(hubSkills.id, id));
    if (!skill) return res.status(404).json({ error: "Skill not found" });
    await db.update(hubSkills).set({ pluggedCount: sql`${hubSkills.pluggedCount} + 1` }).where(eq(hubSkills.id, id));
    res.json({
      success: true,
      message: `Skill "${skill.name}" plugged into ${targetType} #${targetId}`,
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to plug skill" });
  }
});

export default router;
