# CAOS — Lista Unificada de Tarefas para o Próximo Programador

> **Sistema:** CAOS (IA Central + Ecossistema Criativo)
> **Última atualização:** Maio 2026
> **Fonte:** Consolidação de ACTIONABLE_TASKS.md + MASTER_PLAN.md + PRIORITIES.md + NEXT_STEPS.md + análise do estado atual do código

---

## 📌 CONTEXTO DO SISTEMA

O projeto **CAOS** é um ecossistema de IA criativa composto por múltiplos subsistemas que ainda carregam nomes de versões anteriores. O objetivo desta lista é guiar o próximo programador para:

1. Unificar tudo sob a identidade **CAOS**
2. Conectar os módulos que estão isolados
3. Implementar os sistemas de segurança (Lobos, Formigas, Abelhas)
4. Completar funcionalidades incompletas

---

## 🗂️ ESTRUTURA ATUAL DOS SUBSISTEMAS

| Subsistema Atual | Deve Virar | Localização |
|---|---|---|
| `aura-sphere` | CAOS Shell / Interface Principal | `artifacts/aura-sphere/` |
| `nexus-ai` | CAOS Nexus / Módulo de Habilidades | `artifacts/nexus-ai/` |
| `AIOn` / `AIOnShell` | CAOS Interface / Painel Central | `artifacts/aura-sphere/src/components/` |
| `creator-hub-rpg` | CAOS Studio / Arsenal Criativo | `artifacts/creator-hub-rpg/` |
| `api-server` | CAOS API Gateway | `artifacts/api-server/` |

---

## 🔴 BLOCO 1 — RENOMEAÇÃO DE IDENTIDADE (Alta Prioridade)

### REN-001 · Renomear `aura-sphere` → CAOS Shell
- [ ] `artifacts/aura-sphere/public/manifest.json` — Alterar `name: "Aura Sphere"` → `"CAOS"` e `short_name: "AuraSphere"` → `"CAOS"`
- [ ] `artifacts/aura-sphere/public/sw.js` — Renomear `CACHE_NAME = 'aura-sphere-cache-v1'` → `'caos-cache-v1'`
- [ ] `artifacts/aura-sphere/src/lib/localProfile.ts` — `STORAGE_KEY_PREFIX = "aura-sphere-profile"` → `"caos-profile"`
- [ ] `artifacts/aura-sphere/src/lib/projects.ts` — `STORAGE_KEY_PREFIX = "aura-sphere-projects"` → `"caos-projects"`
- [ ] `artifacts/aura-sphere/src/hooks/useVisualCustomization.ts` — `'aura-sphere-visual-state'` → `'caos-visual-state'`
- [ ] `replit.md` — Atualizar referências de "Aura Sphere" → "CAOS"
- [ ] `lib/db/src/schema/aura-sphere.ts` — Renomear tabelas para `caos_profiles`, `caos_messages` (requer migration)

### REN-002 · Renomear `nexus-ai` → CAOS Nexus
- [ ] `artifacts/nexus-ai/` — Renomear pacote `@workspace/nexus-ai` → `@workspace/caos-nexus`
- [ ] `lib/db/src/schema/nexus.ts` — Renomear tabelas `nexus_skills` → `caos_nexus_skills`, `nexus_conversations` → `caos_nexus_conversations`, etc. (requer migration)
- [ ] `artifacts/api-server/src/routes/nexus-ai.ts` — Renomear arquivo e variável `nexusAiRouter` → `caosNexusRouter`
- [ ] `artifacts/api-server/src/routes/index.ts` — Atualizar import e registro do router
- [ ] `artifacts/creator-hub-rpg/src/pages/projects.tsx` linha 100 — Alterar placeholder `"ex: Operação Nexus V2"` → `"ex: Operação CAOS V2"`
- [ ] `artifacts/mockup-sandbox/src/components/mockups/nexus-themes/` — Renomear pasta para `caos-themes/`

### REN-003 · Renomear `AIOn` → CAOS Interface
- [ ] `artifacts/aura-sphere/src/components/AIOnShell.tsx` → `CaosShell.tsx` (renomear arquivo e componente)
- [ ] `artifacts/aura-sphere/src/components/AIOnShellTabs.tsx` → `CaosShellTabs.tsx`
- [ ] `artifacts/aura-sphere/src/pages/Index.tsx` — Atualizar import de `<AIOnShell>` → `<CaosShell>`
- [ ] `artifacts/aura-sphere/src/App.tsx` — Atualizar rotas que usam `AIOnShellTabs`

---

## 🟠 BLOCO 2 — INTEGRAÇÃO ENTRE MÓDULOS (Alta Prioridade)

### INT-001 · Conectar Creator Hub (CAOS Studio) com API
- [ ] Verificar que as rotas `/api/items`, `/api/themes`, `/api/agents`, `/api/skills`, `/api/projects` estão registradas sem conflito em `artifacts/api-server/src/routes/index.ts`
- [ ] Confirmar que a rota `/api/skills` do creator-hub não conflita com a `/skills` do nexus-ai (mover hub skills para `/api/hub/skills` se necessário)
- [ ] Testar end-to-end: criar item no CAOS Studio → aparecer no banco → aparecer no Arsenal

### INT-002 · Conectar CAOS Shell com CAOS Nexus
- [ ] As habilidades do Nexus (`nexus_skills`) devem aparecer como Protocolos no CAOS Studio
- [ ] Criar endpoint unificado `GET /api/caos/capacidades` que retorna habilidades do nexus + protocolos do hub
- [ ] Atualizar CAOS Shell para usar o sistema de Protocolos do Studio

### INT-003 · Sincronização de Dados Unificada
- [ ] Criar rota `GET /api/caos/status` que retorna estado de todos os subsistemas (itens, entidades, protocolos, missões, conversas)
- [ ] Este endpoint é o "coração" do dashboard Central CAOS

---

## 🟡 BLOCO 3 — SISTEMAS DE SEGURANÇA (Média-Alta Prioridade)

> **Contexto:** Os documentos históricos do projeto mencionam três agentes de segurança com nomes de animais — Lobos, Formigas e Abelhas. O código atual tem apenas um rate limiter básico (`chat.ts`) e stubs para endpoints de segurança (`stub-v1.ts`). Estes sistemas precisam ser IMPLEMENTADOS de verdade.

### Arquitetura Proposta: A Tríade de Defesa do CAOS

```
┌─────────────────────────────────────────────────────────────┐
│                    CAOS · TRÍADE DE DEFESA                  │
├─────────────┬───────────────────────┬───────────────────────┤
│   🐺 LOBOS  │    🐜 FORMIGAS        │    🐝 ABELHAS         │
│  (Guardiões)│    (Vigilantes)       │    (Executoras)       │
├─────────────┼───────────────────────┼───────────────────────┤
│ Rate limit  │  Detecção de padrões  │  Resposta automática  │
│ por IP/user │  suspeitos e anomalias│  e bloqueio reativo   │
│ Throttling  │  Log de auditoria     │  Alertas e notifs     │
│ Autenticação│  Análise de payloads  │  Quarentena de IPs    │
└─────────────┴───────────────────────┴───────────────────────┘
```

---

### SEG-001 · 🐺 LOBOS — Guardiões de Acesso (Rate Limiter Avançado)
**Status atual:** Implementação básica em `chat.ts` (30 req/min/IP). Precisa ser generalizado.

**O que implementar:**
- [ ] Criar `artifacts/api-server/src/security/lobos.ts` — middleware de rate limiting reutilizável
- [ ] Rate limit por **IP** (atual, manter)
- [ ] Rate limit por **rota** (endpoints críticos têm limites diferentes)
- [ ] Rate limit por **user_id** para usuários autenticados (mais generoso)
- [ ] Limite progressivo: 1ª violação = aviso, 2ª = delay 5s, 3ª = bloqueio 1h
- [ ] Persistir estado de bloqueio no banco (tabela `caos_security_blocks`)
- [ ] Endpoint `GET /api/caos/security/blocks` para visualização no dashboard

```typescript
// Estrutura sugerida de lobos.ts
export const lobos = {
  chatLimit: rateLimit({ windowMs: 60_000, max: 30 }),
  apiGeneralLimit: rateLimit({ windowMs: 60_000, max: 100 }),
  fusaoLimit: rateLimit({ windowMs: 3_600_000, max: 10 }), // Fusão de artefatos
  sensitiveLimit: rateLimit({ windowMs: 60_000, max: 5 }),
};
```

---

### SEG-002 · 🐜 FORMIGAS — Vigilantes de Padrões (Detecção de Anomalias)
**Status atual:** Apenas stubs em `stub-v1.ts`. Nenhuma detecção real.

**O que implementar:**
- [ ] Criar `artifacts/api-server/src/security/formigas.ts` — sistema de detecção de padrões
- [ ] Log de todas as requisições em tabela `caos_audit_log` (ip, rota, user, timestamp, payload_size, status)
- [ ] Detectar padrões suspeitos:
  - Muitas requisições de um mesmo IP em janela curta (já coberto pelos Lobos)
  - Payloads com padrões de injection (SQL, XSS, prompt injection para IA)
  - Tentativas de acessar rotas não autorizadas repetidamente
  - Atividade em horários incomuns (heurística configurável)
- [ ] Implementar `GET /api/caos/security/issues` com dados REAIS (substituir stub)
- [ ] Implementar `POST /api/caos/security/audit` com análise real de código (ou heurística básica)
- [ ] Tabela: `caos_security_issues` (id, severity, description, component, ip, user_id, detected_at, status)

```typescript
// Middleware das Formigas — inserir em todas as rotas
export async function formigasMiddleware(req, res, next) {
  await logRequest(req); // sempre loga
  const threats = await analyzePayload(req.body, req.path);
  if (threats.length > 0) await flagSuspiciousActivity(req.ip, threats);
  next();
}
```

---

### SEG-003 · 🐝 ABELHAS — Executoras de Resposta (Ação Reativa)
**Status atual:** Inexistente. Nenhuma resposta automática a ameaças.

**O que implementar:**
- [ ] Criar `artifacts/api-server/src/security/abelhas.ts` — sistema de resposta a ameaças
- [ ] Quando as Formigas detectam ameaça → Abelhas executam ação:
  - **Nível 1 (baixo):** Registra e continua
  - **Nível 2 (médio):** Resposta com delay artificial (honeypot)
  - **Nível 3 (alto):** Bloqueia IP por 1h e notifica no dashboard
  - **Nível 4 (crítico):** Bloqueia IP por 24h, notifica e requer revisão manual
- [ ] Dashboard de ameaças ativas: `GET /api/caos/security/threats`
- [ ] Sistema de whitelist/blacklist: `POST /api/caos/security/whitelist`, `POST /api/caos/security/blacklist`
- [ ] Quarentena de IPs suspeitos (resposta 429 com mensagem genérica)
- [ ] Endpoint de revisão manual de bloqueios (para o admin desbloquear)

---

### SEG-004 · Implementar o SecurityDashboard Real
- [ ] `artifacts/aura-sphere/src/components/SecurityDashboard.tsx` já existe com UI completa
- [ ] Substituir os stubs em `stub-v1.ts` com implementações reais
- [ ] Conectar `GET /api/v1/security/issues` → tabela `caos_security_issues`
- [ ] Conectar `POST /api/v1/security/audit` → lógica das Formigas
- [ ] Conectar `PATCH /api/v1/security/issues/:id/status` → atualizar banco
- [ ] Adicionar no StatusDashboard o status dos Lobos (bloqueios ativos), Formigas (padrões detectados) e Abelhas (ameaças em quarentena)
- [ ] Traduzir labels ingleses restantes no SecurityDashboard (Open → Aberto, Resolved → Resolvido, Ignored → Ignorado)

---

### SEG-005 · Schema de Banco para Segurança
- [ ] Criar `lib/db/src/schema/security.ts` com as tabelas:
  ```typescript
  caos_audit_log       // log de todas as requisições
  caos_security_issues // problemas detectados pelas Formigas
  caos_security_blocks // IPs bloqueados pelos Lobos/Abelhas
  ```
- [ ] Rodar `pnpm --filter @workspace/db run push` para aplicar

---

## 🟢 BLOCO 4 — FUNCIONALIDADES PENDENTES DO CAOS STUDIO (Média Prioridade)

### STUDIO-001 · Sistema de Fusão de Artefatos
- [ ] Criar endpoint `POST /api/items/fusao` que recebe dois `item_id` e gera um novo item Épico ou Lendário
- [ ] Lógica: raridade resultado = raridade superior + 1 tier (ou Lendário se já Épico)
- [ ] Nome e descrição gerados por IA (opcional — pode ser mock por ora)
- [ ] UI: botão "Fundir" no Arsenal que abre seletor de dois itens
- [ ] Registrar fusão no audit log

### STUDIO-002 · Conectar Entidades com Protocolos
- [ ] Ao visualizar uma Entidade, permitir selecionar Protocolos para "plugar" nela
- [ ] Chamar `POST /api/hub-skills/:id/plug` ao plugar
- [ ] Exibir lista de protocolos plugados no card da Entidade

### STUDIO-003 · Sistema de Construção de Missão
- [ ] Ao criar Missão, permitir selecionar Fragmento (tema), Entidades e Protocolos
- [ ] Botão "Construir Missão" chama `POST /api/projects/:id/build`
- [ ] Mostrar status de progresso: Rascunho → Construindo → Concluída
- [ ] Animação de loading durante "Construindo" (3 segundos atual → pode ser estendido)

### STUDIO-004 · Detalhe de Artefato Completo
- [ ] Na página `/itens/:id` — botão "Clonar" ainda não tem função (apenas UI)
- [ ] Implementar chamada `POST /api/items/:id/clone` no botão Clonar
- [ ] Redirecionar para o novo item após clonar

### STUDIO-005 · Busca e Filtros Avançados no Arsenal
- [ ] Adicionar campo de busca por nome no Arsenal
- [ ] Filtro por data (mais recentes / mais antigos)
- [ ] Ordenação por raridade (Lendários primeiro)
- [ ] Paginação (atualmente carrega tudo)

---

## 🔵 BLOCO 5 — FUNCIONALIDADES HERDADAS (Baixa-Média Prioridade)

> Estas tarefas foram planejadas em sessões anteriores e são válidas para o ecossistema CAOS

### HER-001 · Sistema de Memória Unificada do CAOS
- [ ] Criar tabela `caos_memories` no banco para armazenar contexto de conversas
- [ ] Endpoint `POST /api/caos/memory` para salvar memória
- [ ] Endpoint `GET /api/caos/memory/busca?q=...` para busca semântica (pode ser busca por texto simples inicialmente)
- [ ] Conectar memória ao chat principal do CAOS Shell

### HER-002 · Chat Offline e Sincronização
- [ ] CAOS Shell já tem lógica de localStorage, mas sync com backend é incompleta
- [ ] Implementar fila de mensagens offline: ao reconectar, enviar mensagens pendentes
- [ ] Indicador visual de modo offline no header do CAOS Shell

### HER-003 · Sistema de Custos de API
- [ ] Implementar rastreamento real de chamadas para OpenAI em `chat.ts`
- [ ] Registrar em tabela `caos_api_usage` (provider, endpoint, tokens, custo_estimado, timestamp)
- [ ] Substituir stub `GET /api/v1/costs/summary` com dados reais
- [ ] Mostrar custo estimado no dashboard Central CAOS

### HER-004 · Stubs do Servidor a Substituir
> `artifacts/api-server/src/routes/stub-v1.ts` tem endpoints falsos. Implementar ou remover:
- [ ] `/v1/abilities/*` → conectar com sistema de Protocolos do CAOS Studio
- [ ] `/v1/actions/*` → implementar fila de ações pendentes (Action Queue real)
- [ ] `/v1/device/profile` → detectar device do usuário (User-Agent parsing)
- [ ] `/v1/memory/*` → conectar com sistema HER-001
- [ ] `/v1/planning/*` → conectar com sistema de Missões do CAOS Studio
- [ ] `/v1/social/*` → manter como stub (baixa prioridade)

---

## ⚫ BLOCO 6 — DÉBITO TÉCNICO E LIMPEZA (Baixa Prioridade)

### DEB-001 · Organização de Rotas da API
- [ ] Verificar conflito entre `/api/skills` (nexus) e `/api/hub-skills` (creator-hub)
- [ ] Mover toda lógica do nexus para prefixo `/api/nexus/` para separar dos módulos hub
- [ ] Documentar todas as rotas em comentário no `index.ts`

### DEB-002 · Migração de Schema de Banco
- [ ] Criar migration para renomear tabelas `hub_*` → `caos_*` (ou manter como está e documentar)
- [ ] Criar migration para renomear `nexus_*` → `caos_nexus_*`
- [ ] Criar migration para renomear `aura_sphere_*` → `caos_shell_*`

### DEB-003 · replit.md e Documentação
- [ ] Atualizar `replit.md` — mudar "Aura Sphere" → "CAOS" em toda documentação
- [ ] Documentar a arquitetura completa do CAOS (quais artifacts existem e para que servem)
- [ ] Criar `ARQUITETURA.md` explicando fluxo de dados entre os módulos

### DEB-004 · Testes Básicos
- [ ] Criar testes de smoke para rotas principais do creator-hub (items, themes, agents, skills, projects)
- [ ] Testar rate limiter dos Lobos com cenário de abuso
- [ ] Testar fluxo completo: criar item → ver no Arsenal → detalhar → clonar → destruir

---

## 📊 SUMÁRIO DE PRIORIDADES

| Bloco | Área | Prioridade | Estimativa |
|---|---|---|---|
| BLOCO 1 — Renomeação | Identidade CAOS | 🔴 Alta | 4-6h |
| BLOCO 2 — Integração | Conectar módulos | 🟠 Alta | 6-10h |
| BLOCO 3 — Segurança | Lobos/Formigas/Abelhas | 🟡 Média-Alta | 12-20h |
| BLOCO 4 — CAOS Studio | Features faltando | 🟢 Média | 8-12h |
| BLOCO 5 — Herdadas | Backlog de sessões | 🔵 Baixa | 10-15h |
| BLOCO 6 — Débito | Limpeza técnica | ⚫ Baixa | 4-6h |

**Total estimado:** 44–69 horas de desenvolvimento

---

## 🚀 SUGESTÃO DE ORDEM DE EXECUÇÃO

```
Sessão 1 (2-3h): REN-001 + REN-002 parcial (só arquivos críticos)
Sessão 2 (3-4h): SEG-001 (Lobos) + SEG-005 (schema) → Formigas básico
Sessão 3 (2-3h): INT-001 (resolver conflito de rotas) + STUDIO-004 (botão clonar)
Sessão 4 (3-4h): SEG-002 (Formigas completo) + SEG-003 (Abelhas básico)
Sessão 5 (2-3h): STUDIO-001 (Fusão) + STUDIO-002 (Entidades + Protocolos)
Sessão 6 (2-3h): SEG-004 (SecurityDashboard real) + HER-003 (custos)
Sessão 7 (2h):   DEB-001 + DEB-003 (limpeza e documentação)
```

---

## 🔐 NOTAS SOBRE OS SISTEMAS DE SEGURANÇA

### Por que Lobos, Formigas e Abelhas?

O nome vem de comportamentos de animais sociais que inspiram estratégias de segurança:

- **🐺 Lobos** são guardas de fronteira — agressivos na primeira linha, bloqueiam acesso indevido antes de entrar
- **🐜 Formigas** são vigilantes silenciosas — observam tudo, detectam padrões anômalos, acumulam inteligência
- **🐝 Abelhas** são executoras coordenadas — quando a colônia é ameaçada, respondem em conjunto com precisão

O código atual só tem os **Lobos básicos** (rate limiter simples em chat.ts). As **Formigas** e **Abelhas** existem apenas como stubs. A Tríade completa tornaria o CAOS muito mais robusto para produção.

### Implementação Crítica: Proteção contra Prompt Injection

Uma ameaça específica do CAOS (sistema de IA): usuários maliciosos podem tentar injetar instruções no chat para manipular a IA. As Formigas devem detectar payloads suspeitos:

```typescript
// Padrões a detectar nas Formigas
const PROMPT_INJECTION_PATTERNS = [
  /ignore (previous|all|above) instructions/i,
  /você (agora é|deve ser|é) uma/i,
  /system:\s*(você|tu|you)/i,
  /\[SYSTEM\]|\[INSTRUÇÃO\]|\[OVERRIDE\]/i,
  /act as (if you (are|were)|a)/i,
];
```

---

*Documento gerado em 13/05/2026 — Consolidação de todas as listas de tarefas do projeto CAOS*
*Fontes: .migration-backup/ACTIONABLE_TASKS.md + MASTER_PLAN.md + PRIORITIES.md + NEXT_STEPS.md + análise do código atual*
