from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    conversation_id: Optional[int] = None  # Nova conversa se None
    ai_name: Optional[str] = None
    prompt_type: Optional[str] = "assistant"  # assistant, developer, creative, analytical, formal, summarizer
    messages: List[Message] = Field(default_factory=list)


class ChatHistoryResponse(BaseModel):
    messages: List[Message]


class MemoryItem(BaseModel):
    user_id: str
    role: str
    content: str
    category: Optional[str] = None


class SearchResult(BaseModel):
    id: str
    role: str
    content: str
    category: str


class SearchResponse(BaseModel):
    results: List[SearchResult]


class MemoryEntryResponse(BaseModel):
    id: str
    role: str
    content: str
    category: str
    created_at: datetime


class MemoryListResponse(BaseModel):
    memories: List[MemoryEntryResponse]


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None
    prompt_type: Optional[str] = "assistant"


class ConversationResponse(BaseModel):
    id: int
    user_id: str
    title: Optional[str]
    system_prompt: Optional[str]
    prompt_type: str
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]

