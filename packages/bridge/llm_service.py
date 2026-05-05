"""
LLM Service - Integração com múltiplos provedores de IA
Suporta: OpenAI, Anthropic (Claude), Lovable e Local
"""

import os
from typing import AsyncGenerator
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuração para provedores de LLM"""
    provider: str
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 2048


class LLMService:
    """Serviço unificado para chamadas a LLMs"""
    
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "anthropic")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))
        
        # Configurar cliente baseado no provedor
        if self.provider == "openai":
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            except ImportError:
                self.provider = "local"
                self.client = None
                self.model = "local"
                print("Aviso: openai package não instalado, usando fallback local")
                
        elif self.provider == "anthropic":
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            except ImportError:
                self.provider = "local"
                self.client = None
                self.model = "local"
                print("Aviso: anthropic package não instalado, usando fallback local")
                
        elif self.provider == "lovable":
            # Lovable has its own API structure
            self.api_key = os.getenv("LOVABLE_API_KEY")
            self.model = "lovable-default"
            
        else:
            # Fallback para modo local/desenvolvimento
            self.provider = "local"
            self.client = None
    
    async def stream_chat_completion(
        self, 
        messages: list[dict],
        system_prompt: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Gera uma resposta de chat streaming de um LLM
        Yields chunks de texto a medida que são recebidos
        """
        
        # Preparar sistema de prompt
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        if self.provider == "openai":
            async for chunk in self._stream_openai(messages, **kwargs):
                yield chunk
        elif self.provider == "anthropic":
            async for chunk in self._stream_anthropic(messages, **kwargs):
                yield chunk
        elif self.provider == "lovable":
            async for chunk in self._stream_lovable(messages, **kwargs):
                yield chunk
        else:
            # Fallback local para desenvolvimento
            async for chunk in self._stream_local(messages, **kwargs):
                yield chunk
    
    async def _stream_openai(
        self, 
        messages: list[dict],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming com OpenAI"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Erro ao chamar OpenAI: {str(e)}"
    
    async def _stream_anthropic(
        self, 
        messages: list[dict],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming com Anthropic Claude"""
        try:
            # Extrair system prompt se existir
            system_prompt = None
            if messages and messages[0].get("role") == "system":
                system_prompt = messages[0]["content"]
                messages = messages[1:]
            
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
                temperature=self.temperature,
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"Erro ao chamar Anthropic: {str(e)}"
    
    async def _stream_lovable(
        self, 
        messages: list[dict],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming com Lovable API"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.lovable.dev/v1/chat",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"messages": messages, **kwargs},
                )
                
                async for chunk in response.aiter_text():
                    if chunk:
                        yield chunk
        except Exception as e:
            yield f"Erro ao chamar Lovable: {str(e)}"
    
    async def _stream_local(
        self, 
        messages: list[dict],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Fallback local para desenvolvimento/teste"""
        import asyncio
        
        # Simular resposta em streaming para fins de testes
        user_message = next(
            (m.get("content", "") for m in messages if m.get("role") == "user"),
            "olá"
        )
        
        responses = {
            "oi": "Olá! Sou Aurora, sua assistente de IA. Como posso ajudar?",
            "qual é seu nome": "Sou Aurora, uma assistente de IA criada para ajudar você.",
            "teste": "Este é um modo de teste. Configure OPENAI_API_KEY ou ANTHROPIC_API_KEY para usar IA real.",
        }
        
        response_text = next(
            (v for k, v in responses.items() if k in user_message.lower()),
            f"Você disse: '{user_message}'. (Modo simulado - configure uma chave de API real)"
        )
        
        # Simular streaming enviando caractere por caractere
        chunk_size = 5
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i+chunk_size]
            yield chunk
            await asyncio.sleep(0.01)  # Pequeno delay para simular streaming


def get_llm_service() -> LLMService:
    """Factory para obter instância de LLM Service"""
    return LLMService()
