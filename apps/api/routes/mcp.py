from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

@router.get("")
def mcp_index():
    return {"status": "ok", "transport": "http", "tools": ["run_full_care_journey", "export_fhir_bundle", "phi_safety_check", "validate_sharp_context"]}
