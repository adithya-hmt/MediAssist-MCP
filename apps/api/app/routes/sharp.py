from fastapi import APIRouter
from app.models import SharpContextIn
from services.sharp_context import validate_sharp_context
router = APIRouter(prefix="/api/sharp", tags=["sharp"])

@router.post("/validate")
def validate(body: SharpContextIn):
    return validate_sharp_context(body.model_dump())
