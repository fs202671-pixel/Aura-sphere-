import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

base_dir = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=base_dir / ".env")

from database import SessionLocal, init_db, ChatMessage, MemoryEntry, User, Conversation, Plan, Task
from schemas import (
    ChatRequest,
    ChatHistoryResponse,
    MemoryItem,
    SearchResponse,
    SearchResult,
    MemoryEntryResponse,
    MemoryListResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse
)

# Initialize database
init_db()

# Simple auth bypass for demo
def get_current_user():
    return {"sub": "demo-user", "email": "demo@example.com"}

ENV = os.getenv("ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"

app = FastAPI(title="Aura Sphere API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "demo_mode": True}

# === PLANNING API ===

from agent.planning_service import planning_service

@app.post("/api/v1/planning/plans")
def create_plan(
    data: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Criar novo plano de estudo/projeto"""
    user_id = current_user.get("sub", "dev-user")
    result = planning_service.create_plan(
        user_id=user_id,
        title=data.get("title"),
        description=data.get("description", "")
    )
    return result


@app.get("/api/v1/planning/plans/{user_id}")
def get_plans(
    user_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Listar planos do usuário"""
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {"plans": planning_service.get_user_plans(user_id)}


@app.post("/api/v1/planning/tasks")
def add_task(
    data: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Adicionar tarefa a um plano"""
    plan_id = data.get("plan_id")
    title = data.get("title")
    priority = data.get("priority", 5)

    result = planning_service.add_task(plan_id, title, priority)
    return result


@app.patch("/api/v1/planning/tasks/{task_id}")
def update_task(
    task_id: int,
    data: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Atualizar progresso de tarefa"""
    progress = data.get("progress", 0)
    result = planning_service.update_task_progress(task_id, progress)
    return result


@app.get("/api/v1/planning/dashboard/{user_id}")
def get_dashboard(
    user_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Dashboard completo de planejamento"""
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return planning_service.get_plan_dashboard(user_id)


# === MEMORY API ===

@app.get("/api/v1/memory", response_model=MemoryListResponse)
def list_memory(
    user_id: str = "demo-user",
    category: Optional[str] = None,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Lista memórias salvas de um usuário com filtros opcionais."""
    with SessionLocal() as session:
        query = session.query(MemoryEntry).filter(MemoryEntry.user_id == user_id)
        if category:
            query = query.filter(MemoryEntry.category == category)

        entries = query.order_by(MemoryEntry.created_at.desc()).limit(100).all()

    return {
        "memories": [
            {
                "id": str(entry.id),
                "role": entry.role,
                "content": entry.content,
                "category": entry.category,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
            }
            for entry in entries
        ]
    }


# === CHAT API (Mock) ===

@app.post("/api/v1/chat")
async def chat(request: ChatRequest, current_user: dict[str, Any] = Depends(get_current_user)):
    """Mock chat endpoint for demo"""
    user_id = request.user_id or current_user.get("sub", "dev-user")
    ai_name = request.ai_name or "Aurora"

    # Save user message
    with SessionLocal() as session:
        session.merge(User(id=user_id, email=current_user.get("email", "unknown")))
        for message in request.messages:
            if message.role != "assistant":
                session.add(
                    ChatMessage(
                        user_id=user_id,
                        role=message.role,
                        content=message.content,
                    )
                )
        session.commit()

    # Mock response
    mock_response = f"Olá! Sou {ai_name}, sua assistente IA. Você disse: '{request.messages[-1].content if request.messages else 'Olá'}'. Esta é uma demonstração do sistema de planejamento que acabamos de implementar!"

    # Save assistant response
    with SessionLocal() as session:
        session.add(
            ChatMessage(
                user_id=user_id,
                role="assistant",
                content=mock_response,
            )
        )
        session.commit()

    async def event_stream():
        """Stream resposta mock em chunks SSE"""
        full_response = mock_response

        yield f"data: {json.dumps({'choices': [{'delta': {'content': full_response}}]})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)