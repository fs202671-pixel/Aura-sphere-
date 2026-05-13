/**
 * 🐜 FORMIGAS — Sistema de Detecção de Padrões Suspeitos
 *
 * Analisa requests em busca de:
 * - Injeção de prompt (chat/IA)
 * - SQL injection
 * - XSS
 * - Path traversal
 * - User-agents de bots maliciosos
 * - Flood de erros 404 (enumeração)
 *
 * Registra tudo no audit log e emite eventos para Abelhas.
 */

import { EventEmitter } from "events";
import type { Request, Response, NextFunction } from "express";
import { getIp } from "./lobos";

export const abelhasEventBus = new EventEmitter();

interface PatternRule {
  id: string;
  name: string;
  description: string;
  severity: "low" | "medium" | "high";
  test: (req: Request) => boolean;
}

const PROMPT_INJECTION = /ignore\s+(previous|all|above)\s+instructions|jailbreak|DAN\s+mode|act\s+as\s+(an?\s+)?AI\s+without|forget\s+(all\s+)?your\s+(previous\s+)?instructions|you\s+are\s+now\s+DAN|bypass\s+(your\s+)?restrictions|no\s+restrictions\s+mode/i;
const SQL_INJECTION = /(\b(select|union|insert|update|delete|drop|truncate|exec|execute)\b.*\bfrom\b|\bor\b\s+['"]?\d+['"]?\s*=\s*['"]?\d+['"]?|--\s*$|;\s*(drop|delete|truncate))/i;
const XSS_PATTERN = /<script[\s>]|javascript:\s*\w|on(load|error|click|mouse|key)\s*=/i;
const PATH_TRAVERSAL = /\.\.\/|\.\.\\|%2e%2e[/\\]|%252e%252e[/\\]/i;
const COMMAND_INJECTION = /[;&|`$]\s*(ls|cat|rm|wget|curl|nc|bash|sh|python|perl)\b/i;
const BOT_USERAGENT = /^(curl|python-requests|Go-http-client|scrapy|masscan|nikto|nmap|sqlmap|dirbuster|wfuzz|zgrab|axios\/0\.\d|libwww-perl)/i;

export const PATTERN_RULES: PatternRule[] = [
  {
    id: "prompt_injection",
    name: "Injeção de Prompt",
    description: "Tentativas de sobrescrever instruções do sistema da IA",
    severity: "high",
    test: (req) => {
      const body = JSON.stringify(req.body ?? "");
      return PROMPT_INJECTION.test(body);
    },
  },
  {
    id: "sql_injection",
    name: "Injeção de SQL",
    description: "Padrões de SQL injection detectados no corpo ou URL",
    severity: "high",
    test: (req) => {
      const target = `${req.url} ${JSON.stringify(req.body ?? "")}`;
      return SQL_INJECTION.test(target);
    },
  },
  {
    id: "xss_attempt",
    name: "Tentativa de XSS",
    description: "Padrões de Cross-Site Scripting detectados",
    severity: "medium",
    test: (req) => {
      const target = `${req.url} ${JSON.stringify(req.body ?? "")}`;
      return XSS_PATTERN.test(target);
    },
  },
  {
    id: "path_traversal",
    name: "Path Traversal",
    description: "Tentativa de navegar por diretórios fora do permitido",
    severity: "medium",
    test: (req) => PATH_TRAVERSAL.test(req.url),
  },
  {
    id: "command_injection",
    name: "Injeção de Comando",
    description: "Padrões de command injection detectados",
    severity: "high",
    test: (req) => {
      const body = JSON.stringify(req.body ?? "");
      return COMMAND_INJECTION.test(body);
    },
  },
  {
    id: "bot_useragent",
    name: "User-Agent de Bot Malicioso",
    description: "Requisição vinda de cliente automatizado não autorizado",
    severity: "low",
    test: (req) => {
      const ua = req.headers["user-agent"] ?? "";
      return BOT_USERAGENT.test(ua);
    },
  },
];

interface FormigaStats {
  totalAnalyzed: number;
  detections: Record<string, number>;
  alertsLast24h: number;
  autoBlocks: number;
  startedAt: number;
}

const stats: FormigaStats = {
  totalAnalyzed: 0,
  detections: {},
  alertsLast24h: 0,
  autoBlocks: 0,
  startedAt: Date.now(),
};

const recentDetections: Array<{
  id: string;
  pattern: string;
  ip: string;
  route: string;
  severity: "low" | "medium" | "high";
  timestamp: number;
}> = [];

const MAX_RECENT = 100;

function recordDetection(
  patternId: string,
  ip: string,
  route: string,
  severity: "low" | "medium" | "high"
) {
  stats.detections[patternId] = (stats.detections[patternId] ?? 0) + 1;
  stats.alertsLast24h += 1;

  const entry = {
    id: `det_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
    pattern: patternId,
    ip,
    route,
    severity,
    timestamp: Date.now(),
  };

  recentDetections.unshift(entry);
  if (recentDetections.length > MAX_RECENT) recentDetections.pop();

  abelhasEventBus.emit("detection", { patternId, ip, route, severity });

  if (severity === "high") {
    stats.autoBlocks += 1;
    abelhasEventBus.emit("high_severity", { patternId, ip, route });
  }
}

async function logToDb(data: {
  action: string;
  ip: string;
  route: string;
  method: string;
  severity: "low" | "medium" | "high";
  pattern?: string;
  details?: Record<string, unknown>;
}): Promise<void> {
  try {
    const { db, caosAuditLog } = await import("@workspace/db");
    await db.insert(caosAuditLog).values({
      action: data.action,
      ip: data.ip,
      route: data.route,
      method: data.method,
      severity: data.severity,
      pattern: data.pattern,
      details: data.details,
    });
  } catch {
    // Silent — não bloquear request por falha no log
  }
}

async function createIssue(data: {
  type: "suspicious" | "blocked" | "warning" | "info";
  title: string;
  description: string;
  severity: "low" | "medium" | "high";
  ip: string;
  pattern: string;
}): Promise<void> {
  try {
    const { db, caosSecurityIssues } = await import("@workspace/db");
    await db.insert(caosSecurityIssues).values({
      type: data.type,
      title: data.title,
      description: data.description,
      severity: data.severity,
      ip: data.ip,
      pattern: data.pattern,
      resolved: false,
    });
  } catch {
    // Silent
  }
}

export function formigasMiddleware(req: Request, _res: Response, next: NextFunction): void {
  stats.totalAnalyzed += 1;

  const ip = getIp(req);
  const route = req.path;
  const method = req.method;

  setImmediate(async () => {
    for (const rule of PATTERN_RULES) {
      try {
        if (rule.test(req)) {
          recordDetection(rule.id, ip, route, rule.severity);

          const maskedIp = ip.replace(/\d+$/, "***");

          await logToDb({
            action: `${rule.name} detectado`,
            ip: maskedIp,
            route,
            method,
            severity: rule.severity,
            pattern: rule.id,
            details: { userAgent: req.headers["user-agent"] },
          });

          if (rule.severity === "high") {
            await createIssue({
              type: "suspicious",
              title: `${rule.name} detectado`,
              description: `As Formigas identificaram "${rule.name}" em ${method} ${route} a partir do IP ${maskedIp}.`,
              severity: rule.severity,
              ip: maskedIp,
              pattern: rule.id,
            });
          }
        }
      } catch {
        // Ignora erro em regra individual
      }
    }
  });

  next();
}

export function getFormigasStatus() {
  const now = Date.now();
  const windowStart = now - 24 * 60 * 60 * 1000;
  const last24h = recentDetections.filter((d) => d.timestamp > windowStart);

  return {
    active: true,
    totalAnalyzed: stats.totalAnalyzed,
    patternsMonitored: PATTERN_RULES.length,
    alertsLast24h: last24h.length,
    autoBlocks: stats.autoBlocks,
    detections: stats.detections,
    recentDetections: recentDetections.slice(0, 20),
    patterns: PATTERN_RULES.map((r) => ({
      id: r.id,
      name: r.name,
      description: r.description,
      severity: r.severity,
      count: stats.detections[r.id] ?? 0,
      status:
        (stats.detections[r.id] ?? 0) > 0
          ? "ativo"
          : "normal",
    })),
  };
}
