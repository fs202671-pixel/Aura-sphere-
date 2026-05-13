/**
 * 🧠 CAOS Memory — Sistema Unificado de Memória
 * Substitui stubs de /v1/memory/*
 */

import { Router, type IRouter, type Request, type Response } from "express";
import { db, caosMemory } from "@workspace/db";
import { eq, desc, and } from "drizzle-orm";
import { getAuth } from "@clerk/express";

const router: IRouter = Router();

// ── GET /v1/memory/list ─────────────────────────────────────────────────────
router.get("/v1/memory/list", async (req: Request, res: Response) => {
  try {
    const { userId } = getAuth(req);
    const memories = await db
      .select()
      .from(caosMemory)
      .where(userId ? eq(caosMemory.userId, userId) : undefined)
      .orderBy(desc(caosMemory.createdAt))
      .limit(100);
    res.json({ memories });
  } catch {
    res.status(500).json({ memories: [] });
  }
});

// ── POST /v1/memory ─────────────────────────────────────────────────────────
router.post("/v1/memory", async (req: Request, res: Response) => {
  try {
    const { userId } = getAuth(req);
    const { key, content, tags = [], source = "manual", importance = 1 } = req.body;
    if (!key || !content) {
      res.status(400).json({ error: "key e content são obrigatórios" });
      return;
    }
    const [mem] = await db
      .insert(caosMemory)
      .values({ userId: userId ?? null, key, content, tags, source, importance })
      .returning();
    res.status(201).json({ success: true, id: mem.id, memory: mem });
  } catch {
    res.status(500).json({ error: "Falha ao salvar memória" });
  }
});

// ── DELETE /v1/memory/:id ───────────────────────────────────────────────────
router.delete("/v1/memory/:id", async (req: Request, res: Response) => {
  try {
    const id = parseInt(req.params.id);
    const { userId } = getAuth(req);
    if (userId) {
      await db
        .delete(caosMemory)
        .where(and(eq(caosMemory.id, id), eq(caosMemory.userId, userId)));
    } else {
      await db.delete(caosMemory).where(eq(caosMemory.id, id));
    }
    res.json({ success: true });
  } catch {
    res.status(500).json({ error: "Falha ao deletar memória" });
  }
});

export default router;
