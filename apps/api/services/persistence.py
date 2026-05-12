from __future__ import annotations

from apps.api.db import SessionLocal, init_db
from apps.api.models_db import CaseRecord, WorkflowRun, AuditRecord

init_db()

def save_case(case: dict) -> None:
    case_id = case.get("case_id") or case.get("patient_id") or "synthetic-case"
    with SessionLocal() as session:
        existing = session.query(CaseRecord).filter_by(case_id=case_id).one_or_none()
        if existing is None:
            session.add(CaseRecord(case_id=case_id, payload=case))
        else:
            existing.payload = case
        session.commit()

def _upsert_unique(session, model, lookup_field: str, lookup_value: str, create_kwargs: dict):
    existing = session.query(model).filter(getattr(model, lookup_field) == lookup_value).one_or_none()
    if existing is None:
        session.add(model(**create_kwargs))
        session.flush()
    else:
        for k, v in create_kwargs.items():
            setattr(existing, k, v)
        session.flush()

def save_run(payload: dict) -> None:
    with SessionLocal() as session:
        existing = session.query(WorkflowRun).filter_by(request_id=payload["request_id"]).one_or_none()
        if existing is None:
            session.add(WorkflowRun(request_id=payload["request_id"], workflow_name=payload.get("tool_name", "workflow"), payload=payload, synthetic_only=True))
        else:
            existing.workflow_name = payload.get("tool_name", "workflow")
            existing.payload = payload
            existing.synthetic_only = True
        session.commit()

def save_audit(payload: dict) -> None:
    with SessionLocal() as session:
        existing = session.query(AuditRecord).filter_by(request_id=payload["request_id"]).one_or_none()
        if existing is None:
            session.add(AuditRecord(request_id=payload["request_id"], event_type=payload.get("event_type", "audit"), details=payload))
        else:
            existing.event_type = payload.get("event_type", "audit")
            existing.details = payload
        session.commit()
