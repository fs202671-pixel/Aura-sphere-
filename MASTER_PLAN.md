# 🎯 MASTER PLAN - Aura Sphere Personal AI Assistant

## 📋 Objetivo Principal
Transformar Aura Sphere em assistente pessoal multifuncional, 100% gratuito por padrão, com gerenciamento de tarefas, habilidades dinâmicas, integração multimídia e execução automática com consentimento do usuário.

---

## 🏗️ FASES DE IMPLEMENTAÇÃO

### **FASE 1: Core Systems (Semanas 1-2)**
Fundação essencial para tudo funcionar

#### 1.1 Sistema de Planejamento e Acompanhamento
- [ ] Dashboard de Planejamento
  - Planos de estudo com milestones e barras de progresso
  - Tarefas com status (planejado, em progresso, concluído)
  - Projetos com subtarefas
  - Negócios/contas com valor e status
  - Aprendizados em tempo real
  
- [ ] API Endpoints
  - `POST /api/v1/planning/plans` - Criar plano
  - `GET /api/v1/planning/plans/{user_id}` - Listar planos com progresso
  - `POST /api/v1/planning/tasks` - Criar tarefa
  - `PATCH /api/v1/planning/tasks/{id}` - Atualizar status/progresso
  - `POST /api/v1/planning/projects` - Criar projeto
  - `GET /api/v1/planning/dashboard` - Dashboard completo

- [ ] Modelo de Dados (Database)
  - Table: `plans` (id, user_id, title, description, status, progress, created_at, updated_at)
  - Table: `tasks` (id, plan_id, title, status, progress, priority, due_date)
  - Table: `projects` (id, user_id, title, status, progress, linked_tasks)
  - Table: `accounts` (id, user_id, type, value, status, description)

#### 1.2 Sistema de Aprovação com Workflow
- [ ] Action Queue System
  - Toda ação que IA fazer passa por fila de aprovação
  - IA propõe ação → Sistema agenda confirmação → Usuário aprova/rejeita
  - Log completo de todas as ações pendentes e realizadas

- [ ] Components
  - `ActionProposal` (id, type, description, parameters, status, created_at)
  - Endpoints: `GET /api/v1/actions/pending`, `POST /api/v1/actions/{id}/approve`, `POST /api/v1/actions/{id}/reject`

#### 1.3 Frontend Dashboard Base
- [ ] Novo Layout Multi-Abas
  - Dashboard (overview)
  - Planejamento (planos, tarefas, progresso)
  - Ações Pendentes (fila de aprovação)
  - Habilidades (galeria)
  - Ferramentas (inventário)
  - Recursos (dados do sistema)
  - Dispositiv (device info e limitações)

---

### **FASE 2: Habilidades Dinâmicas (Semanas 3-4)**

#### 2.1 Sistema de Adição de Habilidades
- [ ] Ability Discovery Engine
  - Buscar repositórios em GitHub (free API com limite)
  - Analisar código aberto
  - Extrair funcionalidades
  - Gerar wrappers Python automaticamente

- [ ] Models
  - `Ability` (id, name, description, source_repo, functions, version, status, created_at)
  - `Skill` (id, ability_id, implementation, parameters, examples)
  - `Tool` (id, user_id, name, type, endpoint, authentication, free_tier_limit)

- [ ] Implementation
  - GitHub search (public repos only, no auth required for basic search)
  - AST parsing para extrair funções
  - Auto-generation de Python wrappers
  - Sandbox testing (via existing RobustnessTester)

- [ ] Endpoints
  - `POST /api/v1/abilities/search` - Buscar habilidade em repositórios
  - `POST /api/v1/abilities/add` - Adicionar habilidade
  - `GET /api/v1/abilities/list` - Listar habilidades do usuário
  - `GET /api/v1/abilities/{id}/details` - Detalhes de habilidade

#### 2.2 Galeria Visual de Recursos
- [ ] Visualization System
  - Cartões para cada habilidade/ferramenta
  - Ícones customizáveis
  - Tags de categoria
  - Busca e filtros

- [ ] Components
  - `AbilityCard` - Nome, descrição, source, usage stats
  - `ToolCard` - Nome, tipo, status, integração
  - Gallery com pagination

---

### **FASE 3: Gerenciamento de Plataformas Sociais (Semanas 5-6)**

#### 3.1 Instagram Integration (Free - Web API)
**Nota**: Usar `instagrapi` (free, community-maintained) em vez de API oficial paga

- [ ] Authentication & Session
  - Armazenar credenciais encryptadas
  - Session persistence
  - Login/logout management
  - Backup codes para segurança

- [ ] Data Collection (Sem pagamento)
  - Ler posts do feed
  - Listar histórico de saves/favorites
  - Extrair tags, hashtags
  - Coletar bios e seguidores (limite)
  - Ler stories (se público)
  - **NÃO acessar dados de contas privadas sem permissão explícita**

- [ ] Models
  - `SocialAccount` (id, user_id, platform, username, auth_token_encrypted, created_at)
  - `SavedContent` (id, account_id, content_id, content_type, title, metadata, saved_at)
  - `ContentCollection` (id, account_id, name, filters, created_at)

- [ ] Features
  - Sincronizar saves do Instagram
  - Organizar por categorias (anime, noticias, trabalho, etc)
  - Recommendations baseadas em saved content
  - Auto-tagging com IA

- [ ] Endpoints
  - `POST /api/v1/social/instagram/login` - Login
  - `GET /api/v1/social/instagram/saves` - Listar saves
  - `POST /api/v1/social/instagram/collections/{id}` - Criar coleção
  - `GET /api/v1/social/instagram/recommendations` - Sugestões

#### 3.2 TikTok, Twitter, YouTube (Free APIs onde possível)
- [ ] TikTok (Research API - limited, free for educational)
- [ ] Twitter (v2 API - free tier with limits)
- [ ] YouTube (Data API - free tier with quota)

#### 3.3 Social Management Actions (Com Aprovação)
- [ ] Ações Propostas
  - Publicar conteúdo
  - Agendar posts
  - Gerenciar seguidores
  - Responder DMs (template-based)
  - Analisar engagement

- [ ] Action Approval System
  - IA propõe ação → User aprova → Execute
  - Preview de resultado
  - Undo/rollback opções

- [ ] Endpoints
  - `POST /api/v1/social/{platform}/actions/propose` - Propor ação
  - `POST /api/v1/social/{platform}/actions/{id}/execute` - Executar após aprovação
  - `GET /api/v1/social/{platform}/analytics` - Analytics (free tier)

---

### **FASE 4: Adaptação Multi-Dispositivo (Semanas 7-8)**

#### 4.1 Device Detection & Adaptation
- [ ] Device Profiler
  - Mobile, tablet, desktop, TV detection
  - Storage availability
  - RAM disponível
  - Conectividade (online/offline)
  - CPU capabilities

- [ ] Models
  - `DeviceProfile` (id, user_id, device_type, os, storage_mb, ram_mb, capabilities, last_seen)

- [ ] Adaptive Features
  - TV mode: Larger UI, voice-first, minimal scrolling
  - Mobile: Optimized for touch, offline-first
  - Desktop: Full features, advanced controls
  - Offline mode: Cache essentials, queue actions

- [ ] Implementation
  ```python
  class DeviceAdaptationEngine:
      def analyze_device() -> DeviceProfile
      def get_optimal_ui_layout() -> dict
      def plan_storage_strategy() -> dict
      def suggest_improvements() -> List[Recommendation]
  ```

- [ ] Endpoints
  - `GET /api/v1/device/profile` - Device info
  - `POST /api/v1/device/optimize` - Plano de otimização
  - `GET /api/v1/device/recommendations` - Sugestões de melhoria

#### 4.2 Modo Multi-Mídia
- [ ] Modos Disponíveis
  - Text (padrão)
  - Voice (speech-to-text, TTS - use Google Cloud free tier)
  - Video/TV (streaming)
  - Developer mode (logs, debugging)

- [ ] Switching
  - User pode alternar modos via UI
  - Contextual defaults por device
  - Persistência de preferência

---

### **FASE 5: Vulnerabilidades & Segurança (Semanas 9-10)**

#### 5.1 Sistema de Detecção de Vulnerabilidades
- [ ] Self-Audit Engine
  - Validação de integridade de código
  - Verificação de sandbox escape attempts
  - Monitoramento de uso de recursos
  - Detecção de padrões suspeitos

- [ ] Models
  - `SecurityIssue` (id, severity, description, component, resolution, reported_at, status)

- [ ] Endpoints
  - `GET /api/v1/security/issues` - Listar problemas
  - `POST /api/v1/security/audit` - Executar auditoria
  - `PATCH /api/v1/security/issues/{id}/status` - User resolve/ignora

#### 5.2 Cost Control System
- [ ] API Cost Tracking
  - Monitor chamadas a APIs pagas
  - Alertas quando aproximando limite ou custos
  - Sugestão de alternativas gratuitas

- [ ] Models
  - `ApiUsage` (id, user_id, provider, endpoint, cost, timestamp)
  - `CostAlert` (id, user_id, type, amount_usd, threshold, action)

---

### **FASE 6: Referências Visuais & Customização (Semana 11)**

#### 6.1 Visual Reference Search
- [ ] Interface Designer
  - IA busca inspirações (Dribbble API free, Pinterest web scraping)
  - Apresenta opções ao user
  - User seleciona estilo preferido
  - IA aplica tema

- [ ] Implementation
  - CSS-in-JS para temas dinâmicos
  - Component biblioteca customizável
  - Preview em tempo real

#### 6.2 UI/UX Customization
- [ ] Opções
  - Color schemes
  - Layout variations
  - Font choices
  - Animation levels
  - Dark/light mode pro-defaults

---

### **FASE 7: Backend & Infrastructure (Semanas 12-13)**

#### 7.1 Upgrade do Backend Bridge
- [ ] Consolidação de Serviços
  - Unificar múltiplas agents (colony, hive, wolves)
  - Criar middleware centralizado para ações
  - Implementar unified action queue

#### 7.2 Persistência & Sincronização
- [ ] Data Sync Framework
  - Offline-first architecture
  - Sync quando online
  - Conflict resolution
  - Backup automático local/cloud (Google Drive API free ou similar)

#### 7.3 Voice Support (Free)
- [ ] Speech Recognition
  - Google Cloud Speech-to-Text (free tier: 60 min/mês)
  - Fallback: Whisper.cpp (offline, open source)
  - Local processing quando possível

- [ ] Text-to-Speech
  - Google Cloud TTS (free tier limitado)
  - Festival/eSpeak (local, offline)
  - Fallback: Seleção manual

---

## 📊 Estrutura de Tarefas

### SPRINT 1-2: Core Planning & Approval System
```
[ ] Database schema (plans, tasks, projects, accounts)
[ ] Backend endpoints para planejamento
[ ] Frontend dashboard layout
[ ] Action queue backend
[ ] Approval UI components
[ ] Tests para fluxo básico
```

### SPRINT 3-4: Habilidades Dinâmicas
```
[ ] GitHub search integration
[ ] AST parser para código
[ ] Ability wrapper generator
[ ] Sandbox testing
[ ] Frontend gallery
[ ] Tests para descoberta e execução
```

### SPRINT 5-6: Social Media Integration
```
[ ] Instagram login/auth (instagrapi)
[ ] Save collection system
[ ] Content organization backend
[ ] Recommendation engine
[ ] Action proposal system
[ ] Tests para fluxos sociais
```

### SPRINT 7-8: Multi-Device Support
```
[ ] Device profiler
[ ] Adaptive layout system
[ ] Storage optimization
[ ] Offline caching
[ ] Voice mode setup
[ ] Tests para cada device type
```

### SPRINT 9-10: Security & Monitoring
```
[ ] Vulnerability scanner
[ ] Cost tracking system
[ ] Alerts and notifications
[ ] Audit logging
[ ] Security dashboard
[ ] Tests para security
```

### SPRINT 11-13: Polish & Deployment
```
[ ] Visual customization
[ ] Theme system
[ ] Performance optimization
[ ] Documentation
[ ] User onboarding
[ ] Deploy to staging
```

---

## 🔧 Stack Recomendado (100% Free)

### Backend
- **LLM**: Ollama (self-hosted) ou Claude free tier
- **Database**: PostgreSQL (free, self-hosted)
- **Cache**: Redis (free, self-hosted)
- **Search**: Milvus (vector DB, free/open-source)
- **File Storage**: MinIO (S3-compatible, free)
- **Message Queue**: RabbitMQ (free, open-source)

### Frontend
- **Framework**: React.js (existing)
- **UI Kit**: Custom components + inspiration boards
- **Voice**: Whisper.cpp + Festival (free/open-source)
- **Video**: HLS.js (free, for streaming)

### APIs Gratuitas
- **Social Media**:
  - Instagram: instagrapi (community, free)
  - TikTok: TikTok Research API (limited, free)
  - Twitter: v2 API (free tier)
  - YouTube: Data API (free quota)
  
- **Utilities**:
  - GitHub: Public API (60 req/hr unauthenticated, 6000/hr authenticated free)
  - Google Cloud: Free tier (Cloud Storage, Cloud Functions limitados)
  - Weather: OpenWeatherMap free tier
  - News: NewsAPI free tier

- **Images/Design Inspiration**:
  - Unsplash API (free)
  - Pexels API (free)
  - Pixabay API (free)
  - Dribbble scraping (careful)

---

## ⚡ Priorização

### Crítica (Semana 1-2)
1. ✅ Dashboard com barras de progresso
2. ✅ Sistema de aprovação de ações
3. ✅ API endpoints básicos

### Alta (Semana 3-6)
4. Habilidades dinâmicas (GitHub search)
5. Instagram integration
6. Social media content organization

### Média (Semana 7-10)
7. Multi-device adaptation
8. Segurança e vulnerabilidades
9. Voice support

### Baixa (Semana 11+)
10. Customização visual
11. Temas e referências
12. Polish & optimization

---

## 📝 Próximos Passos

1. **Confirmar com usuário**:
   - Prioridades aceitáveis?
   - Timeline realista?
   - Stack válido?

2. **Setup inicial**:
   - Criar estrutura DB
   - Setup de APIs gratuitas (GitHub, Google Cloud)
   - Preparar exemplo simples

3. **Implementação iterativa**:
   - 1-2 semanas por sprint
   - Demos com usuário
   - Feedback loops

