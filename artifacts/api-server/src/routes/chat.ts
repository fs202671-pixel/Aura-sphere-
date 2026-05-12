import { Router, type IRouter, type Request, type Response } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";
import { getAuth } from "@clerk/express";

const router: IRouter = Router();

// Simple in-memory rate limiter for unauthenticated (local) requests.
// Limits to 30 requests per minute per IP to prevent API quota abuse.
const localRateMap = new Map<string, { count: number; resetAt: number }>();
const LOCAL_RATE_LIMIT = 30;
const RATE_WINDOW_MS = 60_000;

function checkLocalRateLimit(ip: string): boolean {
  const now = Date.now();
  const entry = localRateMap.get(ip);
  if (!entry || now > entry.resetAt) {
    localRateMap.set(ip, { count: 1, resetAt: now + RATE_WINDOW_MS });
    return true;
  }
  if (entry.count >= LOCAL_RATE_LIMIT) return false;
  entry.count += 1;
  return true;
}

// Periodically purge stale entries to avoid memory growth.
setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of localRateMap) {
    if (now > entry.resetAt) localRateMap.delete(key);
  }
}, RATE_WINDOW_MS * 2);

router.post("/chat", async (req: Request, res: Response) => {
  const auth = getAuth(req);
  const isClerkAuth = Boolean(auth?.userId);

  // Local/demo requests are rate-limited by IP.
  if (!isClerkAuth) {
    const ip = (req.headers["x-forwarded-for"] as string | undefined)?.split(",")[0]?.trim()
      ?? req.socket.remoteAddress
      ?? "unknown";
    if (!checkLocalRateLimit(ip)) {
      res.status(429).json({ error: "Taxa limite excedida. Tente novamente em um minuto." });
      return;
    }
  }

  const body = req.body as {
    messages?: { role: string; content: string }[];
    aiName?: string;
    provider?: string;
  };
  const { messages } = body;

  if (!messages || !Array.isArray(messages)) {
    res.status(400).json({ error: "messages array required" });
    return;
  }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  try {
    const stream = await openai.chat.completions.create({
      model: "gpt-4o",
      max_completion_tokens: 8192,
      messages: messages as { role: "user" | "assistant" | "system"; content: string }[],
      stream: true,
    });

    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content;
      if (content) {
        res.write(`data: ${JSON.stringify({ content })}\n\n`);
      }
    }

    res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
    res.end();
  } catch (err) {
    req.log.error({ err }, "Chat completion error");
    res.write(`data: ${JSON.stringify({ error: "Erro ao processar resposta da IA" })}\n\n`);
    res.end();
  }
});

export default router;
