from __future__ import annotations

from fastapi import APIRouter

from apps.api.services.demo_case import get_synthetic_patient_case
from apps.api.services.persistence import save_run
from services.workflow_primitives import run_full_care_journey

router = APIRouter()

@router.post("/journey")
def journey(payload: dict | None = None):
    case = payload or get_synthetic_patient_case()
    result = run_full_care_journey(case)
    save_run(result)
    return result
