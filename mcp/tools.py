import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.privacy import phi_safety_check, assert_synthetic_patient_case
from services.sharp_context import validate_sharp_context
from services.care_brief import generate_care_brief
from services.care_gaps import detect_care_gaps
from services.follow_up import generate_follow_up_plan
from services.fhir_export import export_fhir_bundle
from services.audit_trace import generate_audit_trace
from services.agent_replay import generate_agent_team_replay
from services.care_journey import run_full_care_journey
from services.gemini_provider import gemini_readiness_status

TOOL_REGISTRY = {
    "phi_safety_check": phi_safety_check,
    "validate_sharp_context": validate_sharp_context,
    "generate_care_brief": generate_care_brief,
    "detect_care_gaps": detect_care_gaps,
    "generate_follow_up_plan": generate_follow_up_plan,
    "export_fhir_bundle": export_fhir_bundle,
    "generate_audit_trace": generate_audit_trace,
    "generate_agent_team_replay": generate_agent_team_replay,
    "run_full_care_journey": run_full_care_journey,
    "check_gemini_readiness": lambda: gemini_readiness_status(),
}
