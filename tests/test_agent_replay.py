"""Tests for synthetic agent team replay."""

from __future__ import annotations

import json
from pathlib import Path

from services.workflow_primitives import generate_agent_team_replay


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _demo_case() -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "examples" / "synthetic_patient_case.json").read_text(encoding="utf-8"))


def test_agent_team_replay_has_sequence() -> None:
    result = generate_agent_team_replay(_demo_case())

    assert isinstance(result, dict)
    assert result["tool_name"] == "generate_agent_team_replay"
    assert result["requires_clinician_review"] is True
    assert len(result["sequence"]) >= 4
    assert "safety_guard" in result["team_roles"]
