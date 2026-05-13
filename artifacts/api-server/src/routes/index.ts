import { Router, type IRouter } from "express";
import healthRouter from "./health";
import caosShellRouter from "./caos-shell";
import chatRouter from "./chat";
import stubV1Router from "./stub-v1";
import caosNexusRouter from "./caos-nexus";
import shellSkillsRouter from "./skills";
import hubItemsRouter from "./caos-studio/items";
import hubThemesRouter from "./caos-studio/themes";
import hubAgentsRouter from "./caos-studio/agents";
import hubSkillsRouter from "./caos-studio/skills";
import hubProjectsRouter from "./caos-studio/projects";
import securityRouter from "./security";
import memoryRouter from "./caos-memory";
import costsRouter from "./caos-costs";
import caosUnifiedRouter from "./caos-unified";
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
router.use(caosNexusRouter);

// ── CAOS Shell (ex-Aura Sphere) ───────────────────────────────────────────
router.use(caosShellRouter);

// ── Chat com IA (tem rate limiter próprio dos Lobos — lobosChat) ──────────
router.use(chatRouter);

// ── Stubs V1 (compatibilidade — apenas endpoints ainda sem implementação) ──
router.use(stubV1Router);

// ── CAOS Shell — Habilidades do usuário (caos_shell_skills) ──────────────
router.use("/shell-skills", shellSkillsRouter);

// ── CAOS Studio — Creator Hub RPG ────────────────────────────────────────
router.use("/items", hubItemsRouter);
router.use("/themes", hubThemesRouter);
router.use("/agents", hubAgentsRouter);
router.use("/hub-skills", hubSkillsRouter);
router.use("/projects", hubProjectsRouter);

// ── CAOS Unified — Status e Capacidades ──────────────────────────────────
router.use(caosUnifiedRouter);

export default router;
