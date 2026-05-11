"""Tests for synthetic care-gap detection."""

from __future__ import annotations

import json
from pathlib import Path

from services.workflow_primitives import detect_care_gaps


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _demo_case() -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "examples" / "synthetic_patient_case.json").read_text(encoding="utf-8"))


def test_detect_care_gaps_returns_structured_output() -> None:
    result = detect_care_gaps(_demo_case())

    assert isinstance(result, dict)
    assert result["tool_name"] == "detect_care_gaps"
    assert result["gap_count"] >= 1
    assert isinstance(result["care_gaps"], list)
    assert all(gap["clinician_review_required"] for gap in result["care_gaps"])
