"""Synthetic care brief workflow with optional Gemini polishing."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from services.fhir_bundle import export_fhir_bundle
from services.gemini_provider import safe_polish_care_brief
from services.healthcare import DEMO_SAFETY_NOTE, emergency_triage_logic, health_risk_assessment_logic, symptom_checker_logic
from services.workflow_primitives import DEFAULT_DISCLAIMER, DEMO_CASES, normalize_patient_case, safe_patient_case, validate_sharp_context


DISCLAIMER = DEFAULT_DISCLAIMER


def _case_for_id(case_id: str) -> dict[str, Any]:
    key = (case_id or "case-alpha").strip().lower()
    return deepcopy(DEMO_CASES.get(key, DEMO_CASES["case-alpha"]))


def _core_care_brief(patient_case: dict[str, Any]) -> dict[str, Any]:
    safe_case, _ = safe_patient_case(patient_case)
    symptom = symptom_checker_logic(safe_case["primary_symptom"])
    triage = emergency_triage_logic(safe_case["symptom_description"])
    risk = health_risk_assessment_logic(int(safe_case["age"]), bool(safe_case["smoking"]), bool(safe_case["diabetes"]))
    triage_level = triage["urgency_level"]
    risk_level = risk["risk_level"]

    return {
        "tool_name": "generate_care_brief",
        "case_id": safe_case["case_id"],
        "synthetic_data_notice": safe_case["synthetic_data_notice"],
        "patient_context": {
            "case_label": safe_case["case_label"],
            "age_band": f"{(int(safe_case['age']) // 10) * 10}s",
            "primary_symptom": safe_case["primary_symptom"],
            "condition_context": safe_case["condition_context"],
        },
        "triage_level": triage_level,
        "risk_level": risk_level,
        "red_flags": symptom["red_flags"],
        "risk_flags": risk["contributing_factors"],
        "recommended_next_steps": [
            "Keep the synthetic context visible for clinician review.",
            "Use the care brief as a coordination artifact, not as medical advice.",
        ]
        if triage_level == "low"
        else [
            "Keep the red-flag context visible for clinician review.",
            "Use the care brief for deterministic handoff support only.",
        ],
        "patient_summary": (
            f"{safe_case['case_label']} is a synthetic case with "
            f"{safe_case['primary_symptom']} context and {risk_level} synthetic risk."
        ),
        "doctor_handoff_brief": (
            f"Synthetic clinician-support handoff: triage={triage_level}; "
            f"risk={risk_level}; red flags preserved for review."
        ),
        "patient_friendly_summary": (
            "This synthetic demo organizes context for a care team. It does not provide "
            "diagnosis, treatment, or prescription advice."
        ),
        "safety_note": DEMO_SAFETY_NOTE,
        "disclaimer": DISCLAIMER,
        "ai_provider": "local",
        "ai_provider_used": False,
        "ai_model": None,
        "ai_provider_status": "local_only",
        "external_ai_safety_check": {},
    }


def build_care_brief_for_case(patient_case: dict[str, Any]) -> dict[str, Any]:
    """Build a synthetic care brief for an already-selected case."""

    safe_case, _ = safe_patient_case(patient_case)
    brief = _core_care_brief(safe_case)
    brief["fhir_bundle"] = export_fhir_bundle(
        safe_case,
        {
            "urgency_level": brief["triage_level"],
            "matched_keywords": brief["red_flags"],
            "reasoning": ["Synthetic care brief generated locally."],
            "recommended_action": brief["recommended_next_steps"],
        },
        {
            "risk_level": brief["risk_level"],
            "risk_score": None,
            "contributing_factors": brief["risk_flags"],
        },
        care_brief=brief,
        generated_by="generate_care_brief",
    )
    brief["sharp_context_validation"] = validate_sharp_context(safe_case)
    return safe_polish_care_brief(brief, safe_case)


def generate_care_brief_logic(case_id: str = "case-alpha") -> dict[str, Any]:
    """Generate a deterministic synthetic care brief, then optionally polish prose."""

    patient_case = _case_for_id(case_id)
    return build_care_brief_for_case(patient_case)
