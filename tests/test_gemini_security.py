"""Security tests for Gemini configuration and readiness output."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from services import gemini_provider
from tools.gemini_readiness import register_tools


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_env_example_uses_placeholder_only() -> None:
    content = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")

    assert "GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE" in content
    assert "AIza" not in content


def test_env_is_ignored() -> None:
    lines = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".env" in lines
    assert ".env.*" in lines
    assert "!.env.example" in lines


def test_readiness_tool_does_not_expose_secrets(monkeypatch) -> None:
    sensitive_value = "redacted-test-value-that-must-not-appear"
    monkeypatch.setenv("ENABLE_GEMINI", "true")
    monkeypatch.setenv("GEMINI_API_KEY", sensitive_value)
    monkeypatch.setenv("ALLOW_SYNTHETIC_EXTERNAL_CALLS", "true")

    mcp = FastMCP("test")
    register_tools(mcp)
    result = asyncio.run(mcp._invoke_tool("check_gemini_readiness", {}))
    rendered = json.dumps(result, sort_keys=True)

    assert sensitive_value not in rendered
    assert "GEMINI_API_KEY" not in rendered
    assert "api_key" not in rendered.lower()
    assert result["gemini_configured"] is True


def test_non_synthetic_data_blocks_gemini(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_GEMINI", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("ALLOW_SYNTHETIC_EXTERNAL_CALLS", "true")

    decision = gemini_provider.can_use_gemini({"case_id": "unknown", "synthetic": False})

    assert decision["safe_to_call"] is False
    assert decision["status"] == "non_synthetic_data_blocked"


def test_phi_like_text_blocks_gemini(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_GEMINI", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("ALLOW_SYNTHETIC_EXTERNAL_CALLS", "true")
    patient_case = {
        "case_id": "case-test",
        "synthetic": True,
        "data_source": "synthetic_json",
        "synthetic_data_notice": "Synthetic example only.",
    }

    decision = gemini_provider.can_use_gemini(patient_case, "MRN: ABC12345")

    assert decision["safe_to_call"] is False
    assert decision["status"] == "phi_risk_blocked"
