from __future__ import annotations

from fastapi import APIRouter

from services.workflow_primitives import phi_safety_check, validate_sharp_context

router = APIRouter()

@router.post("/phi")
def phi_check(payload: dict | None = None):
    return phi_safety_check(payload)

@router.post("/sharp")
def sharp_check(payload: dict | None = None):
    return validate_sharp_context(payload)
