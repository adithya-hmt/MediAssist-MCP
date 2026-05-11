"""Optional Gemini provider with privacy-first routing.

Gemini is never required for local demos. This module only allows calls when
the environment explicitly enables Gemini, provides a server-side key, allows
synthetic external calls, and the payload passes synthetic/PHI safety checks.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

try:
    from google import genai
    from google.genai import types
except Exception:  # pragma: no cover - depends on optional dependency install state.
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]


PLACEHOLDER_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
DEFAULT_MODEL = "gemini-2.5-flash"
ADVANCED_MODEL = "gemini-2.5-pro"

PHI_PATTERNS = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:mrn|medical record|ssn|dob|date of birth)\s*[:#]?\s*[A-Za-z0-9/.-]+\b", re.IGNORECASE),
]


def _env_bool(name: str, default: bool = False) -> bool:
    fallback = "true" if default else "false"
    return os.getenv(name, fallback).strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _model_mode() -> str:
    return os.getenv("GEMINI_MODEL_MODE", "balanced").strip().lower()


def _api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


def _is_placeholder_key(value: str) -> bool:
    normalized = value.strip()
    return not normalized or normalized == PLACEHOLDER_KEY or normalized.upper().startswith("PASTE_")


def _allow_synthetic_external_calls() -> bool:
    return _env_bool("ALLOW_SYNTHETIC_EXTERNAL_CALLS", False)


def _public_demo_mode() -> bool:
    return _env_bool("PUBLIC_DEMO_MODE", True)


def _block_external_calls_on_phi() -> bool:
    return _env_bool("BLOCK_EXTERNAL_CALLS_ON_PHI", True)


def is_gemini_enabled() -> bool:
    """Return whether Gemini is enabled by configuration."""

    return _env_bool("ENABLE_GEMINI", False) and _model_mode() != "local"


def is_gemini_configured() -> bool:
    """Return whether a non-placeholder server-side Gemini key is present."""

    return not _is_placeholder_key(_api_key())


def select_gemini_model(task_type: str = "summary") -> str:
    """Select the least powerful Gemini model needed for a safe task."""

    default_model = os.getenv("GEMINI_DEFAULT_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    advanced_model = os.getenv("GEMINI_ADVANCED_MODEL", ADVANCED_MODEL).strip() or ADVANCED_MODEL
    mode = _model_mode()

    if task_type == "doctor_handoff" and mode in {"advanced", "auto"}:
        return advanced_model
    return default_model


def _has_phi_risk(text: str) -> bool:
    return any(pattern.search(text) for pattern in PHI_PATTERNS)


def _is_synthetic_case(patient_case: dict[str, Any]) -> bool:
    if patient_case.get("synthetic") is True:
        return True
    if str(patient_case.get("data_source", "")).lower() == "synthetic_json":
        return True
    if "synthetic" in str(patient_case.get("synthetic_data_notice", "")).lower():
        return True
    return False


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, default=str)
    except TypeError:
        return "{}"


def can_use_gemini(patient_case: dict[str, Any], text: str | None = None) -> dict[str, Any]:
    """Return a redacted safety decision for a possible Gemini call."""

    checks = {
        "gemini_enabled": is_gemini_enabled(),
        "gemini_configured": is_gemini_configured(),
        "allow_synthetic_external_calls": _allow_synthetic_external_calls(),
        "synthetic_case": _is_synthetic_case(patient_case),
        "phi_risk_detected": False,
        "public_demo_mode": _public_demo_mode(),
    }

    if _model_mode() == "local":
        return {"safe_to_call": False, "status": "local_only", "checks": checks}
    if not checks["gemini_enabled"]:
        return {"safe_to_call": False, "status": "gemini_disabled", "checks": checks}
    if not checks["gemini_configured"]:
        return {"safe_to_call": False, "status": "gemini_key_missing", "checks": checks}
    if not checks["allow_synthetic_external_calls"]:
        return {"safe_to_call": False, "status": "synthetic_external_calls_disabled", "checks": checks}
    if not checks["synthetic_case"]:
        return {"safe_to_call": False, "status": "non_synthetic_data_blocked", "checks": checks}

    if _block_external_calls_on_phi():
        combined = f"{_safe_json(patient_case)}\n{text or ''}"
        checks["phi_risk_detected"] = _has_phi_risk(combined)
        if checks["phi_risk_detected"]:
            return {"safe_to_call": False, "status": "phi_risk_blocked", "checks": checks}

    return {"safe_to_call": True, "status": "safe_to_call", "checks": checks}


def gemini_readiness_status() -> dict[str, Any]:
    """Return public-safe Gemini readiness metadata."""

    enabled = is_gemini_enabled()
    configured = is_gemini_configured()
    allow_external = _allow_synthetic_external_calls()
    safe_to_call = enabled and configured and allow_external and _model_mode() != "local"

    return {
        "gemini_enabled": enabled,
        "gemini_configured": configured,
        "default_model": os.getenv("GEMINI_DEFAULT_MODEL", DEFAULT_MODEL),
        "advanced_model": os.getenv("GEMINI_ADVANCED_MODEL", ADVANCED_MODEL),
        "model_mode": _model_mode(),
        "allow_synthetic_external_calls": allow_external,
        "public_demo_mode": _public_demo_mode(),
        "safe_to_call": safe_to_call,
        "status": "ready_for_synthetic_external_calls" if safe_to_call else "local_fallback_active",
        "note": "Gemini is optional. The project works offline without it.",
    }


def generate_gemini_text(prompt: str, context: dict[str, Any], task_type: str = "summary") -> dict[str, Any]:
    """Generate text with Gemini when safe, otherwise return a local fallback status."""

    patient_case = context.get("patient_case", context)
    safety = can_use_gemini(patient_case, f"{prompt}\n{_safe_json(context)}")
    model = select_gemini_model(task_type)

    if not safety["safe_to_call"]:
        return {
            "used": False,
            "model": None,
            "status": safety["status"],
            "text": "",
            "external_ai_safety_check": safety,
        }

    if genai is None:
        return {
            "used": False,
            "model": None,
            "status": "gemini_error_local_fallback",
            "text": "",
            "external_ai_safety_check": safety,
        }

    try:
        timeout_ms = _env_int("GEMINI_TIMEOUT_SECONDS", 20) * 1000
        http_options = types.HttpOptions(timeout=timeout_ms) if types is not None else {"timeout": timeout_ms}
        generation_config = (
            types.GenerateContentConfig(temperature=0.2, max_output_tokens=512)
            if types is not None
            else {"temperature": 0.2, "max_output_tokens": 512}
        )
        client = genai.Client(api_key=_api_key(), http_options=http_options)
        contents = (
            f"{prompt}\n\n"
            "Use only this redacted synthetic context. Return compact JSON only.\n"
            f"{json.dumps(context, sort_keys=True, default=str)}"
        )
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generation_config,
        )
        return {
            "used": True,
            "model": model,
            "status": "gemini_used_successfully",
            "text": getattr(response, "text", "") or "",
            "external_ai_safety_check": safety,
        }
    except Exception:
        return {
            "used": False,
            "model": None,
            "status": "gemini_error_local_fallback",
            "text": "",
            "external_ai_safety_check": safety,
        }


def _extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        parsed = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def safe_polish_care_brief(local_brief: dict[str, Any], patient_case: dict[str, Any]) -> dict[str, Any]:
    """Optionally polish care-brief prose while preserving deterministic clinical fields."""

    safety = can_use_gemini(patient_case, _safe_json(local_brief))
    brief = {
        **local_brief,
        "ai_provider": "local",
        "ai_provider_used": False,
        "ai_model": None,
        "ai_provider_status": safety["status"],
        "external_ai_safety_check": safety,
    }
    if not safety["safe_to_call"]:
        return brief

    prompt = (
        "Polish only these clinician-support fields for clarity: patient_summary, "
        "doctor_handoff_brief, patient_friendly_summary. Do not add diagnosis, "
        "treatment, prescription, new risk flags, or new recommendations. Return JSON "
        "with exactly those three keys."
    )
    context = {
        "patient_case": patient_case,
        "local_brief": {
            "patient_summary": local_brief.get("patient_summary"),
            "doctor_handoff_brief": local_brief.get("doctor_handoff_brief"),
            "patient_friendly_summary": local_brief.get("patient_friendly_summary"),
        },
    }
    result = generate_gemini_text(prompt, context, task_type="doctor_handoff")

    if not result["used"]:
        return {
            **brief,
            "ai_provider_status": result["status"],
            "external_ai_safety_check": result["external_ai_safety_check"],
        }

    polished = _extract_json_object(result["text"]) or {}
    allowed_fields = ("patient_summary", "doctor_handoff_brief", "patient_friendly_summary")
    for field_name in allowed_fields:
        value = polished.get(field_name)
        if isinstance(value, str) and value.strip():
            brief[field_name] = value.strip()

    brief.update(
        {
            "ai_provider": "gemini",
            "ai_provider_used": True,
            "ai_model": result["model"],
            "ai_provider_status": "gemini_used_successfully",
            "external_ai_safety_check": result["external_ai_safety_check"],
        }
    )
    return brief
