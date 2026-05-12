from fastapi import APIRouter
from app.models import PatientCaseIn
from services.care_brief import generate_care_brief
from services.care_gaps import detect_care_gaps
from services.follow_up import generate_follow_up_plan
from services.care_journey import run_full_care_journey
router = APIRouter(prefix="/api", tags=["workflow"])

@router.post("/care-brief/generate")
def care_brief(body: PatientCaseIn):
    return generate_care_brief(body.model_dump())

@router.post("/care-gaps/detect")
def care_gaps(body: PatientCaseIn):
    return detect_care_gaps(body.model_dump())

@router.post("/follow-up/generate")
def follow_up(body: PatientCaseIn):
    return generate_follow_up_plan(body.model_dump())

@router.post("/care-journey/run")
def care_journey(body: PatientCaseIn):
    return run_full_care_journey(body.model_dump())
