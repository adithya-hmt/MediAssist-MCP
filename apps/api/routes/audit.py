from __future__ import annotations

from fastapi import APIRouter

from apps.api.services.persistence import save_audit
from services.workflow_primitives import generate_audit_trace

router = APIRouter()

@router.post("")
def audit(payload: dict | None = None):
    result = generate_audit_trace(payload or {})
    save_audit(result)
    return result
