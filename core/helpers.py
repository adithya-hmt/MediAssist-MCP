"""Reusable helper functions for safe, beginner-friendly logic."""

from __future__ import annotations

from datetime import date, datetime
from math import pow

from .errors import InputValidationError


def normalize_text(value: str) -> str:
    """Normalize user-entered text for matching and comparisons."""

    if not isinstance(value, str):
        raise InputValidationError("Expected a text value.")
    cleaned = value.strip()
    if not cleaned:
        raise InputValidationError("Input cannot be empty.")
    return cleaned


def parse_bool(value: bool | str | int) -> bool:
    """Convert common truthy inputs into a real boolean."""

    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "y", "1"}:
            return True
        if lowered in {"false", "no", "n", "0"}:
            return False
    raise InputValidationError("Expected a boolean-like value.")


def normalize_date(value: str | date) -> date:
    """Parse a date input into a date object."""

    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise InputValidationError("Date must be a string in YYYY-MM-DD format.")
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise InputValidationError("Date must use YYYY-MM-DD format.") from exc


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from kilograms and centimeters."""

    if weight_kg <= 0:
        raise InputValidationError("Weight must be greater than zero.")
    if height_cm <= 0:
        raise InputValidationError("Height must be greater than zero.")
    height_m = height_cm / 100.0
    return round(weight_kg / pow(height_m, 2), 1)


def bmi_category(bmi: float) -> str:
    """Map a BMI number to a readable category."""

    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "healthy"
    if bmi < 30:
        return "overweight"
    return "obese"

