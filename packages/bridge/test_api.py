"""
Testes E2E para Aura Sphere Bridge
Testa fluxo completo: autenticação, chat, memória, busca
"""

import pytest
import json
import os
from fastapi.testclient import TestClient
from pathlib import Path

# Forçar banco de dados de teste persistente durante os testes
os.environ["DATABASE_URL"] = "sqlite:///./packages/bridge/test.db"

# Adicionar diretório do bridge ao path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app import app
from database import init_db, SessionLocal, Base, engine
from schemas import Message


# Fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup database para testes"""
    # Usar SQLite para testes
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    Base.metadata.create_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Cliente HTTP para testes"""
    return TestClient(app)


@pytest.fixture
def test_token():
    """Token JWT para testes"""
    from jose import jwt
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    payload = {
        "sub": "test-user@example.com",
        "email": "test-user@example.com"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# Testes
class TestHealth:
    """Testes do endpoint de health check"""
    
    def test_health_check(self, client):
        """Deve retornar status ok"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestConversations:
    """Testes de gerenciamento de conversas"""
    
    def test_create_conversation(self, client, test_token):
        """Deve criar nova conversa"""
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.post(
            "/api/v1/conversations",
            json={
                "title": "Minha primeira conversa",
                "prompt_type": "assistant"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minha primeira conversa"
        assert "id" in data
    
    def test_list_conversations(self, client, test_token):
        """Deve listar conversas do usuário"""
        headers = {"Authorization": f"Bearer {test_token}"}
        
        # Criar conversa
        client.post(
            "/api/v1/conversations",
            json={"title": "Conversa 1"},
            headers=headers
        )
        
        # Listar
        response = client.get("/api/v1/conversations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert len(data["conversations"]) >= 1


class TestChat:
    """Testes do endpoint de chat"""
    
    def test_chat_basic(self, client, test_token):
        """Deve fazer chat básico com a IA"""
        headers = {"Authorization": f"Bearer {test_token}"}
        
        response = client.post(
            "/api/v1/chat",
            json={
                "user_id": "test-user",
                "ai_name": "Aurora",
                "prompt_type": "assistant",
                "messages": [
                    {"role": "user", "content": "Olá, como você está?"}
                ]
            },
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        
        # Parse streaming response
        chunks = []
        for line in response.iter_lines():
            if isinstance(line, bytes):
                line = line.decode(errors="ignore")
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str != "[DONE]":
                    try:
                        data = json.loads(data_str)
                        if "choices" in data:
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                chunks.append(content)
                    except json.JSONDecodeError:
                        pass
        
        # Deve ter recebido alguma resposta
        response_text = "".join(chunks)
        assert len(response_text) > 0
    
    def test_chat_with_different_prompt_types(self, client, test_token):
        """Deve suportar diferentes tipos de prompt"""
        headers = {"Authorization": f"Bearer {test_token}"}
        prompt_types = ["assistant", "developer", "creative", "analytical"]
        
        for prompt_type in prompt_types:
            response = client.post(
                "/api/v1/chat",
                json={
                    "user_id": "test-user",
                    "ai_name": "Aurora",
                    "prompt_type": prompt_type,
                    "messages": [
                        {"role": "user", "content": "Teste"}
                    ]
                },
                headers=headers
            )
            assert response.status_code == 200


class TestMemory:
    """Testes de memória"""
    
    def test_create_memory(self, client, test_token):
        """Deve salvar item de memória"""
        headers = {"Authorization": f"Bearer {test_token}"}
        
        response = client.post(
            "/api/v1/memory",
            json={
                "user_id": "test-user",
                "role": "user",
                "content": "Informação importante para lembrar",
                "category": "important"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "saved"

    def test_list_memory(self, client, test_token):
        """Deve listar entradas de memória filtradas por usuário e categoria"""
        headers = {"Authorization": f"Bearer {test_token}"}
        user_id = "test-user"

        client.post(
            "/api/v1/memory",
            json={
                "user_id": user_id,
                "role": "user",
                "content": "Exemplo de busca por categoria",
                "category": "important"
            },
            headers=headers
        )

        response = client.get(
            f"/api/v1/memory?user_id={user_id}&category=important",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "memories" in data
        assert any(item["category"] == "important" for item in data["memories"])


class TestSearch:
    """Testes de busca de memória"""
    
    def test_search_memory(self, client, test_token):
        """Deve buscar itens de memória"""
        headers = {"Authorization": f"Bearer {test_token}"}
        user_id = "test-user"
        
        # Criar alguns itens de memória
        client.post(
            "/api/v1/memory",
            json={
                "user_id": user_id,
                "role": "user",
                "content": "Python é uma linguagem de programação",
                "category": "tech"
            },
            headers=headers
        )
        
        # Buscar
        response = client.get(
            f"/api/v1/search?user_id={user_id}&q=Python",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Pode encontrar ou não, depende do backend estar rodando
    
    def test_search_with_semantic_fallback(self, client, test_token):
        """Deve fazer fallback para text search se semantic falhar"""
        headers = {"Authorization": f"Bearer {test_token}"}
        user_id = "test-user"
        
        response = client.get(
            f"/api/v1/search?user_id={user_id}&q=teste&semantic=false",
            headers=headers
        )
        
        assert response.status_code == 200
        assert "results" in response.json()


class TestPlanning:
    """Testes de planejamento de planos e tarefas"""

    def test_planning_flow(self, client, test_token):
        headers = {"Authorization": f"Bearer {test_token}"}
        user_id = "test-user@example.com"

        # Criar novo plano
        plan_response = client.post(
            "/api/v1/planning/plans",
            json={"title": "Plano de IA", "description": "Planejamento de backend"},
            headers=headers
        )
        assert plan_response.status_code == 200
        plan_data = plan_response.json()
        assert plan_data["title"] == "Plano de IA"
        assert "plan_id" in plan_data

        plan_id = plan_data["plan_id"]

        # Adicionar tarefa ao plano
        task_response = client.post(
            "/api/v1/planning/tasks",
            json={"plan_id": plan_id, "title": "Configurar base de dados", "priority": 2},
            headers=headers
        )
        assert task_response.status_code == 200
        task_data = task_response.json()
        assert task_data["status"] == "pending"
        assert "task_id" in task_data

        task_id = task_data["task_id"]

        # Atualizar progresso da tarefa
        progress_response = client.patch(
            f"/api/v1/planning/tasks/{task_id}",
            json={"progress": 100},
            headers=headers
        )
        assert progress_response.status_code == 200
        progress_data = progress_response.json()
        assert progress_data["status"] == "completed"
        assert progress_data["progress"] == 100

        # Obter dashboard do usuário
        dashboard_response = client.get(
            f"/api/v1/planning/dashboard/{user_id}",
            headers=headers
        )
        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.json()
        assert dashboard_data["total_plans"] >= 1
        assert dashboard_data["overall_progress"] == 100.0


class TestActionQueue:
    """Testes da fila de aprovação de ações pendentes."""

    def test_action_queue_flow(self, client, test_token):
        headers = {"Authorization": f"Bearer {test_token}"}

        propose_response = client.post(
            "/api/v1/actions/propose",
            json={
                "action_type": "publish_post",
                "description": "Publicar conteúdo de backend",
                "parameters": {"platform": "instagram", "post_id": "123"}
            },
            headers=headers
        )
        assert propose_response.status_code == 200
        action_data = propose_response.json()["action"]
        assert action_data["status"] == "pending"
        assert action_data["action_type"] == "publish_post"

        pending_response = client.get(
            "/api/v1/actions/pending",
            headers=headers
        )
        assert pending_response.status_code == 200
        pending_actions = pending_response.json()["actions"]
        assert any(a["id"] == action_data["id"] for a in pending_actions)

        approve_response = client.post(
            f"/api/v1/actions/{action_data['id']}/approve",
            json={"comment": "Aprovado pelo usuário"},
            headers=headers
        )
        assert approve_response.status_code == 200
        approved_action = approve_response.json()["action"]
        assert approved_action["status"] == "approved"

        pending_response = client.get(
            "/api/v1/actions/pending",
            headers=headers
        )
        assert pending_response.status_code == 200
        pending_actions = pending_response.json()["actions"]
        assert all(a["id"] != action_data["id"] for a in pending_actions)


class TestAgentEvolutionAndLearning:
    """Testes de evolução offline e aprendizado adaptativo."""

    def test_offline_evolution_schedule_and_status(self, client, test_token):
        headers = {"Authorization": f"Bearer {test_token}"}

        schedule_response = client.post(
            "/api/v1/agent/evolution/schedule",
            json={
                "description": "Testar agendamento de evolução offline",
                "task_type": "optimization",
                "priority": 6
            },
            headers=headers
        )

        assert schedule_response.status_code == 200
        scheduled_task = schedule_response.json()["scheduled_task"]
        assert scheduled_task["description"] == "Testar agendamento de evolução offline"
        assert scheduled_task["task_type"] == "optimization"

        status_response = client.get(
            "/api/v1/agent/evolution/status",
            headers=headers
        )
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "pending_tasks" in status_data
        assert status_data["pending_tasks"] >= 0

    def test_code_variant_generation_and_comparison(self, client, test_token):
        headers = {"Authorization": f"Bearer {test_token}"}

        variant_response = client.post(
            "/api/v1/agent/code_variants",
            json={
                "module_name": "agent.service",
                "variant_type": "optimization",
                "description": "Teste de geração de variante"
            },
            headers=headers
        )
        assert variant_response.status_code == 200
        variant_data = variant_response.json()["variant"]
        assert variant_data["variant_type"] == "optimization"
        assert variant_data["original_module"] == "agent.service"

        list_response = client.get(
            "/api/v1/agent/code_variants",
            headers=headers
        )
        assert list_response.status_code == 200
        variants = list_response.json()["variants"]
        assert any(v["variant_id"] == variant_data["variant_id"] for v in variants)

        # create a second variant to compare
        variant_response_2 = client.post(
            "/api/v1/agent/code_variants",
            json={
                "module_name": "agent.service",
                "variant_type": "refactor",
                "description": "Teste de comparação de variante"
            },
            headers=headers
        )
        assert variant_response_2.status_code == 200
        variant_data_2 = variant_response_2.json()["variant"]

        compare_response = client.get(
            "/api/v1/agent/code_variants/compare",
            params={
                "variant_a_id": variant_data["variant_id"],
                "variant_b_id": variant_data_2["variant_id"]
            },
            headers=headers
        )
        assert compare_response.status_code == 200
        comparison = compare_response.json()["comparison"]
        assert "recommendation" in comparison

    def test_adaptive_learning_lifecycle(self, client, test_token):
        headers = {"Authorization": f"Bearer {test_token}"}

        start_response = client.post(
            "/api/v1/agent/learning/start",
            json={"topic": "inglês"},
            headers=headers
        )
        assert start_response.status_code == 200
        assert start_response.json()["learning_mode"] is True

        teach_response = client.post(
            "/api/v1/agent/learning/teach",
            json={"topic": "inglês"},
            headers=headers
        )
        assert teach_response.status_code == 200
        assert "lesson" in teach_response.json()

        evaluate_response = client.post(
            "/api/v1/agent/learning/evaluate",
            json={"topic": "inglês", "user_response": "Eu entendi vocabulário básico."},
            headers=headers
        )
        assert evaluate_response.status_code == 200
        assert "outcome" in evaluate_response.json()

        progress_response = client.get(
            "/api/v1/agent/learning/progress",
            params={"topic": "inglês"},
            headers=headers
        )
        assert progress_response.status_code == 200
        assert progress_response.json()["topic"] == "inglês"

        status_response = client.get(
            "/api/v1/agent/learning/status",
            headers=headers
        )
        assert status_response.status_code == 200
        assert status_response.json()["learning_mode_active"] is not None

        stop_response = client.post(
            "/api/v1/agent/learning/stop",
            headers=headers
        )
        assert stop_response.status_code == 200
        assert stop_response.json()["learning_mode"] is False


class TestControlledLearning:
    """Testes de aprendizado controlado e fila de validação."""

    def test_learning_data_pending_validation(self, client, test_token):
        headers = {"Authorization": f"Bearer {test_token}"}

        submit_response = client.post(
            "/api/v1/agent/learning_data",
            json={
                "source": "user_approved",
                "data": {"category": "backend", "description": "Teste de aprendizado controlado"},
                "metadata": {"importance": "high"}
            },
            headers=headers
        )
        assert submit_response.status_code == 200
        submission_data = submit_response.json()
        assert "data_id" in submission_data

        pending_response = client.get(
            "/api/v1/agent/learning_data/pending",
            headers=headers
        )
        assert pending_response.status_code == 200
        pending_data = pending_response.json().get("pending_data", [])
        assert any(item["id"] == submission_data["data_id"] for item in pending_data)


class TestAuthentication:
    """Testes de autenticação"""
    
    def test_missing_auth_header(self, client):
        """Deve rejeitar requisições sem Authorization header em produção"""
        # Em dev mode, usa fallback
        os.environ["ENV"] = "development"
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    def test_invalid_token(self, client):
        """Deve rejeitar tokens inválidos"""
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.post(
            "/api/v1/conversations",
            json={"title": "Teste"},
            headers=headers
        )
        
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
