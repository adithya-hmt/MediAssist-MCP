from fastapi import APIRouter
from services.audit_trace import generate_audit_trace
from services.agent_replay import generate_agent_team_replay
from app.models import PatientCaseIn
router = APIRouter(prefix="/api", tags=["audit"])

@router.post("/audit/generate")
def audit(body: dict):
    return generate_audit_trace(body)

@router.post("/agent-replay/generate")
def agent_replay(body: PatientCaseIn):
    return generate_agent_team_replay(body.model_dump())
