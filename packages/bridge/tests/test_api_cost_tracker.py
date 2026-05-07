"""
Testes unitários para ApiCostTracker
"""

import pytest
from datetime import datetime, timedelta
from agent.api_cost_tracker import ApiCostTracker, ApiUsageRecord


class TestApiCostTracker:
    """Testes para o ApiCostTracker"""

    def setup_method(self):
        """Setup para cada teste"""
        self.tracker = ApiCostTracker()

    def test_log_usage_basic(self):
        """Testa registro básico de uso de API"""
        record_id = self.tracker.log_usage(
            user_id="user123",
            provider="openai",
            endpoint="chat",
            cost_usd=0.015,
            model="gpt-4",
            tokens_used=150
        )

        assert record_id.startswith("cost-")
        assert len(self.tracker.records) == 1

        record = self.tracker.records[0]
        assert record.user_id == "user123"
        assert record.provider == "openai"
        assert record.endpoint == "chat"
        assert record.cost_usd == 0.015
        assert record.model == "gpt-4"
        assert record.tokens_used == 150

    def test_calculate_cost_openai_gpt4(self):
        """Testa cálculo de custo para OpenAI GPT-4"""
        cost = self.tracker.calculate_cost(
            provider="openai",
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50
        )

        # GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens
        expected = (100 * 0.03 / 1000) + (50 * 0.06 / 1000)
        assert cost == expected

    def test_calculate_cost_openai_gpt35(self):
        """Testa cálculo de custo para OpenAI GPT-3.5-turbo"""
        cost = self.tracker.calculate_cost(
            provider="openai",
            model="gpt-3.5-turbo",
            prompt_tokens=1000,
            completion_tokens=500
        )

        # GPT-3.5-turbo: $0.0005/1K prompt, $0.0015/1K completion
        expected = (1000 * 0.0005 / 1000) + (500 * 0.0015 / 1000)
        assert cost == expected

    def test_calculate_cost_anthropic_claude(self):
        """Testa cálculo de custo para Anthropic Claude"""
        cost = self.tracker.calculate_cost(
            provider="anthropic",
            model="claude-3-opus",
            prompt_tokens=1000,
            completion_tokens=2000
        )

        # Claude-3-opus: $0.015/1K prompt, $0.075/1K completion
        expected = round((1000 * 0.015 / 1000) + (2000 * 0.075 / 1000), 6)
        assert cost == expected

    def test_calculate_cost_unknown_provider(self):
        """Testa cálculo de custo para provider desconhecido"""
        cost = self.tracker.calculate_cost(
            provider="unknown_provider",
            model="unknown_model",
            prompt_tokens=100,
            completion_tokens=50
        )

        assert cost == 0.0

    def test_calculate_cost_unknown_model(self):
        """Testa cálculo de custo para modelo desconhecido (usa fallback)"""
        cost = self.tracker.calculate_cost(
            provider="openai",
            model="unknown_model",
            prompt_tokens=100,
            completion_tokens=50
        )

        # Deve usar GPT-4 como fallback (primeiro modelo)
        expected = (100 * 0.03 / 1000) + (50 * 0.06 / 1000)
        assert cost == expected

    def test_get_summary_empty(self):
        """Testa resumo quando não há registros"""
        summary = self.tracker.get_summary("user123", days=30)

        assert summary["total_cost_usd"] == 0.0
        assert summary["record_count"] == 0
        assert summary["average_daily_cost"] == 0.0
        assert summary["estimated_monthly_cost"] == 0.0
        assert summary["exceeded_threshold"] == False
        assert summary["period_days"] == 30

    def test_get_summary_with_records(self):
        """Testa resumo com registros existentes"""
        # Adicionar alguns registros
        self.tracker.log_usage("user123", "openai", "chat", 0.015, "gpt-4", 150)
        self.tracker.log_usage("user123", "openai", "embeddings", 0.005, "text-embedding-ada-002", 100)
        self.tracker.log_usage("user123", "anthropic", "chat", 0.025, "claude-3-opus", 200)

        summary = self.tracker.get_summary("user123", days=30)

        assert summary["total_cost_usd"] == 0.045
        assert summary["record_count"] == 3
        assert summary["by_provider"]["openai"] == 0.02
        assert summary["by_provider"]["anthropic"] == 0.025
        assert summary["by_endpoint"]["openai/chat"] == 0.015
        assert summary["by_endpoint"]["openai/embeddings"] == 0.005
        assert summary["by_endpoint"]["anthropic/chat"] == 0.025

    def test_get_summary_different_users(self):
        """Testa que resumos são separados por usuário"""
        self.tracker.log_usage("user123", "openai", "chat", 0.015)
        self.tracker.log_usage("user456", "openai", "chat", 0.020)

        summary123 = self.tracker.get_summary("user123")
        summary456 = self.tracker.get_summary("user456")

        assert summary123["total_cost_usd"] == 0.015
        assert summary456["total_cost_usd"] == 0.020

    def test_get_free_alternatives_openai_chat(self):
        """Testa alternativas gratuitas para OpenAI chat"""
        alternatives = self.tracker.get_free_alternatives("openai", "chat")

        assert len(alternatives) > 0
        assert any("Ollama" in alt["name"] for alt in alternatives)
        assert any("Hugging Face" in alt["name"] for alt in alternatives)

        for alt in alternatives:
            assert "name" in alt
            assert "description" in alt
            assert "cost" in alt

    def test_get_free_alternatives_openai_embeddings(self):
        """Testa alternativas gratuitas para OpenAI embeddings"""
        alternatives = self.tracker.get_free_alternatives("openai", "embeddings")

        assert len(alternatives) > 0
        assert any("Sentence Transformers" in alt["name"] for alt in alternatives)

    def test_get_free_alternatives_unknown(self):
        """Testa alternativas para endpoint desconhecido (retorna genérico)"""
        alternatives = self.tracker.get_free_alternatives("unknown", "unknown")

        assert len(alternatives) > 0
        assert any("Local inference" in alt["name"] for alt in alternatives)

    def test_get_usage_trends_empty(self):
        """Testa tendências quando não há dados"""
        trends = self.tracker.get_usage_trends("user123", days=30)

        assert trends["daily_breakdown"] == {}
        assert trends["dates"] == []
        assert trends["costs"] == []
        assert trends["peak_day"] == 0
        assert trends["trend"] == "insufficient_data"

    def test_get_usage_trends_with_data(self):
        """Testa cálculo de tendências com dados"""
        # Criar registros em dias diferentes (simulando)
        base_time = datetime.now()

        # Dia 1: 2 registros
        record1 = ApiUsageRecord(
            id="test1", user_id="user123", provider="openai", endpoint="chat",
            cost_usd=0.01, timestamp=base_time - timedelta(days=2)
        )
        record2 = ApiUsageRecord(
            id="test2", user_id="user123", provider="openai", endpoint="chat",
            cost_usd=0.02, timestamp=base_time - timedelta(days=2)
        )

        # Dia 2: 1 registro
        record3 = ApiUsageRecord(
            id="test3", user_id="user123", provider="openai", endpoint="chat",
            cost_usd=0.015, timestamp=base_time - timedelta(days=1)
        )

        self.tracker.records = [record1, record2, record3]

        trends = self.tracker.get_usage_trends("user123", days=30)

        assert len(trends["dates"]) == 2
        assert trends["peak_day"] == 0.03  # Dia 1 teve $0.03 total
        assert trends["trend"] == "decreasing"  # Dia 2 teve menos que dia 1

    def test_calculate_trend_increasing(self):
        """Testa cálculo de tendência crescente"""
        values = [0.01, 0.02, 0.03, 0.05, 0.08]  # Crescendo
        trend = self.tracker._calculate_trend(values)
        assert trend == "increasing"

    def test_calculate_trend_decreasing(self):
        """Testa cálculo de tendência decrescente"""
        values = [0.08, 0.05, 0.03, 0.02, 0.01]  # Decrescendo
        trend = self.tracker._calculate_trend(values)
        assert trend == "decreasing"

    def test_calculate_trend_stable(self):
        """Testa cálculo de tendência estável"""
        values = [0.02, 0.025, 0.022, 0.024, 0.021]  # Estável
        trend = self.tracker._calculate_trend(values)
        assert trend == "stable"

    def test_calculate_trend_insufficient_data(self):
        """Testa tendência com dados insuficientes"""
        trend = self.tracker._calculate_trend([0.01])
        assert trend == "insufficient_data"

        trend = self.tracker._calculate_trend([])
        assert trend == "insufficient_data"

    def test_cost_alert_generation(self):
        """Testa geração de alertas de custo"""
        # Configurar threshold baixo para teste
        self.tracker.cost_threshold_usd = 0.01

        # Primeiro uso - abaixo do threshold
        self.tracker.log_usage("user123", "openai", "chat", 0.005)
        assert len(self.tracker.alerts) == 0

        # Segundo uso - ultrapassa threshold
        self.tracker.log_usage("user123", "openai", "chat", 0.008)
        assert len(self.tracker.alerts) == 1

        alert = self.tracker.alerts[0]
        assert alert["user_id"] == "user123"
        assert alert["current_daily_cost"] > 0.01
        assert alert["threshold"] == 0.01
        assert "exceeded threshold" in alert["message"]

    def test_export_records(self):
        """Testa exportação de registros"""
        self.tracker.log_usage("user123", "openai", "chat", 0.015, "gpt-4", 150)

        exported = self.tracker.export_records("user123", days=30)

        assert len(exported) == 1
        record = exported[0]
        assert record["user_id"] == "user123"
        assert record["provider"] == "openai"
        assert record["cost_usd"] == 0.015
        assert "timestamp" in record
        assert "id" in record

    def test_export_records_filtered_by_user(self):
        """Testa que export filtra por usuário"""
        self.tracker.log_usage("user123", "openai", "chat", 0.015)
        self.tracker.log_usage("user456", "openai", "chat", 0.020)

        exported123 = self.tracker.export_records("user123")
        exported456 = self.tracker.export_records("user456")

        assert len(exported123) == 1
        assert len(exported456) == 1
        assert exported123[0]["cost_usd"] == 0.015
        assert exported456[0]["cost_usd"] == 0.020

    def test_export_records_filtered_by_date(self):
        """Testa que export filtra por período"""
        old_date = datetime.now() - timedelta(days=60)

        # Registro recente
        self.tracker.log_usage("user123", "openai", "chat", 0.015)

        # Registro antigo (adicionado manualmente)
        old_record = ApiUsageRecord(
            id="old", user_id="user123", provider="openai", endpoint="chat",
            cost_usd=0.010, timestamp=old_date
        )
        self.tracker.records.append(old_record)

        # Exportar últimos 30 dias
        exported = self.tracker.export_records("user123", days=30)

        assert len(exported) == 1  # Apenas o registro recente
        assert exported[0]["cost_usd"] == 0.015

    def test_unique_record_ids(self):
        """Testa que IDs de registros são únicos"""
        id1 = self.tracker.log_usage("user123", "openai", "chat", 0.015)
        id2 = self.tracker.log_usage("user123", "openai", "chat", 0.020)

        assert id1 != id2
        assert id1.startswith("cost-")
        assert id2.startswith("cost-")

    def test_metadata_storage(self):
        """Testa armazenamento de metadados"""
        metadata = {"request_id": "req-123", "region": "us-east-1"}
        self.tracker.log_usage(
            user_id="user123",
            provider="openai",
            endpoint="chat",
            cost_usd=0.015,
            metadata=metadata
        )

        record = self.tracker.records[0]
        assert record.metadata == metadata

    def test_response_time_tracking(self):
        """Testa rastreamento de tempo de resposta"""
        self.tracker.log_usage(
            user_id="user123",
            provider="openai",
            endpoint="chat",
            cost_usd=0.015,
            response_time_ms=1250.5
        )

        record = self.tracker.records[0]
        assert record.response_time_ms == 1250.5