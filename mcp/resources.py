import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

SYNTHETIC_PATIENT = {
    "patient_id": "synthetic-patient-001",
    "encounter_id": "synthetic-encounter-001",
    "name": "Demo Patient",
    "source": "synthetic-demo",
    "synthetic_only": True,
    "age": 42,
    "sex": "not specified",
    "symptoms": ["persistent cough", "mild fever", "fatigue"],
    "observations": {"temperature_c": 38.1, "heart_rate": 92, "spo2": 97, "respiratory_rate": 18},
    "history": ["synthetic asthma history"],
    "medications": ["synthetic inhaler record"],
    "notes": "Synthetic demo case for workflow testing only.",
}

RESOURCES = [
    {
        "uri": "synthetic://patient/demo",
        "name": "Synthetic Demo Patient",
        "description": "A fully synthetic patient case for workflow demonstration. No real PHI.",
        "mimeType": "application/json",
        "content": json.dumps(SYNTHETIC_PATIENT, indent=2),
    },
    {
        "uri": "synthetic://encounter/demo",
        "name": "Synthetic Demo Encounter",
        "description": "A synthetic encounter record for workflow demonstration.",
        "mimeType": "application/json",
        "content": json.dumps({
            "encounter_id": "synthetic-encounter-001",
            "patient_id": "synthetic-patient-001",
            "type": "outpatient",
            "status": "finished",
            "source": "synthetic-demo",
            "notes": "Synthetic demo encounter only.",
        }, indent=2),
    },
    {
        "uri": "synthetic://policy/phi-safety",
        "name": "PHI Safety Policy",
        "description": "Policy document describing PHI safety checks and synthetic-only constraints.",
        "mimeType": "text/plain",
        "content": (
            "PHI Safety Policy\n"
            "=================\n"
            "1. Only synthetic data is processed in this demo.\n"
            "2. Real PHI (emails, phone numbers, IDs) is detected and blocked.\n"
            "3. All outputs are for demonstration purposes only.\n"
            "4. Clinician review is required before any clinical action.\n"
            "5. No external calls are made unless explicitly enabled.\n"
        ),
    },
    {
        "uri": "synthetic://sharp/context-template",
        "name": "SHARP Context Template",
        "description": "Template for a valid SHARP context for synthetic demo workflows.",
        "mimeType": "application/json",
        "content": json.dumps({
            "patient_id": "synthetic-patient-001",
            "encounter_id": "synthetic-encounter-001",
            "user_role": "clinician",
            "scopes": ["summarize", "triage_support", "generate_handoff", "create_follow_up_plan", "export_synthetic_fhir_bundle"],
            "source": "synthetic-demo",
        }, indent=2),
    },
]
