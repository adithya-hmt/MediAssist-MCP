"""Synthetic care brief workflow with optional Gemini polishing."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from services.gemini_provider import safe_polish_care_brief
from services.healthcare import (
    DEMO_SAFETY_NOTE,
    emergency_triage_logic,
    health_risk_assessment_logic,
    symptom_checker_logic,
)


DISCLAIMER = "Synthetic demo output only. This is clinician-support context, not diagnosis or treatment."

SYNTHETIC_CASES: dict[str, dict[str, Any]] = {
    "case-alpha": {
        "case_id": "case-alpha",
        "case_label": "Synthetic Case Alpha",
        "synthetic": True,
        "data_source": "synthetic_json",
        "age": 46,
        "primary_symptom": "fever",
        "symptom_description": "fever, chills, and fatigue",
        "condition_context": "diabetes",
        "smoking": False,
        "diabetes": True,
        "synthetic_data_notice": "Synthetic example only. No real patient data or PHI.",
    },
    "case-beta": {
        "case_id": "case-beta",
        "case_label": "Synthetic Case Beta",
        "synthetic": True,
        "data_source": "synthetic_json",
        "age": 68,
        "primary_symptom": "chest pain",
        "symptom_description": "chest pain and shortness of breath",
        "condition_context": "hypertension",
        "smoking": True,
        "diabetes": False,
        "synthetic_data_notice": "Synthetic example only. No real patient data or PHI.",
    },
}


def _case_for_id(case_id: str) -> dict[str, Any]:
    key = (case_id or "case-alpha").strip().lower()
    return deepcopy(SYNTHETIC_CASES.get(key, SYNTHETIC_CASES["case-alpha"]))


def _recommended_steps(triage_level: str) -> list[str]:
    if triage_level == "critical":
        return [
            "Synthetic routing: prioritize urgent clinician review in a real workflow.",
            "Keep the red-flag context visible for licensed clinical handoff.",
        ]
    if triage_level == "medium":
        return [
            "Synthetic routing: queue for prompt clinician review in a real workflow.",
            "Monitor for red-flag escalation in the structured brief.",
        ]
    return [
        "Synthetic routing: keep local supportive context and routine review notes together.",
        "Escalate only if red-flag context appears in a real workflow.",
    ]


def _fhir_style_bundle(patient_case: dict[str, Any], triage_level: str, risk_level: str) -> dict[str, Any]:
    case_id = patient_case["case_id"]
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "synthetic": True,
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": case_id,
                    "meta": {"tag": [{"code": "synthetic-demo"}]},
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": f"{case_id}-triage",
                    "status": "final",
                    "code": {"text": "Synthetic triage level"},
                    "valueString": triage_level,
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": f"{case_id}-risk",
                    "status": "final",
                    "code": {"text": "Synthetic risk level"},
                    "valueString": risk_level,
                }
            },
        ],
    }


def _sharp_context_validation(patient_case: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "valid_synthetic_context",
        "synthetic_context": patient_case.get("synthetic") is True,
        "external_ehr_connection": False,
        "authorization_required": False,
        "phi_processed": False,
    }


def _local_care_brief(patient_case: dict[str, Any]) -> dict[str, Any]:
    symptom = symptom_checker_logic(patient_case["primary_symptom"])
    triage = emergency_triage_logic(patient_case["symptom_description"])
    risk = health_risk_assessment_logic(
        int(patient_case["age"]),
        bool(patient_case["smoking"]),
        bool(patient_case["diabetes"]),
    )
    triage_level = triage["urgency_level"]
    risk_level = risk["risk_level"]

    return {
        "tool_name": "generate_care_brief",
        "case_id": patient_case["case_id"],
        "synthetic_data_notice": patient_case["synthetic_data_notice"],
        "patient_context": {
            "case_label": patient_case["case_label"],
            "age_band": f"{(int(patient_case['age']) // 10) * 10}s",
            "primary_symptom": patient_case["primary_symptom"],
            "condition_context": patient_case["condition_context"],
        },
        "triage_level": triage_level,
        "risk_level": risk_level,
        "red_flags": symptom["red_flags"],
        "risk_flags": risk["contributing_factors"],
        "recommended_next_steps": _recommended_steps(triage_level),
        "patient_summary": (
            f"{patient_case['case_label']} is a synthetic case with "
            f"{patient_case['primary_symptom']} context and {risk_level} synthetic risk."
        ),
        "doctor_handoff_brief": (
            f"Synthetic clinician-support handoff: triage={triage_level}; "
            f"risk={risk_level}; red flags preserved for review."
        ),
        "patient_friendly_summary": (
            "This synthetic demo organizes context for a care team. It does not provide "
            "diagnosis, treatment, or prescription advice."
        ),
        "fhir_bundle": _fhir_style_bundle(patient_case, triage_level, risk_level),
        "sharp_context_validation": _sharp_context_validation(patient_case),
        "safety_note": DEMO_SAFETY_NOTE,
        "disclaimer": DISCLAIMER,
        "ai_provider": "local",
        "ai_provider_used": False,
        "ai_model": None,
        "ai_provider_status": "local_only",
        "external_ai_safety_check": {},
    }


def generate_care_brief_logic(case_id: str = "case-alpha") -> dict[str, Any]:
    """Generate a deterministic synthetic care brief, then optionally polish prose."""

    patient_case = _case_for_id(case_id)
    local_brief = _local_care_brief(patient_case)
    return safe_polish_care_brief(local_brief, patient_case)
