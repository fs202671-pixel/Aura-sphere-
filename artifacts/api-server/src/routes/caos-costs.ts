/**
 * 💰 CAOS API Costs — Rastreamento de Custos de API
 * Substitui stubs de /v1/costs/*
 */

import { Router, type IRouter, type Request, type Response } from "express";
import { db, caosApiCosts } from "@workspace/db";
import { desc, gte, sql } from "drizzle-orm";

const router: IRouter = Router();

// Preços aproximados por 1M tokens (USD)
const PRICING: Record<string, { input: number; output: number }> = {
  "gpt-4o": { input: 2.5, output: 10 },
  "gpt-4o-mini": { input: 0.15, output: 0.6 },
  "gpt-4": { input: 30, output: 60 },
  "gpt-3.5-turbo": { input: 0.5, output: 1.5 },
  "default": { input: 2.5, output: 10 },
};

function calcCost(model: string, inputTokens: number, outputTokens: number): string {
  const p = PRICING[model] ?? PRICING["default"];
  const cost = (inputTokens * p.input + outputTokens * p.output) / 1_000_000;
  return cost.toFixed(6);
}

// ── POST /v1/costs/track (interno) ──────────────────────────────────────────
router.post("/v1/costs/track", async (req: Request, res: Response) => {
  try {
    const { provider = "openai", model, inputTokens = 0, outputTokens = 0, route, userId } = req.body;
    if (!model) {
      res.status(400).json({ error: "model é obrigatório" });
      return;
    }
    const costUsd = calcCost(model, inputTokens, outputTokens);
    await db.insert(caosApiCosts).values({ provider, model, inputTokens, outputTokens, costUsd, route, userId });
    res.json({ success: true, costUsd });
  } catch {
    res.status(500).json({ error: "Falha ao registrar custo" });
  }
});

// ── GET /v1/costs/summary ────────────────────────────────────────────────────
router.get("/v1/costs/summary", async (_req: Request, res: Response) => {
  try {
    const [result] = await db
      .select({
        totalRequests: sql<number>`count(*)::int`,
        totalInput: sql<number>`sum(input_tokens)::int`,
        totalOutput: sql<number>`sum(output_tokens)::int`,
      })
      .from(caosApiCosts);

    const costs = await db.select().from(caosApiCosts).orderBy(desc(caosApiCosts.createdAt)).limit(500);

    const totalCost = costs.reduce((sum, c) => sum + parseFloat(c.costUsd), 0);
    const byModel: Record<string, { requests: number; cost: number }> = {};
    for (const c of costs) {
      if (!byModel[c.model]) byModel[c.model] = { requests: 0, cost: 0 };
      byModel[c.model].requests += 1;
      byModel[c.model].cost += parseFloat(c.costUsd);
    }

    res.json({
      total: parseFloat(totalCost.toFixed(6)),
      currency: "USD",
      totalRequests: result?.totalRequests ?? 0,
      totalInputTokens: result?.totalInput ?? 0,
      totalOutputTokens: result?.totalOutput ?? 0,
      byModel,
    });
  } catch {
    res.status(500).json({ total: 0, currency: "USD" });
  }
});

// ── GET /v1/costs/trends ─────────────────────────────────────────────────────
router.get("/v1/costs/trends", async (_req: Request, res: Response) => {
  try {
    const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    const costs = await db
      .select()
      .from(caosApiCosts)
      .where(gte(caosApiCosts.createdAt, since))
      .orderBy(desc(caosApiCosts.createdAt));

    const byDay: Record<string, number> = {};
    for (const c of costs) {
      const day = c.createdAt.toISOString().split("T")[0];
      byDay[day] = (byDay[day] ?? 0) + parseFloat(c.costUsd);
    }

    const trends = Object.entries(byDay)
      .map(([date, cost]) => ({ date, cost: parseFloat(cost.toFixed(6)) }))
      .sort((a, b) => a.date.localeCompare(b.date));

    res.json({ trends });
  } catch {
    res.status(500).json({ trends: [] });
  }
});

// ── GET /v1/costs/alerts ─────────────────────────────────────────────────────
router.get("/v1/costs/alerts", async (_req: Request, res: Response) => {
  try {
    const since = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const [{ total }] = await db
      .select({ total: sql<string>`coalesce(sum(cost_usd::numeric), 0)::text` })
      .from(caosApiCosts)
      .where(gte(caosApiCosts.createdAt, since));

    const dailyCost = parseFloat(total ?? "0");
    const alerts = dailyCost > 1.0
      ? [{ type: "warning", message: `Custo das últimas 24h: $${dailyCost.toFixed(4)}`, threshold: 1.0 }]
      : [];

    res.json({ alerts });
  } catch {
    res.status(500).json({ alerts: [] });
  }
});

// ── GET /v1/costs/free-alternatives ──────────────────────────────────────────
router.get("/v1/costs/free-alternatives", (_req: Request, res: Response) => {
  res.json({
    alternatives: [
      { name: "Ollama (local)", description: "Rode LLMs localmente sem custo de API", url: "https://ollama.ai" },
      { name: "Groq", description: "LLama 3 e Mixtral gratuitamente com rate limit", url: "https://groq.com" },
      { name: "Google Gemini Free", description: "Gemini 1.5 Flash com tier gratuito generoso", url: "https://aistudio.google.com" },
    ],
  });
});

export default router;
