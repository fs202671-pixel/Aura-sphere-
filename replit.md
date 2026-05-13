# CAOS — Creative AI Operating System

Um ecossistema completo de IA criativa com identidade RPG, mobile-first, 100% em português.
O sistema converte tudo que é criado (designs, temas, agentes de IA, habilidades, projetos) em itens colecionáveis com raridade (Comum / Raro / Épico / Lendário).

## Subsistemas

| Artifact | Package | Nome no CAOS | Função |
|---|---|---|---|
| `artifacts/aura-sphere` | `@workspace/caos-shell` | **CAOS Shell** | Interface principal de chat com IA, voice, memória, PWA |
| `artifacts/nexus-ai` | `@workspace/caos-nexus` | **CAOS Nexus** | Sistema de habilidades RPG dinâmicas da IA |
| `artifacts/creator-hub-rpg` | `@workspace/caos-studio` | **CAOS Studio** | Arsenal criativo — itens, temas, agentes, protocolos, missões |
| `artifacts/api-server` | `@workspace/api-server` | **CAOS API Gateway** | Backend unificado (Express 5) para todos os módulos |

## Run & Operate

```bash
pnpm --filter @workspace/api-server run dev   # API Gateway (porta 8080)
pnpm --filter @workspace/caos-studio run dev  # CAOS Studio (porta variável)
pnpm --filter @workspace/caos-shell run dev   # CAOS Shell (porta variável)
pnpm --filter @workspace/caos-nexus run dev   # CAOS Nexus (porta variável)
pnpm run typecheck                             # typecheck completo
pnpm --filter @workspace/db run push          # aplicar schema DB (dev only)
node lib/db/migrations/apply.mjs              # aplicar migration SQL (renomear tabelas em prod)
```

Variável obrigatória: `DATABASE_URL` — string de conexão PostgreSQL

## Stack

- **Workspace:** pnpm workspaces, Node.js 24, TypeScript 5.9
- **Frontend:** React 19.1.7 + Vite 7 + Tailwind CSS v3 + shadcn/ui + wouter
- **API:** Express 5 (`artifacts/api-server`)
- **DB:** PostgreSQL + Drizzle ORM
- **Validação:** Zod (`zod/v4`), `drizzle-zod`
- **Build:** esbuild (servidor), Vite (frontend)

## Arquitetura de Dados

```
lib/db/src/schema/
├── caos-shell.ts   → caos_profiles, caos_chat_messages, caos_shell_memories, caos_shell_skills
├── caos-nexus.ts   → caos_ai_profiles, caos_nexus_skills, caos_nexus_conversations,
│                     caos_nexus_messages, caos_nexus_activity_log
├── caos-studio.ts  → caos_hub_items, caos_hub_themes, caos_hub_agents,
│                     caos_hub_skills, caos_hub_projects
└── security.ts     → caos_audit_log, caos_security_issues, caos_memory, caos_api_costs
```

## Rotas da API

```
── CAOS Shell ─────────────────────────────────────────
GET/POST /api/memories             → Memórias do usuário (caos_shell_memories)
GET/POST/DELETE /api/chat-messages → Histórico de chat
GET/POST /api/profiles/:id         → Perfil do usuário
GET/POST/PATCH/DELETE /api/shell-skills → Habilidades por usuário (caos_shell_skills)
GET/POST /api/shell-skills/study   → Estudo de tópico via IA (SSE streaming)
POST /api/shell-skills/fuse        → Fusão de habilidades via IA (SSE streaming)

── CAOS Nexus ─────────────────────────────────────────
GET/PATCH /api/ai/profile          → Perfil da IA (caos_ai_profiles)
GET /api/ai/stats                  → Estatísticas do perfil
GET/POST /api/ai/conversations     → Conversas (caos_nexus_conversations)
GET/POST /api/ai/conversations/:id/messages → Mensagens de conversa
GET/POST/DELETE /api/skills        → Habilidades RPG (caos_nexus_skills)
GET /api/skills/categories         → Categorias de habilidades
POST /api/skills/study             → Estudar tópico e propor habilidades (IA)
POST /api/skills/fuse              → Fundir habilidades (IA)
POST /api/skills/:id/acquire       → Adquirir habilidade

── CAOS Studio ────────────────────────────────────────
GET/POST/PATCH/DELETE /api/items   → Artefatos (caos_hub_items)
GET/POST/PATCH/DELETE /api/themes  → Fragmentos de tema (caos_hub_themes)
GET/POST/PATCH/DELETE /api/agents  → Entidades IA (caos_hub_agents)
GET/POST/PATCH/DELETE /api/hub-skills → Protocolos (caos_hub_skills)
GET/POST/PATCH/DELETE /api/projects   → Missões (caos_hub_projects)
POST /api/items/fusao              → Fusão de artefatos

── CAOS Unificado ─────────────────────────────────────
GET /api/caos/status               → Saúde e estatísticas de todos os subsistemas
GET /api/caos/capacidades          → Capacidades combinadas (nexus+studio+shell)
POST /api/caos/capacidades/busca   → Busca cross-sistema com relevância

── Segurança ──────────────────────────────────────────
GET /api/security/lobos/status     → Status do rate limiter (Lobos)
GET /api/security/formigas/status  → Status do detector de padrões (Formigas)
GET /api/security/abelhas/status   → Status do sistema de resposta (Abelhas)
GET /api/security/audit-log        → Log de auditoria (caos_audit_log)
GET/POST /api/security/issues      → Issues de segurança (caos_security_issues)
POST/DELETE /api/caos/security/whitelist|blacklist → Gestão de IPs

── Memória IA ─────────────────────────────────────────
GET /api/v1/memory                 → Memória semântica (caos_memory)
GET /api/v1/memory/busca           → Busca ilike em memórias

── Custos ─────────────────────────────────────────────
POST /api/v1/costs/track           → Rastrear custo de chamada API
GET /api/v1/costs/summary          → Resumo de custos (caos_api_costs)
GET /api/v1/costs/trends           → Tendências de uso
GET /api/v1/costs/alerts           → Alertas de limite
```

## Sistemas de Segurança (Tríade do CAOS)

| Sistema | Arquivo | Status |
|---|---|---|
| 🐺 Lobos (rate limiter) | `src/security/lobos.ts` | ✅ Implementado — rate limit por IP e usuário |
| 🐜 Formigas (detecção de padrões) | `src/security/formigas.ts` | ✅ Implementado — detecta padrões suspeitos |
| 🐝 Abelhas (resposta a ameaças) | `src/security/abelhas.ts` | ✅ Implementado — whitelist/blacklist dinâmicos |

## Estrutura de Arquivos

```
artifacts/
├── aura-sphere/src/              # CAOS Shell (@workspace/caos-shell)
│   ├── components/CaosShell.tsx         → Interface principal
│   ├── components/CaosShellTabs.tsx     → Tabs de navegação
│   ├── components/AbilitiesGallery.tsx  → Galeria de habilidades → /api/shell-skills
│   ├── components/SkillStudyModal.tsx   → Estudo via IA → /api/shell-skills/study
│   ├── components/SkillFusionModal.tsx  → Fusão via IA → /api/shell-skills/fuse
│   ├── components/ThemeBuilder.tsx      → Builder de temas (localStorage: caos_custom_themes)
│   ├── hooks/useLocalAuth.ts            → Auth local (localStorage: caos_local_user)
│   ├── hooks/useSyncService.ts          → Sync memórias → /api/memories
│   └── lib/localProfile.ts             → Perfil local (localStorage: caos-profile)
├── nexus-ai/src/                 # CAOS Nexus (@workspace/caos-nexus)
│   ├── pages/skills.tsx         → Gerenciamento de habilidades RPG
│   ├── pages/chat.tsx           → Chat com IA → /api/ai/conversations
│   ├── pages/study.tsx          → Estudar tópicos
│   ├── pages/fuse.tsx           → Fundir habilidades
│   ├── pages/security.tsx       → Dashboard de segurança → /api/security/*
│   ├── pages/professor.tsx      → Modo professor (chat educacional)
│   └── lib/nexus-api.ts         → Cliente API com React Query
├── creator-hub-rpg/src/          # CAOS Studio (@workspace/caos-studio)
│   ├── pages/library.tsx        → Arsenal de artefatos → /api/items
│   ├── pages/agents.tsx         → Entidades IA → /api/agents
│   ├── pages/skills.tsx         → Protocolos → /api/hub-skills
│   ├── pages/themes.tsx         → Fragmentos → /api/themes
│   └── pages/projects.tsx       → Missões → /api/projects
└── api-server/src/routes/        # CAOS API Gateway
    ├── caos-shell.ts            → Shell: profiles, chat-messages, memories
    ├── caos-nexus.ts            → Nexus: ai/profile, skills, conversations
    ├── caos-unified.ts          → Status unificado + busca cross-sistema
    ├── skills.ts                → Shell skills (montado em /shell-skills)
    ├── caos-studio/             → Studio: items, themes, agents, skills, projects
    ├── security.ts              → Segurança: audit, issues, whitelist/blacklist
    ├── caos-memory.ts           → Memória semântica IA
    ├── caos-costs.ts            → Rastreamento de custos de API
    └── stub-v1.ts               → Stubs V1 (device, planning, social, search)

lib/
├── db/src/schema/
│   ├── caos-shell.ts    → Tabelas do CAOS Shell
│   ├── caos-nexus.ts    → Tabelas do CAOS Nexus
│   ├── caos-studio.ts   → Tabelas do CAOS Studio
│   └── security.ts      → Tabelas de segurança e sistema
├── db/migrations/
│   ├── 001_rename_to_caos.sql  → Migration de rename de tabelas
│   └── apply.mjs               → Script aplicador de migration
├── api-spec/openapi.yaml        → Spec OpenAPI do CAOS Studio
└── api-client-react/            → Client React Query gerado para CAOS Studio
```

## Decisões de Arquitetura

- **Auth:** Local-only via localStorage (`useLocalAuth`). Clerk está instalado no backend mas desativado nas rotas de shell. Usuário local criado automaticamente.
- **IDs de usuário:** Formato `local_XXXXX` ou `demo_XXXXX` para usuários não autenticados.
- **Mobile-first:** CAOS Studio tem nav inferior fixa, layout de 2 colunas em mobile, header compacto.
- **Identidade:** Todo texto visível ao usuário deve estar em **português brasileiro**.
- **RPG System:** Cada artefato criado tem raridade (Common/Rare/Epic/Legendary). Raridades têm bordas e brilhos diferentes.
- **Offline:** CAOS Shell tem Service Worker e suporte PWA. Chat funciona offline com fila de sincronização.
- **OpenAI:** Import lazy (`getOpenAI()`) para evitar crash no boot quando a integração não está configurada.

## Preferências do Usuário

- **SEM tela de login** — app abre diretamente na interface.
- **SEM Clerk, Supabase ou Lovable** — auth local apenas.
- **Mobile first** — toda UI deve funcionar bem em tela de 390px.
- **100% português** — nenhum texto em inglês na interface final.
- **Identidade CAOS** — nenhum nome de sistema anterior deve aparecer na UI.

## Gotchas

- Tailwind v3 (não v4) — usa `@tailwind base/components/utilities` e postcss
- CAOS Studio usa `wouter` para roteamento; CAOS Shell usa `react-router-dom`
- Vite config não usa `@tailwindcss/vite` — usa postcss
- `@capacitor/core` removido — stub em `platform.ts` para build web
- `@supabase/supabase-js` não instalado — stub mantém imports funcionando
- `@clerk/express` instalado no api-server mas sem middleware global — `getAuth()` pode lançar exceção se chamado sem o middleware (tratado com try/catch no caos-shell.ts)
- `@clerk/react` incompatível com React 19.1.7 + Vite 7 — não instalar no frontend
- esbuild bundla a API em `dist/index.mjs` (~3.1mb) — normal para backend com todas as deps

## Próximas Tarefas

Ver arquivo `CAOS_TAREFAS.md` na raiz do projeto para a lista completa de tarefas pendentes.
