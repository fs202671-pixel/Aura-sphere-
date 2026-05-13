import { Router, type IRouter, type Request, type Response } from "express";
import { getAuth } from "@clerk/express";
import { lobosChat } from "../security/lobos";

let _openai: any = null;
async function getOpenAI() {
  if (!_openai) {
    try {
      const mod = await import("@workspace/integrations-openai-ai-server");
      _openai = mod.openai;
    } catch {
      throw new Error("OpenAI integration not provisioned");
    }
  }
  return _openai;
}

const router: IRouter = Router();

// 🐺 LOBOS — rate limiter do chat (30 req/min IP, 100 auth)
router.use("/chat", lobosChat);

router.post("/chat", async (req: Request, res: Response) => {
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
    const openai = await getOpenAI();
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
