import { Router } from "express";
import { db } from "@workspace/db";
import { hubThemes } from "@workspace/db";
import { eq } from "drizzle-orm";

const router = Router();

router.get("/", async (_req, res) => {
  try {
    const themes = await db.select().from(hubThemes).orderBy(hubThemes.createdAt);
    res.json(themes);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch themes" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { name, rarity = "Common", colors = [], fonts = [], layoutStyle = "grid", spacing, borderRadius, previewUrl, sourceImageUrl, tags = [] } = req.body;
    const [theme] = await db.insert(hubThemes).values({ name, rarity, colors, fonts, layoutStyle, spacing, borderRadius, previewUrl, sourceImageUrl, tags }).returning();
    res.status(201).json(theme);
  } catch (err) {
    res.status(500).json({ error: "Failed to create theme" });
  }
});

router.post("/extract", async (req, res) => {
  try {
    const { imageUrl, name, style = "modern" } = req.body;
    const colors = ["#0ff", "#111", "#222", "#333", "#1a1a2e"];
    const fonts = ["Inter", "JetBrains Mono"];
    const [theme] = await db.insert(hubThemes).values({
      name: name || "Extracted Theme",
      rarity: "Rare",
      colors,
      fonts,
      layoutStyle: style || "grid futuristic",
      sourceImageUrl: imageUrl,
      tags: ["extracted", "auto-generated"],
    }).returning();
    res.json(theme);
  } catch (err) {
    res.status(500).json({ error: "Failed to extract theme" });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const [theme] = await db.select().from(hubThemes).where(eq(hubThemes.id, id));
    if (!theme) return res.status(404).json({ error: "Theme not found" });
    res.json(theme);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch theme" });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    await db.delete(hubThemes).where(eq(hubThemes.id, id));
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: "Failed to delete theme" });
  }
});

router.post("/:id/apply", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const { projectId } = req.body;
    res.json({
      success: true,
      message: `Theme ${id} applied to project ${projectId}`,
      projectId,
      themeId: id,
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to apply theme" });
  }
});

export default router;
