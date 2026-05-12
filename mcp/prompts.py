PROMPTS = [
    {
        "name": "run_care_journey",
        "description": "Run a full synthetic care journey for a demo patient case.",
        "template": (
            "You are a healthcare coordination assistant. Use the run_full_care_journey tool "
            "with the synthetic demo patient from synthetic://patient/demo. "
            "Present the key findings: safety status, triage level, care gaps, and follow-up plan. "
            "Always remind the user this is a synthetic demo only and not medical advice."
        ),
    },
    {
        "name": "check_phi_safety",
        "description": "Check a text snippet for PHI patterns using the safety checker.",
        "template": (
            "Use the phi_safety_check tool to check the following text for PHI patterns. "
            "Report whether any sensitive data was detected and what was redacted. "
            "Text: {{text}}"
        ),
    },
    {
        "name": "validate_context",
        "description": "Validate a SHARP context dict for required fields and allowed actions.",
        "template": (
            "Use the validate_sharp_context tool to validate this context: {{context}}. "
            "Report any missing fields, and list the allowed and blocked actions."
        ),
    },
    {
        "name": "generate_fhir_bundle",
        "description": "Generate a synthetic FHIR bundle from a patient case.",
        "template": (
            "Use the export_fhir_bundle tool with the synthetic demo patient. "
            "List all FHIR resource types in the bundle. "
            "Remind the user this is a demo FHIR mapping only, not certified clinical FHIR."
        ),
    },
    {
        "name": "explain_agent_replay",
        "description": "Generate and explain the agent team replay for the demo case.",
        "template": (
            "Use the generate_agent_team_replay tool with the synthetic demo patient. "
            "Walk through each agent step: what it did, its output, and who it handed off to. "
            "Explain how this demonstrates a multi-agent healthcare coordination workflow."
        ),
    },
]
