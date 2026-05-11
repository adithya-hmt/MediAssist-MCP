"""Tests for synthetic follow-up planning."""

from __future__ import annotations

import json
from pathlib import Path

from services.workflow_primitives import generate_follow_up_plan


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _demo_case() -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "examples" / "synthetic_patient_case.json").read_text(encoding="utf-8"))


def test_follow_up_plan_contains_required_fields() -> None:
    result = generate_follow_up_plan(_demo_case())

    assert isinstance(result, dict)
    assert result["tool_name"] == "generate_follow_up_plan"
    assert result["requires_clinician_review"] is True
    assert result["recommended_follow_up_type"]
    assert result["timeframe"]
    assert result["clinician_actions"]
