"""
Módulo de Aprendizado Híbrido - Sistema de aprendizado multimodal

Este módulo implementa um sistema de aprendizado que combina
múltiplas fontes de conhecimento e técnicas de aprendizado.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
import asyncio
import random
from collections import defaultdict


class LearningSource(Enum):
    """Fontes de aprendizado disponíveis."""
    USER_INTERACTION = "user_interaction"
    SYSTEM_LOGS = "system_logs"
    EXTERNAL_DATA = "external_data"
    CODE_EXECUTION = "code_execution"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE_METRICS = "performance_metrics"
    USER_FEEDBACK = "user_feedback"
    SIMULATION = "simulation"


class LearningTechnique(Enum):
    """Técnicas de aprendizado disponíveis."""
    SUPERVISED = "supervised"          # Aprendizado supervisionado
    UNSUPERVISED = "unsupervised"      # Aprendizado não-supervisionado
    REINFORCEMENT = "reinforcement"    # Aprendizado por reforço
    TRANSFER = "transfer"              # Transfer learning
    FEW_SHOT = "few_shot"              # Few-shot learning
    META_LEARNING = "meta_learning"    # Meta-aprendizado


class KnowledgeUnit:
    """
    Unidade de conhecimento aprendida.
    """

    def __init__(self, content: Any, source: LearningSource,
                 technique: LearningTechnique, confidence: float,
                 metadata: Dict[str, Any] = None):
        self.content = content
        self.source = source
        self.technique = technique
        self.confidence = confidence
        self.metadata = metadata or {}

        # Controle de qualidade
        self.validation_count = 0
        self.successful_applications = 0
        self.last_used = None

        # Identificação
        self.knowledge_id = f"ku_{int(datetime.now().timestamp())}_{hash(str(content)) % 10000}"
        self.created_at = datetime.now().isoformat()

    def apply_knowledge(self) -> None:
        """Registra aplicação do conhecimento."""
        self.last_used = datetime.now().isoformat()
        self.validation_count += 1

    def record_success(self) -> None:
        """Registra aplicação bem-sucedida."""
        self.successful_applications += 1

    def get_effectiveness(self) -> float:
        """Retorna efetividade do conhecimento."""
        if self.validation_count == 0:
            return 0.0
        return self.successful_applications / self.validation_count


class HybridLearner:
    """
    Sistema de aprendizado híbrido multimodal.

    Funcionalidades:
    - Integração de múltiplas fontes de aprendizado
    - Técnicas de aprendizado combinadas
    - Validação cruzada de conhecimento
    - Adaptação baseada em contexto
    - Meta-aprendizado para otimização
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.learning_dir = data_dir / "hybrid_learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        self.knowledge_base_file = self.learning_dir / "knowledge_base.json"
        self.learning_sessions_file = self.learning_dir / "learning_sessions.json"

        self.knowledge_base: Dict[str, KnowledgeUnit] = {}
        self.learning_sessions: List[Dict[str, Any]] = []

        # Configurações
        self.max_knowledge_units = 10000
        self.min_confidence_threshold = 0.6
        self.learning_batch_size = 50

        # Estatísticas de aprendizado
        self.learning_stats = {
            "total_sessions": 0,
            "knowledge_units_learned": 0,
            "avg_confidence": 0.0,
            "technique_effectiveness": defaultdict(float)
        }

        self._load_knowledge_base()

    async def learn_from_sources(self, sources: List[LearningSource],
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Aprende de múltiplas fontes simultaneamente.
        """

        context = context or {}
        session_start = datetime.now()

        learning_results = {
            "session_id": f"session_{int(session_start.timestamp())}",
            "sources_used": [s.value for s in sources],
            "knowledge_learned": 0,
            "techniques_applied": [],
            "validation_results": [],
            "performance_metrics": {}
        }

        # Coletar dados de todas as fontes
        raw_data = {}
        for source in sources:
            try:
                data = await self._collect_source_data(source, context)
                raw_data[source] = data
            except Exception as e:
                print(f"Error collecting data from {source.value}: {e}")

        # Aplicar técnicas de aprendizado híbridas
        for technique in LearningTechnique:
            try:
                technique_results = await self._apply_learning_technique(
                    technique, raw_data, context
                )

                if technique_results["knowledge_units"] > 0:
                    learning_results["techniques_applied"].append(technique.value)
                    learning_results["knowledge_learned"] += technique_results["knowledge_units"]

                    # Registrar efetividade da técnica
                    effectiveness = technique_results.get("effectiveness", 0.5)
                    self.learning_stats["technique_effectiveness"][technique.value] = (
                        (self.learning_stats["technique_effectiveness"][technique.value] *
                         self.learning_stats["total_sessions"]) + effectiveness
                    ) / (self.learning_stats["total_sessions"] + 1)

            except Exception as e:
                print(f"Error applying {technique.value}: {e}")

        # Validação cruzada do conhecimento aprendido
        validation_results = await self._cross_validate_knowledge()
        learning_results["validation_results"] = validation_results

        # Otimizar conhecimento baseado em validação
        await self._optimize_knowledge_base()

        # Registrar sessão de aprendizado
        session_duration = (datetime.now() - session_start).total_seconds()
        session_record = {
            "session_id": learning_results["session_id"],
            "start_time": session_start.isoformat(),
            "duration_seconds": session_duration,
            "results": learning_results
        }
        self.learning_sessions.append(session_record)

        # Atualizar estatísticas globais
        self.learning_stats["total_sessions"] += 1
        self.learning_stats["knowledge_units_learned"] += learning_results["knowledge_learned"]

        # Recalcular confiança média
        if self.knowledge_base:
            confidences = [ku.confidence for ku in self.knowledge_base.values()]
            self.learning_stats["avg_confidence"] = sum(confidences) / len(confidences)

        self._save_knowledge_base()
        return learning_results

    async def _collect_source_data(self, source: LearningSource,
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coleta dados de uma fonte específica.
        """

        # Implementação simulada - em produção se conectaria às fontes reais
        if source == LearningSource.USER_INTERACTION:
            return {
                "interactions": [
                    {"type": "command", "content": "create file", "outcome": "success"},
                    {"type": "feedback", "content": "good response", "rating": 0.8}
                ]
            }

        elif source == LearningSource.SYSTEM_LOGS:
            return {
                "logs": [
                    {"level": "info", "message": "Task completed successfully"},
                    {"level": "error", "message": "Connection timeout"}
                ]
            }

        elif source == LearningSource.CODE_EXECUTION:
            return {
                "executions": [
                    {"code": "print('hello')", "result": "success", "performance": 0.95},
                    {"code": "invalid syntax", "result": "error", "error_type": "syntax"}
                ]
            }

        elif source == LearningSource.ERROR_ANALYSIS:
            return {
                "errors": [
                    {"type": "ValueError", "frequency": 10, "context": "user input validation"},
                    {"type": "TimeoutError", "frequency": 5, "context": "network operations"}
                ]
            }

        elif source == LearningSource.PERFORMANCE_METRICS:
            return {
                "metrics": {
                    "response_time_avg": 0.234,
                    "cpu_usage_avg": 0.45,
                    "memory_usage_avg": 0.67,
                    "error_rate": 0.02
                }
            }

        elif source == LearningSource.USER_FEEDBACK:
            return {
                "feedback": [
                    {"rating": 0.9, "comments": "Very helpful"},
                    {"rating": 0.6, "comments": "Could be more detailed"}
                ]
            }

        return {}

    async def _apply_learning_technique(self, technique: LearningTechnique,
                                      raw_data: Dict[LearningSource, Dict],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica uma técnica de aprendizado específica.
        """

        results = {
            "knowledge_units": 0,
            "effectiveness": 0.5,
            "learned_patterns": []
        }

        if technique == LearningTechnique.SUPERVISED:
            results = await self._apply_supervised_learning(raw_data)

        elif technique == LearningTechnique.UNSUPERVISED:
            results = await self._apply_unsupervised_learning(raw_data)

        elif technique == LearningTechnique.REINFORCEMENT:
            results = await self._apply_reinforcement_learning(raw_data)

        elif technique == LearningTechnique.TRANSFER:
            results = await self._apply_transfer_learning(raw_data)

        elif technique == LearningTechnique.FEW_SHOT:
            results = await self._apply_few_shot_learning(raw_data)

        elif technique == LearningTechnique.META_LEARNING:
            results = await self._apply_meta_learning(raw_data)

        return results

    async def _apply_supervised_learning(self, raw_data: Dict[LearningSource, Dict]) -> Dict[str, Any]:
        """Aplica aprendizado supervisionado."""
        # Implementação simplificada
        knowledge_units = 0

        # Aprender de interações do usuário
        if LearningSource.USER_INTERACTION in raw_data:
            interactions = raw_data[LearningSource.USER_INTERACTION].get("interactions", [])
            for interaction in interactions:
                if interaction.get("outcome") == "success":
                    # Criar unidade de conhecimento
                    content = f"Successful pattern: {interaction['content']}"
                    ku = KnowledgeUnit(
                        content=content,
                        source=LearningSource.USER_INTERACTION,
                        technique=LearningTechnique.SUPERVISED,
                        confidence=0.8,
                        metadata={"interaction": interaction}
                    )
                    self.knowledge_base[ku.knowledge_id] = ku
                    knowledge_units += 1

        return {
            "knowledge_units": knowledge_units,
            "effectiveness": 0.75,
            "learned_patterns": ["successful_interactions"]
        }

    async def _apply_unsupervised_learning(self, raw_data: Dict[LearningSource, Dict]) -> Dict[str, Any]:
        """Aplica aprendizado não-supervisionado."""
        # Implementação simplificada - clustering de logs
        knowledge_units = 0

        if LearningSource.SYSTEM_LOGS in raw_data:
            logs = raw_data[LearningSource.SYSTEM_LOGS].get("logs", [])

            # Agrupar logs por tipo
            error_logs = [log for log in logs if log.get("level") == "error"]
            if error_logs:
                content = f"Error pattern detected: {len(error_logs)} errors of similar type"
                ku = KnowledgeUnit(
                    content=content,
                    source=LearningSource.SYSTEM_LOGS,
                    technique=LearningTechnique.UNSUPERVISED,
                    confidence=0.6,
                    metadata={"error_count": len(error_logs)}
                )
                self.knowledge_base[ku.knowledge_id] = ku
                knowledge_units += 1

        return {
            "knowledge_units": knowledge_units,
            "effectiveness": 0.65,
            "learned_patterns": ["error_clustering"]
        }

    async def _apply_reinforcement_learning(self, raw_data: Dict[LearningSource, Dict]) -> Dict[str, Any]:
        """Aplica aprendizado por reforço."""
        # Implementação simplificada baseada em feedback
        knowledge_units = 0

        if LearningSource.USER_FEEDBACK in raw_data:
            feedback_list = raw_data[LearningSource.USER_FEEDBACK].get("feedback", [])
            positive_feedback = [f for f in feedback_list if f.get("rating", 0) > 0.7]

            if positive_feedback:
                content = f"Positive reinforcement pattern: {len(positive_feedback)} positive feedbacks"
                ku = KnowledgeUnit(
                    content=content,
                    source=LearningSource.USER_FEEDBACK,
                    technique=LearningTechnique.REINFORCEMENT,
                    confidence=0.7,
                    metadata={"positive_count": len(positive_feedback)}
                )
                self.knowledge_base[ku.knowledge_id] = ku
                knowledge_units += 1

        return {
            "knowledge_units": knowledge_units,
            "effectiveness": 0.8,
            "learned_patterns": ["reinforcement_patterns"]
        }

    async def _apply_transfer_learning(self, raw_data: Dict[LearningSource, Dict]) -> Dict[str, Any]:
        """Aplica transfer learning."""
        # Implementação simplificada - transferir conhecimento entre domínios
        knowledge_units = 0

        # Transferir padrões de execução de código para validação
        if LearningSource.CODE_EXECUTION in raw_data:
            executions = raw_data[LearningSource.CODE_EXECUTION].get("executions", [])
            successful_patterns = [e for e in executions if e.get("result") == "success"]

            if successful_patterns:
                content = f"Transferred success patterns from code execution: {len(successful_patterns)} patterns"
                ku = KnowledgeUnit(
                    content=content,
                    source=LearningSource.CODE_EXECUTION,
                    technique=LearningTechnique.TRANSFER,
                    confidence=0.75,
                    metadata={"patterns_transferred": len(successful_patterns)}
                )
                self.knowledge_base[ku.knowledge_id] = ku
                knowledge_units += 1

        return {
            "knowledge_units": knowledge_units,
            "effectiveness": 0.7,
            "learned_patterns": ["transferred_patterns"]
        }

    async def _apply_few_shot_learning(self, raw_data: Dict[LearningSource, Dict]) -> Dict[str, Any]:
        """Aplica few-shot learning."""
        # Implementação simplificada - aprender de poucos exemplos
        knowledge_units = 0

        # Aprender de métricas de performance com poucos dados
        if LearningSource.PERFORMANCE_METRICS in raw_data:
            metrics = raw_data[LearningSource.PERFORMANCE_METRICS].get("metrics", {})

            if metrics.get("error_rate", 1.0) < 0.1:  # Baixa taxa de erro
                content = f"Few-shot learning: Low error rate indicates good performance pattern"
                ku = KnowledgeUnit(
                    content=content,
                    source=LearningSource.PERFORMANCE_METRICS,
                    technique=LearningTechnique.FEW_SHOT,
                    confidence=0.65,
                    metadata={"error_rate": metrics.get("error_rate")}
                )
                self.knowledge_base[ku.knowledge_id] = ku
                knowledge_units += 1

        return {
            "knowledge_units": knowledge_units,
            "effectiveness": 0.6,
            "learned_patterns": ["few_shot_patterns"]
        }

    async def _apply_meta_learning(self, raw_data: Dict[LearningSource, Dict]) -> Dict[str, Any]:
        """Aplica meta-aprendizado."""
        # Implementação simplificada - aprender como aprender
        knowledge_units = 0

        # Meta-aprendizado sobre efetividade de técnicas
        technique_effectiveness = dict(self.learning_stats["technique_effectiveness"])

        if technique_effectiveness:
            best_technique = max(technique_effectiveness.items(), key=lambda x: x[1])
            content = f"Meta-learning: {best_technique[0]} is most effective technique (score: {best_technique[1]:.2f})"

            ku = KnowledgeUnit(
                content=content,
                source=LearningSource.SYSTEM_LOGS,  # Meta-aprendizado do sistema
                technique=LearningTechnique.META_LEARNING,
                confidence=0.9,
                metadata={"best_technique": best_technique}
            )
            self.knowledge_base[ku.knowledge_id] = ku
            knowledge_units += 1

        return {
            "knowledge_units": knowledge_units,
            "effectiveness": 0.85,
            "learned_patterns": ["meta_learning_insights"]
        }

    async def _cross_validate_knowledge(self) -> List[Dict[str, Any]]:
        """
        Realiza validação cruzada do conhecimento aprendido.
        """

        validation_results = []

        # Validar amostra do conhecimento
        sample_size = min(10, len(self.knowledge_base))
        if sample_size > 0:
            sample_ids = random.sample(list(self.knowledge_base.keys()), sample_size)

            for ku_id in sample_ids:
                ku = self.knowledge_base[ku_id]

                # Validação simples - verificar se conhecimento é aplicável
                is_valid = ku.confidence >= self.min_confidence_threshold

                validation_results.append({
                    "knowledge_id": ku_id,
                    "is_valid": is_valid,
                    "confidence": ku.confidence,
                    "technique": ku.technique.value
                })

        return validation_results

    async def _optimize_knowledge_base(self) -> None:
        """
        Otimiza base de conhecimento removendo conhecimento obsoleto ou de baixa qualidade.
        """

        # Remover conhecimento com baixa confiança
        to_remove = []
        for ku_id, ku in self.knowledge_base.items():
            if ku.confidence < 0.3:  # Muito baixa confiança
                to_remove.append(ku_id)
            elif ku.validation_count > 10 and ku.get_effectiveness() < 0.4:  # Baixa efetividade
                to_remove.append(ku_id)

        for ku_id in to_remove:
            del self.knowledge_base[ku_id]

        # Limitar tamanho da base de conhecimento
        if len(self.knowledge_base) > self.max_knowledge_units:
            # Remover os menos efetivos
            sorted_kus = sorted(self.knowledge_base.items(),
                              key=lambda x: x[1].get_effectiveness())
            to_remove = [ku_id for ku_id, _ in sorted_kus[:len(sorted_kus) - self.max_knowledge_units]]

            for ku_id in to_remove:
                del self.knowledge_base[ku_id]

    def query_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeUnit]:
        """
        Consulta conhecimento relevante.
        """

        # Busca simples baseada em similaridade de texto
        relevant_knowledge = []

        query_lower = query.lower()

        for ku in self.knowledge_base.values():
            content_str = str(ku.content).lower()

            # Calcular similaridade simples
            if any(word in content_str for word in query_lower.split()):
                relevance_score = ku.confidence * ku.get_effectiveness()
                relevant_knowledge.append((ku, relevance_score))

        # Ordenar por relevância
        relevant_knowledge.sort(key=lambda x: x[1], reverse=True)

        # Retornar top resultados
        return [ku for ku, _ in relevant_knowledge[:limit]]

    def get_learning_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de aprendizado."""

        return {
            **self.learning_stats,
            "current_knowledge_units": len(self.knowledge_base),
            "technique_distribution": dict(self.learning_stats["technique_effectiveness"]),
            "recent_sessions": len(self.learning_sessions[-10:])
        }

    def _load_knowledge_base(self) -> None:
        """Carrega base de conhecimento do disco."""

        if self.knowledge_base_file.exists():
            try:
                kb_data = json.loads(self.knowledge_base_file.read_text(encoding='utf-8'))

                for ku_data in kb_data.get("knowledge_units", []):
                    ku = KnowledgeUnit(
                        content=ku_data["content"],
                        source=LearningSource(ku_data["source"]),
                        technique=LearningTechnique(ku_data["technique"]),
                        confidence=ku_data["confidence"],
                        metadata=ku_data.get("metadata", {})
                    )

                    # Restaurar dados adicionais
                    ku.knowledge_id = ku_data["knowledge_id"]
                    ku.validation_count = ku_data.get("validation_count", 0)
                    ku.successful_applications = ku_data.get("successful_applications", 0)
                    ku.last_used = ku_data.get("last_used")
                    ku.created_at = ku_data.get("created_at", ku.created_at)

                    self.knowledge_base[ku.knowledge_id] = ku

                # Restaurar estatísticas
                if "stats" in kb_data:
                    self.learning_stats.update(kb_data["stats"])

            except Exception as e:
                print(f"Error loading knowledge base: {e}")

        # Carregar sessões
        if self.learning_sessions_file.exists():
            try:
                self.learning_sessions = json.loads(
                    self.learning_sessions_file.read_text(encoding='utf-8')
                )
            except Exception:
                self.learning_sessions = []

    def _save_knowledge_base(self) -> None:
        """Salva base de conhecimento no disco."""

        self.learning_dir.mkdir(parents=True, exist_ok=True)

        # Serializar unidades de conhecimento
        kb_data = {
            "knowledge_units": [],
            "stats": self.learning_stats,
            "last_updated": datetime.now().isoformat()
        }

        for ku in self.knowledge_base.values():
            kb_data["knowledge_units"].append({
                "knowledge_id": ku.knowledge_id,
                "content": ku.content,
                "source": ku.source.value,
                "technique": ku.technique.value,
                "confidence": ku.confidence,
                "metadata": ku.metadata,
                "validation_count": ku.validation_count,
                "successful_applications": ku.successful_applications,
                "last_used": ku.last_used,
                "created_at": ku.created_at
            })

        self.knowledge_base_file.write_text(
            json.dumps(kb_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Salvar sessões de aprendizado
        self.learning_sessions_file.write_text(
            json.dumps(self.learning_sessions[-100:], ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
