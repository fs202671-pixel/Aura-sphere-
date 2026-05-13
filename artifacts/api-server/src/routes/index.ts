import { Router, type IRouter } from "express";
import healthRouter from "./health";
import auraSphereRouter from "./aura-sphere";
import chatRouter from "./chat";
import stubV1Router from "./stub-v1";
import nexusAiRouter from "./nexus-ai";
import hubItemsRouter from "./creator-hub/items";
import hubThemesRouter from "./creator-hub/themes";
import hubAgentsRouter from "./creator-hub/agents";
import hubSkillsRouter from "./creator-hub/skills";
import hubProjectsRouter from "./creator-hub/projects";
import securityRouter from "./security";
import memoryRouter from "./caos-memory";
import costsRouter from "./caos-costs";
import { lobosApi, getRateLimitStatus } from "../security/lobos";
import { formigasMiddleware } from "../security/formigas";

const router: IRouter = Router();

// ── 🐺 LOBOS — rate limiting geral em todas as rotas de API ───────────────
router.use("/api", lobosApi);

// ── 🐜 FORMIGAS — detecção de padrões suspeitos (não bloqueante) ──────────
router.use(formigasMiddleware);

// ── Health ────────────────────────────────────────────────────────────────
router.use(healthRouter);

// ── Segurança — status dos Lobos ──────────────────────────────────────────
router.get("/api/security/lobos/status", (_req, res) => {
  res.json(getRateLimitStatus());
});

// ── Sistemas de Segurança — Formigas, Abelhas, Audit, Issues ─────────────
router.use(securityRouter);

// ── CAOS Memory — Sistema Unificado de Memória ────────────────────────────
router.use(memoryRouter);

// ── CAOS Costs — Rastreamento de Custos de API ────────────────────────────
router.use(costsRouter);

// ── Nexus AI (CAOS Nexus) ─────────────────────────────────────────────────
router.use(nexusAiRouter);

// ── Aura Sphere (CAOS Shell) ──────────────────────────────────────────────
router.use(auraSphereRouter);

// ── Chat com IA (tem rate limiter próprio dos Lobos — lobosChat) ──────────
router.use(chatRouter);

// ── Stubs V1 (compatibilidade — apenas endpoints ainda sem implementação) ──
router.use(stubV1Router);

// ── CAOS Studio — Creator Hub RPG ────────────────────────────────────────
router.use("/items", hubItemsRouter);
router.use("/themes", hubThemesRouter);
router.use("/agents", hubAgentsRouter);
// Hub skills em /hub-skills para não conflitar com rota /skills do nexus
router.use("/hub-skills", hubSkillsRouter);
router.use("/skills", hubSkillsRouter);
router.use("/projects", hubProjectsRouter);

export default router;
