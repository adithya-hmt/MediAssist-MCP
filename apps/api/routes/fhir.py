from __future__ import annotations

from fastapi import APIRouter

from apps.api.services.demo_case import get_synthetic_patient_case
from services.fhir_bundle import export_fhir_bundle

router = APIRouter()

@router.post("/bundle")
def bundle(payload: dict | None = None):
    case = payload or get_synthetic_patient_case()
    return export_fhir_bundle(case)
