from fastapi import APIRouter
from app.models import PatientCaseIn
from services.gemini_provider import gemini_readiness_status, safe_polish_care_brief
router = APIRouter(prefix="/api/gemini", tags=["gemini"])

@router.get("/readiness")
def gemini_readiness():
    return gemini_readiness_status()

@router.post("/polish")
def gemini_polish(body: PatientCaseIn):
    from services.care_brief import generate_care_brief
    local_brief = generate_care_brief(body.model_dump())
    return safe_polish_care_brief(local_brief, body.model_dump())
