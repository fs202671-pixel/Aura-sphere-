/**
 * Rotas reais do sistema de segurança CAOS
 * Substitui os stubs de /v1/security/* e adiciona endpoints novos.
 */

import { Router, type IRouter, type Request, type Response } from "express";
import { db, caosAuditLog, caosSecurityIssues } from "@workspace/db";
import { eq, desc, gte, sql } from "drizzle-orm";
import { getFormigasStatus } from "../security/formigas";
import { getAbelhasStatus } from "../security/abelhas";
import { getRateLimitStatus } from "../security/lobos";

const router: IRouter = Router();

// ── GET /v1/security/issues ─────────────────────────────────────────────────
router.get("/v1/security/issues", async (_req: Request, res: Response) => {
  try {
    const issues = await db
      .select()
      .from(caosSecurityIssues)
      .orderBy(desc(caosSecurityIssues.createdAt))
      .limit(50);
    res.json({ issues });
  } catch {
    res.status(500).json({ issues: [] });
  }
});

// ── GET /v1/security/summary ────────────────────────────────────────────────
router.get("/v1/security/summary", async (_req: Request, res: Response) => {
  try {
    const abelhas = getAbelhasStatus();
    const [{ count: openCount }] = await db
      .select({ count: sql<number>`count(*)::int` })
      .from(caosSecurityIssues)
      .where(eq(caosSecurityIssues.resolved, false));

    res.json({
      score: abelhas.score,
      openIssues: openCount ?? 0,
      quarantinedIps: abelhas.quarantinedCount,
      reactionsToday: abelhas.reactionsToday,
    });
  } catch {
    res.status(500).json({ score: 100, issues: 0 });
  }
});

// ── POST /v1/security/audit ─────────────────────────────────────────────────
router.post("/v1/security/audit", async (req: Request, res: Response) => {
  try {
    const { action, ip = "manual", route = "/", method = "MANUAL", severity = "low", pattern, details } = req.body;
    if (!action) {
      res.status(400).json({ error: "action é obrigatório" });
      return;
    }
    await db.insert(caosAuditLog).values({ action, ip, route, method, severity, pattern, details });
    res.json({ success: true });
  } catch {
    res.status(500).json({ error: "Falha ao registrar auditoria" });
  }
});

// ── PATCH /v1/security/issues/:id/status ───────────────────────────────────
router.patch("/v1/security/issues/:id/status", async (req: Request, res: Response) => {
  try {
    const id = parseInt(req.params.id);
    const { resolved } = req.body;
    const [issue] = await db
      .update(caosSecurityIssues)
      .set({ resolved: !!resolved, resolvedAt: resolved ? new Date() : null })
      .where(eq(caosSecurityIssues.id, id))
      .returning();
    if (!issue) {
      res.status(404).json({ error: "Issue não encontrada" });
      return;
    }
    res.json(issue);
  } catch {
    res.status(500).json({ error: "Falha ao atualizar issue" });
  }
});

// ── GET /api/security/audit-log ─────────────────────────────────────────────
router.get("/api/security/audit-log", async (req: Request, res: Response) => {
  try {
    const limit = Math.min(parseInt(req.query.limit as string) || 50, 200);
    const logs = await db
      .select()
      .from(caosAuditLog)
      .orderBy(desc(caosAuditLog.createdAt))
      .limit(limit);
    res.json({ logs });
  } catch {
    res.status(500).json({ logs: [] });
  }
});

// ── GET /api/security/formigas/status ───────────────────────────────────────
router.get("/api/security/formigas/status", (_req: Request, res: Response) => {
  res.json(getFormigasStatus());
});

// ── GET /api/security/abelhas/status ────────────────────────────────────────
router.get("/api/security/abelhas/status", (_req: Request, res: Response) => {
  res.json(getAbelhasStatus());
});

// ── GET /api/caos/status ────────────────────────────────────────────────────
router.get("/api/caos/status", async (_req: Request, res: Response) => {
  try {
    const lobos = getRateLimitStatus();
    const formigas = getFormigasStatus();
    const abelhas = getAbelhasStatus();

    const [{ openIssues }] = await db
      .select({ openIssues: sql<number>`count(*)::int` })
      .from(caosSecurityIssues)
      .where(eq(caosSecurityIssues.resolved, false));

    const [{ auditCount }] = await db
      .select({ auditCount: sql<number>`count(*)::int` })
      .from(caosAuditLog)
      .where(gte(caosAuditLog.createdAt, new Date(Date.now() - 24 * 60 * 60 * 1000)));

    res.json({
      version: "1.0.0",
      name: "CAOS Hub",
      status: "operational",
      timestamp: new Date().toISOString(),
      security: {
        score: abelhas.score,
        lobos: {
          trackedIps: lobos.trackedIps,
          trackedUsers: lobos.trackedUsers,
          blockedIps: lobos.blockedIps.length,
        },
        formigas: {
          active: formigas.active,
          patternsMonitored: formigas.patternsMonitored,
          alertsLast24h: formigas.alertsLast24h,
        },
        abelhas: {
          active: abelhas.active,
          reactionsToday: abelhas.reactionsToday,
          quarantinedCount: abelhas.quarantinedCount,
        },
        openIssues: openIssues ?? 0,
        auditEntriesLast24h: auditCount ?? 0,
      },
      modules: {
        chat: "online",
        studio: "online",
        study: "online",
        nexus: "online",
        security: "online",
      },
    });
  } catch (err) {
    res.status(500).json({ status: "degraded", error: String(err) });
  }
});

export default router;
