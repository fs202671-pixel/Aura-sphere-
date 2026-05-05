import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from database import SessionLocal, ActionProposal


def _serialize_parameters(parameters: Any) -> str:
    if parameters is None:
        return ""
    if isinstance(parameters, str):
        return parameters
    try:
        return json.dumps(parameters, ensure_ascii=False)
    except Exception:
        return str(parameters)


def _deserialize_parameters(value: str) -> Any:
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return value


class ActionQueueService:
    """Serviço para gerenciar ações pendentes que requerem aprovação."""

    def submit_action_proposal(
        self,
        user_id: str,
        action_type: str,
        description: str,
        parameters: Optional[Any] = None,
        expires_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        with SessionLocal() as session:
            proposal = ActionProposal(
                user_id=user_id,
                action_type=action_type,
                description=description,
                parameters=_serialize_parameters(parameters),
                status="pending",
                expires_at=expires_at,
            )
            session.add(proposal)
            session.commit()
            session.refresh(proposal)

            return self._to_dict(proposal)

    def get_pending_actions(
        self,
        user_id: Optional[str] = None,
        status: str = "pending",
    ) -> List[Dict[str, Any]]:
        with SessionLocal() as session:
            query = session.query(ActionProposal).filter(ActionProposal.status == status)
            if user_id:
                query = query.filter(ActionProposal.user_id == user_id)

            proposals = query.order_by(ActionProposal.created_at.desc()).all()
            return [self._to_dict(p) for p in proposals]

    def approve_action(self, action_id: int, approved_by: str) -> Optional[Dict[str, Any]]:
        with SessionLocal() as session:
            proposal = session.query(ActionProposal).filter(ActionProposal.id == action_id).first()
            if not proposal or proposal.status != "pending":
                return None

            proposal.status = "approved"
            proposal.executed_at = datetime.now()
            session.commit()
            session.refresh(proposal)
            return self._to_dict(proposal)

    def reject_action(self, action_id: int, rejected_by: str, reason: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with SessionLocal() as session:
            proposal = session.query(ActionProposal).filter(ActionProposal.id == action_id).first()
            if not proposal or proposal.status != "pending":
                return None

            proposal.status = "rejected"
            proposal.executed_at = datetime.now()
            session.commit()
            session.refresh(proposal)
            return self._to_dict(proposal)

    def _to_dict(self, proposal: ActionProposal) -> Dict[str, Any]:
        return {
            "id": proposal.id,
            "user_id": proposal.user_id,
            "action_type": proposal.action_type,
            "description": proposal.description,
            "parameters": _deserialize_parameters(proposal.parameters),
            "status": proposal.status,
            "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
            "expires_at": proposal.expires_at.isoformat() if proposal.expires_at else None,
            "executed_at": proposal.executed_at.isoformat() if proposal.executed_at else None,
        }
