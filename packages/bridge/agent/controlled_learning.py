"""
Controlled Learning System - Aprendizado validado com dados confiáveis

Este módulo implementa um sistema de aprendizado que APENAS aprende
de dados que foram validados e aprovados pelo usuário.
"""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import hashlib


class ValidationStatus(Enum):
    """Status de validação de dados."""
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class DataSource(Enum):
    """Fonte de dados."""
    USER_APPROVED = "user_approved"
    SYSTEM_LOGS = "system_logs"
    EXECUTION_RESULTS = "execution_results"
    DEPLOYMENT_HISTORY = "deployment_history"
    ANOMALY_DETECTION = "anomaly_detection"


class ControlledLearner:
    """
    Sistema de aprendizado controlado.
    
    Princípios:
    - NUNCA aprende de dados não-validados
    - Prioriza dados aprovados pelo usuário
    - Rastreia origem de todo dado de aprendizado
    - Pode desaprender se dado depois é rejeitado
    - Separa conhecimento confiável de especulação
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.learn_dir = data_dir / "learning"
        self.learn_dir.mkdir(parents=True, exist_ok=True)
        
        self.validated_data_log = self.learn_dir / "validated_data.json"
        self.learning_model_log = self.learn_dir / "learning_model.json"
        self.data_lineage_log = self.learn_dir / "data_lineage.json"
        
        self.validated_data: List[Dict] = []
        self.learning_model: Dict[str, Any] = {}
        self.data_lineage: List[Dict] = []
        
        self._load_state()

    def submit_data_for_validation(self, source: DataSource,
                                   data: Dict[str, Any],
                                   metadata: Optional[Dict] = None) -> str:
        """
        Submete dados para validação.
        Dados não-validados NOT são usados para aprendizado.
        """
        
        data_id = hashlib.md5(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()[:12]
        
        submission = {
            "id": data_id,
            "timestamp": datetime.now().isoformat(),
            "source": source.value,
            "data": data,
            "metadata": metadata or {},
            "status": ValidationStatus.PENDING.value,
            "validation_timestamp": None,
            "validator_user_id": None
        }
        
        self.validated_data.append(submission)
        
        # Registrar na linhagem
        self.data_lineage.append({
            "data_id": data_id,
            "action": "submitted",
            "timestamp": datetime.now().isoformat(),
            "source": source.value
        })
        
        self._save_state()
        
        return data_id

    def validate_data(self, data_id: str, user_id: str,
                     approved: bool, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Valida (aprova/rejeita) dados para aprendizado.
        Apenas usuário pode validar.
        """
        
        validation_result = {
            "data_id": data_id,
            "approved": approved,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "reason": reason
        }
        
        # Encontrar submissão
        for submission in self.validated_data:
            if submission["id"] == data_id:
                submission["status"] = (
                    ValidationStatus.VALIDATED.value if approved
                    else ValidationStatus.REJECTED.value
                )
                submission["validation_timestamp"] = datetime.now().isoformat()
                submission["validator_user_id"] = user_id
                
                # Registrar na linhagem
                self.data_lineage.append({
                    "data_id": data_id,
                    "action": "validated" if approved else "rejected",
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                })
                
                # Se aprovado, aprender
                if approved:
                    self._learn_from_data(submission)
                
                break
        
        self._save_state()
        return validation_result

    def _learn_from_data(self, validated_submission: Dict[str, Any]) -> None:
        """
        Aprende de dados validados.
        Este é o ÚNICO caminho para o sistema aprender.
        """
        
        data = validated_submission["data"]
        source = validated_submission["source"]
        
        # Atualizar modelo de aprendizado
        category = data.get("category", "general")
        
        if category not in self.learning_model:
            self.learning_model[category] = {
                "examples": [],
                "patterns": [],
                "confidence": 0.0,
                "source_distribution": {}
            }
        
        # Adicionar exemplo
        self.learning_model[category]["examples"].append({
            "data_id": validated_submission["id"],
            "data": data,
            "learned_at": datetime.now().isoformat()
        })
        
        # Atualizar distribuição de fonte
        if source not in self.learning_model[category]["source_distribution"]:
            self.learning_model[category]["source_distribution"][source] = 0
        self.learning_model[category]["source_distribution"][source] += 1
        
        # Registrar aprendizado na linhagem
        self.data_lineage.append({
            "data_id": validated_submission["id"],
            "action": "learned_from",
            "timestamp": datetime.now().isoformat(),
            "category": category
        })

    def unlearn_data(self, data_id: str, reason: str) -> Dict[str, Any]:
        """
        Remove conhecimento aprendido de dados depois rejeitados.
        Mantém rastreabilidade completa.
        """
        
        unlearn_result = {
            "data_id": data_id,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "reason": reason
        }
        
        # Encontrar e remover de exemplos
        for category in self.learning_model.values():
            category["examples"] = [
                ex for ex in category["examples"]
                if ex["data_id"] != data_id
            ]
        
        # Registrar na linhagem
        self.data_lineage.append({
            "data_id": data_id,
            "action": "unlearned",
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        })
        
        unlearn_result["success"] = True
        self._save_state()
        return unlearn_result

    def get_learned_knowledge(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna conhecimento aprendido.
        APENAS conhecimento de dados validados.
        """
        
        if category:
            return self.learning_model.get(category, {})
        
        return self.learning_model

    def get_knowledge_confidence(self, category: str) -> float:
        """
        Retorna nível de confiança do conhecimento.
        Baseado em quantidade de exemplos validados.
        """
        
        if category not in self.learning_model:
            return 0.0
        
        examples = len(self.learning_model[category]["examples"])
        
        # Confiança cresce com quantidade de exemplos
        # Máximo em 50 exemplos
        confidence = min(1.0, examples / 50.0)
        
        return confidence

    def get_data_lineage(self, data_id: str) -> List[Dict]:
        """
        Retorna história completa de um dado.
        Rastreamento total: submissão → validação → aprendizado.
        """
        
        return [
            event for event in self.data_lineage
            if event.get("data_id") == data_id
        ]

    def get_pending_validations(self) -> List[Dict]:
        """
        Retorna dados aguardando validação do usuário.
        """
        
        return [
            data for data in self.validated_data
            if data["status"] == ValidationStatus.PENDING.value
        ]

    def export_learning_report(self) -> Dict[str, Any]:
        """
        Exporta relatório completo de aprendizado.
        """
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_data_submitted": len(self.validated_data),
            "total_validated": len([
                d for d in self.validated_data
                if d["status"] == ValidationStatus.VALIDATED.value
            ]),
            "total_rejected": len([
                d for d in self.validated_data
                if d["status"] == ValidationStatus.REJECTED.value
            ]),
            "learning_model_categories": len(self.learning_model),
            "data_by_source": {},
            "categories_learned": {}
        }
        
        # Análise por fonte
        for data in self.validated_data:
            source = data["source"]
            if source not in report["data_by_source"]:
                report["data_by_source"][source] = {"total": 0, "validated": 0}
            
            report["data_by_source"][source]["total"] += 1
            if data["status"] == ValidationStatus.VALIDATED.value:
                report["data_by_source"][source]["validated"] += 1
        
        # Análise por categoria
        for category, knowledge in self.learning_model.items():
            report["categories_learned"][category] = {
                "examples_count": len(knowledge["examples"]),
                "confidence": self.get_knowledge_confidence(category),
                "sources": knowledge["source_distribution"]
            }
        
        return report

    def _load_state(self) -> None:
        """Carrega estado do aprendizado."""
        
        if self.validated_data_log.exists():
            try:
                self.validated_data = json.loads(
                    self.validated_data_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.validated_data = []
        
        if self.learning_model_log.exists():
            try:
                self.learning_model = json.loads(
                    self.learning_model_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.learning_model = {}
        
        if self.data_lineage_log.exists():
            try:
                self.data_lineage = json.loads(
                    self.data_lineage_log.read_text(encoding='utf-8')
                )
            except Exception:
                self.data_lineage = []

    def _save_state(self) -> None:
        """Persiste estado do aprendizado."""
        
        self.learn_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar dados validados submetidos
        self.validated_data_log.write_text(
            json.dumps(self.validated_data[-1000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        # Salvar modelo de aprendizado
        self.learning_model_log.write_text(
            json.dumps(self.learning_model, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        # Salvar linhagem de dados
        self.data_lineage_log.write_text(
            json.dumps(self.data_lineage[-5000:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
