"""Tests for synthetic audit trace generation."""

from __future__ import annotations

import json
from pathlib import Path

from services.workflow_primitives import generate_audit_trace, run_full_care_journey


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _demo_case() -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "examples" / "synthetic_patient_case.json").read_text(encoding="utf-8"))


def test_audit_trace_contains_steps_and_disclaimers() -> None:
    journey = run_full_care_journey(_demo_case())
    trace = generate_audit_trace(
        _demo_case(),
        safety_status=journey["safety_status"],
        sharp_context_status=journey["sharp_context_status"],
        triage_result=journey["triage_result"],
        risk_result=journey["risk_assessment"],
        care_gaps=journey["care_gaps"],
        follow_up_plan=journey["follow_up_plan"],
        fhir_bundle=journey["fhir_bundle"],
    )

    assert isinstance(trace, dict)
    assert trace["tool_name"] == "generate_audit_trace"
    assert len(trace["steps"]) >= 4
    assert trace["requires_clinician_review"] is True
