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
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

base_dir = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=base_dir / ".env")

from database import SessionLocal, init_db, ChatMessage, MemoryEntry, User, Conversation
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
import sys
sys.path.append(str(base_dir / "packages"))
from mempalace.memory import MemoryEngine
from llm_service import get_llm_service
from embedding_service import get_embedding_service
from agent import get_agent_service
from agent.planning_service import planning_service
from agent.action_queue_service import ActionQueueService
from mcp_server import server as mcp_server
from orchestrator import get_central_orchestrator

# MCP SSE Transport
from mcp.server.sse import SseServerTransport
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

ENV = os.getenv("ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
API_ORIGINS = [os.getenv("CORS_ORIGIN", "http://localhost:3000"), "http://localhost:3000"]

app = FastAPI(title="Aura-Sphere Bridge", version="0.1.0")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

init_db()
memory_engine = MemoryEngine()
agent_service = get_agent_service()
action_queue_service = ActionQueueService()

# Initialize MCP SSE Transport
mcp_transport = SseServerTransport("/api/v1/mcp/messages")


def get_current_user(authorization: str | None = Header(None)) -> dict[str, Any]:
    if not authorization:
        if ENV != "production":
            return {"sub": "dev-user", "email": "dev@local", "name": "Developer"}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "env": ENV}


# === MCP ENDPOINTS ===

@app.get("/api/v1/mcp/sse")
async def mcp_sse(request: Request):
    """MCP Server-Sent Events endpoint for tool calls."""
    async with mcp_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name="aura-sphere-mcp",
                server_version="0.1.0",
                capabilities=mcp_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


@app.post("/api/v1/mcp/messages")
async def mcp_messages(request: Request):
    """MCP message handling endpoint."""
    await mcp_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


@app.get("/api/v1/agent/session")
def get_agent_session(current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna o estado atual da sessão do agente."""
    return agent_service.get_session_report()


@app.post("/api/v1/agent/task")
def add_agent_task(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Adiciona uma nova tarefa à sessão do agente."""
    description = payload.get("description", "Tarefa sem descrição")
    task = agent_service.add_session_task(description)
    return {"task_id": task.id, "status": task.status, "description": task.description}


@app.post("/api/v1/agent/task/{task_id}/complete")
def complete_agent_task(
    task_id: str,
    payload: dict = {},
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Marca uma tarefa de agente como concluída."""
    details = payload.get("details") if isinstance(payload, dict) else None
    success = agent_service.complete_session_task(task_id, details)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"task_id": task_id, "completed": True}


@app.post("/api/v1/agent/sandbox")
def execute_agent_sandbox(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Executa código em sandbox com validações de permissão."""
    code = payload.get("code", "")
    inputs = payload.get("inputs", {})
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing code payload")
    result = agent_service.run_code_in_sandbox(code=code, inputs=inputs, user_id=current_user.get("sub", "dev-user"))
    return result


@app.post("/api/v1/agent/modification")
def submit_agent_modification(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Submete uma proposta de modificação para aprovação do usuário."""
    description = payload.get("description")
    target_files = payload.get("target_files", [])
    patch_summary = payload.get("patch_summary", "")
    detailed_changes = payload.get("detailed_changes", {})
    file_patches = payload.get("file_patches", {})

    if not description or not target_files or not patch_summary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="description, target_files and patch_summary are required"
        )

    if not isinstance(file_patches, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file_patches must be a dict matching target_files"
        )

    proposal = agent_service.submit_modification_proposal(
        description=description,
        target_files=target_files,
        patch_summary=patch_summary,
        file_patches=file_patches,
        detailed_changes=detailed_changes,
        user_id=current_user.get("sub", "dev-user")
    )
    return {"proposal": proposal}


@app.get("/api/v1/agent/modification")
def list_agent_modifications(
    status: str | None = None,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Lista propostas de modificação do agente."""
    proposals = agent_service.get_modification_proposals(status=status)
    return {"proposals": proposals}


@app.post("/api/v1/agent/modification/{proposal_id}/approve")
def approve_agent_modification(
    proposal_id: str,
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Aprova uma proposta de modificação pendente."""
    approval_comment = payload.get("comment")
    proposal = agent_service.approve_modification_proposal(
        proposal_id=proposal_id,
        approved_by=current_user.get("sub", "dev-user"),
        approval_comment=approval_comment
    )
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found or cannot be approved")
    return {"proposal": proposal}


@app.post("/api/v1/agent/modification/{proposal_id}/reject")
def reject_agent_modification(
    proposal_id: str,
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Rejeita uma proposta de modificação pendente."""
    reason = payload.get("reason")
    proposal = agent_service.reject_modification_proposal(
        proposal_id=proposal_id,
        rejected_by=current_user.get("sub", "dev-user"),
        reason=reason
    )
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found or cannot be rejected")
    return {"proposal": proposal}


@app.get("/api/v1/agent/modification/{proposal_id}")
def get_agent_modification(proposal_id: str, current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna uma proposta de modificação específica."""
    proposals = agent_service.get_modification_proposals()
    for proposal in proposals:
        if proposal["id"] == proposal_id:
            return {"proposal": proposal}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")


@app.get("/api/v1/actions/pending")
def list_pending_actions(
    status: str = "pending",
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Lista ações pendentes que requerem aprovação do usuário."""
    actions = action_queue_service.get_pending_actions(
        user_id=current_user.get("sub", "dev-user"),
        status=status
    )
    return {"actions": actions}


@app.post("/api/v1/actions/propose")
def propose_action(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Submete uma nova ação para aprovação."""
    action_type = payload.get("action_type")
    description = payload.get("description")
    parameters = payload.get("parameters", {})
    expires_at = payload.get("expires_at")

    if not action_type or not description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="action_type and description are required")

    result = action_queue_service.submit_action_proposal(
        user_id=current_user.get("sub", "dev-user"),
        action_type=action_type,
        description=description,
        parameters=parameters,
        expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
    )
    return {"action": result}


@app.post("/api/v1/actions/{action_id}/approve")
def approve_action(
    action_id: int,
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Aprova uma ação pendente."""
    result = action_queue_service.approve_action(
        action_id=action_id,
        approved_by=current_user.get("sub", "dev-user")
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found or cannot be approved")
    return {"action": result}


@app.post("/api/v1/actions/{action_id}/reject")
def reject_action(
    action_id: int,
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Rejeita uma ação pendente."""
    reason = payload.get("reason")
    result = action_queue_service.reject_action(
        action_id=action_id,
        rejected_by=current_user.get("sub", "dev-user"),
        reason=reason
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found or cannot be rejected")
    return {"action": result}


@app.get("/api/v1/agent/offline_mode")
def get_agent_offline_mode(current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna o modo offline do agente."""
    return {"offline_mode": agent_service.offline_mode}


@app.post("/api/v1/agent/offline_mode")
def set_agent_offline_mode(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Ativa ou desativa o modo offline do agente."""
    enabled = payload.get("enabled")
    if enabled is None or not isinstance(enabled, bool):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="enabled must be a boolean")
    agent_service.set_offline_mode(enabled)
    return {"offline_mode": agent_service.offline_mode}


@app.post("/api/v1/agent/offline_candidate")
def create_agent_offline_candidate(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Cria um candidato de evolução offline e valida em sandbox."""
    description = payload.get("description")
    candidate_code = payload.get("candidate_code")
    target_files = payload.get("target_files", [])
    patch_summary = payload.get("patch_summary")
    detailed_changes = payload.get("detailed_changes", {})

    if not description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="description is required")

    result = agent_service.run_offline_evolution_candidate(
        description=description,
        candidate_code=candidate_code,
        target_files=target_files,
        patch_summary=patch_summary,
        detailed_changes=detailed_changes,
        user_id=current_user.get("sub", "dev-user")
    )

    return {"offline_candidate": result}


@app.get("/api/v1/agent/supervisor")
def get_agent_supervisor(current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna o estado do supervisor do agente."""
    return agent_service.get_supervisor_status()


# === NOVOS ENDPOINTS DE GOVERNANÇA ===

@app.post("/api/v1/agent/user_command")
def execute_user_command(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Executa comando do usuário com prioridade máxima."""
    command = payload.get("command")
    parameters = payload.get("parameters", {})
    force = payload.get("force", False)
    
    if not command:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="command is required")
    
    result = agent_service.execute_user_command(
        user_id=current_user.get("sub", "dev-user"),
        command=command,
        parameters=parameters,
        force=force
    )
    return result


@app.post("/api/v1/agent/override_decision")
def override_agent_decision(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Permite que usuário sobrescreva decisão da IA."""
    agent_id = payload.get("agent_id", "aura-agent")
    original_decision = payload.get("original_decision")
    override_with = payload.get("override_with")
    reason = payload.get("reason")
    
    if original_decision is None or override_with is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="original_decision and override_with are required"
        )
    
    result = agent_service.override_agent_decision(
        user_id=current_user.get("sub", "dev-user"),
        agent_id=agent_id,
        original_decision=original_decision,
        override_with=override_with,
        reason=reason
    )
    return result


@app.post("/api/v1/agent/deploy_pipeline")
def run_deploy_pipeline(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Executa pipeline completo de deploy."""
    patch = payload.get("patch", {})
    user_approval = payload.get("user_approval", False)
    
    if not patch:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="patch is required")
    
    result = agent_service.run_deploy_pipeline(patch, user_approval)
    return result


@app.post("/api/v1/agent/learning_data")
def submit_learning_data(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Submete dados para aprendizado controlado."""
    source = payload.get("source", "user_approved")
    data = payload.get("data", {})
    metadata = payload.get("metadata", {})
    
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="data is required")
    
    data_id = agent_service.submit_data_for_learning(source, data, metadata)
    return {"data_id": data_id}


@app.post("/api/v1/agent/learning_data/{data_id}/validate")
def validate_learning_data(
    data_id: str,
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Valida dados para aprendizado."""
    approved = payload.get("approved", False)
    reason = payload.get("reason")
    
    result = agent_service.validate_learning_data(
        data_id=data_id,
        user_id=current_user.get("sub", "dev-user"),
        approved=approved,
        reason=reason
    )
    return result


@app.get("/api/v1/agent/learning_data/pending")
def get_pending_learning_data(current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna dados aguardando validação."""
    return {
        "pending_data": agent_service.controlled_learner.get_pending_validations()
    }


@app.post("/api/v1/agent/robustness_test")
def run_robustness_test(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Executa testes de robustez."""
    test_type = payload.get("test_type", "security")
    
    result = agent_service.run_robustness_tests(test_type)
    return result


@app.post("/api/v1/agent/destructive_action")
def request_destructive_action(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Submete requisição de ação destrutiva."""
    action_type = payload.get("action_type")
    target = payload.get("target")
    reason = payload.get("reason")
    
    if not action_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="action_type is required")
    
    request_id = agent_service.request_destructive_action(
        action_type=action_type,
        user_id=current_user.get("sub", "dev-user"),
        target=target,
        reason=reason
    )
    return {"request_id": request_id}


@app.post("/api/v1/agent/destructive_action/{request_id}/confirm")
def confirm_destructive_action(
    request_id: str,
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Confirma ação destrutiva."""
    result = agent_service.confirm_destructive_action(
        request_id=request_id,
        user_id=current_user.get("sub", "dev-user")
    )
    return result


@app.post("/api/v1/agent/destructive_action/{request_id}/execute")
def execute_destructive_action(
    request_id: str,
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Executa ação destrutiva confirmada."""
    backup_created = payload.get("backup_created", False)
    
    result = agent_service.execute_destructive_action(request_id, backup_created)
    return result


@app.get("/api/v1/agent/governance/status")
def get_governance_status(current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna status de governança."""
    return agent_service.get_governance_status()


@app.get("/api/v1/agent/governance/report")
def get_governance_report(current_user: dict[str, Any] = Depends(get_current_user)):
    """Gera relatório completo de governança."""
    return agent_service.get_governance_report()


@app.get("/api/v1/agent/audit_trail")
def get_audit_trail(
    event_type: str | None = None,
    user_id: str | None = None,
    entity: str | None = None,
    limit: int = 100,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Retorna audit trail com filtros."""
    filters = {}
    if event_type:
        filters["event_type"] = event_type
    if user_id:
        filters["user_id"] = user_id
    if entity:
        filters["entity"] = entity
    
    return {"audit_trail": agent_service.get_audit_trail(filters, limit)}


@app.get("/api/v1/agent/learning/report")
def get_learning_report(current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna relatório de aprendizado controlado."""
    return agent_service.get_learning_report()


# === OFFLINE EVOLUTION & ADAPTIVE LEARNING API ===

@app.get("/api/v1/agent/evolution/status")
def get_offline_evolution_status(current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna o status do agendador de evolução offline."""
    return agent_service.get_offline_evolution_status()


@app.post("/api/v1/agent/evolution/schedule")
def schedule_offline_evolution_task(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Agenda uma tarefa de evolução offline."""
    description = payload.get("description")
    task_type = payload.get("task_type")
    priority = payload.get("priority", 5)
    should_run_at = payload.get("should_run_at")

    if not description or not task_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="description and task_type are required")

    scheduled_task = agent_service.schedule_offline_evolution(
        description=description,
        task_type=task_type,
        priority=priority,
        should_run_at=datetime.fromisoformat(should_run_at) if should_run_at else None
    )
    return {"scheduled_task": scheduled_task}


@app.post("/api/v1/agent/evolution/mode")
def set_offline_evolution_mode(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Ativa ou desativa o modo de evolução offline."""
    enabled = payload.get("enabled")
    if enabled is None or not isinstance(enabled, bool):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="enabled must be a boolean")
    agent_service.set_offline_evolution_mode(enabled)
    return {"offline_evolution_mode": enabled}


@app.post("/api/v1/agent/code_variants")
def generate_code_variant(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Gera um variante de código alternativo."""
    module_name = payload.get("module_name")
    variant_type = payload.get("variant_type")
    description = payload.get("description")
    algorithm_name = payload.get("algorithm_name")

    if not module_name or not variant_type or not description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="module_name, variant_type and description are required")

    result = agent_service.generate_alternative_code_variant(
        module_name=module_name,
        variant_type=variant_type,
        description=description,
        algorithm_name=algorithm_name
    )
    return {"variant": result}


@app.get("/api/v1/agent/code_variants")
def list_code_variants(
    module_name: str | None = None,
    variant_type: str | None = None,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Lista variantes de código geradas."""
    return {"variants": agent_service.list_code_variants(module_name=module_name, variant_type=variant_type)}


@app.get("/api/v1/agent/code_variants/compare")
def compare_code_variants(
    variant_a_id: str,
    variant_b_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Compara duas variantes de código."""
    comparison = agent_service.compare_code_variants(variant_a_id, variant_b_id)
    if comparison is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    return {"comparison": comparison}


@app.post("/api/v1/agent/learning/start")
def start_adaptive_learning(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Inicia modo de aprendizado adaptativo."""
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="topic is required")
    return agent_service.start_adaptive_learning(topic, user_id=current_user.get("sub", "dev-user"))


@app.post("/api/v1/agent/learning/teach")
def teach_adaptive_learning(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Solicita a próxima lição do modo de aprendizado."""
    topic = payload.get("topic")
    if not topic:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="topic is required")
    return agent_service.teach_topic(topic, user_id=current_user.get("sub", "dev-user"))


@app.post("/api/v1/agent/learning/evaluate")
def evaluate_adaptive_learning(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Avalia resposta do usuário no modo de aprendizado."""
    topic = payload.get("topic")
    user_response = payload.get("user_response")
    if not topic or user_response is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="topic and user_response are required")
    return agent_service.evaluate_learning_response(topic, user_response, user_id=current_user.get("sub", "dev-user"))


@app.get("/api/v1/agent/learning/progress")
def get_adaptive_learning_progress(
    topic: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Retorna o progresso de aprendizado para um tópico."""
    return agent_service.get_learning_progress(topic, user_id=current_user.get("sub", "dev-user"))


@app.post("/api/v1/agent/learning/stop")
def stop_adaptive_learning(
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Finaliza o modo de aprendizado adaptativo."""
    return agent_service.stop_adaptive_learning(user_id=current_user.get("sub", "dev-user"))


@app.get("/api/v1/agent/learning/status")
def get_adaptive_learning_status(
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Retorna status do sistema de aprendizado adaptativo."""
    return agent_service.get_learning_status()


@app.get("/api/v1/agent/robustness/report")
def get_robustness_report(
    limit: int = 100,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Retorna relatório de testes de robustez."""
    return agent_service.get_robustness_report(limit)


@app.get("/api/v1/agent/destructive/history")
def get_destructive_history(
    limit: int = 100,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Retorna histórico de ações destrutivas."""
    return {"history": agent_service.get_destructive_history(limit)}


@app.get("/api/v1/agent/user_obedience/history")
def get_user_obedience_history(
    user_id: str | None = None,
    limit: int = 100,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Retorna histórico de comandos do usuário."""
    return {"history": agent_service.get_user_obedience_history(user_id, limit)}


@app.post("/api/v1/conversations", response_model=ConversationResponse)
def create_conversation(
    payload: ConversationCreate,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Criar nova conversa/sessão para um usuário"""
    user_id = current_user.get("sub", "dev-user")
    
    with SessionLocal() as session:
        session.merge(User(id=user_id, email=current_user.get("email", "unknown")))
        
        conversation = Conversation(
            user_id=user_id,
            title=payload.title or f"Conversa {datetime.now().strftime('%d/%m %H:%M')}",
            system_prompt=payload.system_prompt,
            prompt_type=payload.prompt_type or "assistant"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            system_prompt=conversation.system_prompt,
            prompt_type=conversation.prompt_type,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )


@app.get("/api/v1/conversations", response_model=ConversationListResponse)
def list_conversations(
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Listar todas as conversas do usuário"""
    user_id = current_user.get("sub", "dev-user")
    
    with SessionLocal() as session:
        conversations = (
            session.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )
        
        return ConversationListResponse(
            conversations=[
                ConversationResponse(
                    id=conv.id,
                    user_id=conv.user_id,
                    title=conv.title,
                    system_prompt=conv.system_prompt,
                    prompt_type=conv.prompt_type,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at
                )
                for conv in conversations
            ]
        )


@app.delete("/api/v1/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Deletar uma conversa"""
    user_id = current_user.get("sub", "dev-user")
    
    with SessionLocal() as session:
        conversation = (
            session.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .filter(Conversation.user_id == user_id)
            .first()
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Deletar mensagens associadas
        session.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).delete()  # TODO: Adicionar conversation_id ao ChatMessage
        
        session.delete(conversation)
        session.commit()
        
        return {"status": "deleted"}


@app.get("/api/v1/history", response_model=ChatHistoryResponse)
def history(user_id: str, current_user: dict[str, Any] = Depends(get_current_user)):
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    with SessionLocal() as session:
        events = (
            session.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at)
            .all()
        )

        return {
            "messages": [
                {"id": str(event.id), "role": event.role, "content": event.content}
                for event in events
            ]
        }


@app.post("/api/v1/memory")
def create_memory(item: MemoryItem, current_user: dict[str, Any] = Depends(get_current_user)):
    if ENV == "production" and current_user.get("sub") != item.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    with SessionLocal() as session:
        session.merge(User(id=item.user_id, email=current_user.get("email", "unknown")))
        session.add(
            MemoryEntry(
                user_id=item.user_id,
                role=item.role,
                content=item.content,
                category=item.category or "chat",
            )
        )
        session.commit()

    memory_engine.add_memory(item.user_id, item.content, category=item.category or "chat")
    return {"status": "saved"}


@app.get("/api/v1/memory", response_model=MemoryListResponse)
def list_memory(
    user_id: str,
    category: Optional[str] = None,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Lista memórias salvas de um usuário com filtros opcionais."""
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

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


def build_system_prompt(ai_name: str, prompt_type: str = None) -> str:
    """Build dynamic system prompt based on AI name and prompt type"""
    base_prompts = {
        "assistant": f"Você é {ai_name}, um assistente útil e educado. Responda de forma clara, curta e objetiva em português.",
        "developer": f"Você é {ai_name}, um experiente desenvolvedor. Ajude com código, debugging e explicações técnicas. Responda em português.",
        "creative": f"Você é {ai_name}, um assistente criativo. Propõe ideias de projetos, sugestões inovadoras e soluções criativas. Responda em português.",
        "analytical": f"Você é {ai_name}, um analista rigoroso. Analise problemas em profundidade, questione suposições e forneça insights. Responda em português.",
        "formal": f"Você é {ai_name}, um assistente profissional e formal. Comunique-se de forma clara e profissional. Responda em português.",
        "summarizer": f"Você é {ai_name}, um especialista em resumos. Sintetize informações complexas de forma clara e concisa. Responda em português.",
    }
    
    prompt_type = prompt_type or "assistant"
    return base_prompts.get(prompt_type, base_prompts["assistant"])


@app.post("/api/v1/chat")
async def chat(request: ChatRequest, current_user: dict[str, Any] = Depends(get_current_user)):
    """
    Endpoint de chat com streaming.
    Integra com LLM Service (OpenAI, Anthropic, Lovable ou Local fallback).
    Salva histórico e memória automaticamente.
    """
    user_id = request.user_id or current_user.get("sub", "dev-user")
    ai_name = request.ai_name or "Aurora"
    prompt_type = request.prompt_type or "assistant"
    
    # Converter mensagens do formato da request para formato OpenAI
    formatted_messages = []
    for msg in request.messages:
        formatted_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Build system prompt dinamicamente
    system_prompt = build_system_prompt(ai_name, prompt_type)
    
    # Salvar usuário e histórico
    def save_user_and_history():
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
    
    save_user_and_history()
    
    # Get LLM service
    llm_service = get_llm_service()
    
    async def event_stream():
        """Stream resposta do LLM em chunks SSE"""
        full_response = ""
        
        try:
            # Stream da resposta do LLM
            async for chunk in llm_service.stream_chat_completion(
                formatted_messages,
                system_prompt=system_prompt
            ):
                full_response += chunk
                payload = {"choices": [{"delta": {"content": chunk}}]}
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.01)  # Pequeno delay para evitar overwhelming
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_msg = f"Erro ao processar chat: {str(e)}"
            full_response = error_msg
            payload = {"choices": [{"delta": {"content": error_msg}}]}
            yield f"data: {json.dumps(payload)}\n\n"
            yield "data: [DONE]\n\n"
        finally:
            # Salvar resposta assistente no histórico
            if full_response:
                with SessionLocal() as session:
                    session.add(
                        ChatMessage(
                            user_id=user_id,
                            role="assistant",
                            content=full_response,
                        )
                    )
                    session.commit()
                
                # Salvar na memória do engine
                memory_engine.add_memory(
                    user_id, 
                    full_response, 
                    category="assistant"
                )
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/v1/search", response_model=SearchResponse)
def search(
    user_id: str, 
    q: str, 
    semantic: bool = True,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Busca em memória com suporte a busca semântica e text search
    
    Args:
        user_id: ID do usuário
        q: Query de busca
        semantic: Se True, usa busca semântica; se False, usa text search (ILIKE)
        current_user: Usuário autenticado
        
    Returns:
        SearchResponse com lista de resultados
    """
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    with SessionLocal() as session:
        # Buscar todas as entradas de memória do usuário
        memory_items = (
            session.query(MemoryEntry)
            .filter(MemoryEntry.user_id == user_id)
            .order_by(MemoryEntry.created_at.desc())
            .all()
        )
        
        if not memory_items:
            return {"results": []}
        
        # Se semantic search está habilitado e temos embeddings
        if semantic and os.getenv("SEMANTIC_SEARCH_ENABLED", "true").lower() == "true":
            try:
                embedding_service = get_embedding_service()
                
                # Preparar candidates para busca semântica
                candidates = [
                    (
                        str(item.id),
                        embedding_service.embed_text(item.content),
                        item.content
                    )
                    for item in memory_items
                ]
                
                # Fazer busca semântica
                search_results = embedding_service.search_similar(
                    q,
                    candidates,
                    top_k=20,
                    threshold=0.2  # Threshold mais baixo para resultados mais amplos
                )
                
                # Converter resultados para SearchResult format
                result_ids = [int(r["id"]) for r in search_results]
                results = []
                for result in search_results:
                    # Encontrar item original
                    item = next(i for i in memory_items if str(i.id) == result["id"])
                    results.append({
                        "id": str(item.id),
                        "role": item.role,
                        "content": item.content,
                        "category": item.category,
                    })
                
                return {"results": results}
            except Exception as e:
                # Fallback para text search se embeddings falhar
                print(f"Erro em busca semântica, usando text search: {str(e)}")
        
        # Fallback: text search com ILIKE
        term = f"%{q.lower()}%"
        items = (
            session.query(MemoryEntry)
            .filter(MemoryEntry.user_id == user_id)
            .filter(MemoryEntry.content.ilike(term))
            .order_by(MemoryEntry.created_at.desc())
            .limit(20)
            .all()
        )
        
        return {
            "results": [
                {
                    "id": str(item.id),
                    "role": item.role,
                    "content": item.content,
                    "category": item.category,
                }
                for item in items
            ]
        }


# === ORCHESTRATOR ENDPOINTS ===

orchestrator = get_central_orchestrator()

@app.post("/api/v1/orchestrator/command")
async def process_orchestrator_command(
    payload: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Processa comando através do orquestrador coletivo"""
    command = payload.get("command")
    if not command:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="command is required")

    user_id = current_user.get("sub", "dev-user")
    result = await orchestrator.process_user_command(command, user_id)
    return result


@app.get("/api/v1/orchestrator/tasks")
async def get_orchestrator_tasks(current_user: dict[str, Any] = Depends(get_current_user)):
    """Retorna tarefas ativas do orquestrador"""
    tasks = await orchestrator.get_active_tasks()
    return {"tasks": tasks}


@app.get("/api/v1/orchestrator/tasks/{task_id}")
async def get_orchestrator_task_status(
    task_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Retorna status de uma tarefa específica"""
    task = await orchestrator.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"task": task}


# === PLANNING API ===

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
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
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
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
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
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
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


@app.post("/api/v1/planning/projects")
def create_project(
    data: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Criar novo projeto"""
    user_id = current_user.get("sub", "dev-user")
    result = planning_service.create_project(
        user_id=user_id,
        title=data.get("title"),
        description=data.get("description", "")
    )
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result


@app.get("/api/v1/planning/projects/{user_id}")
def get_projects(
    user_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Listar projetos do usuário"""
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return {"projects": planning_service.get_user_projects(user_id)}


@app.post("/api/v1/planning/accounts")
def create_account(
    data: dict,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Criar nova conta (bank, business, learning)"""
    user_id = current_user.get("sub", "dev-user")
    account_type = data.get("account_type", "business")
    account_name = data.get("account_name") or data.get("name")
    value_usd = data.get("value_usd", 0.0)
    description = data.get("description", "")
    
    if not account_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="account_name is required")
    
    result = planning_service.create_account(
        user_id=user_id,
        account_type=account_type,
        account_name=account_name,
        value_usd=value_usd,
        description=description
    )
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result


@app.get("/api/v1/planning/accounts/{user_id}")
def get_accounts(
    user_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """Listar contas do usuário"""
    if ENV == "production" and current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return {"accounts": planning_service.get_user_accounts(user_id)}
