"""Deterministic follow-up planning for synthetic care-coordination demos."""

from __future__ import annotations

from typing import Any

from services.care_gaps import detect_care_gaps
from services.healthcare import emergency_triage_logic, health_risk_assessment_logic
from services.workflow_primitives import DEFAULT_DISCLAIMER, safe_patient_case


def _warning_signs(triage_level: str, red_flags: list[str]) -> list[str]:
    signs = list(red_flags)
    if triage_level == "critical":
        signs.extend(["new collapse", "worsening shortness of breath", "new confusion"])
    elif triage_level == "medium":
        signs.extend(["worsening pain", "new breathing difficulty", "rapid symptom change"])
    else:
        signs.extend(["persistent symptoms", "new red flags", "difficulty keeping fluids down"])
    return list(dict.fromkeys(signs))


def generate_follow_up_plan(patient_case: dict[str, Any], care_brief: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a synthetic follow-up plan based on local deterministic logic."""

    safe_case, safety = safe_patient_case(patient_case)
    triage = emergency_triage_logic(safe_case["symptom_description"])
    risk = health_risk_assessment_logic(int(safe_case["age"]), bool(safe_case["smoking"]), bool(safe_case["diabetes"]))
    gap_result = detect_care_gaps(safe_case)

    if care_brief:
        triage_level = str(care_brief.get("triage_level", triage["urgency_level"]))
        risk_level = str(care_brief.get("risk_level", risk["risk_level"]))
        red_flags = list(care_brief.get("red_flags", []))
    else:
        triage_level = triage["urgency_level"]
        risk_level = risk["risk_level"]
        red_flags = list(triage.get("matched_keywords", []))

    if triage_level == "critical":
        recommended_follow_up_type = "same-day urgent review"
        suggested_timeframe = "today"
    elif triage_level == "medium" or gap_result["priority"] == "high":
        recommended_follow_up_type = "prompt clinician review"
        suggested_timeframe = "within 24 to 72 hours"
    elif risk_level == "high" or gap_result["priority"] == "medium":
        recommended_follow_up_type = "routine clinician review"
        suggested_timeframe = "within 1 to 2 weeks"
    else:
        recommended_follow_up_type = "preventive follow-up"
        suggested_timeframe = "within 2 to 4 weeks"

    preparation_notes = [
        "Bring the synthetic symptom timeline and any questions you want answered.",
        "Keep a simple note of changes, triggers, and anything that made the symptoms better or worse.",
        "Use the care brief as a coordination aid, not as diagnosis or treatment advice.",
    ]
    if safe_case.get("current_medications"):
        preparation_notes.append("Bring the medication list so the team can check it for reconciliation.")
    if safe_case.get("condition_context"):
        preparation_notes.append(f"Include the chronic-care context: {safe_case['condition_context']}.")

    questions_for_clinician = [
        "What should be monitored before the next review?",
        "Which warning signs would change the follow-up timeline?",
        "Are there care gaps that should be closed at the next visit?",
    ]
    if safe_case.get("condition_context") == "diabetes":
        questions_for_clinician.append("Is the synthetic diabetes follow-up cadence on track?")
    if safe_case.get("condition_context") == "hypertension":
        questions_for_clinician.append("Does the blood-pressure follow-up plan need adjustment?")
    if safe_case.get("primary_symptom") == "chest pain":
        questions_for_clinician.append("What escalation threshold should be used for this chest-pain context?")

    return {
        "tool_name": "generate_follow_up_plan",
        "case_id": safe_case["case_id"],
        "recommended_follow_up_type": recommended_follow_up_type,
        "suggested_timeframe": suggested_timeframe,
        "timeframe": suggested_timeframe,
        "preparation_notes": list(dict.fromkeys(preparation_notes)),
        "questions_for_clinician": list(dict.fromkeys(questions_for_clinician)),
        "warning_signs": _warning_signs(triage_level, red_flags),
        "linked_care_gap_priority": gap_result["priority"],
        "linked_care_gaps": [gap["gap_id"] for gap in gap_result["care_gaps"]],
        "phi_safety_status": safety["status"],
        "requires_clinician_review": gap_result["clinician_review_required"] or triage_level != "low",
        "summary": (
            f"Synthetic follow-up plan for a {triage_level} triage case with {risk_level} risk. "
            "This is for coordination only and not a treatment plan."
        ),
        "synthetic_data_notice": safe_case.get("synthetic_data_notice", "Synthetic example only. No real patient data or PHI."),
        "disclaimer": DEFAULT_DISCLAIMER,
    }
