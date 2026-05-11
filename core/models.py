"""Pydantic response models for all healthcare tools."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class BaseToolResponse(BaseModel):
    """Common envelope for every tool response."""

    success: bool = True
    tool_name: str
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    disclaimer: str = (
        "Synthetic demo output only. This does not diagnose, treat, replace professional care, "
        "or process PHI."
    )


class SymptomCheckerResponse(BaseToolResponse):
    """Response model for symptom checks."""

    tool_name: str = "symptom_checker"
    symptom: str
    possible_conditions: list[str]
    confidence_score: float
    recommendation: str
    red_flags: list[str] = Field(default_factory=list)


class MedicineInfoResponse(BaseToolResponse):
    """Response model for medicine lookups."""

    tool_name: str = "medicine_info"
    medicine_name: str
    usage: str
    dosage: str
    warnings: list[str]


class BmiResponse(BaseToolResponse):
    """Response model for BMI calculations."""

    tool_name: str = "bmi_calculator"
    weight_kg: float
    height_cm: float
    bmi: float
    category: Literal["underweight", "healthy", "overweight", "obese"]
    health_advice: list[str]


class AppointmentResponse(BaseToolResponse):
    """Response model for synthetic appointment scheduling."""

    tool_name: str = "appointment_scheduler"
    confirmation_id: str
    name: str
    appointment_date: date
    clinic_name: str
    status: str
    message: str


class RiskAssessmentResponse(BaseToolResponse):
    """Response model for simple health risk scoring."""

    tool_name: str = "health_risk_assessment"
    age: int
    smoking: bool
    diabetes: bool
    risk_score: int
    risk_level: Literal["low", "medium", "high"]
    contributing_factors: list[str]
    advice: list[str]


class TriageResponse(BaseToolResponse):
    """Response model for emergency triage."""

    tool_name: str = "emergency_triage"
    symptoms: str
    urgency_level: Literal["low", "medium", "critical"]
    matched_keywords: list[str] = Field(default_factory=list)
    reasoning: list[str]
    recommended_action: list[str]


class NutritionResponse(BaseToolResponse):
    """Response model for nutrition guidance."""

    tool_name: str = "nutrition_recommendation"
    condition: str
    diet_suggestions: list[str]
    foods_to_include: list[str]
    foods_to_limit: list[str]
    hydration_tips: list[str]


class MentalHealthResponse(BaseToolResponse):
    """Response model for wellness guidance."""

    tool_name: str = "mental_health_support"
    mood: str
    guidance: list[str]
    calming_suggestions: list[str]
    crisis_note: str
