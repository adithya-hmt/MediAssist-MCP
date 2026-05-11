"""Pure, local healthcare workflows for MediAssist-MCP.

These functions intentionally avoid paid APIs and real patient data.
The MCP server and the Streamlit frontend both use the same logic so the
hackathon demo stays consistent and easy to maintain.
"""

from __future__ import annotations

import re
from datetime import date
from hashlib import sha1
from typing import Any

from core.errors import InputValidationError
from core.helpers import bmi_category, calculate_bmi, normalize_date, normalize_text, parse_bool
from core.repository import find_medicine_record, find_mood_record, find_nutrition_record, load_healthcare_data


DEMO_SAFETY_NOTE = (
    "Synthetic demo output only. This does not diagnose, treat, replace professional care, or process PHI."
)


def _with_safety_note(payload: dict[str, Any]) -> dict[str, Any]:
    """Attach the offline demo safety note to frontend-visible local outputs."""

    return {**payload, "safety_note": DEMO_SAFETY_NOTE}


def _tokenize(text: str) -> set[str]:
    """Split text into simple lowercase tokens for keyword matching."""

    return set(re.findall(r"[a-z0-9']+", text.lower()))


def _default_symptom_response() -> dict[str, Any]:
    """Return the fallback symptom checker response."""

    data = load_healthcare_data()
    default = data["symptom_default"]
    return _with_safety_note({
        "possible_conditions": default["possible_conditions"],
        "confidence_score": default["confidence"],
        "recommendation": default["recommendation"],
        "red_flags": default["red_flags"],
    })


def symptom_checker_logic(symptom: str) -> dict[str, Any]:
    """Do a simple local symptom-to-condition lookup."""

    cleaned_symptom = normalize_text(symptom).lower()
    tokens = _tokenize(cleaned_symptom)
    data = load_healthcare_data()

    best_key = None
    best_score = 0.0

    for key, profile in data["symptoms"].items():
        keywords = set(profile.get("keywords", []))
        overlap = len(tokens & keywords)
        score = 0.0

        # Direct phrase matches are stronger than loose token overlap.
        if key in cleaned_symptom:
            score = profile.get("confidence", 0.8)
        elif overlap:
            score = min(0.45 + overlap * 0.12, profile.get("confidence", 0.8))

        if score > best_score:
            best_key = key
            best_score = score

    if best_key is None or best_score <= 0:
        return _default_symptom_response()

    profile = data["symptoms"][best_key]
    confidence = round(max(best_score, profile.get("confidence", 0.8)), 2)
    return _with_safety_note({
        "possible_conditions": profile["possible_conditions"],
        "confidence_score": confidence,
        "recommendation": profile["recommendation"],
        "red_flags": profile["red_flags"],
    })


def emergency_triage_logic(symptoms: str) -> dict[str, Any]:
    """Categorize urgency using a tiny keyword-matching triage model."""

    cleaned = normalize_text(symptoms).lower()
    data = load_healthcare_data()
    triage_rules = data["triage"]

    critical_matches = [term for term in triage_rules["critical"] if term in cleaned]
    medium_matches = [term for term in triage_rules["medium"] if term in cleaned]
    low_matches = [term for term in triage_rules["low"] if term in cleaned]

    if critical_matches:
        return _with_safety_note({
            "urgency_level": "critical",
            "matched_keywords": critical_matches,
            "reasoning": [
                "One or more critical keywords matched the symptom description.",
                "This pattern should be treated as an emergency in a real-world scenario.",
            ],
            "recommended_action": [
                "Seek emergency care now.",
                "Call local emergency services if this is happening outside the demo.",
            ],
        })

    if medium_matches:
        return _with_safety_note({
            "urgency_level": "medium",
            "matched_keywords": medium_matches,
            "reasoning": [
                "A medium-risk keyword matched the symptom description.",
                "Prompt clinical advice would be reasonable if this were a real case.",
            ],
            "recommended_action": [
                "Arrange prompt medical advice.",
                "Watch for worsening or new red-flag symptoms.",
            ],
        })

    if low_matches:
        return _with_safety_note({
            "urgency_level": "low",
            "matched_keywords": low_matches,
            "reasoning": [
                "Only low-risk patterns matched the symptom description.",
                "Supportive care and observation are reasonable for a mild demo scenario.",
            ],
            "recommended_action": [
                "Monitor symptoms and rest.",
                "Escalate if the symptoms change or intensify.",
            ],
        })

    return _with_safety_note({
        "urgency_level": "low",
        "matched_keywords": [],
        "reasoning": [
            "No high-risk triage keyword matched.",
            "The symptom pattern looks low urgency for a synthetic demo.",
        ],
        "recommended_action": [
            "Use supportive care and observe for changes.",
            "Ask a clinician if symptoms persist or become more concerning.",
        ],
    })


def bmi_calculator_logic(weight: float, height: float) -> dict[str, Any]:
    """Calculate BMI and return a friendly interpretation."""

    bmi_value = calculate_bmi(weight, height)
    category = bmi_category(bmi_value)

    advice_map = {
        "underweight": [
            "Focus on regular meals with nutrient-dense foods.",
            "Check in with a clinician if the pattern persists.",
        ],
        "healthy": [
            "Keep up balanced meals and steady movement.",
            "Maintain the habits that are working for you now.",
        ],
        "overweight": [
            "Aim for gradual changes that are easy to repeat.",
            "Build meals around protein, fiber, and portion awareness.",
        ],
        "obese": [
            "Start with small sustainable goals and support if available.",
            "Even modest changes can improve health markers over time.",
        ],
    }

    return _with_safety_note({
        "weight_kg": float(weight),
        "height_cm": float(height),
        "bmi": bmi_value,
        "category": category,
        "health_advice": advice_map[category],
    })


def medicine_info_logic(medicine_name: str) -> dict[str, Any]:
    """Look up a medicine in the local synthetic JSON data."""

    cleaned_name = normalize_text(medicine_name)
    record = find_medicine_record(cleaned_name)

    if record is None:
        return _with_safety_note({
            "medicine_name": cleaned_name,
            "usage": "No exact synthetic match was found, so this is general medicine guidance.",
            "dosage": "This offline demo does not provide dosing instructions.",
            "warnings": [
                "Check for allergies before taking any medicine.",
                "Read the label carefully and avoid doubling ingredients.",
            ],
        })

    return _with_safety_note({
        "medicine_name": record["display_name"],
        "usage": record["usage"],
        "dosage": record["dosage"],
        "warnings": record["warnings"],
    })


def nutrition_recommendation_logic(condition: str) -> dict[str, Any]:
    """Return diet suggestions for a condition using the local dataset."""

    cleaned = normalize_text(condition)
    record = find_nutrition_record(cleaned)

    if record is None:
        return _with_safety_note({
            "condition": cleaned,
            "diet_suggestions": [
                "Build meals around vegetables, fruit, whole grains, and lean protein.",
                "Keep hydration steady throughout the day.",
                "Favor simple meals when symptoms are unsettled.",
            ],
            "foods_to_include": ["vegetables", "fruit", "whole grains", "lean protein"],
            "foods_to_limit": ["very salty food", "sugary drinks", "ultra-processed snacks"],
            "hydration_tips": ["Drink water regularly.", "Adjust fluids to your activity level and climate."],
        })

    return _with_safety_note({
        "condition": cleaned,
        "diet_suggestions": record["diet_suggestions"],
        "foods_to_include": record["foods_to_include"],
        "foods_to_limit": record["foods_to_limit"],
        "hydration_tips": record["hydration_tips"],
    })


def appointment_scheduler_logic(name: str, appointment_date: str | date) -> dict[str, Any]:
    """Create a fake but polished appointment confirmation."""

    cleaned_name = normalize_text(name)
    normalized_date = normalize_date(appointment_date)
    data = load_healthcare_data()
    clinic_name = data["appointments"]["clinic_name"]

    # Stable confirmation IDs make the demo feel realistic without storing any state.
    confirmation_seed = sha1(f"{cleaned_name}|{normalized_date.isoformat()}".encode("utf-8")).hexdigest()[:8].upper()
    confirmation_id = f"MA-{normalized_date.strftime('%Y%m%d')}-{confirmation_seed}"

    return _with_safety_note({
        "confirmation_id": confirmation_id,
        "name": cleaned_name,
        "appointment_date": normalized_date.isoformat(),
        "clinic_name": clinic_name,
        "status": "confirmed",
        "message": "This is a synthetic confirmation for demo and testing only.",
    })


def mental_health_support_logic(mood: str) -> dict[str, Any]:
    """Return encouraging wellness guidance for a mood input."""

    cleaned = normalize_text(mood).lower()
    profile = find_mood_record(cleaned) or find_mood_record("overwhelmed") or load_healthcare_data()["moods"]["overwhelmed"]

    return _with_safety_note({
        "mood": mood,
        "guidance": profile["guidance"],
        "calming_suggestions": profile["calming_suggestions"],
        "crisis_note": (
            "If this reflects a real crisis or self-harm risk, contact local emergency services "
            "or a trusted crisis line immediately."
        ),
    })


def health_risk_assessment_logic(age: int, smoking: bool, diabetes: bool) -> dict[str, Any]:
    """Return a compact synthetic risk assessment."""

    if age < 0:
        raise InputValidationError("Age must be zero or greater.")

    smoking_flag = parse_bool(smoking)
    diabetes_flag = parse_bool(diabetes)
    risk_data = load_healthcare_data()["risk"]

    risk_score = 0
    contributing_factors: list[str] = []

    if age >= 65:
        risk_score += risk_data["age_65_plus"]
        contributing_factors.append("age 65 or older")
    elif age >= 50:
        risk_score += risk_data["age_50_plus"]
        contributing_factors.append("age 50 to 64")
    elif age >= 35:
        risk_score += risk_data["age_35_plus"]
        contributing_factors.append("age 35 to 49")

    if smoking_flag:
        risk_score += risk_data["smoking"]
        contributing_factors.append("smoking history")

    if diabetes_flag:
        risk_score += risk_data["diabetes"]
        contributing_factors.append("diabetes history")

    if risk_score < risk_data["medium_threshold"]:
        risk_level = "low"
        advice = [
            "Keep up with routine health checkups.",
            "Stick with the basics: sleep, movement, hydration, and regular meals.",
        ]
    elif risk_score < risk_data["high_threshold"]:
        risk_level = "medium"
        advice = [
            "Review modifiable risk factors with a clinician.",
            "Use a steady plan for food, movement, and follow-up monitoring.",
        ]
    else:
        risk_level = "high"
        advice = [
            "Consider a clinical review for more personalized prevention steps.",
            "A structured plan can help reduce risk over time.",
        ]

    return _with_safety_note({
        "age": age,
        "smoking": smoking_flag,
        "diabetes": diabetes_flag,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "contributing_factors": contributing_factors or ["no major synthetic risk flags"],
        "advice": advice,
    })
