from fastapi import APIRouter
router = APIRouter(prefix="/api/mcp", tags=["mcp"])

TOOLS = [
    {"name": "phi_safety_check", "description": "Check text for PHI patterns and redact", "input": "text: str", "output": "safety report", "demo_relevance": "Privacy gate"},
    {"name": "validate_sharp_context", "description": "Validate SHARP context fields and allowed actions", "input": "context: dict", "output": "validation result", "demo_relevance": "Access control"},
    {"name": "generate_care_brief", "description": "Generate SBAR-format care brief from patient case", "input": "patient_case: dict", "output": "care brief", "demo_relevance": "Clinician handoff"},
    {"name": "detect_care_gaps", "description": "Detect care gaps in patient case", "input": "patient_case: dict", "output": "gaps list", "demo_relevance": "Quality improvement"},
    {"name": "generate_follow_up_plan", "description": "Generate follow-up plan", "input": "patient_case: dict", "output": "follow-up plan", "demo_relevance": "Care continuity"},
    {"name": "export_fhir_bundle", "description": "Export FHIR-style bundle from patient case", "input": "patient_case: dict", "output": "FHIR bundle", "demo_relevance": "Interoperability"},
    {"name": "generate_audit_trace", "description": "Generate audit trace for workflow result", "input": "workflow_result: dict", "output": "audit trace", "demo_relevance": "Compliance"},
    {"name": "generate_agent_team_replay", "description": "Generate deterministic agent team replay", "input": "patient_case: dict", "output": "agent replay", "demo_relevance": "Transparency"},
    {"name": "run_full_care_journey", "description": "Run complete care journey pipeline", "input": "patient_case: dict", "output": "full journey result", "demo_relevance": "End-to-end demo"},
    {"name": "check_gemini_readiness", "description": "Check if Gemini is configured and ready", "input": "none", "output": "readiness status", "demo_relevance": "AI provider status"},
]

@router.get("/tools")
def mcp_tools():
    return {"tools": TOOLS, "count": len(TOOLS)}
