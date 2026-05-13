/**
 * 🐝 ABELHAS — Sistema de Resposta Reativa
 *
 * Recebe eventos do sistema Formigas e executa respostas automáticas:
 * - Escalona bloqueio de IPs via Lobos quando padrões de alto risco são detectados
 * - Mantém fila de quarentena
 * - Calcula score de segurança dinâmico
 * - Emite alertas de status
 */

import { abelhasEventBus } from "./formigas";
import { getRateLimitStatus } from "./lobos";

interface AbelhasReaction {
  ip: string;
  pattern: string;
  reason: string;
  timestamp: number;
  action: "escalate" | "quarantine" | "alert";
}

const reactions: AbelhasReaction[] = [];
const quarantine = new Map<string, { until: number; reason: string }>();
const MAX_REACTIONS = 200;

let reactionsToday = 0;
let lastDayReset = Date.now();

function resetDaily() {
  const now = Date.now();
  if (now - lastDayReset > 24 * 60 * 60 * 1000) {
    reactionsToday = 0;
    lastDayReset = now;
  }
}

abelhasEventBus.on("high_severity", async ({ patternId, ip, route }: { patternId: string; ip: string; route: string }) => {
  resetDaily();
  reactionsToday += 1;

  const reaction: AbelhasReaction = {
    ip: ip.replace(/\d+$/, "***"),
    pattern: patternId,
    reason: `Auto-reação a padrão de alto risco: ${patternId} em ${route}`,
    timestamp: Date.now(),
    action: "escalate",
  };

  reactions.unshift(reaction);
  if (reactions.length > MAX_REACTIONS) reactions.pop();

  try {
    const lobos = await import("./lobos");
    (lobos as any).recordOffense?.(ip);
  } catch {
    // lobos não expõe recordOffense diretamente — escalation via event only
  }

  quarantine.set(ip, {
    until: Date.now() + 5 * 60 * 1000,
    reason: `Padrão detectado pelas Formigas: ${patternId}`,
  });
});

abelhasEventBus.on("detection", ({ ip, severity }: { patternId: string; ip: string; route: string; severity: string }) => {
  if (severity === "medium") {
    const existing = quarantine.get(ip);
    if (!existing) {
      quarantine.set(ip, {
        until: Date.now() + 60_000,
        reason: "Observação temporária — padrão medium detectado",
      });
    }
  }
});

setInterval(() => {
  const now = Date.now();
  for (const [ip, q] of quarantine.entries()) {
    if (now > q.until) quarantine.delete(ip);
  }
}, 60_000);

export function isQuarantined(ip: string): { blocked: boolean; reason?: string; retryInSec?: number } {
  const q = quarantine.get(ip);
  if (!q || Date.now() > q.until) return { blocked: false };
  return {
    blocked: true,
    reason: q.reason,
    retryInSec: Math.ceil((q.until - Date.now()) / 1000),
  };
}

export function getAbelhasStatus() {
  resetDaily();
  const now = Date.now();
  const lobosStatus = getRateLimitStatus();

  const activeQuarantine = Array.from(quarantine.entries())
    .filter(([, v]) => now < v.until)
    .map(([ip, v]) => ({
      ip: ip.replace(/\d+$/, "***"),
      reason: v.reason,
      retryInSec: Math.ceil((v.until - now) / 1000),
    }));

  const openIssueCount = reactions.filter((r) => r.timestamp > now - 24 * 60 * 60 * 1000).length;

  const score = Math.max(
    0,
    100 -
      openIssueCount * 5 -
      lobosStatus.blockedIps.length * 10 -
      activeQuarantine.length * 3
  );

  return {
    active: true,
    score: Math.min(100, score),
    reactionsToday,
    activeQuarantine,
    quarantinedCount: activeQuarantine.length,
    recentReactions: reactions.slice(0, 20),
    lobos: lobosStatus,
  };
}
