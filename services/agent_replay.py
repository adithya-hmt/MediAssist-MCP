"""Deterministic specialist-agent replay for demo clarity."""

from __future__ import annotations

from typing import Any

from services.care_gaps import detect_care_gaps
from services.follow_up import generate_follow_up_plan
from services.fhir_bundle import export_fhir_bundle
from services.healthcare import emergency_triage_logic, health_risk_assessment_logic, symptom_checker_logic
from services.workflow_primitives import DEFAULT_DISCLAIMER, phi_safety_check, safe_patient_case, stable_trace_id, validate_sharp_context


def _step(
    agent_name: str,
    action: str,
    output_summary: str,
    handoff_to: str,
    confidence: float,
    safety_notes: list[str],
) -> dict[str, Any]:
    return {
        "agent_name": agent_name,
        "action": action,
        "output_summary": output_summary,
        "handoff_to": handoff_to,
        "confidence": round(confidence, 2),
        "safety_notes": safety_notes,
    }


def generate_agent_team_replay(patient_case: dict[str, Any]) -> dict[str, Any]:
    """Simulate specialist agent collaboration as a deterministic replay trace."""

    safe_case, safety = safe_patient_case(patient_case)
    sharp = validate_sharp_context(safe_case)
    symptom = symptom_checker_logic(safe_case["primary_symptom"])
    triage = emergency_triage_logic(safe_case["symptom_description"])
    risk = health_risk_assessment_logic(int(safe_case["age"]), bool(safe_case["smoking"]), bool(safe_case["diabetes"]))
    care_gaps = detect_care_gaps(safe_case)
    follow_up = generate_follow_up_plan(safe_case)
    bundle = export_fhir_bundle(
        safe_case,
        triage,
        risk,
        care_gaps=care_gaps,
        follow_up_plan=follow_up,
        generated_by="generate_agent_team_replay",
    )

    steps = [
        _step(
            "Intake Agent",
            "Normalize the synthetic case and capture the primary symptom.",
            f"Case {safe_case['case_id']} normalized with symptom '{safe_case['primary_symptom']}'.",
            "Safety Agent",
            0.98,
            ["Synthetic demo input only.", "No external systems accessed."],
        ),
        _step(
            "Safety Agent",
            "Run PHI and synthetic-only safety checks.",
            f"Safety status {safety['status']}; SHARP context {sharp['status']}.",
            "Triage Agent",
            0.97,
            ["Unsafe payloads are redirected to a synthetic fallback case."],
        ),
        _step(
            "Triage Agent",
            "Score symptom urgency using the local triage rules.",
            f"Urgency level evaluated as {triage['urgency_level']}.",
            "Care Gap Agent",
            0.96,
            ["Triage stays deterministic and local."],
        ),
        _step(
            "Care Gap Agent",
            "Detect preventive and coordination gaps.",
            f"Detected {len(care_gaps['care_gaps'])} care gaps with priority {care_gaps['priority']}.",
            "FHIR Mapping Agent",
            0.95,
            ["Care gaps are advisory, not diagnostic."],
        ),
        _step(
            "FHIR Mapping Agent",
            "Map the synthetic workflow into a FHIR-style bundle.",
            f"FHIR bundle includes {len(bundle['entry'])} synthetic resources.",
            "Handoff Agent",
            0.95,
            ["Bundle contains no real patient data and no external connection."],
        ),
        _step(
            "Handoff Agent",
            "Compose a clinician-support handoff summary.",
            f"Handoff prepared using {triage['urgency_level']} triage and {risk['risk_level']} risk context.",
            "Follow-Up Agent",
            0.94,
            ["The handoff keeps recommendations deterministic and local."],
        ),
        _step(
            "Follow-Up Agent",
            "Draft the follow-up plan and warning signs.",
            f"Recommended {follow_up['recommended_follow_up_type']} within {follow_up['suggested_timeframe']}.",
            "complete",
            0.94,
            ["Follow-up guidance supports clinician review only."],
        ),
    ]

    return {
        "tool_name": "generate_agent_team_replay",
        "trace_id": stable_trace_id("replay", {"case_id": safe_case["case_id"], "steps": len(steps)}),
        "case_id": safe_case["case_id"],
        "agent_name": "Replay Orchestrator",
        "action": "deterministic specialist collaboration replay",
        "output_summary": "A seven-agent synthetic workflow replay for hackathon demos.",
        "handoff_to": "complete",
        "confidence": 0.96,
        "steps": steps,
        "synthetic_only_status": safety["status"],
        "phi_safety_status": safety["status"],
        "safety_notes": [
            "This is a deterministic replay trace, not an autonomous agent loop.",
            "No real PHI is processed or stored.",
        ],
        "disclaimer": DEFAULT_DISCLAIMER,
    }
