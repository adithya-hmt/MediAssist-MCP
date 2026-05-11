"""Tests for optional Gemini provider routing."""

from __future__ import annotations

from types import SimpleNamespace

from services.care_brief import generate_care_brief_logic
from services import gemini_provider


def _synthetic_case() -> dict[str, object]:
    return {
        "case_id": "case-test",
        "synthetic": True,
        "data_source": "synthetic_json",
        "synthetic_data_notice": "Synthetic example only.",
    }


def test_gemini_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_GEMINI", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ALLOW_SYNTHETIC_EXTERNAL_CALLS", raising=False)

    assert gemini_provider.is_gemini_enabled() is False
    assert gemini_provider.can_use_gemini(_synthetic_case())["status"] == "gemini_disabled"


def test_missing_key_does_not_crash(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_GEMINI", "true")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("ALLOW_SYNTHETIC_EXTERNAL_CALLS", "true")

    result = gemini_provider.generate_gemini_text("Summarize", {"patient_case": _synthetic_case()})

    assert result["used"] is False
    assert result["status"] == "gemini_key_missing"


def test_allow_synthetic_external_calls_false_blocks(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_GEMINI", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("ALLOW_SYNTHETIC_EXTERNAL_CALLS", "false")

    decision = gemini_provider.can_use_gemini(_synthetic_case())

    assert decision["safe_to_call"] is False
    assert decision["status"] == "synthetic_external_calls_disabled"


def test_model_selection_balanced_and_advanced(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL_MODE", "balanced")
    assert gemini_provider.select_gemini_model("summary") == "gemini-2.5-flash"
    assert gemini_provider.select_gemini_model("doctor_handoff") == "gemini-2.5-flash"

    monkeypatch.setenv("GEMINI_MODEL_MODE", "advanced")
    assert gemini_provider.select_gemini_model("doctor_handoff") == "gemini-2.5-pro"

    monkeypatch.setenv("GEMINI_MODEL_MODE", "auto")
    assert gemini_provider.select_gemini_model("doctor_handoff") == "gemini-2.5-pro"


def test_generate_care_brief_works_without_gemini(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_GEMINI", "false")

    brief = generate_care_brief_logic("case-alpha")

    assert brief["ai_provider"] == "local"
    assert brief["ai_provider_used"] is False
    assert brief["ai_model"] is None
    assert brief["triage_level"] in {"low", "medium", "critical"}
    assert brief["fhir_bundle"]["resourceType"] == "Bundle"
    assert brief["sharp_context_validation"]["external_ehr_connection"] is False


def test_gemini_provider_fallback_works_on_exception(monkeypatch) -> None:
    class BrokenModels:
        def generate_content(self, **kwargs):
            raise RuntimeError("network unavailable")

    class BrokenClient:
        def __init__(self, **kwargs):
            self.models = BrokenModels()

    fake_genai = SimpleNamespace(Client=BrokenClient)
    fake_types = SimpleNamespace(
        HttpOptions=lambda **kwargs: kwargs,
        GenerateContentConfig=lambda **kwargs: kwargs,
    )

    monkeypatch.setenv("ENABLE_GEMINI", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("ALLOW_SYNTHETIC_EXTERNAL_CALLS", "true")
    monkeypatch.setattr(gemini_provider, "genai", fake_genai)
    monkeypatch.setattr(gemini_provider, "types", fake_types)

    result = gemini_provider.generate_gemini_text("Summarize", {"patient_case": _synthetic_case()})

    assert result["used"] is False
    assert result["status"] == "gemini_error_local_fallback"


def test_generate_gemini_text_blocks_phi_in_context(monkeypatch) -> None:
    class UnexpectedClient:
        def __init__(self, **kwargs):
            raise AssertionError("Gemini client should not be created for PHI-risk context")

    monkeypatch.setenv("ENABLE_GEMINI", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("ALLOW_SYNTHETIC_EXTERNAL_CALLS", "true")
    monkeypatch.setattr(gemini_provider, "genai", SimpleNamespace(Client=UnexpectedClient))

    result = gemini_provider.generate_gemini_text(
        "Summarize",
        {"patient_case": _synthetic_case(), "extra_context": "MRN: ABC12345"},
    )

    assert result["used"] is False
    assert result["status"] == "phi_risk_blocked"
