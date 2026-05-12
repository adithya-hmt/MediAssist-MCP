from fastapi import APIRouter

from apps.api.services.demo_case import get_synthetic_patient_case
from apps.api.services.persistence import save_case

router = APIRouter()


@router.get("")
def list_cases():
    case = get_synthetic_patient_case()
    save_case(case)
    return {"items": [case]}
