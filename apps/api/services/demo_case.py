from __future__ import annotations

from datetime import date


def get_synthetic_patient_case() -> dict:
    return {
        "patient_id": "synthetic-patient-001",
        "encounter_id": "synthetic-encounter-001",
        "name": "Avery Carter",
        "age": 42,
        "sex": "female",
        "chief_complaint": "fatigue and mild shortness of breath on exertion",
        "vitals": {"bp": "128/82", "hr": 84, "rr": 16, "temp_c": 36.8, "spo2": 98},
        "history": ["seasonal allergies", "borderline hypertension"],
        "medications": ["multivitamin"],
        "allergies": ["none reported"],
        "last_visit": str(date.today()),
        "source": "synthetic-demo",
    }
