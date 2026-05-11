"""Tests for the full synthetic care journey."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from server import mcp
from services.workflow_primitives import run_full_care_journey


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _demo_case() -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "examples" / "synthetic_patient_case.json").read_text(encoding="utf-8"))


def test_full_care_journey_service_returns_required_keys() -> None:
    result = run_full_care_journey(_demo_case())

    assert isinstance(result, dict)
    for key in [
        "request_id",
        "synthetic_patient_snapshot",
        "safety_status",
        "sharp_context_status",
        "triage_result",
        "risk_assessment",
        "care_gaps",
        "follow_up_plan",
        "doctor_handoff_brief",
        "patient_friendly_summary",
        "fhir_resources_generated",
        "audit_trace",
        "disclaimers",
        "synthetic_data_notice",
    ]:
        assert key in result

    assert result["requires_clinician_review"] is True
    assert "Patient" in result["fhir_resources_generated"]
    assert result["safety_status"]["safe_to_process"] is True


def test_full_care_journey_tool_is_registered() -> None:
    result = asyncio.run(mcp._invoke_tool("run_full_care_journey", {"patient_case": _demo_case()}))

    assert result["tool_name"] == "run_full_care_journey"
    assert result["request_id"]
    assert "audit_trace" in result
