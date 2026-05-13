/**
 * Stubs V1 — endpoints ainda sem implementação real.
 * Security, memory e costs foram movidos para rotas próprias.
 */
import { Router, type IRouter } from "express";

const router: IRouter = Router();

// ── Habilidades (planejamento futuro) ──────────────────────────────────────
router.get("/v1/abilities/list", (_req, res) => res.json({ abilities: [] }));
router.post("/v1/abilities/add", (_req, res) => res.json({ success: true }));
router.post("/v1/abilities/search", (_req, res) => res.json({ results: [] }));

// ── Ações pendentes (planejamento futuro) ──────────────────────────────────
router.get("/v1/actions/pending", (_req, res) => res.json({ actions: [] }));
router.post("/v1/actions/:id/approve", (_req, res) => res.json({ success: true }));
router.post("/v1/actions/:id/reject", (_req, res) => res.json({ success: true }));

// ── Device / Sync ──────────────────────────────────────────────────────────
router.get("/v1/device/profile", (_req, res) => res.json({ device: null }));
router.get("/v1/device/sync/status", (_req, res) => res.json({ status: "idle" }));
router.post("/v1/device/optimize", (_req, res) => res.json({ success: true }));

// ── Planning ───────────────────────────────────────────────────────────────
router.get("/v1/planning/plans/:userId", (_req, res) => res.json({ plans: [] }));
router.post("/v1/planning/plans", (_req, res) => res.json({ success: true }));

// ── Social ─────────────────────────────────────────────────────────────────
router.get("/v1/social/instagram/collections", (_req, res) => res.json({ collections: [] }));
router.get("/v1/social/instagram/sync", (_req, res) => res.json({ success: true, items: [] }));
router.post("/v1/social/instagram/login", (_req, res) => res.json({ success: false, message: "Não disponível neste plano" }));
router.get("/v1/social/instagram/recommendations", (_req, res) => res.json({ recommendations: [] }));

// ── Busca Global ───────────────────────────────────────────────────────────
router.get("/v1/search", (_req, res) => res.json({ results: [] }));

export default router;
