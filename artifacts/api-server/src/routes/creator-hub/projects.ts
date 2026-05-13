import { Router } from "express";
import { db } from "@workspace/db";
import { hubProjects } from "@workspace/db";
import { eq } from "drizzle-orm";

const router = Router();

router.get("/", async (_req, res) => {
  try {
    const projects = await db.select().from(hubProjects).orderBy(hubProjects.createdAt);
    res.json(projects);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch projects" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { name, description, rarity = "Common", themeId, agentIds = [], skillIds = [] } = req.body;
    const [project] = await db.insert(hubProjects).values({ name, description, rarity, themeId, agentIds, skillIds }).returning();
    res.status(201).json(project);
  } catch (err) {
    res.status(500).json({ error: "Failed to create project" });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [project] = await db.select().from(hubProjects).where(eq(hubProjects.id, id));
    if (!project) return res.status(404).json({ error: "Project not found" });
    res.json(project);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch project" });
  }
});

router.patch("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { name, description, status, themeId, agentIds, skillIds } = req.body;
    const updates: Partial<typeof hubProjects.$inferInsert> = {};
    if (name !== undefined) updates.name = name;
    if (description !== undefined) updates.description = description;
    if (status !== undefined) updates.status = status;
    if (themeId !== undefined) updates.themeId = themeId;
    if (agentIds !== undefined) updates.agentIds = agentIds;
    if (skillIds !== undefined) updates.skillIds = skillIds;
    const [project] = await db.update(hubProjects).set(updates).where(eq(hubProjects.id, id)).returning();
    if (!project) return res.status(404).json({ error: "Project not found" });
    res.json(project);
  } catch (err) {
    res.status(500).json({ error: "Failed to update project" });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    await db.delete(hubProjects).where(eq(hubProjects.id, id));
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: "Failed to delete project" });
  }
});

router.post("/:id/build", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [project] = await db.select().from(hubProjects).where(eq(hubProjects.id, id));
    if (!project) return res.status(404).json({ error: "Project not found" });
    await db.update(hubProjects).set({ status: "building" }).where(eq(hubProjects.id, id));
    setTimeout(async () => {
      await db.update(hubProjects).set({ status: "complete" }).where(eq(hubProjects.id, id));
    }, 3000);
    res.json({
      success: true,
      message: `Build initiated for "${project.name}"`,
      projectId: id,
      generatedFiles: [
        "src/App.tsx",
        "src/components/Layout.tsx",
        "src/pages/Home.tsx",
        "package.json",
        "vite.config.ts",
        "tailwind.config.ts",
      ],
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to build project" });
  }
});

export default router;
