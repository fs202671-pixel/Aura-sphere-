# 💰 FREE-FIRST STRATEGY - Como Manter 100% Gratuito

## 🎯 Princípio-Chave
**Padrão: Gratuito | Opção: Pago sob demanda com consentimento**

Cada funcionalidade tem uma implementação gratuita primeiro. APIs pagas são opcionais e requerem aprovação explícita do usuário.

---

## 📊 Matriz Funcionalidades vs APIs

### Planning & Monitoring
| Funcionalidade | Solução Gratuita | Alternativa Paga | Política |
|---|---|---|---|
| Planos & Tarefas | PostgreSQL local | - | Sempre local |
| Progresso & Barras | Cálculo simples no Backend | - | Nenhum custo |
| Notificações | Push local (web) | Twilio SMS | Pedir confirmação se SMS |
| Alertas | Em-app notifications | Email SMTP | Use SendGrid free tier |

### Habilidades Dinâmicas
| Funcionalidade | Solução Gratuita | Alternativa Paga | Política |
|---|---|---|---|
| GitHub Search | API pública (60 req/hr) | - | Válido por sempre |
| Extrair Código | AST parsing local | - | Processamento local |
| Sandbox Execution | Ollama local/Docker | AWS Lambda | Usar local primeira |
| Código Gerado | Armazena local/banco | - | Sem sync externo |

### Social Media Integration
| Funcionalidade | Solução Gratuita | Alternativa Paga | Política |
|---|---|---|---|
| Instagram Scrapping | instagrapi (community) | - | Community-maintained |
| Login/Auth | Session local | - | Offline-first |
| Saves Collection | PostgreSQL | - | Sem limite |
| Categorização | IA local (Ollama) | Claude API | Pedir confirmação |
| Analytics | Counts básicos | Meta API | Bloqueado sem permissão |
| Scheduling Posts | Local queue | Buffer/Later | Pedir confirmação |

### Voice & Media
| Funcionalidade | Solução Gratuita | Alternativa Paga | Política |
|---|---|---|---|
| Speech-to-Text | Whisper.cpp (offline) | Google Cloud STT | Pedir confirmação |
| Text-to-Speech | Festival (offline) | Google Cloud TTS | Pedir confirmação |
| Streaming | HLS.js local | CDN pago | Usar local |

### Cloud & Storage
| Funcionalidade | Solução Gratuita | Alternativa Paga | Política |
|---|---|---|---|
| Backup Local | Pasta local/USB | Google Drive API free | Usar local primeira |
| File Storage | MinIO local | AWS S3 | Usar local primeira |
| Sync Offline | Local cache | Nextcloud/Synology | Nenhum servidor externo por padrão |

---

## 🔧 Setup Inicial (Tudo Gratuito)

### 1. Backend Stack (Zero Cost)
```bash
# Banco de dados
docker run -d --name postgres postgres:15

# Cache
docker run -d --name redis redis:7

# Vector DB (para embeddings)
docker run -d --name milvus milvusdb/milvus:latest

# File Storage (S3-compatible)
docker run -d --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  minio/minio server /data

# LLM Local
docker run -d --name ollama ollama/ollama
# Pull model: ollama pull llama2:latest
```

### 2. Free API Credentials
```env
# GitHub API (60 req/hr without auth, no token needed)
# Usado automaticamente com fallback

# Google Cloud (free tier - 60 min/month speech)
# Opcional, pedir confirmação ao user

# OpenWeather (free tier)
OPENWEATHER_API_KEY=get-free-at-openweathermap.org

# NewsAPI (free tier - 100 req/day)
NEWSAPI_KEY=get-free-at-newsapi.org
```

### 3. Python Requirements (Apenas Open Source)
```
# Essentials
fastapi
sqlalchemy
pydantic

# Social media (community)
instagrapi  # Free, community-maintained Instagram

# Voice (offline)
numpy  # Whisper.cpp dependency
scipy  # Audio processing

# AI/ML (local)
ollama-client  # Local LLM
transformers  # Hugging Face models (local)
sentence-transformers  # Embeddings locally

# Utilities
requests
cryptography
pyyaml
```

---

## 💡 Estratégia por Feature

### Habilidades Dinâmicas (100% Free)
```python
class AbilityDiscoveryEngine:
    """
    Workflow:
    1. User solicita: "Adicione uma habilidade de fazer resize de imagens"
    2. IA busca no GitHub: language:python image resize stars:>50
    3. Extrai funções com segurança usando AST
    4. Gera wrapper seguro com sandbox
    5. Testa localmente
    6. User aprova
    7. Habilidade ativada
    
    Custo: 0 (apenas API gratuita do GitHub)
    """
    
    def discover_repo(keyword):
        # GitHub API free: 60 req/hour
        # Usar: ?q=language:python+stars:>10+sort:stars
        pass
    
    def extract_functions(repo_url):
        # Clone repo locally
        # Parse com AST
        # Retornar funções seguras
        pass
    
    def generate_wrapper(functions):
        # Create sandbox wrapper
        # Add validation
        # Return safe code
        pass
    
    def test_locally(wrapper_code):
        # Execute em Docker sandbox
        # Sem acesso externo
        pass
```

### Instagram Integration (Free with `instagrapi`)
```python
class InstagramIntegration:
    """
    Workflow:
    1. User logs in com username/password (encriptado local)
    2. IA sincroniza saves em background
    3. Categoriza automaticamente (local IA)
    4. Organiza em coleções
    5. User pode ver organized gallery
    6. IA recomenda baseado em saves
    
    Custo: 0
    
    Nota: instagrapi é community-maintained
    Se Instagram bloquear, fallback para scrapy ou playwright
    """
    
    def login(username, password):
        # Criar sessão
        # Encriptar credentials
        # Store local
        pass
    
    def sync_saves():
        # Fetch todos os saves do user
        # Armazena em DB local
        # Sem enviar para nenhum servidor
        pass
    
    def categorize_saves():
        # Usar Ollama local para categorizar
        # Exemplo: detector.analyze_image() → "Anime"
        # Sem custos de API
        pass
    
    def get_recommendations(theme=None):
        # Semantic search em saves local
        # Usar embeddings gerados localmente
        # Retornar recomendações
        pass
```

### Voice Support (Free with Whisper.cpp)
```python
class VoiceSupport:
    """
    Workflow:
    1. User ativa modo voice
    2. IA escuta (offline - Whisper.cpp)
    3. Transcreve texto
    4. Processa comando
    5. Responde com TTS (Festival offline)
    
    Custo: 0
    
    Fallback pago: Google Cloud Speech + TTS (com permissão)
    """
    
    def speech_to_text(audio_file):
        # Usar: Whisper.cpp (offline)
        # Ou: SpeechRecognition com Google free tier
        pass
    
    def text_to_speech(text):
        # Usar: Festival ou eSpeak (offline)
        # Ou: Google Cloud TTS (com permissão do user)
        pass
```

### Cloud Storage (Local-First)
```python
class StorageStrategy:
    """
    Hierarquia:
    1. Local Filesystem (padrão, zero custo)
    2. Local NAS/External Drive (se conectado)
    3. MinIO local (mais controle)
    4. Google Drive free tier (15GB, com permissão)
    5. AWS S3 (pago, com permissão e cartão)
    
    User nunca paga por storage a menos que escolha explicitamente
    """
    
    def get_optimal_storage():
        # Detectar: storage local disponível?
        # Recomendação: use local
        if has_external_drive:
            return "Use external drive para backup"
        elif storage_low:
            return "Ativar Google Drive backup? (15GB free)"
        else:
            return "Armazenamento local suficiente"
    
    def save_file(file, path):
        # Sempre salvar local primeiro
        # Então optionalmente sync para nuvem
        local_path = save_to_local(file, path)
        
        if user_opted_cloud_backup:
            async_sync_to_googledrive(local_path)
        
        return local_path
```

---

## 🚨 Handling Paid APIs

### Regra de Ouro
**Nenhuma API paga é chamada sem:**
1. ❌ **Nunca** incluída no código default
2. ✅ **Sempre** oferecida como opção ao user
3. ✅ **Sempre** pedir cartão/confirmação antes
4. ✅ **Sempre** mostrar custo estimado
5. ✅ **Sempre** permitir fallback gratuito

### Exemplo: API de Tradução
```python
def translate_text(text, target_lang):
    # Opção 1: Gratuita (local - offline)
    try:
        # Use Ollama local para tradução
        result = ollama_translate(text, target_lang)
        return result
    except:
        pass
    
    # Opção 2: Paga (com permissão)
    if user_has_google_translate_api:
        # Verificar estimated cost
        cost = estimate_google_translate_cost(text)
        
        # Pedir confirmação
        if user_confirms(f"Tradução vai custar ~${cost}?"):
            return google_translate(text, target_lang)
    
    # Fallback: não traduzir
    return text + " (Tradução não disponível)"
```

### Implementação de Cost Guard
```python
class CostGuard:
    """Vigilante de custos - alerta user antes de gastar"""
    
    def __init__(self, user_budget_usd=10.0):
        self.monthly_budget = user_budget_usd
        self.spent_this_month = 0
        self.pending_approvals = []
    
    def propose_paid_action(self, action_name, estimated_cost):
        """
        Propõe ação que vai custar dinheiro
        """
        if self.spent_this_month + estimated_cost > self.monthly_budget:
            return {
                "status": "BLOCKED",
                "reason": f"Budget limite atingido. Gasto: ${self.spent_this_month}/${self.monthly_budget}",
                "action": None
            }
        
        return {
            "status": "PENDING_APPROVAL",
            "message": f"Isso vai custar ~${estimated_cost}. Aprova?",
            "action_id": self.pending_approvals.append({
                "name": action_name,
                "cost": estimated_cost,
                "timestamp": now()
            })
        }
    
    def user_approves_action(self, action_id):
        action = self.pending_approvals.pop(action_id)
        self.spent_this_month += action["cost"]
        execute_action(action)
    
    def user_rejects_action(self, action_id):
        self.pending_approvals.pop(action_id)
        # Tentar alternativa gratuita
```

---

## 📋 Free API Quotas (Manter dentro de limites)

| API | Limite Gratuito | Renovação | Recomendação |
|---|---|---|---|
| GitHub | 60 req/hr (sem auth) | Por hora | Usar cache local |
| Twitter v2 | 450 req/15min | 15 minutos | Batch requests |
| YouTube Data | 10k quota/dia | Diária | Suficiente para 1 user |
| OpenWeather | 60 req/min | Por minuto | OK para updates |
| NewsAPI | 100 req/dia | Diária | Cache resultados |
| Google Cloud | 60 min speech/mês | Mensal | Use Whisper.cpp |

**Dica**: Usar Redis para cache de todas as chamadas por 24h

---

## 🔐 Security for Free APIs

```python
class FreeAPIManager:
    """Gerenciar lib de APIs gratuitas seguramente"""
    
    def __init__(self):
        self.rate_limits = {}
        self.cache = {}
        self.failed_apis = set()
    
    def call_api(self, api_name, endpoint, params):
        # 1. Verificar cache (24h TTL)
        if self.is_cached(api_name, endpoint, params):
            return self.get_cached(api_name, endpoint, params)
        
        # 2. Verificar rate limit
        if self.is_rate_limited(api_name):
            return self.get_cached_fallback() or raise_error()
        
        # 3. Tentar chamar
        try:
            result = request(api_name, endpoint, params)
            self.cache[(api_name, endpoint, json(params))] = (result, now())
            return result
        except Exception as e:
            self.failed_apis.add(api_name)
            return self.get_cached_fallback()
    
    def is_rate_limited(self, api_name):
        if api_name not in self.rate_limits:
            self.rate_limits[api_name] = {"last": now(), "count": 0}
        
        last, count = self.rate_limits[api_name].values()
        if now() - last < 1 * HOUR:
            return count >= self.get_limit(api_name)
        else:
            self.rate_limits[api_name] = {"last": now(), "count": 0}
            return False
```

---

## 💼 Cost Report for User

Mesmo que tudo seja gratuito, manter user informado:

```
📊 COST SUMMARY - May 2024
├─ Paid APIs Used: 0
├─ Total Spent: $0.00
├─ Potential Costs (if opted-in):
│  ├─ Google TTS: ~$0.03/hour of speech
│  ├─ AWS Lambda: ~$0.20/million requests
│  └─ Claude API: ~$0.003 per call
└─ Recommendation: Continue with free alternatives
```

---

## ✅ Checklist - Staying Free

Before shipping any feature:
- [ ] Existe alternativa gratuita?
  - [ ] Sim? Usar como default
  - [ ] Não? Criar alternativa open-source?
  
- [ ] Se precisar API paga:
  - [ ] Está pedindo permissão do user?
  - [ ] Mostrando custo estimado?
  - [ ] Oferecendo fallback gratuito?
  - [ ] Incluindo em cost report?
  
- [ ] Performance:
  - [ ] Cacheando resultados?
  - [ ] Respeitando rate limits?
  - [ ] Offline-first onde possível?

---

## 🎯 Free Forever Commitment

> "Aura Sphere funcionará completamente sem custos de API. Alternativas pagas são sempre opcionais e nunca incluídas por padrão. O usuário tem controle total sobre custos."

