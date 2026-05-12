import json, os
from fastapi import APIRouter
router = APIRouter(prefix="/api/demo", tags=["demo"])

@router.get("/patient")
def demo_patient():
    p = os.path.join(os.path.dirname(__file__), "../../../../data/synthetic/patient_case.json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {
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
        "notes": "Synthetic demo case for workflow testing only."
    }
