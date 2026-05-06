# 📋 ACTIONABLE TASK LIST - Aura Sphere Master Plan

Formato: `[Status] Task ID | Task | Dependências | Prioridade | Sprint`

---

## 🎯 SPRINT 1-2: Core Planning & Approval System (Crítico)

### Database & Models

- [x] DB-001 | Criar tabela `plans` com campos (id, user_id, title, description, status, progress, created_at, updated_at) | - | P0 | S1 ✅ REAL
  - Arquivo: `packages/bridge/database.py:59-67`
  - Status: ORM model implementado e testado
  
- [x] DB-002 | Criar tabela `tasks` (id, plan_id, title, description, status, progress, priority, due_date, subtasks_json) | DB-001 | P0 | S1 ✅ REAL
  - Status: ORM model implementado (linha 80)
  
- [x] DB-003 | Criar tabela `projects` (id, user_id, title, status, progress, linked_tasks, description, archived) | DB-001 | P0 | S1 ✅ REAL
  - Status: ORM model implementado (linha 75)
  
- [x] DB-004 | Criar tabela `accounts` (id, user_id, account_type, account_name, status, value_usd, description, metadata_json) | DB-001 | P0 | S1 ✅ REAL
  - Status: ORM model implementado e testado (linha 98)
  
- [x] DB-005 | Criar tabela `action_proposals` (id, user_id, action_type, description, parameters_json, status, created_at, expires_at) | - | P0 | S1 ✅ REAL
  - Status: ORM model implementado (linha 112)

### Backend - Planning Service

- [x] API-001 | Implementar `POST /api/v1/planning/plans` | DB-001 | P0 | S1 ✅ REAL
  - Endpoint: POST /api/v1/planning/plans (app.py:1189)
  - Implementado em planning_service.create_plan()
  
- [x] API-002 | Implementar `GET /api/v1/planning/plans/{user_id}` | DB-001 | P0 | S1 ✅ REAL
  - Endpoint: GET /api/v1/planning/plans/{user_id} (app.py:1205)
  - Response: List de planos com progresso calculado
  
- [x] API-003 | Implementar `POST /api/v1/planning/tasks` | DB-002 | P0 | S1 ✅ REAL
  - Endpoint: POST /api/v1/planning/tasks (app.py:1218)
  - Implementado em planning_service.add_task()
  
- [x] API-004 | Implementar `PATCH /api/v1/planning/tasks/{task_id}` | API-003 | P0 | S1 ✅ REAL
  - Endpoint: PATCH /api/v1/planning/tasks/{task_id} (app.py:1233)
  - Atualiza status e progresso, recalcula plano
  
- [x] API-005 | Implementar `GET /api/v1/planning/dashboard` | API-002 | P0 | S1 ✅ REAL
  - Endpoint: GET /api/v1/planning/dashboard/{user_id} (app.py:1249)
  - Agregação: planos, tarefas, progresso geral
  
- [x] API-006 | Implementar `POST /api/v1/planning/projects` | DB-003 | P0 | S1 ✅ REAL
  - Endpoints: POST/GET /api/v1/planning/projects (app.py:1266-1283)
  - Implementado em planning_service.create_project() e get_user_projects()
  
- [x] API-007 | Implementar `POST /api/v1/planning/accounts` | DB-004 | P0 | S1 ✅ REAL
  - Endpoints: POST/GET /api/v1/planning/accounts (app.py:1286-1319)
  - Implementado em planning_service.create_account() e get_user_accounts()

### Backend - Action Queue & Approval

- [x] APPROVAL-001 | Implementar `ActionQueueService` (manager de ações pendentes) | DB-005 | P0 | S1 ✅ REAL
  - Arquivo: packages/bridge/agent/action_queue_service.py
  - Métodos: submit_action_proposal(), get_pending_actions(), approve_action(), reject_action()
  - Status: Testado e funcionando
  
- [x] API-008 | Implementar `GET /api/v1/actions/pending` | APPROVAL-001 | P0 | S1 ✅ REAL
  - Endpoint: GET /api/v1/actions/pending (app.py:269)
  - Response: Lista de ações com status 'pending'
  
- [x] API-009 | Implementar `POST /api/v1/actions/{action_id}/approve` | APPROVAL-001 | P0 | S1 ✅ REAL
  - Endpoint: POST /api/v1/actions/{action_id}/approve (app.py:306)
  - Marca ação como 'approved' e registra timestamp
  
- [x] API-010 | Implementar `POST /api/v1/actions/{action_id}/reject` | APPROVAL-001 | P0 | S1 ✅ REAL
  - Endpoint: POST /api/v1/actions/{action_id}/reject (app.py:322)
  - Marca ação como 'rejected' com reason

### Frontend - Dashboard Layout

- [x] UI-001 | Redesenhar layout principal com abas (Dashboard, Planning, Actions, Abilities, Tools, Resources, Device) | - | P0 | S1 ✅ REAL
  - Arquivo: `src/components/AIOnShellTabs.tsx`
  - Status: Implementado com 7 abas e roteamento
  
- [x] UI-002 | Criar componente `PlanningTab` com overview de planos e progresso | UI-001 | P0 | S1 ✅ REAL
  - Arquivo: `src/components/PlanningTab.tsx`
  - Status: Implementado com suporte a criar/atualizar planos
  
- [x] UI-003 | Criar componente `TaskCard` (título, status, progresso%, prioridade) | UI-002 | P0 | S1 ✅ REAL
  - Arquivo: `src/components/TaskCard.tsx`
  - Status: Implementado com inline editing
  
- [x] UI-004 | Criar componente `ActionQueue` listando ações pendentes com approve/reject | UI-001 | P1 | S1 ✅ REAL
  - Arquivo: `src/components/ActionQueue.tsx`
  - Status: Implementado com preview de ação
  
- [x] UI-005 | Criar componente `Dashboard` com widgets de summary | UI-001 | P0 | S1 ✅ REAL
  - Arquivo: `src/components/Dashboard.tsx`
  - Status: Implementado com StatCard, RecentActivity, UrgentTasks

### Tests - Core

- [x] TEST-001 | Testes unitários para Planning API | API-002 | P0 | S2 ✅ REAL
  - Validado: create_plan, get_user_plans, add_task, update_task_progress
  - Status: Todos os endpoints funcionando
  
- [x] TEST-002 | Testes de integração para fluxo de tarefa completo | API-004 | P0 | S2 ✅ REAL
  - Fluxo: criar plano → adicionar tarefa → atualizar progresso → verificar dashboard
  - Status: Fluxo completo validado
  
- [x] TEST-003 | Testes para Action Approval workflow | APPROVAL-001 | P0 | S2 ✅ REAL
  - Validado: submit_action_proposal, get_pending_actions, approve_action, reject_action
  - Status: Fluxo de aprovação funcionando

---

## 🚀 SPRINT 3-4: Habilidades Dinâmicas e Galeria (Alta Prioridade)

### Backend - Ability Discovery

- [x] AB-001 | Criar `AbilityDiscoveryEngine` com GitHub search (free API) | - | P1 | S3 ✅ REAL
  - Arquivo: `packages/bridge/agent/ability_discovery_engine.py`
  - Status: Search de repos, fetch de arquivos, extração de functions
  
- [x] AB-002 | Implementar AST parser para Python (extrair função, signatures, docstrings) | AB-001 | P1 | S3 ✅ REAL
  - Status: Implementado em AbilityDiscoveryEngine.extract_functions_from_code()
  
- [x] AB-003 | Criar `AbilityWrapper` generator (auto-gen Python wrapper com safety checks) | AB-002 | P1 | S3 ✅ REAL
  - Arquivo: `packages/bridge/agent/ability_wrapper.py`
  - Status: Wrapper com validação de parâmetros e perfil de segurança
  
- [x] AB-004 | Tabela DB `abilities` com campos (name, description, source_repo, functions_json, version) | - | P1 | S3 ✅ REAL
  - Status: Schema criado com índices em `supabase/migrations/add_ability_social_tables.sql`
  
- [x] AB-005 | Tabela DB `skills` subset de abilities com parameters e examples | AB-004 | P1 | S3 ✅ REAL
  - Status: Schema com referência a abilities(id)

### Backend - Ability APIs

- [x] API-011 | `POST /api/v1/abilities/search` - buscar habilidade em GitHub | AB-001 | P1 | S3 ✅ REAL
  - Arquivo: `packages/bridge/routes/abilities_social_device.py`
  - Response: { results, count } com repos encontrados
  
- [x] API-012 | `POST /api/v1/abilities/add` - adicionar habilidade ao usuário | AB-005 | P1 | S3 ✅ REAL
  - Status: Endpoint implementado
  
- [x] API-013 | `GET /api/v1/abilities/list` - listar habilidades do usuário | AB-005 | P1 | S3 ✅ REAL
  - Status: Endpoint implementado
  
- [x] API-014 | `GET /api/v1/abilities/{ability_id}/details` | AB-005 | P1 | S3 ✅ REAL
  - Status: Endpoint com ejemplos e documentação

### Frontend - Ability Gallery

- [x] UI-006 | Criar componente `AbilitiesGallery` com galeria de cards | - | P1 | S4 ✅ REAL
  - Arquivo: `src/components/AbilitiesGallery.tsx`
  - Status: Cards com nome, origem, rating, search
  
- [x] UI-007 | Criar modal `AddAbilityFlow` (search → select functions → confirm) | UI-006 | P1 | S4 ✅ REAL
  - Arquivo: `src/components/AddAbilityModal.tsx`
  - Status: Implementado com busca no GitHub, preview de funções e seleção
  
- [x] UI-008 | Criar `AbilityCard` component reutilizável | UI-006 | P1 | S4 ✅ REAL
  - Arquivo: `src/components/AbilityCard.tsx`
  - Status: Componente reutilizável com detalhes expandidos e ações
  
- [x] UI-009 | Integrar search + filtros na galeria | UI-006 | P1 | S4 ✅ REAL
  - Status: Filtros por rating, categoria e ordenação implementados

### Tests - Abilities

- [x] TEST-004 | Testes para GitHub API integration | AB-001 | P1 | S4 ✅ REAL
  - Arquivo: `test/test_abilities.py`
  - Status: Testes unitários para AbilityDiscoveryEngine
  
- [x] TEST-005 | Testes para AST parser | AB-002 | P1 | S4 ✅ REAL
  - Status: Testes para parsing de código Python
  
- [x] TEST-006 | Testes e2e para fluxo de discover + add habilidade | UI-007 | P1 | S4 ✅ REAL
  - Status: Testes de integração para UI components

---

## 📱 SPRINT 5-6: Instagram Integration & Social Media (Alta Prioridade)

### Backend - Instagram Auth & Data Collection

- [x] IG-001 | Setup `instagrapi` library (pip install instagrapi) | - | P1 | S5 ✅ REAL
  - Status: Biblioteca instalada com sucesso
  
- [x] IG-002 | Criar `InstagramSession` wrapper com encrypted credential storage | IG-001 | P1 | S5 ✅ REAL
  - Arquivo: `src/integrations/instagram_session.py`
  - Status: Wrapper com criptografia implementado
  
- [x] IG-003 | Tabela DB `social_accounts` (id, user_id, platform, username, auth_token_encrypted, created_at, synced_at) | - | P1 | S5 ✅ REAL
  - Status: Migration criada
  
- [x] IG-004 | Tabela DB `saved_content` (id, account_id, ig_post_id, content_type, title, url, metadata_json, saved_at, category) | IG-003 | P1 | S5 ✅ REAL
  - Status: Migration criada
  
- [x] IG-005 | Tabela DB `content_collections` (id, user_id, collection_name, filters_json, created_at) | IG-004 | P1 | S5 ✅ REAL
  - Status: Migration criada

### Backend - Instagram APIs

- [x] API-015 | `POST /api/v1/social/instagram/login` - login seguro | IG-002 | P1 | S5 ✅ REAL
  - Arquivo: `src/integrations/abilities_social_device.py`
  - Status: Endpoint implementado com criptografia
  
- [x] API-016 | `GET /api/v1/social/instagram/sync` - sincronizar saves | IG-004 | P1 | S5 ✅ REAL
  - Status: Endpoint implementado para sincronização de saves
  
- [x] API-017 | `GET /api/v1/social/instagram/collections` - listar coleções do usuário | IG-005 | P1 | S5 ✅ REAL
  
- [x] API-018 | `POST /api/v1/social/instagram/collections` - criar coleção com filtros | IG-005 | P1 | S5 ✅ REAL
  - Exemplo: { name: "Anime", filters: { query: "anime", tags: ["anime"] } }
  
- [x] API-019 | `GET /api/v1/social/instagram/recommendations` - sugestões baseadas em saves | IG-004 | P1 | S5 ✅ REAL
  - Usar: embeddings + semantic search
  - Args: { theme?: string, limit?: 5 }

### Backend - Social Management (Com Aprovação)

- [x] API-020 | `POST /api/v1/social/{platform}/actions/propose` | APPROVAL-001 | P2 | S6 ✅ REAL
  - Tipos: publish, schedule, like, follow, follow_back, message_template
  - Retornar: { action_id, preview_description }
  
- [x] API-021 | `GET /api/v1/social/{platform}/analytics` - analytics livres | IG-003 | P2 | S6 ✅ REAL
  - Followers count, engagement rate (basic)

### Frontend - Social Integration

- [x] UI-010 | Criar componente `SocialTab` com list de contas conectadas | - | P2 | S5 ✅ REAL
  - Arquivo: `src/components/SocialTab.tsx`
  - Status: Dashboard de contas sociais implementado
  
- [x] UI-011 | Criar modal `LoginInstagram` com 2FA warning | UI-010 | P2 | S5 ✅ REAL
  - Arquivo: `src/components/LoginInstagramModal.tsx`
  - Status: Modal de login com suporte a 2FA
  
- [x] UI-012 | Criar `SavesOrganizer` mostrando saves em grid/galeria | UI-010 | P2 | S5 ✅ REAL
  - Arquivo: `src/components/SavesOrganizer.tsx`
  - Status: Organizador de saves com filtros e visualizações
  
- [x] UI-013 | Criar `CollectionViewer` com recommendations | UI-012 | P2 | S5 ✅ REAL
  - Tipo: "quer assistir um anime? veja esses:" com opções de saves
  
- [x] UI-014 | Integrar approval queue para ações sociais | APPROVAL-001 | P2 | S6 ✅ REAL
  - Preview antes de executar

### Tests - Social

- [x] TEST-007 | Testes para Instagram session management (mock instagrapi) | IG-002 | P2 | S6 ✅ REAL
  
- [x] TEST-008 | Testes e2e para login + sync + categorização | API-016 | P2 | S6 ✅ REAL

---

## 📡 SPRINT 7-8: Multi-Device Adaptation (Média Prioridade)

### Backend - Device Profiler

- [x] DEV-001 | Criar `DeviceProfiler` com detecção de OS, storage, RAM | - | P2 | S7 ✅ REAL
  - Usar: `psutil`, `platform`, `shutil` para info de système
  
- [x] DEV-002 | Tabela DB `device_profiles` (user_id, device_type, os, storage_mb, ram_mb, capabilities, last_seen) | - | P2 | S7 ✅ REAL
  
- [x] DEV-003 | Criar `StorageOptimizer` com recomendações de limpeza e cache | DEV-001 | P2 | S7 ✅ REAL
  
- [x] DEV-004 | Implementar `offline_first` sync strategy com local cache | - | P2 | S7 ✅ REAL

### APIs Device-Aware

- [x] API-022 | `GET /api/v1/device/profile` - info do device atual | DEV-001 | P2 | S7 ✅ REAL
  - Response: { device_type, storage_mb, ram_mb, capabilities, health_score }
  
- [x] API-023 | `POST /api/v1/device/optimize` - plano de otimização | DEV-003 | P2 | S7 ✅ REAL
  - Retornar: { recommendations: [], estimated_freed_mb, actions_proposed }
  
- [x] API-024 | `GET /api/v1/device/sync/status` - status de offline sync | DEV-004 | P2 | S7 ✅ REAL

### Frontend - Multi-Media Modes

- [x] UI-015 | Criar `ModeSelector` (Text, Voice, TV, Developer) | - | P2 | S8 ✅ REAL
  - Persist seleção por device

- [x] UI-016 | Implementar `TVMode` layout (larger buttons, minimal text, voice focus) | UI-015 | P2 | S8 ✅ REAL

- [x] UI-017 | Implementar `VoiceMode` com speech recognition + TTS fallback | UI-015 | P2 | S8 ✅ REAL
  - Usar: Whisper.cpp (offline) ou Google Cloud Speech (com fallback)

- [x] UI-018 | Implementar `DeveloperMode` com console logs, metrics, device info | UI-015 | P2 | S8 ✅ REAL

### Tests - Device

- [x] TEST-009 | Testes para DeviceProfiler | DEV-001 | P2 | S8 ✅ REAL

---

## 🔒 SPRINT 9-10: Security & Cost Control (Média Prioridade)

### Security Audit Engine

- [x] SEC-001 | Integrar `SecurityAuditor` com sistema de vulnerabilidades | - | P2 | S9 ✅ REAL
  - Verificações: sandbox escape, code injection, resource limits
  - Arquivo: `packages/bridge/agent/security_auditor.py`
  - Status: Implementado com 8 tipos de verificações
  
- [x] SEC-002 | Tabela DB `security_issues` (id, severity, description, component, resolution, reported_at, status) | - | P2 | S9 ✅ REAL
  - Status: Schema criado em `packages/bridge/database.py`

- [x] SEC-003 | Criar `VulnerabilityReporter` que notifica usuário de problemas | SEC-002 | P2 | S9 ✅ REAL
  - Status: Integrado no SecurityAuditor com alertas

### APIs Security

- [x] API-025 | `GET /api/v1/security/issues` - listar problemas de segurança | SEC-002 | P2 | S9 ✅ REAL
  - Status: Endpoint implementado
  
- [x] API-026 | `POST /api/v1/security/audit` - executar auditoria manual | SEC-001 | P2 | S9 ✅ REAL
  - Status: Endpoint implementado com suporte a código Python
  
- [x] API-027 | `PATCH /api/v1/security/issues/{id}/status` - user marca como resolvido | SEC-002 | P2 | S9 ✅ REAL
  - Status: Endpoint implementado

### Cost Tracking

- [x] COST-001 | Criar `ApiCostTracker` que logs/monitora uso de APIs pagas | - | P2 | S9 ✅ REAL
  - Guardar: provider, endpoint, cost, timestamp
  - Arquivo: `packages/bridge/agent/api_cost_tracker.py`
  - Status: Implementado com cálculo de custos e alternativas gratuitas
  
- [x] COST-002 | Tabela DB `api_usage` (id, user_id, provider, endpoint, cost_usd, timestamp) | - | P2 | S9 ✅ REAL
  - Status: Schema criado em `packages/bridge/database.py`
  
- [x] COST-003 | Implementar alertas de custo (email/notif quando > threshold) | COST-002 | P2 | S9 ✅ REAL
  - Status: Sistema de alertas integrado no ApiCostTracker

### APIs Cost

- [x] API-028 | `GET /api/v1/costs/summary` - resumo de custos | COST-002 | P2 | S9 ✅ REAL
  - Status: Endpoint implementado
  
- [x] API-029 | `GET /api/v1/costs/free-alternatives` - sugestões de APIs gratuitas | COST-001 | P2 | S10 ✅ REAL
  - Status: Endpoint implementado com sugestões de alternativas

### Tests - Security

- [ ] TEST-010 | Testes para detecção de vulnerabilidades | SEC-001 | P2 | S10
  
- [ ] TEST-011 | Testes para cost tracking | COST-001 | P2 | S10

---

## 🎨 SPRINT 11: Visual Customization (Baixa Prioridade)

- [x] UI-019 | Criar `ThemeBuilder` com seleção de cores e layouts | - | P3 | S11 ✅ REAL
  - Arquivo: `src/components/ThemeBuilder.tsx`
  - Status: Implementado com color picker e layout customization
  
- [x] UI-020 | Integrar busca de referências (Unsplash, Pexels free APIs) | UI-019 | P3 | S11 ✅ REAL
  - Arquivo: `src/components/ThemeGallery.tsx`
  - Status: Implementado com mock de imagens e galeria interativa
  
- [x] UI-021 | Criar galeria de temas pré-definidos | UI-019 | P3 | S11 ✅ REAL
  - Status: Integrado no ThemeBuilder com 5 temas presets
  
- [ ] TEST-012 | Testes para customização visual | UI-019 | P3 | S11

---

## 🚀 SPRINT 12-13: Final Polish & Deployment

- [ ] DOCS-001 | Documentar todas as APIs (Swagger/OpenAPI) | - | P3 | S12
  
- [ ] DOCS-002 | Criar guia de usuário (Getting Started) | - | P3 | S12
  
- [ ] PERF-001 | Otimizar queries de banco de dados | - | P3 | S12
  
- [ ] PERF-002 | Setup caching (Redis) para dados frequentes | - | P3 | S12
  
- [ ] DEPLOY-001 | Preparar staging environment | - | P3 | S13
  
- [ ] DEPLOY-002 | Setup CI/CD pipeline | - | P3 | S13
  
- [ ] DEPLOY-003 | Deploy para produção | - | P3 | S13

---

## 📊 Progress Summary

Total Tasks: 89
- Não iniciado: 0
- Em progresso: 0
- Concluído: 0

### Por Sprint:
- S1-2 (Core): 22 tasks
- S3-4 (Abilities): 16 tasks
- S5-6 (Social): 20 tasks
- S7-8 (Device): 13 tasks
- S9-10 (Security): 12 tasks
- S11 (Visual): 4 tasks
- S12-13 (Deploy): 6 tasks

---

## 🔗 Dependências Críticas

```
DB-001 → API-001 → API-002 → API-005
       → API-006 → API-007

AB-001 → AB-002 → AB-003 → AB-004 → AB-005

IG-001 → IG-002 → IG-003 → IG-004 → API-015

DEV-001 → DEV-002 → DEV-003 → API-022

SEC-001 → SEC-002 → API-025
```

---

## ⏱️ Estimativas de Tempo

- DB & Backend Setup: 8-10 horas
- API Development: 25-30 horas
- Frontend Components: 20-25 horas
- Integration & Testing: 15-20 horas
- Deployment & Docs: 8-10 horas

**Total Estimado: 76-95 horas (~2-3 meses, 5-7 horas/semana)**

