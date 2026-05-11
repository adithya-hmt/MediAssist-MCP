"""Synthetic healthcare data access helpers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "healthcare_data.json"


@lru_cache(maxsize=1)
def load_healthcare_data() -> dict[str, Any]:
    """Load the synthetic data bundle once and cache it in memory."""

    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _matches_name(candidate: str, name: str, aliases: list[str] | None = None) -> bool:
    """Check whether a candidate name or one of its aliases matches the query."""

    normalized = name.strip().lower()
    candidate_normalized = candidate.strip().lower()

    if candidate_normalized == normalized:
        return True

    # Keep the matching flexible enough for demo phrases like "high blood pressure".
    if candidate_normalized in normalized or normalized in candidate_normalized:
        return True

    if aliases:
        alias_pool = {alias.strip().lower() for alias in aliases}
        if normalized in alias_pool:
            return True
        return any(alias in normalized or normalized in alias for alias in alias_pool)

    return False


def find_medicine_record(name: str) -> dict[str, Any] | None:
    """Return a medicine record by normalized name."""

    data = load_healthcare_data()
    medicines = data.get("medicines", {})

    for key, record in medicines.items():
        aliases = record.get("aliases", [])
        if _matches_name(key, name, aliases):
            return {
                "key": key,
                "display_name": record.get("display_name", key.title()),
                **record,
            }

    return None


def find_nutrition_record(condition: str) -> dict[str, Any] | None:
    """Return a nutrition record by normalized condition name."""

    data = load_healthcare_data()
    nutrition = data.get("nutrition", {})

    for key, record in nutrition.items():
        aliases = record.get("aliases", [])
        if _matches_name(key, condition, aliases):
            return {
                "key": key,
                **record,
            }

    return None


def find_mood_record(mood: str) -> dict[str, Any] | None:
    """Return a mood guidance record by normalized mood."""

    data = load_healthcare_data()
    moods = data.get("moods", {})

    for key, record in moods.items():
        aliases = record.get("aliases", [])
        if _matches_name(key, mood, aliases):
            return record

    return moods.get("overwhelmed")


def get_triage_rules() -> dict[str, Any]:
    """Return triage heuristics."""

    return load_healthcare_data().get("triage", {})


def get_symptom_profiles() -> dict[str, Any]:
    """Return symptom profiles and fallback guidance."""

    data = load_healthcare_data()
    return {
        "symptoms": data.get("symptoms", {}),
        "symptom_default": data.get("symptom_default", {}),
    }

