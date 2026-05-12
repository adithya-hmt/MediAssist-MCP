from pydantic import BaseModel
from typing import Any, Optional

class PatientCaseIn(BaseModel):
    patient_id: str
    encounter_id: str
    name: str = "Demo Patient"
    source: str = "synthetic-demo"
    synthetic_only: bool = True
    age: Optional[int] = None
    sex: Optional[str] = None
    symptoms: list[str] = []
    observations: dict[str, Any] = {}
    history: list[str] = []
    medications: list[str] = []
    notes: str = ""

class PrivacyCheckIn(BaseModel):
    text: str

class SharpContextIn(BaseModel):
    patient_id: str = ""
    encounter_id: str = ""
    user_role: str = ""
    scopes: list[str] = []
    source: str = ""
