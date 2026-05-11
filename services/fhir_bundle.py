"""Synthetic FHIR-style bundle export helpers."""

from __future__ import annotations

from typing import Any

from services.workflow_primitives import normalize_patient_case, stable_trace_id, utc_timestamp
from services.workflow_primitives import DEFAULT_DISCLAIMER, DEFAULT_SYNTHETIC_NOTICE


def _resource_id(case_id: str, suffix: str) -> str:
    return stable_trace_id(f"{case_id}-{suffix}", {"case_id": case_id, "suffix": suffix})


def _observation(case_id: str, suffix: str, title: str, value: Any) -> dict[str, Any]:
    return {
        "resourceType": "Observation",
        "id": _resource_id(case_id, suffix),
        "status": "final",
        "code": {"text": title},
        "valueString": str(value),
    }


def export_fhir_bundle(
    patient_case: dict[str, Any],
    triage_result: dict[str, Any],
    risk_result: dict[str, Any],
    care_gaps: dict[str, Any] | None = None,
    follow_up_plan: dict[str, Any] | None = None,
    care_brief: dict[str, Any] | None = None,
    generated_by: str = "export_fhir_bundle",
    audit_trace_id: str | None = None,
) -> dict[str, Any]:
    """Create a deterministic synthetic FHIR-style bundle."""

    case = normalize_patient_case(patient_case)
    case_id = str(case["case_id"])
    bundle_timestamp = utc_timestamp()
    current_medications = list(case.get("current_medications", []))
    resource_entries: list[dict[str, Any]] = []

    patient_resource = {
        "resourceType": "Patient",
        "id": case_id,
        "name": [{"text": case.get("case_label", case_id)}],
        "meta": {"tag": [{"code": "synthetic-demo"}]},
    }
    resource_entries.append({"resource": patient_resource})

    resource_entries.append(
        {
            "resource": {
                "resourceType": "Encounter",
                "id": _resource_id(case_id, "encounter"),
                "status": "finished",
                "class": {"code": "AMB", "display": "ambulatory", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
                "subject": {"reference": f"Patient/{case_id}"},
                "reasonCode": [{"text": case.get("primary_symptom", "synthetic symptom context")}],
            }
        }
    )

    resource_entries.append({"resource": _observation(case_id, "triage", "Synthetic triage level", triage_result["urgency_level"])})
    resource_entries.append({"resource": _observation(case_id, "risk", "Synthetic risk level", risk_result["risk_level"])})
    resource_entries.append(
        {
            "resource": {
                "resourceType": "Condition",
                "id": _resource_id(case_id, "condition"),
                "clinicalStatus": {"text": "active"},
                "verificationStatus": {"text": "confirmed"},
                "code": {
                    "text": case.get("condition_context", case.get("primary_symptom", "synthetic condition context"))
                },
                "subject": {"reference": f"Patient/{case_id}"},
            }
        }
    )

    if care_gaps:
        resource_entries.append(
            {
                "resource": _observation(
                    case_id,
                    "care-gaps",
                    "Synthetic care gaps count",
                    len(care_gaps.get("care_gaps", [])),
                )
            }
        )

    if current_medications:
        resource_entries.append(
            {
                "resource": {
                    "resourceType": "MedicationRequest",
                    "id": _resource_id(case_id, "medication-request"),
                    "status": "draft",
                    "intent": "plan",
                    "subject": {"reference": f"Patient/{case_id}"},
                    "medicationCodeableConcept": {"text": ", ".join(current_medications)},
                    "reasonCode": [{"text": "synthetic medication reconciliation review"}],
                    "note": [
                        {
                            "text": "Synthetic medication review placeholder only. No prescribing guidance is provided.",
                        }
                    ],
                }
            }
        )

    if follow_up_plan:
        resource_entries.append(
            {
                "resource": {
                    "resourceType": "Appointment",
                    "id": _resource_id(case_id, "appointment"),
                    "status": "proposed",
                    "description": follow_up_plan.get("recommended_follow_up_type", "synthetic follow-up"),
                    "reasonCode": [{"text": "synthetic follow-up coordination"}],
                    "subject": {"reference": f"Patient/{case_id}"},
                }
            }
        )

    care_plan_notes = []
    if care_brief:
        care_plan_notes.append(care_brief.get("doctor_handoff_brief", "Synthetic handoff summary unavailable."))
    if follow_up_plan:
        care_plan_notes.extend(follow_up_plan.get("preparation_notes", []))
    if care_gaps:
        care_plan_notes.extend(gap.get("suggested_action", "") for gap in care_gaps.get("care_gaps", []))

    resource_entries.append(
        {
            "resource": {
                "resourceType": "CarePlan",
                "id": _resource_id(case_id, "care-plan"),
                "status": "active",
                "intent": "plan",
                "title": "Synthetic care coordination plan",
                "subject": {"reference": f"Patient/{case_id}"},
                "description": "Deterministic care coordination plan for a synthetic demo case.",
                "activity": [
                    {"detail": {"kind": "ServiceRequest", "code": {"text": step}}}
                    for step in (
                        care_brief.get("recommended_next_steps", []) if care_brief else []
                    )
                ],
                "note": [{"text": note} for note in care_plan_notes if note],
            }
        }
    )

    provenance_agents = [
        {"type": {"text": "software"}, "who": {"display": "MediAssist-MCP"}},
        {"type": {"text": "workflow"}, "who": {"display": generated_by}},
    ]
    if audit_trace_id:
        provenance_agents.append({"type": {"text": "trace"}, "who": {"display": audit_trace_id}})

    resource_entries.append(
        {
            "resource": {
                "resourceType": "Provenance",
                "id": _resource_id(case_id, "provenance"),
                "recorded": bundle_timestamp,
                "target": [{"reference": f"Patient/{case_id}"}],
                "agent": provenance_agents,
                "reason": [{"text": "synthetic demo generation"}],
            }
        }
    )

    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "case_id": case_id,
        "case_label": case.get("case_label"),
        "generated_by": generated_by,
        "timestamp": bundle_timestamp,
        "synthetic_only": True,
        "contains_phi": False,
        "demo_use_only": True,
        "synthetic_data_notice": case.get("synthetic_data_notice", DEFAULT_SYNTHETIC_NOTICE),
        "disclaimer": DEFAULT_DISCLAIMER,
        "entry": resource_entries,
        "meta": {"tag": [{"code": "synthetic-demo"}]},
    }
    if care_brief and care_brief.get("ai_provider"):
        bundle["ai_provider"] = care_brief.get("ai_provider")
        bundle["ai_provider_status"] = care_brief.get("ai_provider_status")
    return bundle
