import type { Request, Response, NextFunction } from "express";

type RateLimitEntry = { count: number; resetAt: number };
type OffenseEntry = { offenses: number; blockUntil: number };

const ipMap = new Map<string, RateLimitEntry>();
const userMap = new Map<string, RateLimitEntry>();
const offenseMap = new Map<string, OffenseEntry>();

const WINDOW_MS = 60_000;

setInterval(() => {
  const now = Date.now();
  for (const [k, v] of ipMap) if (now > v.resetAt) ipMap.delete(k);
  for (const [k, v] of userMap) if (now > v.resetAt) userMap.delete(k);
  for (const [k, v] of offenseMap) if (now > v.blockUntil) offenseMap.delete(k);
}, WINDOW_MS * 2);

export function getIp(req: Request): string {
  return (
    (req.headers["x-forwarded-for"] as string | undefined)?.split(",")[0]?.trim() ??
    req.socket.remoteAddress ??
    "unknown"
  );
}

function isBlockedIp(ip: string): boolean {
  const e = offenseMap.get(ip);
  return !!e && Date.now() < e.blockUntil;
}

function recordOffense(ip: string): void {
  const now = Date.now();
  const e = offenseMap.get(ip) ?? { offenses: 0, blockUntil: 0 };
  e.offenses += 1;
  // Progressivo: 1ª violação = 5s, 2ª = 60s, 3ª+ = 1h
  if (e.offenses === 1) e.blockUntil = now + 5_000;
  else if (e.offenses === 2) e.blockUntil = now + 60_000;
  else e.blockUntil = now + 3_600_000;
  offenseMap.set(ip, e);
}

function checkLimit(map: Map<string, RateLimitEntry>, key: string, max: number): boolean {
  const now = Date.now();
  const e = map.get(key);
  if (!e || now > e.resetAt) {
    map.set(key, { count: 1, resetAt: now + WINDOW_MS });
    return true;
  }
  if (e.count >= max) return false;
  e.count += 1;
  return true;
}

export interface LobosOptions {
  ipLimit?: number;
  userLimit?: number;
  message?: string;
}

/**
 * 🐺 LOBOS — Middleware guardião de taxa de requisições.
 * Limite por IP (não autenticado) com bloqueio progressivo.
 * Limite por userId (autenticado) mais generoso.
 */
export function lobos(options: LobosOptions = {}) {
  const {
    ipLimit = 60,
    userLimit = 200,
    message = "Taxa limite excedida. Tente novamente em breve.",
  } = options;

  return function lobosMiddleware(req: Request, res: Response, next: NextFunction): void {
    const ip = getIp(req);

    if (isBlockedIp(ip)) {
      const e = offenseMap.get(ip)!;
      const retryAfterSec = Math.ceil((e.blockUntil - Date.now()) / 1000);
      res.status(429).json({ error: message, retryAfter: retryAfterSec, bloqueado: true });
      return;
    }

    const userId = (req as any).auth?.userId as string | undefined;
    const allowed = userId
      ? checkLimit(userMap, userId, userLimit)
      : checkLimit(ipMap, ip, ipLimit);

    if (!allowed) {
      if (!userId) recordOffense(ip);
      res.status(429).json({ error: message, retryAfter: 60 });
      return;
    }

    next();
  };
}

// ── Instâncias pré-configuradas por nível de proteção ─────────────────────

/** Chat/IA — mais restritivo (30 req/min IP, 100 auth) */
export const lobosChat = lobos({
  ipLimit: 30,
  userLimit: 100,
  message: "Taxa de chat excedida. Aguarde 1 minuto.",
});

/** API geral — moderado */
export const lobosApi = lobos({ ipLimit: 60, userLimit: 200 });

/** Ações sensíveis (fusão, delete, etc.) — bem restritivo */
export const lobosStrict = lobos({
  ipLimit: 10,
  userLimit: 30,
  message: "Muitas tentativas. Aguarde antes de tentar novamente.",
});

// ── Dashboard helpers ──────────────────────────────────────────────────────

export interface BlockedIpInfo {
  ip: string;
  blockUntil: number;
  offenses: number;
  retryInSec: number;
}

export function getBlockedIps(): BlockedIpInfo[] {
  const now = Date.now();
  return Array.from(offenseMap.entries())
    .filter(([, v]) => v.blockUntil > now)
    .map(([ip, v]) => ({
      ip: ip.replace(/\d+$/, "***"),
      blockUntil: v.blockUntil,
      offenses: v.offenses,
      retryInSec: Math.ceil((v.blockUntil - now) / 1000),
    }));
}

export interface RateLimitStatus {
  blockedIps: BlockedIpInfo[];
  trackedIps: number;
  trackedUsers: number;
}

export function getRateLimitStatus(): RateLimitStatus {
  return {
    blockedIps: getBlockedIps(),
    trackedIps: ipMap.size,
    trackedUsers: userMap.size,
  };
}
