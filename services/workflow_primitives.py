"""Shared synthetic-care workflow primitives.

These helpers keep the new hackathon workflows deterministic, offline, and
safe by normalizing demo cases, checking for PHI-like patterns, and producing
stable IDs and timestamps for traceability.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha1
from typing import Any

from services.healthcare import emergency_triage_logic, health_risk_assessment_logic


DEFAULT_DISCLAIMER = "Synthetic demo output only. This does not diagnose, treat, replace professional care, or process PHI."
DEFAULT_SYNTHETIC_NOTICE = "Synthetic example only. No real patient data or PHI."


DEMO_CASES: dict[str, dict[str, Any]] = {
    "case-alpha": {
        "case_id": "case-alpha",
        "case_label": "Synthetic Case Alpha",
        "synthetic": True,
        "data_source": "synthetic_json",
        "age": 46,
        "primary_symptom": "fever",
        "symptom_description": "fever, chills, fatigue, and thirst",
        "condition_context": "diabetes",
        "smoking": False,
        "diabetes": True,
        "current_medications": ["metformin"],
        "last_follow_up_months_ago": 14,
        "preventive_gaps": ["annual diabetes review overdue", "vaccination review due"],
        "follow_up_preference": "primary care",
        "care_setting": "primary care",
        "synthetic_data_notice": DEFAULT_SYNTHETIC_NOTICE,
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
        "current_medications": ["amlodipine"],
        "last_follow_up_months_ago": 8,
        "preventive_gaps": ["blood pressure review overdue"],
        "follow_up_preference": "urgent care",
        "care_setting": "urgent care",
        "synthetic_data_notice": DEFAULT_SYNTHETIC_NOTICE,
    },
    "case-gamma": {
        "case_id": "case-gamma",
        "case_label": "Synthetic Case Gamma",
        "synthetic": True,
        "data_source": "synthetic_json",
        "age": 34,
        "primary_symptom": "headache",
        "symptom_description": "headache, poor sleep, and stress",
        "condition_context": "stress",
        "smoking": False,
        "diabetes": False,
        "current_medications": [],
        "last_follow_up_months_ago": 22,
        "preventive_gaps": ["wellness visit overdue", "sleep review overdue"],
        "follow_up_preference": "telehealth",
        "care_setting": "primary care",
        "synthetic_data_notice": DEFAULT_SYNTHETIC_NOTICE,
    },
}


PHI_PATTERNS = [
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE), "[REDACTED_EMAIL]"),
    (
        "phone",
        re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"),
        "[REDACTED_PHONE]",
    ),
    ("aadhaar_like", re.compile(r"(?<!\d)(?:\d[ -]?){11}\d(?!\d)"), "[REDACTED_ID]"),
    ("credit_card_like", re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)"), "[REDACTED_CARD]"),
    ("url", re.compile(r"\b(?:https?://|www\.)[^\s<>\]\)]+", re.IGNORECASE), "[REDACTED_URL]"),
    (
        "mrn_like",
        re.compile(r"\b(?:mrn|medical record|ssn|dob|date of birth)\s*[:#]?\s*[A-Za-z0-9/.-]+\b", re.IGNORECASE),
        "[REDACTED_ID]",
    ),
    (
        "token_or_key",
        re.compile(
            r"\b(?:sk-[A-Za-z0-9_-]{16,}|pk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|"
            r"AIza[0-9A-Za-z_-]{10,}|xox[baprs]-[A-Za-z0-9-]{10,}|(?:api[_-]?key|secret|token|password|passwd)\s*[:=]\s*[^\s,;]+)",
            re.IGNORECASE,
        ),
        "[REDACTED_SECRET]",
    ),
]


def _json_text(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, default=str)
    except TypeError:
        return str(value)


def _raw_case_dict(patient_case: dict[str, Any] | None) -> dict[str, Any]:
    """Return the raw case dictionary without synthetic defaults."""

    return dict(patient_case or {})


def normalize_patient_case(patient_case: dict[str, Any] | None) -> dict[str, Any]:
    """Merge a user-supplied case with a synthetic demo template."""

    incoming = dict(patient_case or {})
    requested_case_id = str(incoming.get("case_id") or "case-alpha").strip().lower()
    base_case = deepcopy(DEMO_CASES.get(requested_case_id, DEMO_CASES["case-alpha"]))
    normalized = {**base_case, **incoming}

    normalized["case_id"] = incoming.get("case_id", base_case["case_id"])
    normalized.setdefault("case_label", base_case["case_label"])
    normalized.setdefault("synthetic", True)
    normalized.setdefault("data_source", "synthetic_json")
    normalized.setdefault("synthetic_data_notice", DEFAULT_SYNTHETIC_NOTICE)
    normalized.setdefault("current_medications", [])
    normalized.setdefault("preventive_gaps", [])
    normalized.setdefault("follow_up_preference", "primary care")
    normalized.setdefault("care_setting", "primary care")
    return normalized


def is_synthetic_case(patient_case: dict[str, Any] | None) -> bool:
    """Return whether the case is explicitly marked synthetic."""

    raw_case = _raw_case_dict(patient_case)
    if str(raw_case.get("case_id", "")).strip().lower() in DEMO_CASES:
        return True
    if raw_case.get("synthetic") is True:
        return True
    if str(raw_case.get("data_source", "")).lower() == "synthetic_json":
        return True
    if "synthetic" in str(raw_case.get("synthetic_data_notice", "")).lower():
        return True
    return False


def safe_patient_case(patient_case: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a safe synthetic case and the original safety receipt."""

    safety = phi_safety_check(patient_case)
    normalized = normalize_patient_case(patient_case)
    if safety["safe_to_process"]:
        return normalized, safety

    fallback = deepcopy(DEMO_CASES.get(normalized["case_id"], DEMO_CASES["case-alpha"]))
    fallback["case_id"] = normalized.get("case_id", fallback["case_id"])
    return fallback, safety


def phi_safety_check(payload: Any) -> dict[str, Any]:
    """Check a payload for PHI-like patterns and synthetic-only status."""

    raw_case = _raw_case_dict(payload if isinstance(payload, dict) else None)
    text = _json_text(payload)
    synthetic_case = True if not isinstance(payload, dict) else is_synthetic_case(raw_case)
    detected_risks: list[dict[str, Any]] = []
    redacted_text = text

    for risk_name, pattern, replacement in PHI_PATTERNS:
        matches = list(pattern.finditer(redacted_text))
        if not matches:
            continue
        detected_risks.append(
            {
                "risk_type": risk_name,
                "match_count": len(matches),
                "redaction": replacement,
            }
        )
        redacted_text = pattern.sub(replacement, redacted_text)

    if not synthetic_case:
        status = "non_synthetic_data_blocked"
        safe_to_process = False
        recommendation = "Use explicit synthetic demo data only."
    elif detected_risks:
        status = "phi_risk_blocked"
        safe_to_process = False
        recommendation = "Redact or remove PHI-like values before processing."
    else:
        status = "synthetic_only_confirmed"
        safe_to_process = True
        recommendation = "Safe for synthetic demo workflows."

    return {
        "safe_to_process": safe_to_process,
        "status": status,
        "synthetic_only": synthetic_case,
        "contains_phi": bool(detected_risks),
        "detected_risks": detected_risks,
        "redacted_preview": redacted_text[:500],
        "recommendation": recommendation,
        "synthetic_only_policy": "Only synthetic demo inputs may flow through the hackathon workflows.",
        "disclaimer": DEFAULT_DISCLAIMER,
        "note": "Only synthetic demo inputs may flow through the hackathon workflows.",
    }


def validate_sharp_context(patient_case: dict[str, Any] | None) -> dict[str, Any]:
    """Return a SHARP-style context validation receipt."""

    raw_case = _raw_case_dict(patient_case)
    case = normalize_patient_case(patient_case)
    required_fields = ["case_id", "primary_symptom", "symptom_description", "synthetic"]
    present_fields = [field for field in required_fields if raw_case.get(field) not in {None, ""}]
    missing_fields = [field for field in required_fields if field not in present_fields]
    synthetic_context = is_synthetic_case(raw_case or case)

    return {
        "status": "valid_synthetic_context" if synthetic_context and not missing_fields else "needs_review",
        "context_type": "care_coordination_demo",
        "synthetic_context": synthetic_context,
        "required_fields_present": present_fields,
        "missing_fields": missing_fields,
        "external_ehr_connection": False,
        "authorization_required": False,
        "phi_processed": False,
        "allowed_actions": [
            "view_synthetic_brief",
            "generate_fhir_bundle",
            "run_follow_up_plan",
            "generate_audit_trace",
        ],
        "blocked_actions": [
            "connect_live_ehr",
            "write_prescription",
            "make_diagnosis",
        ],
        "notes": [
            "SHARP-style context is synthetic and demo-only.",
            "No external patient data stores are accessed.",
        ],
        "synthetic_data_notice": DEFAULT_SYNTHETIC_NOTICE,
        "disclaimer": DEFAULT_DISCLAIMER,
    }


def stable_trace_id(prefix: str, payload: Any) -> str:
    """Build a compact deterministic identifier for workflow artifacts."""

    digest = sha1(_json_text(payload).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def utc_timestamp() -> str:
    """Return an ISO-8601 timestamp in UTC."""

    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def case_input_keys(patient_case: dict[str, Any] | None) -> list[str]:
    """Summarize the inputs used without copying raw values into traces."""

    case = normalize_patient_case(patient_case)
    return sorted(case.keys())


def demo_cases_resource() -> dict[str, Any]:
    """Return the synthetic demo cases for documentation and future resources."""

    return {
        "resource": "synthetic://patients/demo-cases",
        "synthetic_only": True,
        "cases": list(DEMO_CASES.values()),
    }


def _case_snapshot(case: dict[str, Any]) -> dict[str, Any]:
    """Return a compact synthetic snapshot for display and traces."""

    return {
        "case_id": case["case_id"],
        "case_label": case["case_label"],
        "age": int(case["age"]),
        "age_band": f"{(int(case['age']) // 10) * 10}s",
        "primary_symptom": case["primary_symptom"],
        "symptom_description": case["symptom_description"],
        "condition_context": case["condition_context"],
        "current_medications": list(case.get("current_medications", [])),
        "care_setting": case.get("care_setting", "primary care"),
        "follow_up_preference": case.get("follow_up_preference", "primary care"),
        "synthetic_data_notice": case.get("synthetic_data_notice", DEFAULT_SYNTHETIC_NOTICE),
    }


def _triage_and_risk(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the local triage and risk logic for a synthetic case."""

    triage_result = emergency_triage_logic(case["symptom_description"])
    risk_result = health_risk_assessment_logic(
        int(case["age"]),
        bool(case.get("smoking", False)),
        bool(case.get("diabetes", False)),
    )
    return triage_result, risk_result


def detect_care_gaps(patient_case: dict[str, Any] | None, triage_result: dict[str, Any] | None = None, risk_result: dict[str, Any] | None = None) -> dict[str, Any]:
    """Detect simple synthetic care coordination gaps."""

    case = normalize_patient_case(patient_case)
    triage_result = triage_result or _triage_and_risk(case)[0]
    risk_result = risk_result or _triage_and_risk(case)[1]

    care_gaps: list[dict[str, Any]] = []

    follow_up_months = int(case.get("last_follow_up_months_ago", 0) or 0)
    if follow_up_months >= 12:
        care_gaps.append(
            {
                "gap_id": "follow-up-overdue",
                "priority": "high" if follow_up_months >= 18 or triage_result["urgency_level"] == "critical" else "medium",
                "title": "Follow-up overdue",
                "rationale": f"Last follow-up was {follow_up_months} months ago.",
                "suggested_action": "Schedule a clinician review for the synthetic case.",
                "clinician_review_required": True,
            }
        )

    preventive_gaps = list(case.get("preventive_gaps", []))
    for index, gap_text in enumerate(preventive_gaps, start=1):
        care_gaps.append(
            {
                "gap_id": f"preventive-gap-{index}",
                "priority": "medium",
                "title": "Preventive care gap",
                "rationale": gap_text,
                "suggested_action": "Review the gap during the next synthetic handoff.",
                "clinician_review_required": True,
            }
        )

    if case.get("diabetes") and risk_result["risk_level"] in {"medium", "high"}:
        care_gaps.append(
            {
                "gap_id": "diabetes-monitoring",
                "priority": "medium",
                "title": "Diabetes monitoring review",
                "rationale": "Synthetic diabetes history suggests a monitoring and prevention review.",
                "suggested_action": "Confirm routine monitoring and education topics in the handoff.",
                "clinician_review_required": True,
            }
        )

    if case.get("smoking"):
        care_gaps.append(
            {
                "gap_id": "smoking-counseling",
                "priority": "low",
                "title": "Smoking history review",
                "rationale": "A synthetic smoking history can prompt prevention counseling.",
                "suggested_action": "Include prevention counseling in the follow-up plan.",
                "clinician_review_required": True,
            }
        )

    if not care_gaps:
        care_gaps.append(
            {
                "gap_id": "no-major-gaps",
                "priority": "low",
                "title": "No major synthetic care gaps",
                "rationale": "The synthetic case does not surface a major care gap in the demo rules.",
                "suggested_action": "Keep the routine review note in the chart.",
                "clinician_review_required": True,
            }
        )

    priority_order = {"high": 0, "medium": 1, "low": 2}
    care_gaps.sort(key=lambda gap: priority_order.get(gap["priority"], 9))

    return {
        "tool_name": "detect_care_gaps",
        "request_id": stable_trace_id("care-gaps", case),
        "case_id": case["case_id"],
        "care_gaps": care_gaps,
        "gap_count": len(care_gaps),
        "summary": [
            "Synthetic care gaps were derived from follow-up timing, preventive review, and risk context.",
            "A licensed clinician should review the handoff before any real-world action.",
        ],
        "requires_clinician_review": True,
        "synthetic_data_notice": case.get("synthetic_data_notice", DEFAULT_SYNTHETIC_NOTICE),
        "disclaimer": DEFAULT_DISCLAIMER,
    }


def generate_follow_up_plan(
    patient_case: dict[str, Any] | None,
    triage_result: dict[str, Any] | None = None,
    risk_result: dict[str, Any] | None = None,
    care_gaps: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a synthetic follow-up plan from triage, risk, and care-gaps context."""

    case = normalize_patient_case(patient_case)
    triage_result = triage_result or _triage_and_risk(case)[0]
    risk_result = risk_result or _triage_and_risk(case)[1]
    care_gaps = care_gaps or detect_care_gaps(case, triage_result, risk_result)

    urgency = triage_result["urgency_level"]
    risk_level = risk_result["risk_level"]
    if urgency == "critical":
        recommended_follow_up_type = "emergency_care"
        timeframe = "immediately"
    elif urgency == "medium" or risk_level == "high":
        recommended_follow_up_type = "prompt_clinician_review"
        timeframe = "within 24 to 72 hours"
    else:
        recommended_follow_up_type = "routine_follow_up"
        timeframe = "within 1 to 2 weeks"

    follow_up_gaps = care_gaps.get("care_gaps", [])
    prep_notes = [
        "Bring the synthetic symptom summary and medication list to the handoff.",
        "Ask the clinician to review preventive gaps and monitoring needs.",
    ]
    if follow_up_gaps:
        prep_notes.append("Keep the highest-priority care gap visible during review.")

    return {
        "tool_name": "generate_follow_up_plan",
        "request_id": stable_trace_id("follow-up", case),
        "case_id": case["case_id"],
        "recommended_follow_up_type": recommended_follow_up_type,
        "timeframe": timeframe,
        "care_setting": case.get("care_setting", "primary care"),
        "triage_level": urgency,
        "risk_level": risk_level,
        "preparation_notes": prep_notes,
        "monitoring_points": [
            "Track whether the symptoms improve, worsen, or change.",
            "Review preventive and medication reconciliation gaps.",
            "Escalate urgently if new red-flag symptoms appear.",
        ],
        "patient_actions": [
            "Use the synthetic summary for the clinician handoff.",
            "Bring any current medications to the review.",
        ],
        "clinician_actions": [
            "Review the care gaps and decide whether additional evaluation is needed.",
            "Confirm the follow-up interval before closing the visit.",
        ],
        "requires_clinician_review": True,
        "summary": (
            f"Synthetic follow-up plan for a {urgency} triage case with {risk_level} risk. "
            "This is for coordination only and not a treatment plan."
        ),
        "synthetic_data_notice": case.get("synthetic_data_notice", DEFAULT_SYNTHETIC_NOTICE),
        "disclaimer": DEFAULT_DISCLAIMER,
    }


def generate_agent_team_replay(
    patient_case: dict[str, Any] | None,
    triage_result: dict[str, Any] | None = None,
    risk_result: dict[str, Any] | None = None,
    care_gaps: dict[str, Any] | None = None,
    follow_up_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a synthetic replay of a care-coordination agent team."""

    case = normalize_patient_case(patient_case)
    triage_result = triage_result or _triage_and_risk(case)[0]
    risk_result = risk_result or _triage_and_risk(case)[1]
    care_gaps = care_gaps or detect_care_gaps(case, triage_result, risk_result)
    follow_up_plan = follow_up_plan or generate_follow_up_plan(case, triage_result, risk_result, care_gaps)

    replay_id = stable_trace_id("team-replay", case)
    sequence = [
        {
            "step": 1,
            "agent": "safety_guard",
            "goal": "Confirm the demo is synthetic-only.",
            "result": "Synthetic case accepted and PHI scan completed.",
        },
        {
            "step": 2,
            "agent": "triage_agent",
            "goal": "Summarize urgency from the symptom context.",
            "result": f"Urgency level identified as {triage_result['urgency_level']}.",
        },
        {
            "step": 3,
            "agent": "risk_agent",
            "goal": "Summarize the prevention/risk context.",
            "result": f"Risk level identified as {risk_result['risk_level']}.",
        },
        {
            "step": 4,
            "agent": "care_gap_agent",
            "goal": "Find coordination gaps that the clinician should review.",
            "result": f"Detected {len(care_gaps.get('care_gaps', []))} care gaps.",
        },
        {
            "step": 5,
            "agent": "follow_up_agent",
            "goal": "Draft a follow-up plan for the handoff.",
            "result": follow_up_plan["recommended_follow_up_type"],
        },
        {
            "step": 6,
            "agent": "reviewer",
            "goal": "Check that the replay never claims diagnosis or treatment.",
            "result": "Clinician review required; no treatment claim issued.",
        },
    ]

    return {
        "tool_name": "generate_agent_team_replay",
        "replay_id": replay_id,
        "request_id": replay_id,
        "case_id": case["case_id"],
        "team_roles": [item["agent"] for item in sequence],
        "sequence": sequence,
        "handoff_summary": (
            "Synthetic agent replay showing safety, triage, risk, gap review, follow-up, and human review."
        ),
        "requires_clinician_review": True,
        "synthetic_data_notice": case.get("synthetic_data_notice", DEFAULT_SYNTHETIC_NOTICE),
        "disclaimer": DEFAULT_DISCLAIMER,
    }


def generate_audit_trace(
    patient_case: dict[str, Any] | None,
    safety_status: dict[str, Any] | None = None,
    sharp_context_status: dict[str, Any] | None = None,
    triage_result: dict[str, Any] | None = None,
    risk_result: dict[str, Any] | None = None,
    care_gaps: dict[str, Any] | None = None,
    follow_up_plan: dict[str, Any] | None = None,
    fhir_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a deterministic audit trace for the synthetic journey."""

    case = normalize_patient_case(patient_case)
    triage_result = triage_result or _triage_and_risk(case)[0]
    risk_result = risk_result or _triage_and_risk(case)[1]
    care_gaps = care_gaps or detect_care_gaps(case, triage_result, risk_result)
    follow_up_plan = follow_up_plan or generate_follow_up_plan(case, triage_result, risk_result, care_gaps)
    request_id = stable_trace_id(
        "audit-trace",
        {
            "case_id": case["case_id"],
            "triage": triage_result["urgency_level"],
            "risk": risk_result["risk_level"],
            "gaps": care_gaps.get("gap_count", len(care_gaps.get("care_gaps", []))),
        },
    )

    steps = [
        {
            "step": "1",
            "name": "PHI safety scan",
            "status": (safety_status or phi_safety_check(case)).get("status", "synthetic_only_confirmed"),
            "evidence": "Synthetic data policy checked before any downstream coordination.",
        },
        {
            "step": "2",
            "name": "SHARP validation",
            "status": (sharp_context_status or validate_sharp_context(case)).get("status", "needs_review"),
            "evidence": "Only synthetic demo context was accepted.",
        },
        {
            "step": "3",
            "name": "Triage and risk evaluation",
            "status": "completed",
            "evidence": f"Urgency={triage_result['urgency_level']}, risk={risk_result['risk_level']}.",
        },
        {
            "step": "4",
            "name": "Care-gap detection",
            "status": "completed",
            "evidence": f"{len(care_gaps.get('care_gaps', []))} synthetic care gaps identified.",
        },
        {
            "step": "5",
            "name": "Follow-up planning",
            "status": "completed",
            "evidence": follow_up_plan["recommended_follow_up_type"],
        },
        {
            "step": "6",
            "name": "FHIR-style export",
            "status": "completed" if fhir_bundle else "not_requested",
            "evidence": "FHIR-style bundle prepared for demo interoperability.",
        },
    ]

    return {
        "tool_name": "generate_audit_trace",
        "request_id": request_id,
        "case_id": case["case_id"],
        "generated_at": utc_timestamp(),
        "inputs_used": case_input_keys(case),
        "safety_status": safety_status or phi_safety_check(case),
        "sharp_context_status": sharp_context_status or validate_sharp_context(case),
        "triage_level": triage_result["urgency_level"],
        "risk_level": risk_result["risk_level"],
        "care_gap_count": len(care_gaps.get("care_gaps", [])),
        "follow_up_type": follow_up_plan["recommended_follow_up_type"],
        "steps": steps,
        "fhir_resources_referenced": [entry["resource"]["resourceType"] for entry in (fhir_bundle or {}).get("entry", [])],
        "requires_clinician_review": True,
        "synthetic_data_notice": case.get("synthetic_data_notice", DEFAULT_SYNTHETIC_NOTICE),
        "disclaimer": DEFAULT_DISCLAIMER,
    }


def run_full_care_journey(patient_case: dict[str, Any] | None) -> dict[str, Any]:
    """Run the full synthetic care coordination demo in one call."""

    safe_case, safety_status = safe_patient_case(patient_case)
    sharp_context_status = validate_sharp_context(safe_case)
    triage_result, risk_result = _triage_and_risk(safe_case)
    care_gaps = detect_care_gaps(safe_case, triage_result, risk_result)
    follow_up_plan = generate_follow_up_plan(safe_case, triage_result, risk_result, care_gaps)
    agent_team_replay = generate_agent_team_replay(safe_case, triage_result, risk_result, care_gaps, follow_up_plan)
    from services.fhir_bundle import export_fhir_bundle

    fhir_bundle = export_fhir_bundle(
        safe_case,
        triage_result,
        risk_result,
        care_gaps=care_gaps,
        follow_up_plan=follow_up_plan,
        care_brief={
            "doctor_handoff_brief": (
                "Synthetic clinician-support handoff: review the triage, risk, and care gaps before any real-world action."
            ),
            "recommended_next_steps": follow_up_plan["clinician_actions"],
        },
        generated_by="run_full_care_journey",
        audit_trace_id=agent_team_replay["replay_id"],
    )
    audit_trace = generate_audit_trace(
        safe_case,
        safety_status=safety_status,
        sharp_context_status=sharp_context_status,
        triage_result=triage_result,
        risk_result=risk_result,
        care_gaps=care_gaps,
        follow_up_plan=follow_up_plan,
        fhir_bundle=fhir_bundle,
    )

    return {
        "tool_name": "run_full_care_journey",
        "request_id": stable_trace_id("journey", safe_case),
        "synthetic_patient_snapshot": _case_snapshot(safe_case),
        "safety_status": safety_status,
        "sharp_context_status": sharp_context_status,
        "triage_result": triage_result,
        "risk_assessment": risk_result,
        "care_gaps": care_gaps,
        "follow_up_plan": follow_up_plan,
        "doctor_handoff_brief": (
            "Synthetic clinician-support handoff: review the triage, risk, and care gaps before any real-world action."
        ),
        "patient_friendly_summary": (
            "This synthetic workflow organizes a care team handoff for a demo case. "
            "It does not diagnose, treat, or prescribe, and a clinician should review the result."
        ),
        "fhir_resources_generated": [entry["resource"]["resourceType"] for entry in fhir_bundle["entry"]],
        "fhir_bundle": fhir_bundle,
        "agent_team_replay": agent_team_replay,
        "audit_trace": audit_trace,
        "disclaimers": [
            DEFAULT_DISCLAIMER,
            "Clinician review required before any real-world action.",
            "Synthetic data only; no real PHI is processed.",
        ],
        "synthetic_data_notice": safe_case.get("synthetic_data_notice", DEFAULT_SYNTHETIC_NOTICE),
        "requires_clinician_review": True,
    }
