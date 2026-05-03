"""
MemPalace Adapter for Aura-sphere
Integra sistema de memória estruturada do MemPalace
"""

import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

# Adicionar caminho do MemPalace
MEMPALACE_PATH = Path(__file__).parent.parent.parent.parent / "external-repos" / "memory-systems" / "mempalace"
if MEMPALACE_PATH.exists():
    sys.path.insert(0, str(MEMPALACE_PATH))

try:
    # Importações do MemPalace (se disponível)
    from mempalace.core.palace import Palace
    from mempalace.backends.chroma import ChromaBackend
    MEMPALACE_AVAILABLE = True
except ImportError:
    MEMPALACE_AVAILABLE = False
    print("⚠️ MemPalace não disponível - usando stubs")

class MemPalaceAdapter:
    """Adaptador para integrar MemPalace com Aura-sphere"""

    def __init__(self, base_path: str = "./memory_palace"):
        self.base_path = Path(base_path)
        self.palace = None
        self.backend = None
        self._initialize_mempalace()

    def _initialize_mempalace(self):
        """Inicializa sistema MemPalace"""
        if not MEMPALACE_AVAILABLE:
            print("🔄 MemPalace não disponível - criando stubs")
            self._create_mock_palace()
            return

        try:
            # Inicializar backend ChromaDB
            self.backend = ChromaBackend(
                persist_directory=str(self.base_path / "chroma_db")
            )

            # Inicializar palace
            self.palace = Palace(
                backend=self.backend,
                base_path=str(self.base_path)
            )

            print("✅ MemPalace inicializado com sucesso")

        except Exception as e:
            print(f"❌ Erro ao inicializar MemPalace: {e}")
            MEMPALACE_AVAILABLE = False
            self._create_mock_palace()

    def _create_mock_palace(self):
        """Cria palace mock para quando MemPalace não está disponível"""
        self.palace = MockPalace()

    async def store_conversation(self, conversation: Dict[str, Any], wing: str = "aura_sphere", room: str = "creative_sessions") -> bool:
        """Armazena conversa no sistema estruturado"""

        try:
            # Preparar dados para armazenamento
            drawer_data = {
                "timestamp": conversation.get("timestamp"),
                "user_input": conversation.get("user_input"),
                "agent_response": conversation.get("agent_response"),
                "context": conversation.get("context", {}),
                "skills_used": conversation.get("skills_used", []),
                "metadata": conversation.get("metadata", {})
            }

            # Armazenar no palace
            await self.palace.store_in_drawer(
                wing=wing,
                room=room,
                drawer=f"session_{conversation.get('session_id', 'unknown')}",
                content=json.dumps(drawer_data),
                metadata={
                    "type": "conversation",
                    "timestamp": drawer_data["timestamp"],
                    "skills": ",".join(drawer_data["skills_used"])
                }
            )

            return True

        except Exception as e:
            print(f"❌ Erro ao armazenar conversa: {e}")
            return False

    async def search_conversations(self, query: str, wing: str = "aura_sphere", room: str = "creative_sessions", limit: int = 10) -> List[Dict[str, Any]]:
        """Busca conversas semanticamente"""

        try:
            # Buscar no palace
            results = await self.palace.search_drawers(
                wing=wing,
                room=room,
                query=query,
                limit=limit
            )

            # Processar resultados
            conversations = []
            for result in results:
                try:
                    content = json.loads(result["content"])
                    conversations.append({
                        "id": result["drawer_id"],
                        "content": content,
                        "similarity": result.get("similarity", 0.0),
                        "metadata": result.get("metadata", {})
                    })
                except json.JSONDecodeError:
                    continue

            return conversations

        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []

    async def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Recupera contexto completo de uma sessão"""

        try:
            # Buscar drawer específico
            drawer_content = await self.palace.get_drawer(
                wing="aura_sphere",
                room="creative_sessions",
                drawer=f"session_{session_id}"
            )

            if drawer_content:
                return json.loads(drawer_content)
            else:
                return {}

        except Exception as e:
            print(f"❌ Erro ao recuperar contexto: {e}")
            return {}

    async def create_memory_wing(self, wing_name: str, description: str = "") -> bool:
        """Cria uma nova wing (categoria) de memória"""

        try:
            await self.palace.create_wing(
                name=wing_name,
                description=description,
                metadata={"type": "aura_sphere_memory"}
            )
            return True

        except Exception as e:
            print(f"❌ Erro ao criar wing: {e}")
            return False

    def list_wings(self) -> List[str]:
        """Lista todas as wings disponíveis"""
        if hasattr(self.palace, 'list_wings'):
            return self.palace.list_wings()
        return ["aura_sphere"]  # Default

    def is_mempalace_available(self) -> bool:
        """Verifica se MemPalace está disponível"""
        return MEMPALACE_AVAILABLE and self.palace is not None

class MockPalace:
    """Mock palace para quando MemPalace não está disponível"""

    def __init__(self):
        self.storage = {}

    async def store_in_drawer(self, wing: str, room: str, drawer: str, content: str, metadata: Dict = None):
        key = f"{wing}/{room}/{drawer}"
        self.storage[key] = {"content": content, "metadata": metadata or {}}

    async def search_drawers(self, wing: str, room: str, query: str, limit: int = 10):
        # Busca simples baseada em substring
        results = []
        for key, data in self.storage.items():
            if query.lower() in data["content"].lower():
                results.append({
                    "drawer_id": key.split("/")[-1],
                    "content": data["content"],
                    "similarity": 0.8,
                    "metadata": data["metadata"]
                })
                if len(results) >= limit:
                    break
        return results

    async def get_drawer(self, wing: str, room: str, drawer: str):
        key = f"{wing}/{room}/{drawer}"
        return self.storage.get(key, {}).get("content")

    async def create_wing(self, name: str, description: str = "", metadata: Dict = None):
        pass
