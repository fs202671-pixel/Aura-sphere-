/**
 * CAOS Unified — Endpoints de integração cross-sistema
 *
 * GET /caos/status      — saúde e estatísticas de todos os subsistemas
 * GET /caos/capacidades — habilidades combinadas: Nexus + Hub + Shell
 */
import { Router, type IRouter } from "express";
import { db } from "@workspace/db";
import {
  nexusSkills,
  nexusConversations,
  nexusActivityLog,
  aiProfiles,
} from "@workspace/db";
import { hubSkills, hubAgents, hubItems, hubProjects } from "@workspace/db";
import { skillsTable, memoriesTable, profilesTable } from "@workspace/db";
import { sql, count } from "drizzle-orm";

const router: IRouter = Router();

// ── GET /caos/status — Visão unificada da saúde do sistema ────────────────
router.get("/caos/status", async (_req, res) => {
  try {
    const [
      nexusSkillCount,
      nexusConvCount,
      nexusActivityCount,
      nexusProfileCount,
      hubSkillCount,
      hubAgentCount,
      hubItemCount,
      hubProjectCount,
      shellSkillCount,
      shellMemoryCount,
      shellProfileCount,
    ] = await Promise.all([
      db.select({ c: count() }).from(nexusSkills),
      db.select({ c: count() }).from(nexusConversations),
      db.select({ c: count() }).from(nexusActivityLog),
      db.select({ c: count() }).from(aiProfiles),
      db.select({ c: count() }).from(hubSkills),
      db.select({ c: count() }).from(hubAgents),
      db.select({ c: count() }).from(hubItems),
      db.select({ c: count() }).from(hubProjects),
      db.select({ c: count() }).from(skillsTable),
      db.select({ c: count() }).from(memoriesTable),
      db.select({ c: count() }).from(profilesTable),
    ]);

    res.json({
      caos: {
        version: "1.0.0",
        timestamp: new Date().toISOString(),
        status: "operational",
      },
      subsystems: {
        "caos-nexus": {
          label: "CAOS Nexus",
          status: "online",
          stats: {
            profiles: nexusProfileCount[0]?.c ?? 0,
            skills: nexusSkillCount[0]?.c ?? 0,
            conversations: nexusConvCount[0]?.c ?? 0,
            activityLogs: nexusActivityCount[0]?.c ?? 0,
          },
        },
        "caos-studio": {
          label: "CAOS Studio",
          status: "online",
          stats: {
            skills: hubSkillCount[0]?.c ?? 0,
            agents: hubAgentCount[0]?.c ?? 0,
            items: hubItemCount[0]?.c ?? 0,
            projects: hubProjectCount[0]?.c ?? 0,
          },
        },
        "caos-shell": {
          label: "CAOS Shell",
          status: "online",
          stats: {
            profiles: shellProfileCount[0]?.c ?? 0,
            skills: shellSkillCount[0]?.c ?? 0,
            memories: shellMemoryCount[0]?.c ?? 0,
          },
        },
      },
    });
  } catch (err) {
    res.status(500).json({ error: "Erro ao coletar status do sistema", detail: String(err) });
  }
});

// ── GET /caos/capacidades — Habilidades combinadas de todos os sistemas ───
router.get("/caos/capacidades", async (req, res) => {
  try {
    const { tipo, limit: limitParam } = req.query;
    const maxItems = Math.min(parseInt(limitParam as string) || 50, 200);

    const results: {
      origem: string;
      tipo: string;
      id: number | string;
      nome: string;
      descricao: string;
      categoria: string;
      nivel?: number;
      icone?: string;
      status?: string;
    }[] = [];

    // Nexus Skills
    if (!tipo || tipo === "nexus") {
      const nSkills = await db
        .select({
          id: nexusSkills.id,
          name: nexusSkills.name,
          description: nexusSkills.description,
          category: nexusSkills.category,
          level: nexusSkills.level,
          icon: nexusSkills.icon,
          status: nexusSkills.status,
        })
        .from(nexusSkills)
        .limit(maxItems);

      for (const s of nSkills) {
        results.push({
          origem: "caos-nexus",
          tipo: "skill-rpg",
          id: s.id,
          nome: s.name,
          descricao: s.description ?? "",
          categoria: s.category,
          nivel: s.level,
          icone: s.icon ?? "🧠",
          status: s.status,
        });
      }
    }

    // Hub Skills (protocolos do Studio)
    if (!tipo || tipo === "studio") {
      const hSkills = await db
        .select({
          id: hubSkills.id,
          name: hubSkills.name,
          description: hubSkills.description,
          category: hubSkills.category,
          icon: hubSkills.icon,
        })
        .from(hubSkills)
        .limit(maxItems);

      for (const s of hSkills) {
        results.push({
          origem: "caos-studio",
          tipo: "protocolo",
          id: s.id,
          nome: s.name,
          descricao: s.description ?? "",
          categoria: s.category ?? "geral",
          icone: s.icon ?? "🔧",
        });
      }

      // Hub Agents
      const hAgents = await db
        .select({
          id: hubAgents.id,
          name: hubAgents.name,
          description: hubAgents.description,
          behavior: hubAgents.behavior,
        })
        .from(hubAgents)
        .limit(maxItems);

      for (const a of hAgents) {
        results.push({
          origem: "caos-studio",
          tipo: "agente",
          id: a.id,
          nome: a.name,
          descricao: a.description ?? "",
          categoria: a.behavior ?? "agente",
          icone: "🤖",
        });
      }
    }

    // Shell Skills (habilidades do usuário)
    if (!tipo || tipo === "shell") {
      const userId = req.query.user_id as string | undefined;
      if (userId) {
        const { eq } = await import("drizzle-orm");
        const sSkills = await db
          .select({
            id: skillsTable.id,
            name: skillsTable.name,
            description: skillsTable.description,
            category: skillsTable.category,
            level: skillsTable.level,
            icon: skillsTable.icon,
            status: skillsTable.status,
          })
          .from(skillsTable)
          .where(eq(skillsTable.userId, userId))
          .limit(maxItems);

        for (const s of sSkills) {
          results.push({
            origem: "caos-shell",
            tipo: "skill-usuario",
            id: s.id,
            nome: s.name,
            descricao: s.description ?? "",
            categoria: s.category,
            nivel: s.level,
            icone: s.icon ?? "⚡",
            status: s.status,
          });
        }
      }
    }

    res.json({
      total: results.length,
      filtro: tipo ?? "todos",
      capacidades: results,
    });
  } catch (err) {
    res.status(500).json({ error: "Erro ao buscar capacidades", detail: String(err) });
  }
});

// ── POST /caos/capacidades/busca — Busca cross-sistema ───────────────────
router.post("/caos/capacidades/busca", async (req, res) => {
  try {
    const { query, sistemas, user_id } = req.body as {
      query?: string;
      sistemas?: string[];
      user_id?: string;
    };

    if (!query || query.trim().length < 2) {
      res.status(400).json({ error: "query deve ter ao menos 2 caracteres" });
      return;
    }

    const { ilike, or } = await import("drizzle-orm");
    const q = `%${query.trim()}%`;
    const filtros = sistemas ?? ["nexus", "studio", "shell"];

    const results: {
      origem: string;
      tipo: string;
      id: number | string;
      nome: string;
      descricao: string;
      categoria: string;
      nivel?: number;
      icone?: string;
      status?: string;
      relevancia: number;
    }[] = [];

    // ── Nexus Skills ────────────────────────────────────────────
    if (filtros.includes("nexus")) {
      const nSkills = await db
        .select()
        .from(nexusSkills)
        .where(
          or(
            ilike(nexusSkills.name, q),
            ilike(nexusSkills.description, q),
            ilike(nexusSkills.category, q),
          ),
        )
        .limit(20);

      for (const s of nSkills) {
        const nomeMatch = s.name.toLowerCase().includes(query.toLowerCase());
        results.push({
          origem: "caos-nexus",
          tipo: "skill-rpg",
          id: s.id,
          nome: s.name,
          descricao: s.description ?? "",
          categoria: s.category,
          nivel: s.level,
          icone: s.icon ?? "🧠",
          status: s.status,
          relevancia: nomeMatch ? 1.0 : 0.6,
        });
      }
    }

    // ── Hub Skills ──────────────────────────────────────────────
    if (filtros.includes("studio")) {
      const hSkills = await db
        .select()
        .from(hubSkills)
        .where(
          or(
            ilike(hubSkills.name, q),
            ilike(hubSkills.description, q),
            ilike(hubSkills.category, q),
          ),
        )
        .limit(20);

      for (const s of hSkills) {
        results.push({
          origem: "caos-studio",
          tipo: "protocolo",
          id: s.id,
          nome: s.name,
          descricao: s.description ?? "",
          categoria: s.category ?? "geral",
          icone: s.icon ?? "🔧",
          relevancia: s.name.toLowerCase().includes(query.toLowerCase()) ? 1.0 : 0.6,
        });
      }

      // Hub Agents
      const hAgents = await db
        .select()
        .from(hubAgents)
        .where(
          or(
            ilike(hubAgents.name, q),
            ilike(hubAgents.description, q),
            ilike(hubAgents.behavior, q),
          ),
        )
        .limit(10);

      for (const a of hAgents) {
        results.push({
          origem: "caos-studio",
          tipo: "agente",
          id: a.id,
          nome: a.name,
          descricao: a.description ?? "",
          categoria: a.behavior ?? "agente",
          icone: "🤖",
          relevancia: a.name.toLowerCase().includes(query.toLowerCase()) ? 1.0 : 0.5,
        });
      }
    }

    // ── Shell Skills (por usuário) ───────────────────────────────
    if (filtros.includes("shell") && user_id) {
      const { eq } = await import("drizzle-orm");
      const sSkills = await db
        .select()
        .from(skillsTable)
        .where(
          or(
            ilike(skillsTable.name, q),
            ilike(skillsTable.description, q),
            ilike(skillsTable.category, q),
          ),
        )
        .limit(20);

      const userSkills = sSkills.filter((s) => s.userId === user_id);
      for (const s of userSkills) {
        results.push({
          origem: "caos-shell",
          tipo: "skill-usuario",
          id: s.id,
          nome: s.name,
          descricao: s.description ?? "",
          categoria: s.category,
          nivel: s.level,
          icone: s.icon ?? "⚡",
          status: s.status,
          relevancia: s.name.toLowerCase().includes(query.toLowerCase()) ? 1.0 : 0.6,
        });
      }
    }

    // Ordenar por relevância
    results.sort((a, b) => b.relevancia - a.relevancia);

    res.json({
      query,
      total: results.length,
      sistemas: filtros,
      resultados: results,
    });
  } catch (err) {
    res.status(500).json({ error: "Erro na busca", detail: String(err) });
  }
});

export default router;

