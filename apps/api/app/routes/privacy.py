from fastapi import APIRouter
from app.models import PrivacyCheckIn
from services.privacy import phi_safety_check, assert_synthetic_patient_case
router = APIRouter(prefix="/api/privacy", tags=["privacy"])

@router.post("/check")
def check_privacy(body: PrivacyCheckIn):
    return phi_safety_check(body.text)
