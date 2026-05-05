"""
OpenJarvis Adapter for Aura-sphere
Integra capacidades do OpenJarvis com o sistema atual
"""

import sys
import os
from typing import TYPE_CHECKING, Dict, Any, List, Optional
from pathlib import Path

# Adicionar caminho do OpenJarvis
OPENJARVIS_PATH = Path(__file__).parent.parent.parent.parent / "external-repos" / "ai-frameworks" / "openjarvis"
if OPENJARVIS_PATH.exists():
    sys.path.insert(0, str(OPENJARVIS_PATH))

try:
    # Importações do OpenJarvis (se disponível)
    from openjarvis.core.agent import Agent
    from openjarvis.skills.skill_manager import SkillManager
    OPENJARVIS_AVAILABLE = True
except ImportError:
    OPENJARVIS_AVAILABLE = False
    print("⚠️ OpenJarvis não disponível - usando stubs")

if TYPE_CHECKING:
    from .service import AgentService

class OpenJarvisAdapter:
    """Adaptador para integrar OpenJarvis com Aura-sphere"""

    def __init__(self, agent_service: "AgentService"):
        self.agent_service = agent_service
        self.jarvis_agent = None
        self.skill_manager = None
        self._initialize_openjarvis()

    def _initialize_openjarvis(self):
        """Inicializa componentes do OpenJarvis"""
        if not OPENJARVIS_AVAILABLE:
            print("🔄 OpenJarvis não disponível - criando stubs")
            return

        try:
            # Inicializar agente OpenJarvis
            self.jarvis_agent = Agent(config={
                "model": "qwen3.5:4b",  # Modelo local
                "local_first": True,
                "enable_tools": True
            })

            # Inicializar gerenciador de skills
            self.skill_manager = SkillManager()
            self._load_aura_sphere_skills()

            print("✅ OpenJarvis inicializado com sucesso")

        except Exception as e:
            print(f"❌ Erro ao inicializar OpenJarvis: {e}")
            OPENJARVIS_AVAILABLE = False

    def _load_aura_sphere_skills(self):
        """Carrega skills específicas do Aura-sphere"""
        if not self.skill_manager:
            return

        # Skills criativas
        creative_skills = [
            "image_generation",
            "image_editing",
            "media_analysis",
            "creative_assistance",
            "prompt_evolution"
        ]

        for skill in creative_skills:
            try:
                self.skill_manager.load_skill(skill)
                print(f"📚 Skill carregada: {skill}")
            except Exception as e:
                print(f"⚠️ Erro ao carregar skill {skill}: {e}")

    async def process_creative_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisições criativas usando OpenJarvis"""

        if not OPENJARVIS_AVAILABLE or not self.jarvis_agent:
            # Fallback para sistema atual
            return await self._fallback_processing(request, context)

        try:
            # Usar OpenJarvis para processamento avançado
            response = await self.jarvis_agent.process_request(
                request=request,
                context=context,
                skills=["creative_assistance", "image_generation"]
            )

            # Integrar com validação do Aura-sphere
            validated_response = await self.agent_service.validate_response(response)

            return {
                "success": True,
                "response": validated_response,
                "source": "openjarvis_enhanced",
                "skills_used": response.get("skills_used", [])
            }

        except Exception as e:
            print(f"❌ Erro no processamento OpenJarvis: {e}")
            return await self._fallback_processing(request, context)

    async def _fallback_processing(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback para processamento com sistema atual"""
        print("🔄 Usando fallback para sistema atual")

        # Usar métodos existentes do AgentService
        if "generate_image" in request.lower():
            return await self.agent_service.generate_image(context.get("prompt", ""))
        elif "edit_image" in request.lower():
            return await self.agent_service.edit_image(context)
        elif "analyze_media" in request.lower():
            return await self.agent_service.analyze_media(context.get("media_path", ""))

        return {
            "success": False,
            "response": "Requisição não reconhecida",
            "source": "fallback"
        }

    async def enhance_memory_system(self, query: str) -> List[Dict[str, Any]]:
        """Melhora capacidades de memória usando técnicas do OpenJarvis"""
        if not OPENJARVIS_AVAILABLE:
            return []

        try:
            # Usar capacidades de pesquisa semântica do OpenJarvis
            memory_results = await self.jarvis_agent.search_memory(
                query=query,
                context_type="creative_session"
            )

            return memory_results.get("results", [])

        except Exception as e:
            print(f"⚠️ Erro na busca de memória: {e}")
            return []

    def get_available_skills(self) -> List[str]:
        """Retorna lista de skills disponíveis"""
        if not self.skill_manager:
            return ["image_generation", "image_editing", "media_analysis"]  # Skills básicas

        return self.skill_manager.list_skills()

    def is_openjarvis_available(self) -> bool:
        """Verifica se OpenJarvis está disponível"""
        return OPENJARVIS_AVAILABLE and self.jarvis_agent is not None
