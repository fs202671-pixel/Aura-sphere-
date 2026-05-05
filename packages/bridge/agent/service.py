from .learning.learning_controller import LearningController
"""
Serviço de Agente - controle de sessão, tarefas e integração com auditoria.

Este módulo implementa a lógica inicial de um serviço de agente seguro,
permitindo criar sessões de trabalho, registrar tarefas de evolução e
sincronizar eventos com o sistema de logging/auditoria.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logging import log_agent_action, audit_logger, LogEvent, LogLevel
from .tools import ToolRegistry, ToolExecutionResult
from .memory import MemoryStore
from .evolution import EvolutionManager, AgentVersion
from .supervisor import AgentSupervisor
from .patch_validator import PatchValidator
from .backup_manager import BackupManager
from .anomaly_detector import AnomalyDetector
from .user_intent import UserIntentInterpreter
from .user_obedience import UserObedienceManager
from .deploy_pipeline import ControlledDeployPipeline
from .controlled_learning import ControlledLearner
from .robustness_testing import RobustnessTestFramework
from .destructive_limiter import DestructiveCapabilityLimiter
from .governance import GovernanceFramework
from .zero_recovery_system import ZeroRecoverySystem
from .observability_dashboard import ObservabilityDashboard
from .advanced_offline_evolution import AdvancedOfflineEvolution
from .parallel_test_environment import ParallelTestEnvironmentManager
from .identity_consistency_system import IdentityConsistencySystem
from .dangerous_modification_protection import DangerousModificationProtection
from .image_generation_system import ImageGenerationSystem
from .image_editing_system import ImageEditingSystem
from .video_pipeline import VideoPipeline
from .media_analysis_system import MediaAnalysisSystem
from .creative_assistance_system import CreativeAssistanceSystem
from .prompt_evolution_system import PromptEvolutionSystem
from .creative_pipeline_system import CreativePipelineSystem
from .evolutionary_styles_system import EvolutionaryStylesSystem
from .resource_control_system import ResourceControlSystem
from .narrative_systems import NarrativeSystems, SemanticValidationSystem
from .creative_universes import CreativeReinterpretationSystem, CreativeUniversesSystem
from .visual_feedback_system import VisualFeedbackSystem, SaturationDetectionSystem
from .cross_evolution_simulation import CrossEvolutionSystem, VisualScenarioSimulationSystem
from .offline_scheduler import OfflineEvolutionScheduler, ExecutionMode
from .alternative_code_generator import AlternativeCodeGenerator
from runtime.sandbox import execute_code_safely
from core.permissions import PermissionLevel

BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROPOSALS_FILE = DATA_DIR / "modification_proposals.json"
PATCH_DIR = DATA_DIR / "patches"
PATCH_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR = DATA_DIR / "patch_backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class SessionTask:
    id: str
    description: str
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def complete(self, details: Optional[Dict[str, Any]] = None) -> None:
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
        if details:
            self.details.update(details)


@dataclass
class ModificationProposal:
    id: str
    description: str
    target_files: List[str]
    patch_summary: str
    detailed_changes: Dict[str, Any]
    file_patches: Dict[str, str] = field(default_factory=dict)
    status: str = "pending"
    requested_by: str = "agent"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def approve(self, approved_by: str, comment: Optional[str] = None) -> None:
        self.status = "approved"
        self.approved_by = approved_by
        self.approved_at = datetime.now().isoformat()
        if comment:
            self.metadata["approval_comment"] = comment

    def reject(self, rejected_by: str, reason: Optional[str] = None) -> None:
        self.status = "rejected"
        self.rejected_by = rejected_by
        self.rejected_at = datetime.now().isoformat()
        self.rejection_reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "target_files": self.target_files,
            "patch_summary": self.patch_summary,
            "detailed_changes": self.detailed_changes,
            "status": self.status,
            "requested_by": self.requested_by,
            "created_at": self.created_at,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "rejected_by": self.rejected_by,
            "rejected_at": self.rejected_at,
            "rejection_reason": self.rejection_reason,
            "metadata": self.metadata,
            "file_patches": self.file_patches,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ModificationProposal":
        return ModificationProposal(
            id=data.get("id"),
            description=data.get("description"),
            target_files=data.get("target_files", []),
            patch_summary=data.get("patch_summary", ""),
            detailed_changes=data.get("detailed_changes", {}),
            file_patches=data.get("file_patches", {}),
            status=data.get("status", "pending"),
            requested_by=data.get("requested_by", "agent"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            approved_by=data.get("approved_by"),
            approved_at=data.get("approved_at"),
            rejected_by=data.get("rejected_by"),
            rejected_at=data.get("rejected_at"),
            rejection_reason=data.get("rejection_reason"),
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ModificationProposal":
        return ModificationProposal(
            id=data.get("id"),
            description=data.get("description"),
            target_files=data.get("target_files", []),
            patch_summary=data.get("patch_summary", ""),
            detailed_changes=data.get("detailed_changes", {}),
            file_patches=data.get("file_patches", {}),
            status=data.get("status", "pending"),
            requested_by=data.get("requested_by", "agent"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            approved_by=data.get("approved_by"),
            approved_at=data.get("approved_at"),
            rejected_by=data.get("rejected_by"),
            rejected_at=data.get("rejected_at"),
            rejection_reason=data.get("rejection_reason"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SessionState:
    session_id: str
    user_id: str
    agent_id: str
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tasks: List[SessionTask] = field(default_factory=list)
    modification_proposals: List[ModificationProposal] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, description: str, details: Optional[Dict[str, Any]] = None) -> SessionTask:
        task = SessionTask(id=str(uuid.uuid4()), description=description, details=details or {})
        self.tasks.append(task)
        return task

    def add_modification_proposal(self, description: str, target_files: List[str], patch_summary: str,
                                  file_patches: Optional[Dict[str, str]] = None,
                                  detailed_changes: Optional[Dict[str, Any]] = None,
                                  requested_by: str = "agent", metadata: Optional[Dict[str, Any]] = None) -> ModificationProposal:
        proposal = ModificationProposal(
            id=str(uuid.uuid4()),
            description=description,
            target_files=target_files,
            patch_summary=patch_summary,
            detailed_changes=detailed_changes or {},
            file_patches=file_patches or {},
            requested_by=requested_by,
            metadata=metadata or {}
        )
        self.modification_proposals.append(proposal)
        return proposal

    def find_modification_proposal(self, proposal_id: str) -> Optional[ModificationProposal]:
        for proposal in self.modification_proposals:
            if proposal.id == proposal_id:
                return proposal
        return None

    def complete_task(self, task_id: str, details: Optional[Dict[str, Any]] = None) -> Optional[SessionTask]:
        for task in self.tasks:
            if task.id == task_id:
                task.complete(details)
                return task
        return None

    def summary(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "started_at": self.started_at,
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks if t.status == "completed"]),
            "pending_tasks": len([t for t in self.tasks if t.status != "completed"]),
            "tasks": [t.__dict__ for t in self.tasks],
            "modification_proposals": [p.to_dict() for p in self.modification_proposals],
        }


class AgentService:
    """Serviço de agente que gerencia sessões de tarefas, ferramentas e evolução."""

    def __init__(self, user_id: str = "dev-user", agent_id: str = "aura-agent", offline_mode: bool = True):
        self.session_state = SessionState(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            agent_id=agent_id,
            metadata={"service_version": "0.1.0", "offline_mode": offline_mode}
        )
        self.offline_mode = offline_mode
        self.tool_registry = ToolRegistry()
        self.memory_store = MemoryStore()
        self.evolution_manager = EvolutionManager()
        self.supervisor = AgentSupervisor()
        self.patch_validator = PatchValidator()
        self.backup_manager = BackupManager(BACKUP_DIR)
        self.anomaly_detector = AnomalyDetector(DATA_DIR / "anomalies.json")
        self.intent_interpreter = UserIntentInterpreter()
        self.user_obedience = UserObedienceManager(DATA_DIR)
        self.deploy_pipeline = ControlledDeployPipeline(DATA_DIR, self.patch_validator, self.backup_manager)
        self.controlled_learner = ControlledLearner(DATA_DIR)
        self.robustness_tester = RobustnessTestFramework(DATA_DIR)
        self.destructive_limiter = DestructiveCapabilityLimiter(DATA_DIR)
        self.governance = GovernanceFramework(DATA_DIR)
        
        # === SISTEMAS DE RECUPERAÇÃO E OBSERVABILIDADE ===
        self.zero_recovery = ZeroRecoverySystem()
        self.observability = ObservabilityDashboard()
        
        # === SISTEMAS DE EVOLUÇÃO AVANÇADA ===
        self.advanced_evolution = AdvancedOfflineEvolution(DATA_DIR)
        self.parallel_testing = ParallelTestEnvironmentManager(base_path=str(REPO_ROOT))
        self.offline_scheduler = OfflineEvolutionScheduler(self.evolution_manager)
        self.alternative_code_generator = AlternativeCodeGenerator()

        # Inicia o agendador de evolução offline automaticamente.
        self.offline_scheduler.set_execution_mode(
            ExecutionMode.EVOLUTION if self.offline_mode else ExecutionMode.ACTIVE
        )
        self.offline_scheduler.start_scheduler()

        # === SISTEMAS DE IDENTIDADE E PROTEÇÃO ===
        self.identity_consistency = IdentityConsistencySystem()
        self.dangerous_modifications = DangerousModificationProtection()
        
        # === SISTEMAS CRIATIVOS MULTIMÍDIA ===
        self.image_generation = ImageGenerationSystem()
        self.image_editing = ImageEditingSystem()
        self.video_pipeline = VideoPipeline()
        self.media_analysis = MediaAnalysisSystem()
        self.creative_assistance = CreativeAssistanceSystem()
        self.prompt_evolution = PromptEvolutionSystem()
        self.creative_pipeline = CreativePipelineSystem()
        self.evolutionary_styles = EvolutionaryStylesSystem()
        self.resource_control = ResourceControlSystem()
        
        # === SISTEMAS NARRATIVOS ===
        self.narrative_systems = NarrativeSystems()
        self.semantic_validation = SemanticValidationSystem()
        
        # === SISTEMAS DE REINTERPRETAÇÃO CRIATIVA ===
        self.creative_reinterpretation = CreativeReinterpretationSystem()
        self.creative_universes = CreativeUniversesSystem()
        
        # === SISTEMAS DE FEEDBACK VISUAL ===
        self.visual_feedback = VisualFeedbackSystem()
        self.saturation_detection = SaturationDetectionSystem()
        
        # === SISTEMAS DE EVOLUÇÃO CRUZADA ===
        self.cross_evolution = CrossEvolutionSystem()
        self.scenario_simulation = VisualScenarioSimulationSystem()
        
        # === SISTEMA DE ENSINO ADAPTATIVO ===
        self.learning_controller = LearningController(persistence_base=str(DATA_DIR / "learning"))

    def log_session_start(self) -> None:
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="session_start",
            details={
                "session_id": self.session_state.session_id,
                "user_id": self.session_state.user_id,
                "metadata": self.session_state.metadata
            },
            level=LogLevel.INFO
        )

    def add_session_task(self, description: str, details: Optional[Dict[str, Any]] = None) -> SessionTask:
        task = self.session_state.add_task(description, details)
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="task_added",
            details={"task_id": task.id, "description": description},
            level=LogLevel.DEBUG
        )
        return task

    def _persist_modification_proposals(self) -> None:
        proposals = [proposal.to_dict() for proposal in self.session_state.modification_proposals]
        PROPOSALS_FILE.write_text(json.dumps(proposals, ensure_ascii=False, indent=2), encoding='utf-8')

    def _load_modification_proposals(self) -> None:
        if PROPOSALS_FILE.exists():
            try:
                raw = json.loads(PROPOSALS_FILE.read_text(encoding='utf-8'))
                self.session_state.modification_proposals = [ModificationProposal.from_dict(entry) for entry in raw]
            except Exception:
                self.session_state.modification_proposals = []

    def set_offline_mode(self, enabled: bool) -> None:
        self.offline_mode = enabled
        self.session_state.metadata["offline_mode"] = enabled
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="offline_mode_changed",
            details={"offline_mode": enabled},
            level=LogLevel.INFO
        )

    def complete_session_task(self, task_id: str, details: Optional[Dict[str, Any]] = None) -> bool:
        task = self.session_state.complete_task(task_id, details)
        if task:
            log_agent_action(
                agent_id=self.session_state.agent_id,
                action="task_completed",
                details={"task_id": task.id, "description": task.description, "completed_at": task.completed_at},
                level=LogLevel.INFO
            )
            return True
        return False

    def get_session_report(self) -> Dict[str, Any]:
        return self.session_state.summary()

    def create_session_task_list(self, descriptions: List[str]) -> None:
        for description in descriptions:
            self.add_session_task(description)

    def audit_session_summary(self) -> None:
        summary = self.get_session_report()
        audit_logger.log_event(
            event_type=LogEvent.USER_INTERACTION,
            agent_id=self.session_state.agent_id,
            action="session_summary",
            details=summary,
            level=LogLevel.AUDIT
        )

    def register_tool(self, tool: Any) -> None:
        self.tool_registry.register(tool)

    def execute_tool(self, tool_name: str, **kwargs: Any) -> ToolExecutionResult:
        return self.tool_registry.execute_tool(tool_name, **kwargs)

    def list_tools(self) -> List[Dict[str, str]]:
        return self.tool_registry.list_tools()

    def store_memory(self, layer: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        entry = self.memory_store.add_entry(layer=layer, content=content, metadata=metadata)
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="memory_stored",
            details={"entry_id": entry.entry_id, "layer": layer},
            level=LogLevel.DEBUG
        )
        return entry.to_dict()

    def search_memory(self, query: str, layer: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        entries = self.memory_store.search(query=query, layer=layer, limit=limit)
        return [entry.to_dict() for entry in entries]

    def save_evolution_candidate(self, description: str, metrics: Optional[Dict[str, Any]] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        version = self.evolution_manager.add_version(description=description, metrics=metrics, metadata=metadata)
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="evolution_candidate_saved",
            details={"version_id": version.version_id, "description": version.description},
            level=LogLevel.INFO
        )
        return version.to_dict()

    def schedule_offline_evolution(self, description: str, task_type: str,
                                   priority: int = 5,
                                   should_run_at: Optional[datetime] = None) -> Dict[str, Any]:
        task = self.offline_scheduler.schedule_task(
            description=description,
            task_type=task_type,
            priority=priority,
            should_run_at=should_run_at
        )
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="offline_evolution_task_scheduled",
            details={"task_id": task.task_id, "description": task.description, "task_type": task.task_type},
            level=LogLevel.INFO
        )
        return task.to_dict()

    def set_offline_evolution_mode(self, enabled: bool) -> None:
        mode = ExecutionMode.EVOLUTION if enabled else ExecutionMode.ACTIVE
        self.offline_scheduler.set_execution_mode(mode)
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="offline_evolution_mode_changed",
            details={"enabled": enabled, "mode": mode.value},
            level=LogLevel.INFO
        )

    def get_offline_evolution_status(self) -> Dict[str, Any]:
        return self.offline_scheduler.get_scheduler_status()

    def generate_alternative_code_variant(self, module_name: str, variant_type: str,
                                          description: str, algorithm_name: Optional[str] = None) -> Dict[str, Any]:
        if variant_type == "optimization":
            variant = self.alternative_code_generator.generate_optimization_variant(module_name, description)
        elif variant_type == "refactor":
            variant = self.alternative_code_generator.generate_refactor_variant(module_name, description)
        elif variant_type == "alternative_algorithm":
            if not algorithm_name:
                raise ValueError("algorithm_name is required for alternative_algorithm variants")
            variant = self.alternative_code_generator.generate_algorithm_variant(module_name, algorithm_name, description)
        else:
            raise ValueError(f"Unknown variant_type: {variant_type}")

        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="alternative_code_variant_generated",
            details={"variant_id": variant.variant_id, "module": module_name, "variant_type": variant.variant_type},
            level=LogLevel.INFO
        )
        return {
            "variant_id": variant.variant_id,
            "original_module": variant.original_module,
            "variant_type": variant.variant_type,
            "description": variant.description,
            "metrics": variant.metrics,
            "complexity_score": variant.complexity_score,
            "code_changes": variant.code_changes
        }

    def list_code_variants(self, module_name: Optional[str] = None,
                           variant_type: Optional[str] = None) -> List[Dict[str, Any]]:
        variants = self.alternative_code_generator.get_variants(module_name=module_name, variant_type=variant_type)
        return [
            {
                "variant_id": v.variant_id,
                "original_module": v.original_module,
                "variant_type": v.variant_type,
                "description": v.description,
                "metrics": v.metrics,
                "complexity_score": v.complexity_score,
                "code_changes": v.code_changes
            }
            for v in variants
        ]

    def compare_code_variants(self, variant_a_id: str, variant_b_id: str) -> Optional[Dict[str, Any]]:
        variants = self.alternative_code_generator.get_variants()
        variant_a = next((v for v in variants if v.variant_id == variant_a_id), None)
        variant_b = next((v for v in variants if v.variant_id == variant_b_id), None)
        if not variant_a or not variant_b:
            return None
        return self.alternative_code_generator.compare_variants(variant_a, variant_b)

    def submit_modification_proposal(self, description: str, target_files: List[str], patch_summary: str,
                                     file_patches: Optional[Dict[str, str]] = None,
                                     detailed_changes: Optional[Dict[str, Any]] = None,
                                     user_id: str = "dev-user", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        proposal = self.session_state.add_modification_proposal(
            description=description,
            target_files=target_files,
            patch_summary=patch_summary,
            file_patches=file_patches,
            detailed_changes=detailed_changes,
            requested_by="agent",
            metadata=metadata or {}
        )
        self._persist_modification_proposals()
        self.add_session_task(
            description=f"Revisar proposta de modificação: {description}",
            details={"proposal_id": proposal.id, "status": proposal.status}
        )
        audit_logger.log_event(
            event_type=LogEvent.USER_INTERACTION,
            agent_id=self.session_state.agent_id,
            user_id=user_id,
            action="modification_proposal_submitted",
            details={
                "proposal_id": proposal.id,
                "description": description,
                "target_files": target_files,
                "patch_summary": patch_summary,
                "metadata": metadata or {}
            },
            level=LogLevel.AUDIT
        )
        return proposal.to_dict()

    def approve_modification_proposal(self, proposal_id: str, approved_by: str,
                                      approval_comment: Optional[str] = None) -> Optional[Dict[str, Any]]:
        proposal = self.session_state.find_modification_proposal(proposal_id)
        if not proposal or proposal.status != "pending":
            return None

        # Validar patch antes de aprovar
        if hasattr(proposal, 'file_patches') and proposal.file_patches:
            is_safe, violations = self.patch_validator.validate_proposal(
                proposal.target_files,
                proposal.file_patches
            )
            if not is_safe:
                audit_logger.log_event(
                    event_type=LogEvent.SECURITY_VIOLATION,
                    agent_id=self.session_state.agent_id,
                    user_id=approved_by,
                    action="modification_validation_failed",
                    details={
                        "proposal_id": proposal.id,
                        "violations": violations
                    },
                    level=LogLevel.CRITICAL
                )
                return None

        proposal.approve(approved_by=approved_by, comment=approval_comment)
        self._persist_modification_proposals()
        self.add_session_task(
            description=f"Aprovar modificação proposta: {proposal.description}",
            details={"proposal_id": proposal.id, "status": proposal.status}
        )
        audit_logger.log_event(
            event_type=LogEvent.USER_INTERACTION,
            agent_id=self.session_state.agent_id,
            user_id=approved_by,
            action="modification_proposal_approved",
            details={
                "proposal_id": proposal.id,
                "approved_by": approved_by,
                "approval_comment": approval_comment
            },
            level=LogLevel.AUDIT
        )
        self._apply_modification(proposal)
        return proposal.to_dict()

    def reject_modification_proposal(self, proposal_id: str, rejected_by: str,
                                     reason: Optional[str] = None) -> Optional[Dict[str, Any]]:
        proposal = self.session_state.find_modification_proposal(proposal_id)
        if not proposal or proposal.status != "pending":
            return None
        proposal.reject(rejected_by=rejected_by, reason=reason)
        self._persist_modification_proposals()
        self.add_session_task(
            description=f"Rejeitar modificação proposta: {proposal.description}",
            details={"proposal_id": proposal.id, "status": proposal.status, "reason": reason}
        )
        audit_logger.log_event(
            event_type=LogEvent.USER_INTERACTION,
            agent_id=self.session_state.agent_id,
            user_id=rejected_by,
            action="modification_proposal_rejected",
            details={
                "proposal_id": proposal.id,
                "rejected_by": rejected_by,
                "reason": reason
            },
            level=LogLevel.AUDIT
        )
        return proposal.to_dict()

    def get_modification_proposals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        proposals = self.session_state.modification_proposals
        if status:
            proposals = [proposal for proposal in proposals if proposal.status == status]
        return [proposal.to_dict() for proposal in proposals]

    def _apply_modification(self, proposal: ModificationProposal) -> bool:
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="modification_apply_attempt",
            details={"proposal_id": proposal.id, "status": proposal.status},
            level=LogLevel.INFO
        )
        patch_file = PATCH_DIR / f"{proposal.id}.json"
        patch_file.write_text(json.dumps(proposal.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')

        if not proposal.file_patches:
            audit_logger.log_event(
                event_type=LogEvent.CORE_VALIDATION,
                agent_id=self.session_state.agent_id,
                user_id=proposal.approved_by,
                action="modification_saved_without_apply",
                details={
                    "proposal_id": proposal.id,
                    "target_files": proposal.target_files,
                    "status": proposal.status,
                    "reason": "no file_patches provided"
                },
                level=LogLevel.WARNING
            )
            return False

        success = True
        applied_files = []
        for relative_path, new_content in proposal.file_patches.items():
            try:
                self._apply_patch_file(relative_path, new_content, proposal)
                applied_files.append(relative_path)
            except Exception as exc:
                success = False
                audit_logger.log_event(
                    event_type=LogEvent.SECURITY_VIOLATION,
                    agent_id=self.session_state.agent_id,
                    user_id=proposal.approved_by,
                    action="modification_apply_failed",
                    details={
                        "proposal_id": proposal.id,
                        "file": relative_path,
                        "error": str(exc)
                    },
                    level=LogLevel.ERROR
                )

        audit_logger.log_event(
            event_type=LogEvent.CORE_VALIDATION,
            agent_id=self.session_state.agent_id,
            user_id=proposal.approved_by,
            action="modification_applied",
            details={
                "proposal_id": proposal.id,
                "description": proposal.description,
                "target_files": proposal.target_files,
                "status": proposal.status,
                "patch_artifact": str(patch_file),
                "applied_files": applied_files,
                "success": success
            },
            level=LogLevel.AUDIT
        )
        return success

    def _apply_patch_file(self, relative_path: str, new_content: str, proposal: ModificationProposal) -> None:
        if Path(relative_path).is_absolute():
            raise ValueError("Apenas caminhos relativos são permitidos para patches")

        target_path = (REPO_ROOT / relative_path).resolve()
        if not str(target_path).startswith(str(REPO_ROOT)):
            raise ValueError("Caminho fora do repositório não permitido")

        if "core" in target_path.parts and "packages" not in target_path.parts:
            raise ValueError("Modificação de arquivos do core não é permitida")

        if not target_path.exists():
            raise FileNotFoundError(f"Arquivo de destino não encontrado: {relative_path}")

        backup_path = BACKUP_DIR / proposal.id / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text(target_path.read_text(encoding='utf-8'), encoding='utf-8')

        target_path.write_text(new_content, encoding='utf-8')

    def choose_best_agent_version(self) -> Optional[Dict[str, Any]]:
        version = self.evolution_manager.choose_best_version()
        return version.to_dict() if version else None

    def compare_agent_versions(self, version_a: AgentVersion, version_b: AgentVersion) -> Dict[str, Any]:
        return self.evolution_manager.compare_versions(version_a, version_b)

    def run_code_in_sandbox(self, code: str, inputs: Optional[Dict[str, Any]] = None,
                             user_id: str = "dev-user") -> Dict[str, Any]:
        result = execute_code_safely(code=code, inputs=inputs or {}, user_id=user_id)

        if result.get("has_security_violations"):
            self.supervisor.record_event("security_violation", {
                "user_id": user_id,
                "sandbox_id": "default",
                "violations": result.get("security_violations")
            })

        if not result.get("success"):
            self.supervisor.record_event("error", {
                "user_id": user_id,
                "sandbox_id": "default",
                "error": result.get("error")
            })

        return result

    def analyze_logs(self) -> Dict[str, Any]:
        all_entries = self.session_state.summary()["tasks"]
        return {
            "task_count": len(all_entries),
            "completed": len([task for task in all_entries if task["status"] == "completed"]),
            "pending": len([task for task in all_entries if task["status"] != "completed"])
        }

    def analyze_system_and_logs(self) -> Dict[str, Any]:
        """Analisa sistema e logs para identificar padrões e oportunidades de melhoria."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {},
            "log_patterns": {},
            "performance_metrics": {},
            "security_insights": {},
            "improvement_opportunities": []
        }

        # Análise de saúde do sistema
        analysis["system_health"] = {
            "total_sessions": 1,  # Simplificado para esta sessão
            "active_components": len([attr for attr in dir(self) if not attr.startswith('_') and hasattr(getattr(self, attr), '__call__')]),
            "memory_usage": "unknown",  # Poderia ser implementado com psutil
            "error_rate": 0.0  # Calcular baseado em logs
        }

        # Análise de padrões nos logs
        log_entries = audit_logger.get_recent_logs(limit=100)
        analysis["log_patterns"] = self._analyze_log_patterns(log_entries)

        # Métricas de performance
        analysis["performance_metrics"] = {
            "average_task_completion_time": "unknown",
            "memory_operations": len(self.memory_store.search("", limit=1000)),
            "tool_executions": len(self.tool_registry.list_tools()),
            "evolution_candidates": len(self.evolution_manager.list_versions())
        }

        # Insights de segurança
        analysis["security_insights"] = {
            "supervisor_events": len(self.supervisor.get_recent_events()),
            "anomaly_detections": len(self.anomaly_detector.get_recent_anomalies()),
            "patch_validations": len(self.get_modification_proposals())
        }

        # Oportunidades de melhoria
        analysis["improvement_opportunities"] = self._identify_improvement_opportunities(analysis)

        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="system_analysis_completed",
            details={"analysis_summary": {k: len(str(v)) for k, v in analysis.items() if k != "timestamp"}},
            level=LogLevel.INFO
        )

        return analysis

    def _analyze_log_patterns(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa padrões nos logs."""
        patterns = {
            "error_frequency": 0,
            "security_events": 0,
            "user_interactions": 0,
            "system_operations": 0,
            "most_common_actions": {},
            "time_patterns": {}
        }

        action_counts = {}
        for entry in log_entries:
            action = entry.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

            if "error" in action.lower():
                patterns["error_frequency"] += 1
            if "security" in action.lower():
                patterns["security_events"] += 1
            if "user" in action.lower():
                patterns["user_interactions"] += 1
            if any(word in action.lower() for word in ["task", "memory", "tool", "evolution"]):
                patterns["system_operations"] += 1

        patterns["most_common_actions"] = dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5])

        return patterns

    def _identify_improvement_opportunities(self, analysis: Dict[str, Any]) -> List[str]:
        """Identifica oportunidades de melhoria baseado na análise."""
        opportunities = []

        # Verificar alta frequência de erros
        if analysis["log_patterns"]["error_frequency"] > 10:
            opportunities.append("Implementar melhor tratamento de erros e validações adicionais")

        # Verificar baixa atividade do usuário
        if analysis["log_patterns"]["user_interactions"] < 5:
            opportunities.append("Melhorar interface e experiência do usuário")

        # Verificar oportunidades de otimização
        if analysis["performance_metrics"]["memory_operations"] > 100:
            opportunities.append("Otimizar operações de memória e implementar cache")

        # Verificar segurança
        if analysis["security_insights"]["anomaly_detections"] > 0:
            opportunities.append("Reforçar detecção e resposta a anomalias")

        # Verificar evolução
        if analysis["performance_metrics"]["evolution_candidates"] < 3:
            opportunities.append("Expandir capacidades de auto-evolução offline")

        return opportunities

    def generate_code_improvement_proposals(self) -> List[Dict[str, Any]]:
        """Gera propostas de melhoria de código baseado na análise do sistema."""
        analysis = self.analyze_system_and_logs()
        proposals = []

        # Proposta baseada em padrões de erro
        if analysis["log_patterns"]["error_frequency"] > 5:
            proposals.append({
                "type": "error_handling",
                "title": "Melhorar tratamento de erros",
                "description": "Implementar try-catch mais robusto e validações adicionais",
                "target_files": ["agent/service.py", "runtime/executor.py"],
                "estimated_impact": "high",
                "complexity": "medium"
            })

        # Proposta baseada em performance
        if analysis["performance_metrics"]["memory_operations"] > 50:
            proposals.append({
                "type": "performance",
                "title": "Otimizar operações de memória",
                "description": "Implementar cache LRU e reduzir operações desnecessárias",
                "target_files": ["agent/memory.py"],
                "estimated_impact": "medium",
                "complexity": "high"
            })

        # Proposta baseada em segurança
        if analysis["security_insights"]["supervisor_events"] > 0:
            proposals.append({
                "type": "security",
                "title": "Reforçar supervisão de segurança",
                "description": "Adicionar mais verificações automáticas e alertas",
                "target_files": ["agent/supervisor.py"],
                "estimated_impact": "high",
                "complexity": "medium"
            })

        # Proposta de evolução
        proposals.append({
            "type": "evolution",
            "title": "Expandir capacidades de aprendizado",
            "description": "Adicionar novos algoritmos de aprendizado controlado",
            "target_files": ["agent/controlled_learning.py"],
            "estimated_impact": "medium",
            "complexity": "high"
        })

        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="code_improvement_proposals_generated",
            details={"proposal_count": len(proposals)},
            level=LogLevel.INFO
        )

        return proposals

    def suggest_patch_updates(self) -> List[Dict[str, Any]]:
        """Sugere patches de atualização baseado na análise."""
        proposals = self.generate_code_improvement_proposals()
        patches = []

        for proposal in proposals:
            patch = {
                "proposal_id": str(uuid.uuid4()),
                "title": proposal["title"],
                "description": proposal["description"],
                "target_files": proposal["target_files"],
                "patch_type": proposal["type"],
                "suggested_changes": self._generate_patch_suggestions(proposal),
                "risk_assessment": self._assess_patch_risk(proposal),
                "testing_requirements": self._generate_testing_requirements(proposal)
            }
            patches.append(patch)

        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="patch_updates_suggested",
            details={"patch_count": len(patches)},
            level=LogLevel.INFO
        )

        return patches

    def _generate_patch_suggestions(self, proposal: Dict[str, Any]) -> Dict[str, str]:
        """Gera sugestões de código para o patch."""
        suggestions = {}

        if proposal["type"] == "error_handling":
            suggestions["agent/service.py"] = """
# Adicionar validação adicional
try:
    result = self.execute_tool(tool_name, **kwargs)
    if not result.success:
        self.supervisor.record_event("tool_execution_failed", {"tool": tool_name})
except Exception as e:
    self.anomaly_detector.record_anomaly("tool_error", {"error": str(e)})
    raise
"""
        elif proposal["type"] == "performance":
            suggestions["agent/memory.py"] = """
# Implementar cache LRU
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_search(self, query: str, layer: str) -> List[MemoryEntry]:
    return self._perform_search(query, layer)
"""

        return suggestions

    def _assess_patch_risk(self, proposal: Dict[str, Any]) -> str:
        """Avalia risco do patch."""
        if proposal["complexity"] == "high" and proposal["estimated_impact"] == "high":
            return "high"
        elif proposal["complexity"] == "medium" or proposal["estimated_impact"] == "high":
            return "medium"
        else:
            return "low"

    def _generate_testing_requirements(self, proposal: Dict[str, Any]) -> List[str]:
        """Gera requisitos de teste para o patch."""
        requirements = ["Teste unitário básico"]

        if proposal["type"] == "security":
            requirements.extend([
                "Teste de penetração",
                "Análise de vulnerabilidades",
                "Teste de carga com cenários de ataque"
            ])
        elif proposal["type"] == "performance":
            requirements.extend([
                "Benchmarking antes/depois",
                "Teste de carga",
                "Análise de uso de memória"
            ])

        requirements.append("Teste de regressão completo")
        return requirements

    def detect_failure_patterns(self) -> Dict[str, Any]:
        """Identifica padrões de falha ou ataque no sistema."""
        detection_results = {
            "timestamp": datetime.now().isoformat(),
            "anomalies_detected": [],
            "attack_patterns": [],
            "failure_patterns": [],
            "recommendations": []
        }

        # Verificar anomalias recentes
        recent_anomalies = self.anomaly_detector.get_recent_anomalies(limit=50)
        detection_results["anomalies_detected"] = recent_anomalies

        # Analisar padrões de falha
        log_entries = audit_logger.get_recent_logs(limit=200)
        failure_patterns = self._analyze_failure_patterns(log_entries)
        detection_results["failure_patterns"] = failure_patterns

        # Detectar possíveis ataques
        attack_indicators = self._detect_attack_patterns(log_entries)
        detection_results["attack_patterns"] = attack_indicators

        # Gerar recomendações
        detection_results["recommendations"] = self._generate_security_recommendations(
            recent_anomalies, failure_patterns, attack_indicators
        )

        # Registrar detecção
        if detection_results["anomalies_detected"] or detection_results["attack_patterns"]:
            log_agent_action(
                agent_id=self.session_state.agent_id,
                action="threat_detection_completed",
                details={
                    "anomalies": len(detection_results["anomalies_detected"]),
                    "attacks": len(detection_results["attack_patterns"]),
                    "failures": len(detection_results["failure_patterns"])
                },
                level=LogLevel.WARNING
            )

        return detection_results

    def _analyze_failure_patterns(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analisa padrões de falha nos logs."""
        patterns = []

        # Contar erros por tipo
        error_counts = {}
        for entry in log_entries:
            if entry.get("level") in ["ERROR", "CRITICAL"]:
                error_type = entry.get("action", "unknown_error")
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

        # Identificar padrões frequentes
        for error_type, count in error_counts.items():
            if count > 3:  # Mais de 3 ocorrências
                patterns.append({
                    "pattern": "frequent_error",
                    "error_type": error_type,
                    "frequency": count,
                    "severity": "medium" if count < 10 else "high"
                })

        return patterns

    def _detect_attack_patterns(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detecta padrões de possível ataque."""
        attack_patterns = []

        # Procurar por tentativas de acesso não autorizado
        unauthorized_attempts = 0
        suspicious_actions = []

        for entry in log_entries:
            action = entry.get("action", "")
            if any(keyword in action.lower() for keyword in ["unauthorized", "forbidden", "violation", "attack"]):
                unauthorized_attempts += 1
                suspicious_actions.append(action)

        if unauthorized_attempts > 0:
            attack_patterns.append({
                "pattern": "unauthorized_access_attempts",
                "frequency": unauthorized_attempts,
                "actions": suspicious_actions[:5],  # Limitar para não sobrecarregar
                "severity": "high" if unauthorized_attempts > 5 else "medium"
            })

        return attack_patterns

    def _generate_security_recommendations(self, anomalies: List[Dict[str, Any]],
                                         failures: List[Dict[str, Any]],
                                         attacks: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações de segurança."""
        recommendations = []

        if anomalies:
            recommendations.append("Revisar e ajustar detector de anomalias")

        if failures:
            recommendations.append("Implementar circuit breakers para operações críticas")

        if attacks:
            recommendations.append("Reforçar autenticação e autorização")
            recommendations.append("Implementar rate limiting para APIs")

        if not recommendations:
            recommendations.append("Sistema de segurança funcionando adequadamente")

        return recommendations

    def run_offline_evolution_candidate(self, description: str, candidate_code: Optional[str] = None,
                                       target_files: Optional[List[str]] = None,
                                       patch_summary: Optional[str] = None,
                                       detailed_changes: Optional[Dict[str, Any]] = None,
                                       user_id: str = "dev-user") -> Dict[str, Any]:
        """Cria um candidato de evolução offline e valida em sandbox."""
        candidate_metadata = {
            "offline_candidate": True,
            "target_files": target_files or [],
            "patch_summary": patch_summary or "",
            "detailed_changes": detailed_changes or {}
        }
        sandbox_result = None
        if candidate_code:
            sandbox_result = self.run_code_in_sandbox(code=candidate_code, inputs={}, user_id=user_id)

        metrics = {
            "quality_score": 0.0,
            "stability": 0.0,
            "security": 0.0,
            "errors": 0,
            "sandbox_passed": bool(sandbox_result and sandbox_result.get("success")),
            "sandbox_output": sandbox_result.get("output") if sandbox_result else None,
            "sandbox_error": sandbox_result.get("error") if sandbox_result else None
        }
        if sandbox_result:
            metrics.update({
                "quality_score": 8.0 if sandbox_result.get("success") else 3.0,
                "stability": 0.9 if sandbox_result.get("success") else 0.2,
                "security": 1.0 if not sandbox_result.get("has_security_violations") else 0.1,
                "errors": 0 if sandbox_result.get("success") else 1
            })

        version = self.evolution_manager.add_version(
            description=description,
            metrics=metrics,
            metadata=candidate_metadata
        )
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="offline_evolution_candidate_created",
            details={"version_id": version.version_id, "description": description, "sandbox_result": sandbox_result},
            level=LogLevel.INFO
        )
        return {
            "version": version.to_dict(),
            "sandbox_result": sandbox_result
        }

    def record_anomaly(self, details: Dict[str, Any]) -> None:
        self.supervisor.record_event("anomaly", details)

    def get_supervisor_status(self) -> Dict[str, Any]:
        return self.supervisor.status()

    def interpret_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Interpreta intenção do usuário."""
        intent = self.intent_interpreter.interpret(user_input)
        is_safe, reason = self.intent_interpreter.validate_intent_safety(intent)

        return {
            "intent_type": intent.intent_type.value,
            "confidence": intent.confidence,
            "action": intent.action,
            "parameters": intent.parameters,
            "risk_level": intent.risk_level,
            "requires_confirmation": intent.requires_confirmation,
            "ambiguities": intent.ambiguities,
            "is_safe": is_safe,
            "safety_reason": reason,
            "user_has_priority": self.intent_interpreter.evaluate_user_override(intent)
        }

    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Retorna resumo de anomalias."""
        return self.anomaly_detector.get_anomaly_summary(hours=24)

    def get_active_anomalies(self) -> List[Dict[str, Any]]:
        """Retorna anomalias ativas."""
        anomalies = self.anomaly_detector.get_active_anomalies()
        return [
            {
                "event_id": a.event_id,
                "anomaly_type": a.anomaly_type,
                "severity": a.severity,
                "timestamp": a.timestamp,
                "details": a.details
            }
            for a in anomalies
        ]

    def resolve_anomaly(self, anomaly_id: str, resolution: Dict[str, Any]) -> bool:
        """Marca uma anomalia como resolvida."""
        return self.anomaly_detector.resolve_anomaly(anomaly_id, resolution)

    def check_if_safe_mode_should_activate(self) -> bool:
        """Verifica se anomalias críticas justificam safe mode."""
        should_activate = self.anomaly_detector.trigger_safe_mode_if_critical()
        if should_activate and not self.supervisor.safe_mode:
            self.supervisor.activate_safe_mode("critical_anomalies_detected")
        return should_activate

    # === NOVOS MÉTODOS DE GOVERNANÇA ===

    def execute_user_command(self, user_id: str, command: str,
                           parameters: Optional[Dict[str, Any]] = None,
                           force: bool = False) -> Dict[str, Any]:
        """Executa comando do usuário com prioridade máxima."""
        result = self.user_obedience.execute_user_command(user_id, command, parameters, force)
        self.governance.register_audit_event("user_command", "user_obedience", "execute", {
            "user_id": user_id,
            "command": command,
            "parameters": parameters,
            "force": force,
            "result": result
        })
        return result

    def override_agent_decision(self, user_id: str, agent_id: str,
                               original_decision: Any,
                               override_with: Any,
                               reason: Optional[str] = None) -> Dict[str, Any]:
        """Permite que usuário sobrescreva decisão da IA."""
        result = self.user_obedience.override_agent_decision(
            user_id, agent_id, original_decision, override_with, reason
        )
        self.governance.register_audit_event("decision_override", "user_obedience", "override", {
            "user_id": user_id,
            "agent_id": agent_id,
            "original": original_decision,
            "override": override_with,
            "reason": reason
        })
        return result

    def run_deploy_pipeline(self, patch: Dict[str, Any],
                          user_approval: bool = False) -> Dict[str, Any]:
        """Executa pipeline completo de deploy."""
        result = self.deploy_pipeline.run_full_pipeline(patch, user_approval)
        self.governance.register_audit_event("deploy_pipeline", "deploy_pipeline", "execute", {
            "patch_id": patch.get("id"),
            "stages": result.get("stages", {}),
            "overall_status": result.get("overall_status")
        })
        return result

    def submit_data_for_learning(self, source: str, data: Dict[str, Any],
                               metadata: Optional[Dict] = None) -> str:
        """Submete dados para aprendizado controlado."""
        from .controlled_learning import DataSource
        data_source = DataSource(source) if hasattr(DataSource, source.upper()) else DataSource.USER_APPROVED
        data_id = self.controlled_learner.submit_data_for_validation(data_source, data, metadata)
        self.governance.register_audit_event("data_submission", "controlled_learning", "submit", {
            "data_id": data_id,
            "source": source,
            "data_keys": list(data.keys())
        })
        return data_id

    def validate_learning_data(self, data_id: str, user_id: str,
                             approved: bool, reason: Optional[str] = None) -> Dict[str, Any]:
        """Valida dados para aprendizado."""
        result = self.controlled_learner.validate_data(data_id, user_id, approved, reason)
        self.governance.register_audit_event("data_validation", "controlled_learning", "validate", {
            "data_id": data_id,
            "user_id": user_id,
            "approved": approved,
            "reason": reason
        })
        return result

    def run_robustness_tests(self, test_type: str = "security") -> Dict[str, Any]:
        """Executa testes de robustez."""
        from .robustness_testing import TestType
        test_enum = TestType(test_type.lower()) if hasattr(TestType, test_type.upper()) else TestType.SECURITY
        
        if test_enum == TestType.SECURITY:
            result = self.robustness_tester.run_security_tests(self.patch_validator.validate_string)
        elif test_enum == TestType.PERFORMANCE:
            result = self.robustness_tester.run_performance_tests(lambda: self.memory_store.search("test"))
        elif test_enum == TestType.INTEGRITY:
            result = self.robustness_tester.run_integrity_tests(lambda k: getattr(self, k, None))
        elif test_enum == TestType.RECOVERY:
            result = self.robustness_tester.run_recovery_tests(
                lambda sid: self.backup_manager.restore_backup(sid),
                ["test_snapshot"]
            )
        else:
            result = {"error": f"Test type {test_type} not implemented"}
        
        self.governance.register_audit_event("robustness_test", "robustness_testing", "run", {
            "test_type": test_type,
            "result": result
        })
        return result

    def request_destructive_action(self, action_type: str, user_id: str,
                                 target: Optional[str] = None,
                                 reason: Optional[str] = None) -> str:
        """Submete requisição de ação destrutiva."""
        from .destructive_limiter import DestructiveAction
        action_enum = DestructiveAction(action_type.lower()) if hasattr(DestructiveAction, action_type.upper()) else DestructiveAction.DELETE_FILES
        request_id = self.destructive_limiter.request_destructive_action(action_enum, user_id, target, reason)
        self.governance.register_audit_event("destructive_request", "destructive_limiter", "request", {
            "request_id": request_id,
            "action_type": action_type,
            "user_id": user_id,
            "target": target
        })
        return request_id

    def confirm_destructive_action(self, request_id: str, user_id: str) -> Dict[str, Any]:
        """Confirma ação destrutiva."""
        result = self.destructive_limiter.confirm_destructive_action(request_id, user_id)
        self.governance.register_audit_event("destructive_confirm", "destructive_limiter", "confirm", {
            "request_id": request_id,
            "user_id": user_id,
            "confirmed": result.get("confirmed", False)
        })
        return result

    def execute_destructive_action(self, request_id: str, backup_created: bool = False) -> Dict[str, Any]:
        """Executa ação destrutiva confirmada."""
        result = self.destructive_limiter.execute_destructive_action(request_id, backup_created)
        self.governance.register_audit_event("destructive_execute", "destructive_limiter", "execute", {
            "request_id": request_id,
            "executed": result.get("executed", False),
            "message": result.get("message")
        })
        return result

    def get_governance_status(self) -> Dict[str, Any]:
        """Retorna status de governança."""
        return self.governance.get_governance_status()

    def get_governance_report(self) -> Dict[str, Any]:
        """Gera relatório completo de governança."""
        return self.governance.generate_governance_report()

    def get_audit_trail(self, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
        """Retorna audit trail com filtros."""
        return self.governance.get_audit_trail(filters, limit)

    def get_learning_report(self) -> Dict[str, Any]:
        """Retorna relatório de aprendizado controlado."""
        return self.controlled_learner.export_learning_report()

    def get_robustness_report(self, limit: int = 100) -> Dict[str, Any]:
        """Retorna relatório de testes de robustez."""
        return self.robustness_tester.get_test_report(limit=limit)

    def get_destructive_history(self, limit: int = 100) -> List[Dict]:
        """Retorna histórico de ações destrutivas."""
        return self.destructive_limiter.get_action_history(limit)

    def get_user_obedience_history(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Retorna histórico de comandos do usuário."""
        return self.user_obedience.get_command_history(user_id, limit)

    # === MÉTODOS PARA SISTEMAS DE RECUPERAÇÃO E OBSERVABILIDADE ===

    def get_zero_recovery_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de recuperação zero."""
        return self.zero_recovery.get_system_status()

    def trigger_emergency_recovery(self, incident_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Dispara recuperação de emergência."""
        return self.zero_recovery.trigger_emergency_recovery(incident_type, details)

    def get_observability_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de observabilidade."""
        return self.observability.get_dashboard_data()

    def record_system_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Registra métrica do sistema."""
        self.observability.record_metric(metric_name, value, tags or {})

    # === MÉTODOS PARA SISTEMAS DE EVOLUÇÃO AVANÇADA ===

    def create_evolution_candidate(self, description: str, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria candidato de evolução avançada."""
        return self.advanced_evolution.create_evolution_candidate(description, candidate_data)

    def run_parallel_tests(self, test_suite: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executa testes em paralelo."""
        return self.parallel_testing.run_parallel_tests(test_suite)

    # === MÉTODOS PARA SISTEMAS DE IDENTIDADE E PROTEÇÃO ===

    def check_identity_consistency(self, entity_id: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica consistência de identidade."""
        return self.identity_consistency.check_consistency(entity_id, current_state)

    def validate_dangerous_modification(self, modification_type: str, target: str, user_id: str) -> Dict[str, Any]:
        """Valida modificação perigosa."""
        return self.dangerous_modifications.validate_modification(modification_type, target, user_id)

    # === MÉTODOS PARA SISTEMAS CRIATIVOS MULTIMÍDIA ===

    def generate_image(self, prompt: str, style: str = "realistic", size: str = "1024x1024") -> Dict[str, Any]:
        """Gera imagem."""
        return self.image_generation.generate_image(prompt, style, size)

    def edit_image(self, image_path: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Edita imagem."""
        return self.image_editing.apply_edits(image_path, edits)

    def process_video(self, operation: str, input_path: str, **kwargs) -> Dict[str, Any]:
        """Processa vídeo."""
        return self.video_pipeline.process_video(operation, input_path, **kwargs)

    def analyze_media(self, media_path: str, analysis_types: List[str] = None) -> Dict[str, Any]:
        """Analisa mídia."""
        return self.media_analysis.analyze_media(media_path, analysis_types)

    def get_creative_assistance(self, project_id: str, request_type: str, **kwargs) -> Dict[str, Any]:
        """Obtém assistência criativa."""
        return self.creative_assistance.get_assistance(project_id, request_type, **kwargs)

    def evolve_prompt(self, prompt_template: Dict[str, Any], evolution_strategy: str) -> Dict[str, Any]:
        """Evolui prompt."""
        return self.prompt_evolution.evolve_prompt(prompt_template, evolution_strategy)

    def execute_creative_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """Executa pipeline criativo."""
        return self.creative_pipeline.execute_pipeline(pipeline_config)

    def evolve_creative_style(self, style_config: Dict[str, Any]) -> Dict[str, Any]:
        """Evolui estilo criativo."""
        return self.evolutionary_styles.evolve_style(style_config)

    def check_resource_limits(self, resource_type: str, requested_amount: float) -> Dict[str, Any]:
        """Verifica limites de recursos."""
        return self.resource_control.check_limits(resource_type, requested_amount)

    # === MÉTODOS PARA SISTEMAS NARRATIVOS ===

    def create_narrative_structure(self, title: str, narrative_type: str, genre: str, **kwargs) -> Dict[str, Any]:
        """Cria estrutura narrativa."""
        return self.narrative_systems.create_narrative_structure(title, narrative_type, genre, **kwargs)

    def generate_narrative_content(self, structure_id: str, segment_type: str, **kwargs) -> Dict[str, Any]:
        """Gera conteúdo narrativo."""
        return self.narrative_systems.generate_narrative_content(structure_id, segment_type, **kwargs)

    def validate_content_semantically(self, content: str, validation_types: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """Valida conteúdo semanticamente."""
        return self.semantic_validation.validate_content(content, "text", validation_types or ["semantic_coherence"], **kwargs)

    # === MÉTODOS PARA SISTEMAS DE REINTERPRETAÇÃO CRIATIVA ===

    def transform_content_creatively(self, content: str, transformation_type: str, **kwargs) -> Dict[str, Any]:
        """Transforma conteúdo criativamente."""
        return self.creative_reinterpretation.transform_content(content, "text", transformation_type, **kwargs)

    def create_creative_universe(self, name: str, universe_type: str, **kwargs) -> Dict[str, Any]:
        """Cria universo criativo."""
        return self.creative_universes.create_universe(name, universe_type, **kwargs)

    # === MÉTODOS PARA SISTEMAS DE FEEDBACK VISUAL ===

    def submit_visual_feedback(self, content_id: str, feedback_type: str, user_id: str, **kwargs) -> Dict[str, Any]:
        """Submete feedback visual."""
        return self.visual_feedback.submit_feedback(content_id, "visual", feedback_type, user_id, **kwargs)

    def analyze_saturation(self, target_type: str, target_id: str, saturation_type: str, **kwargs) -> Dict[str, Any]:
        """Analisa saturação."""
        return self.saturation_detection.analyze_saturation(target_type, target_id, saturation_type, **kwargs)

    # === MÉTODOS PARA SISTEMAS DE EVOLUÇÃO CRUZADA ===

    def perform_cross_evolution(self, evolution_type: str, source_systems: List[str], target_system: str, **kwargs) -> Dict[str, Any]:
        """Realiza evolução cruzada."""
        return self.cross_evolution.perform_cross_evolution(evolution_type, source_systems, target_system, **kwargs)

    def run_scenario_simulation(self, simulation_type: str, initial_conditions: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Executa simulação de cenário."""
        return self.scenario_simulation.run_scenario_simulation(simulation_type, initial_conditions, **kwargs)

    # === MÉTODOS PARA SISTEMA DE ENSINO ADAPTATIVO ===

    def start_adaptive_learning(self, topic: str, user_id: str = "dev-user") -> Dict[str, Any]:
        """Inicia modo de ensino adaptativo para um tópico."""
        result = self.learning_controller.start_learning(topic)
        
        # Registra no audit log
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="adaptive_learning_started",
            details={
                "topic": topic,
                "user_id": user_id,
                "learning_mode": result.get("learning_mode", False)
            },
            level=LogLevel.INFO
        )
        
        # Adiciona tarefa de sessão
        self.add_session_task(
            description=f"Aprendizado ativo: {topic}",
            details={"topic": topic, "learning_mode": True}
        )
        
        return result

    def teach_topic(self, topic: str, user_id: str = "dev-user") -> Dict[str, Any]:
        """Ensina o tópico atual no modo de aprendizado."""
        result = self.learning_controller.teach(topic)
        
        # Registra no audit log
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="topic_teaching_delivered",
            details={
                "topic": topic,
                "user_id": user_id,
                "lesson": result.get("lesson", ""),
                "level": result.get("level", "")
            },
            level=LogLevel.DEBUG
        )
        
        return result

    def evaluate_learning_response(self, topic: str, user_response: str, user_id: str = "dev-user") -> Dict[str, Any]:
        """Avalia resposta do usuário no aprendizado."""
        result = self.learning_controller.evaluate(topic, user_response)
        
        # Registra no audit log
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="learning_response_evaluated",
            details={
                "topic": topic,
                "user_id": user_id,
                "outcome": result.get("outcome", ""),
                "current_level": result.get("current_level", "")
            },
            level=LogLevel.INFO
        )
        
        return result

    def get_learning_progress(self, topic: str, user_id: str = "dev-user") -> Dict[str, Any]:
        """Retorna progresso do usuário em um tópico."""
        result = self.learning_controller.progress(topic)
        
        # Registra no audit log
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="learning_progress_checked",
            details={
                "topic": topic,
                "user_id": user_id,
                "level": result.get("level", 0),
                "score": result.get("score", 0)
            },
            level=LogLevel.DEBUG
        )
        
        return result

    def stop_adaptive_learning(self, user_id: str = "dev-user") -> Dict[str, Any]:
        """Finaliza modo de ensino adaptativo."""
        result = self.learning_controller.stop_learning()
        
        # Registra no audit log
        log_agent_action(
            agent_id=self.session_state.agent_id,
            action="adaptive_learning_stopped",
            details={
                "user_id": user_id,
                "topic": result.get("topic", ""),
                "learning_mode": result.get("learning_mode", False)
            },
            level=LogLevel.INFO
        )
        
        # Completa tarefa de sessão
        self.complete_session_task(
            task_id=None,  # TODO: implementar busca por tarefa de aprendizado ativa
            details={"topic": result.get("topic", ""), "learning_completed": True}
        )
        
        return result

    def is_learning_mode_active(self) -> bool:
        """Verifica se o modo de aprendizado está ativo."""
        return self.learning_controller.is_learning_active()

    def get_learning_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema de aprendizado."""
        return {
            "learning_mode_active": self.is_learning_mode_active(),
            "current_topic": getattr(self.learning_controller.session_manager, 'current_topic', None),
            "available_topics": self.learning_controller.student_model.list_topics(),
            "learning_capabilities": [
                "start_adaptive_learning",
                "teach_topic", 
                "evaluate_learning_response",
                "get_learning_progress",
                "stop_adaptive_learning"
            ]
        }


def get_agent_service(user_id: str = "dev-user", agent_id: str = "aura-agent") -> AgentService:
    return AgentService(user_id=user_id, agent_id=agent_id)
