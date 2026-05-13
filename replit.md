# CAOS — Sistema Central de IA Criativa

Um ecossistema completo de IA criativa com identidade RPG, mobile-first, 100% em português.
O sistema converte tudo que é criado (designs, temas, agentes de IA, habilidades, projetos) em itens colecionáveis com raridade (Comum / Raro / Épico / Lendário).

## Subsistemas

| Artifact | Nome no CAOS | Função |
|---|---|---|
| `artifacts/creator-hub-rpg` | **CAOS Studio** | Arsenal criativo principal — itens, fragmentos, entidades, protocolos, missões |
| `artifacts/aura-sphere` | **CAOS Shell** | Interface de chat com IA, modo multi-mídia, memória, voice |
| `artifacts/nexus-ai` | **CAOS Nexus** | Sistema de habilidades dinâmicas da IA |
| `artifacts/api-server` | **CAOS API Gateway** | Backend unificado (Express 5) para todos os módulos |

> ⚠️ **Nota para o próximo programador:** Os nomes `aura-sphere`, `nexus-ai` e `AIOn` são nomes antigos. Todo o sistema deve convergir para a identidade **CAOS**. Ver `CAOS_TAREFAS.md` para o plano completo de renomeação e tarefas pendentes.

## Run & Operate

```bash
pnpm --filter @workspace/api-server run dev       # API Gateway (porta 8080)
pnpm --filter @workspace/creator-hub-rpg run dev  # CAOS Studio (porta variável)
pnpm --filter @workspace/aura-sphere run dev      # CAOS Shell (porta variável)
pnpm --filter @workspace/nexus-ai run dev         # CAOS Nexus (porta variável)
pnpm run typecheck                                 # typecheck completo
pnpm --filter @workspace/db run push              # aplicar schema DB (dev only)
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
├── creator-hub.ts   → hub_items, hub_themes, hub_agents, hub_skills, hub_projects
├── nexus.ts         → nexus_skills, nexus_conversations, nexus_messages, nexus_activity_log
└── aura-sphere.ts   → profiles, chat_messages
```

## Rotas da API

```
/api/items          → CAOS Studio · Artefatos
/api/themes         → CAOS Studio · Fragmentos
/api/agents         → CAOS Studio · Entidades
/api/hub-skills     → CAOS Studio · Protocolos
/api/projects       → CAOS Studio · Missões
/api/chat           → CAOS Shell · Chat com IA (streaming SSE)
/api/nexus/*        → CAOS Nexus · Habilidades, conversas
/api/v1/*           → Stubs compatíveis (segurança, device, memory — ver stub-v1.ts)
```

## Sistemas de Segurança (Tríade do CAOS)

| Sistema | Arquivo | Status |
|---|---|---|
| 🐺 Lobos (rate limiter) | `src/routes/chat.ts` | ✅ Básico implementado |
| 🐜 Formigas (detecção de padrões) | `src/security/formigas.ts` | ❌ Não implementado |
| 🐝 Abelhas (resposta a ameaças) | `src/security/abelhas.ts` | ❌ Não implementado |

Ver `CAOS_TAREFAS.md` · Bloco 3 para o plano completo de implementação.

## Onde as coisas ficam

```
artifacts/
├── creator-hub-rpg/src/
│   ├── components/layout.tsx       → Layout mobile-first com nav inferior
│   ├── components/ui-rpg.tsx       → RarityBadge, TypeBadge, ItemCard
│   └── pages/                      → dashboard, library, agents, skills, themes, projects, item-detail
├── aura-sphere/src/
│   ├── components/AIOnShell.tsx    → Interface principal (renomear para CaosShell.tsx)
│   ├── components/SecurityDashboard.tsx → Dashboard de segurança (UI pronta, stubs no backend)
│   └── lib/localProfile.ts         → Perfil local (localStorage)
└── api-server/src/routes/
    ├── creator-hub/                → Rotas do CAOS Studio
    ├── nexus-ai.ts                 → Rotas do CAOS Nexus
    ├── chat.ts                     → Chat IA com rate limiter (Lobos básicos)
    └── stub-v1.ts                  → Endpoints stub (substituir progressivamente)
```

## Decisões de Arquitetura

- **Auth:** Local-only via localStorage (`useLocalAuth`). Sem Clerk, Supabase ou login obrigatório. Usuário local criado automaticamente na primeira visita.
- **Mobile-first:** CAOS Studio tem nav inferior fixa, layout de 2 colunas em mobile, header compacto.
- **Identidade:** Todo texto visível ao usuário deve estar em **português brasileiro**. Raridades: Comum/Raro/Épico/Lendário.
- **RPG System:** Cada artefato criado tem raridade. Raridades mais altas têm bordas e brilhos diferentes (CSS: `rarity-Common`, `rarity-Rare`, `rarity-Epic`, `rarity-Legendary`).
- **Offline:** Aura Sphere tem Service Worker e suporte PWA. Chat funciona offline com fila de sincronização.

## Preferências do Usuário

- **SEM tela de login** — app abre diretamente na interface.
- **SEM Clerk, Supabase ou Lovable** — auth local apenas.
- **Mobile first** — toda UI deve funcionar bem em tela de 390px.
- **100% português** — nenhum texto em inglês na interface final.
- **Identidade CAOS** — nenhum nome de sistema anterior deve aparecer na UI.

## Próximas Tarefas

Ver arquivo `CAOS_TAREFAS.md` na raiz do projeto para a lista completa e unificada de todas as tarefas pendentes, organizadas por prioridade e bloco de trabalho.

## Gotchas

- Tailwind v3 (não v4) — usa `@tailwind base/components/utilities` e postcss
- CAOS Studio usa `wouter` para roteamento; Aura Sphere usa `react-router-dom`
- Vite config não usa `@tailwindcss/vite` — usa postcss
- `@capacitor/core` removido — stub em `platform.ts` para build web
- `@supabase/supabase-js` não instalado — stub mantém imports funcionando
- `@clerk/react` incompatível com React 19.1.7 + Vite 7 — não instalar
- OpenAI usa import lazy (`getOpenAI()`) para evitar crash no boot quando a integração não está configurada
