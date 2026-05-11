"""Deterministic care gap detection for synthetic healthcare demos."""

from __future__ import annotations

from typing import Any

from services.healthcare import emergency_triage_logic, health_risk_assessment_logic
from services.workflow_primitives import DEFAULT_DISCLAIMER, phi_safety_check, safe_patient_case


def _gap(
    gap_id: str,
    title: str,
    priority: str,
    rationale: str,
    suggested_action: str,
    evidence: list[str],
) -> dict[str, Any]:
    return {
        "gap_id": gap_id,
        "title": title,
        "priority": priority,
        "rationale": rationale,
        "suggested_action": suggested_action,
        "evidence": evidence,
        "clinician_review_required": priority in {"high", "urgent"},
    }


def detect_care_gaps(patient_case: dict[str, Any]) -> dict[str, Any]:
    """Return a structured synthetic care-gap assessment."""

    safe_case, safety = safe_patient_case(patient_case)
    triage = emergency_triage_logic(safe_case["symptom_description"])
    risk = health_risk_assessment_logic(int(safe_case["age"]), bool(safe_case["smoking"]), bool(safe_case["diabetes"]))

    gaps: list[dict[str, Any]] = []
    rationale: list[str] = []
    suggested_actions: list[str] = []

    last_follow_up = int(safe_case.get("last_follow_up_months_ago", 0) or 0)
    preventive_gaps = list(safe_case.get("preventive_gaps", []))
    current_medications = list(safe_case.get("current_medications", []))

    if triage["urgency_level"] == "critical":
        gap = _gap(
            "urgent_symptom_review",
            "Urgent symptom review needed",
            "high",
            "The symptom pattern contains critical keywords that deserve prompt clinician review in a real workflow.",
            "Escalate for same-day clinician review and keep red-flag context visible.",
            triage.get("matched_keywords", []) or [safe_case["primary_symptom"]],
        )
        gaps.append(gap)
        rationale.append(gap["rationale"])
        suggested_actions.append(gap["suggested_action"])

    if triage["urgency_level"] == "medium":
        gap = _gap(
            "prompt_triage_review",
            "Prompt symptom review needed",
            "medium",
            "The symptom pattern is not low risk and would benefit from a prompt clinical look.",
            "Arrange prompt clinician review and monitor for new red flags.",
            triage.get("matched_keywords", []) or [safe_case["primary_symptom"]],
        )
        gaps.append(gap)
        rationale.append(gap["rationale"])
        suggested_actions.append(gap["suggested_action"])

    if last_follow_up >= 12:
        gap = _gap(
            "overdue_follow_up",
            "Preventive follow-up appears overdue",
            "medium" if risk["risk_level"] != "high" else "high",
            f"The case indicates {last_follow_up} months since the last follow-up, which is long enough to warrant a review.",
            "Schedule a preventive follow-up and review screening or chronic-care needs.",
            [f"last_follow_up_months_ago={last_follow_up}"],
        )
        gaps.append(gap)
        rationale.append(gap["rationale"])
        suggested_actions.append(gap["suggested_action"])

    for item in preventive_gaps:
        gap = _gap(
            f"preventive_gap_{len(gaps) + 1}",
            str(item).strip().capitalize(),
            "medium",
            f"The synthetic case flags a preventive care gap: {item}.",
            "Close the preventive gap during the next review.",
            [str(item)],
        )
        gaps.append(gap)
        rationale.append(gap["rationale"])
        suggested_actions.append(gap["suggested_action"])

    if current_medications:
        gap = _gap(
            "medication_reconciliation",
            "Medication reconciliation review needed",
            "medium" if risk["risk_level"] != "high" else "high",
            "The case has active medication context and benefits from a medication reconciliation review.",
            "Review the medication list with the clinician and confirm the synthetic record is current.",
            current_medications,
        )
        gaps.append(gap)
        rationale.append(gap["rationale"])
        suggested_actions.append(gap["suggested_action"])

    if safe_case.get("condition_context") in {"diabetes", "hypertension", "high cholesterol"}:
        gap = _gap(
            "chronic_condition_review",
            "Chronic-care review needed",
            "medium" if risk["risk_level"] == "low" else "high",
            f"The case carries a chronic-condition context ({safe_case['condition_context']}) that benefits from planned follow-up.",
            "Use a structured chronic-care review and keep the care plan visible.",
            [safe_case["condition_context"]],
        )
        gaps.append(gap)
        rationale.append(gap["rationale"])
        suggested_actions.append(gap["suggested_action"])

    if not gaps:
        gaps.append(
            _gap(
                "routine_monitoring",
                "Routine monitoring only",
                "low",
                "No significant care gaps were detected in the synthetic demo context.",
                "Continue routine observation and preserve the synthetic notes.",
                [safe_case["case_id"]],
            )
        )
        rationale.append("No significant care gaps were detected in the synthetic demo context.")
        suggested_actions.append("Continue routine observation and preserve the synthetic notes.")

    overall_priority = "low"
    if any(gap["priority"] == "high" for gap in gaps):
        overall_priority = "high"
    elif any(gap["priority"] == "medium" for gap in gaps):
        overall_priority = "medium"

    clinician_review_required = overall_priority in {"medium", "high"} or triage["urgency_level"] != "low"

    return {
        "tool_name": "detect_care_gaps",
        "case_id": safe_case["case_id"],
        "care_gaps": gaps,
        "gap_count": len(gaps),
        "priority": overall_priority,
        "rationale": list(dict.fromkeys(rationale)),
        "suggested_action": list(dict.fromkeys(suggested_actions)),
        "clinician_review_required": clinician_review_required,
        "requires_clinician_review": clinician_review_required,
        "triage_level": triage["urgency_level"],
        "risk_level": risk["risk_level"],
        "phi_safety_status": safety["status"],
        "synthetic_only_status": safety["status"],
        "summary": [
            "Synthetic care gaps were derived from follow-up timing, preventive review, and risk context.",
            "A licensed clinician should review the handoff before any real-world action.",
        ],
        "synthetic_data_notice": safe_case.get("synthetic_data_notice", "Synthetic example only. No real patient data or PHI."),
        "disclaimer": DEFAULT_DISCLAIMER,
    }
