"""Audit trace generation for deterministic synthetic workflows."""

from __future__ import annotations

from typing import Any

from services.workflow_primitives import case_input_keys, stable_trace_id, utc_timestamp


def _resource_types(bundle: dict[str, Any] | None) -> list[str]:
    if not bundle:
        return []
    resources: list[str] = []
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")
        if resource_type and resource_type not in resources:
            resources.append(resource_type)
    return resources


def generate_audit_trace(workflow_result: dict[str, Any]) -> dict[str, Any]:
    """Return a redacted audit trace for a workflow artifact."""

    patient_case = workflow_result.get("patient_case", {})
    bundle = workflow_result.get("fhir_bundle", {})
    trace_source = {
        "case_id": workflow_result.get("case_id") or patient_case.get("case_id"),
        "workflow_steps": workflow_result.get("workflow_steps", []),
        "ai_provider_status": workflow_result.get("ai_provider_status"),
        "bundle_count": len(bundle.get("entry", [])) if isinstance(bundle, dict) else 0,
    }
    trace_id = workflow_result.get("trace_id") or stable_trace_id("trace", trace_source)

    return {
        "tool_name": "generate_audit_trace",
        "trace_id": trace_id,
        "timestamp": utc_timestamp(),
        "tools_called": list(workflow_result.get("workflow_steps", [])),
        "inputs_used": case_input_keys(patient_case),
        "synthetic_only_status": workflow_result.get("synthetic_only_status", "synthetic_only_confirmed"),
        "phi_safety_status": workflow_result.get("phi_safety_check", {}).get("status", "unknown"),
        "ai_provider_used": bool(workflow_result.get("ai_provider_used", False)),
        "ai_provider_status": workflow_result.get("ai_provider_status", "local_only"),
        "fhir_resources_generated": _resource_types(bundle),
        "disclaimer": workflow_result.get(
            "disclaimer",
            "Synthetic demo output only. This does not diagnose, treat, replace professional care, or process PHI.",
        ),
    }
