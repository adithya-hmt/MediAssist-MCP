from fastapi import APIRouter
from app.models import PatientCaseIn
from services.fhir_export import export_fhir_bundle
router = APIRouter(prefix="/api/fhir", tags=["fhir"])

@router.post("/export")
def fhir_export(body: PatientCaseIn):
    return export_fhir_bundle(body.model_dump())
