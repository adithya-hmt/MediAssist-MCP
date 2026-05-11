"""Full synthetic care journey orchestration."""

from __future__ import annotations

from typing import Any

from services.agent_replay import generate_agent_team_replay
from services.audit_trace import generate_audit_trace
from services.care_brief import build_care_brief_for_case
from services.care_gaps import detect_care_gaps
from services.fhir_bundle import export_fhir_bundle
from services.follow_up import generate_follow_up_plan
from services.healthcare import emergency_triage_logic, health_risk_assessment_logic, symptom_checker_logic
from services.workflow_primitives import DEFAULT_DISCLAIMER, phi_safety_check, safe_patient_case, stable_trace_id, validate_sharp_context


def run_full_care_journey(patient_case: dict[str, Any]) -> dict[str, Any]:
    """Run the full deterministic synthetic care journey."""

    safe_case, safety = safe_patient_case(patient_case)
    sharp = validate_sharp_context(safe_case)
    symptom = symptom_checker_logic(safe_case["primary_symptom"])
    triage = emergency_triage_logic(safe_case["symptom_description"])
    risk = health_risk_assessment_logic(int(safe_case["age"]), bool(safe_case["smoking"]), bool(safe_case["diabetes"]))
    care_gaps = detect_care_gaps(safe_case)
    care_brief = build_care_brief_for_case(safe_case)
    follow_up = generate_follow_up_plan(safe_case, care_brief=care_brief)
    fhir_bundle = export_fhir_bundle(
        safe_case,
        triage,
        risk,
        care_gaps=care_gaps,
        follow_up_plan=follow_up,
        care_brief=care_brief,
        generated_by="run_full_care_journey",
    )

    workflow_steps = [
        "phi_safety_check",
        "sharp_context_validation",
        "symptom_checker_logic",
        "emergency_triage_logic",
        "health_risk_assessment_logic",
        "detect_care_gaps",
        "generate_follow_up_plan",
        "build_care_brief_for_case",
        "export_fhir_bundle",
        "generate_audit_trace",
    ]

    base_result = {
        "tool_name": "run_full_care_journey",
        "journey_id": stable_trace_id("journey", {"case_id": safe_case["case_id"], "symptom": safe_case["primary_symptom"]}),
        "case_id": safe_case["case_id"],
        "case_label": safe_case.get("case_label"),
        "synthetic_patient_snapshot": {
            "case_id": safe_case["case_id"],
            "case_label": safe_case.get("case_label"),
            "age": safe_case.get("age"),
            "age_band": f"{(int(safe_case['age']) // 10) * 10}s",
            "primary_symptom": safe_case.get("primary_symptom"),
            "symptom_description": safe_case.get("symptom_description"),
            "condition_context": safe_case.get("condition_context"),
            "current_medications": list(safe_case.get("current_medications", [])),
            "care_setting": safe_case.get("care_setting"),
            "follow_up_preference": safe_case.get("follow_up_preference"),
            "synthetic_data_notice": safe_case.get("synthetic_data_notice"),
        },
        "patient_case": safe_case,
        "workflow_status": "completed" if safety["safe_to_process"] else "completed_with_safety_warning",
        "workflow_steps": workflow_steps,
        "synthetic_only_status": safety["status"],
        "phi_safety_check": safety,
        "sharp_context_validation": sharp,
        "symptom_assessment": {
            "symptom_checker": symptom,
            "triage": triage,
        },
        "risk_assessment": risk,
        "care_gaps": care_gaps,
        "follow_up_plan": follow_up,
        "care_brief": care_brief,
        "fhir_bundle": fhir_bundle,
        "ai_provider_used": care_brief.get("ai_provider_used", False),
        "ai_provider": care_brief.get("ai_provider"),
        "ai_provider_status": care_brief.get("ai_provider_status", "local_only"),
        "request_id": stable_trace_id("journey", safe_case),
        "disclaimer": DEFAULT_DISCLAIMER,
    }

    base_result["audit_trace"] = generate_audit_trace(base_result)
    base_result["agent_team_replay"] = generate_agent_team_replay(safe_case)
    base_result["summary"] = {
        "triage_level": triage["urgency_level"],
        "risk_level": risk["risk_level"],
        "care_gap_priority": care_gaps["priority"],
        "follow_up_type": follow_up["recommended_follow_up_type"],
        "fhir_resources_generated": len(fhir_bundle.get("entry", [])),
        "ai_provider_status": base_result["ai_provider_status"],
    }
    return base_result
