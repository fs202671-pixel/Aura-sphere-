"""
API Cost Tracker - Monitora custos de APIs externas
"""

from typing import Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import hashlib
import uuid


@dataclass
class ApiUsageRecord:
    """Representa um uso de API registrado"""
    id: str
    user_id: str
    provider: str  # "openai", "anthropic", "google", etc.
    endpoint: str
    cost_usd: float
    timestamp: datetime
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time_ms: Optional[float] = None
    metadata: dict[str, Any] = None
    
    def to_dict(self):
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class ApiCostTracker:
    """Serviço de rastreamento de custos de API"""
    
    # Custos padrão por provider (valores fictícios para demo)
    PROVIDER_COSTS = {
        "openai": {
            "gpt-4": {"prompt_tokens": 0.03 / 1000, "completion_tokens": 0.06 / 1000},
            "gpt-3.5-turbo": {"prompt_tokens": 0.0005 / 1000, "completion_tokens": 0.0015 / 1000},
        },
        "anthropic": {
            "claude-3-opus": {"prompt_tokens": 0.015 / 1000, "completion_tokens": 0.075 / 1000},
            "claude-3-sonnet": {"prompt_tokens": 0.003 / 1000, "completion_tokens": 0.015 / 1000},
        },
        "google": {
            "palm-2": {"prompt_tokens": 0.0005 / 1000, "completion_tokens": 0.0005 / 1000},
        },
        "huggingface": {
            "inference-api": {"request": 0.01},  # Por requisição
        }
    }
    
    def __init__(self):
        self.records: list[ApiUsageRecord] = []
        self.cost_threshold_usd = 10.0  # Alerta quando ultrapassar
        self.alerts: list[dict[str, Any]] = []
    
    def log_usage(
        self,
        user_id: str,
        provider: str,
        endpoint: str,
        cost_usd: float,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        response_time_ms: Optional[float] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Registra um uso de API"""
        record_id = self._generate_id(user_id, provider, endpoint)
        
        record = ApiUsageRecord(
            id=record_id,
            user_id=user_id,
            provider=provider,
            endpoint=endpoint,
            cost_usd=cost_usd,
            timestamp=datetime.now(),
            model=model,
            tokens_used=tokens_used,
            response_time_ms=response_time_ms,
            metadata=metadata or {}
        )
        
        self.records.append(record)
        
        # Verificar se deve gerar alerta
        total_today = self._calculate_cost_for_period(user_id, days=1)
        if total_today > self.cost_threshold_usd:
            self._create_alert(user_id, total_today)
        
        return record_id
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Calcula custo baseado em tokens"""
        if provider not in self.PROVIDER_COSTS:
            return 0.0
        
        if model not in self.PROVIDER_COSTS[provider]:
            # Usar primeiro modelo disponível como fallback
            model = list(self.PROVIDER_COSTS[provider].keys())[0]
        
        model_costs = self.PROVIDER_COSTS[provider][model]
        
        prompt_cost = (prompt_tokens * model_costs.get("prompt_tokens", 0)) if "prompt_tokens" in model_costs else 0
        completion_cost = (completion_tokens * model_costs.get("completion_tokens", 0)) if "completion_tokens" in model_costs else 0
        
        total_cost = prompt_cost + completion_cost
        return round(total_cost, 6)  # Round to 6 decimal places to avoid floating point issues
    
    def get_summary(self, user_id: str, days: int = 30) -> dict[str, Any]:
        """Retorna um resumo de custos"""
        start_date = datetime.now() - timedelta(days=days)
        
        relevant_records = [
            r for r in self.records
            if r.user_id == user_id and r.timestamp >= start_date
        ]
        
        total_cost = sum(r.cost_usd for r in relevant_records)
        
        cost_by_provider = {}
        for record in relevant_records:
            if record.provider not in cost_by_provider:
                cost_by_provider[record.provider] = 0
            cost_by_provider[record.provider] += record.cost_usd
        
        cost_by_endpoint = {}
        for record in relevant_records:
            key = f"{record.provider}/{record.endpoint}"
            if key not in cost_by_endpoint:
                cost_by_endpoint[key] = 0
            cost_by_endpoint[key] += record.cost_usd
        
        return {
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "by_provider": cost_by_provider,
            "by_endpoint": cost_by_endpoint,
            "record_count": len(relevant_records),
            "average_daily_cost": round(total_cost / max(days, 1), 4),
            "estimated_monthly_cost": round((total_cost / max(days, 1)) * 30, 2),
            "exceeded_threshold": total_cost > self.cost_threshold_usd
        }
    
    def get_free_alternatives(self, provider: str, endpoint: str) -> list[dict[str, str]]:
        """Retorna alternativas gratuitas para um endpoint pago"""
        alternatives = {
            ("openai", "chat"): [
                {"name": "Ollama", "description": "Local LLM running open source models", "cost": "Free (self-hosted)"},
                {"name": "Hugging Face Inference API", "description": "Free tier with rate limits", "cost": "Free tier available"},
                {"name": "LLaMA 2", "description": "Open source model by Meta", "cost": "Free"},
            ],
            ("openai", "embeddings"): [
                {"name": "Sentence Transformers", "description": "Local embedding models", "cost": "Free"},
                {"name": "FastEmbed", "description": "Fast local embeddings", "cost": "Free"},
            ],
            ("google", "translate"): [
                {"name": "LibreTranslate", "description": "Open source translation API", "cost": "Free (self-hosted)"},
                {"name": "MyMemory Translation API", "description": "Free translation service", "cost": "Free"},
            ],
            ("generic", "generic"): [
                {"name": "Local inference", "description": "Run models locally with GPU", "cost": "Free (initial hardware cost)"},
                {"name": "Community models", "description": "Open source alternatives", "cost": "Free"},
            ]
        }
        
        key = (provider, endpoint)
        return alternatives.get(key, alternatives.get(("generic", "generic"), []))
    
    def get_usage_trends(self, user_id: str, days: int = 30) -> dict[str, Any]:
        """Retorna tendências de uso"""
        start_date = datetime.now() - timedelta(days=days)
        
        relevant_records = [
            r for r in self.records
            if r.user_id == user_id and r.timestamp >= start_date
        ]
        
        # Agrupar por dia
        daily_costs = {}
        for record in relevant_records:
            date_key = record.timestamp.strftime("%Y-%m-%d")
            if date_key not in daily_costs:
                daily_costs[date_key] = 0
            daily_costs[date_key] += record.cost_usd
        
        sorted_dates = sorted(daily_costs.keys())
        costs_progression = [daily_costs[date] for date in sorted_dates]
        
        return {
            "daily_breakdown": daily_costs,
            "dates": sorted_dates,
            "costs": costs_progression,
            "peak_day": max(costs_progression) if costs_progression else 0,
            "trend": self._calculate_trend(costs_progression)
        }
    
    def _calculate_trend(self, values: list[float]) -> str:
        """Calcula tendência de custos"""
        if len(values) < 2:
            return "insufficient_data"
        
        first_half_avg = sum(values[:len(values)//2]) / max(len(values)//2, 1)
        second_half_avg = sum(values[len(values)//2:]) / max(len(values) - len(values)//2, 1)
        
        if second_half_avg > first_half_avg * 1.2:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _create_alert(self, user_id: str, current_cost: float):
        """Cria um alerta de custo"""
        alert = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "current_daily_cost": current_cost,
            "threshold": self.cost_threshold_usd,
            "message": f"Daily API costs (${current_cost:.2f}) exceeded threshold (${self.cost_threshold_usd:.2f})!",
            "severity": "high" if current_cost > self.cost_threshold_usd * 2 else "medium"
        }
        
        self.alerts.append(alert)
    
    def _calculate_cost_for_period(self, user_id: str, days: int) -> float:
        """Calcula custo total para um período"""
        start_date = datetime.now() - timedelta(days=days)
        
        relevant_records = [
            r for r in self.records
            if r.user_id == user_id and r.timestamp >= start_date
        ]
        
        return sum(r.cost_usd for r in relevant_records)
    
    def _generate_id(self, user_id: str, provider: str, endpoint: str) -> str:
        """Gera um ID único para o registro"""
        timestamp = str(uuid.uuid4())[0:8]
        return f"cost-{timestamp}-{user_id[:3]}"
    
    def export_records(self, user_id: str, days: int = 30) -> list[dict[str, Any]]:
        """Exporta registros em formato dict"""
        start_date = datetime.now() - timedelta(days=days)
        
        relevant_records = [
            r for r in self.records
            if r.user_id == user_id and r.timestamp >= start_date
        ]
        
        return [r.to_dict() for r in relevant_records]
