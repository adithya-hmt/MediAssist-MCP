"""Offline regression tests for the synthetic healthcare workflows."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from integrations import ollama_optional
from services.healthcare import (
    appointment_scheduler_logic,
    bmi_calculator_logic,
    emergency_triage_logic,
    medicine_info_logic,
    symptom_checker_logic,
)


class OfflineWorkflowTests(unittest.TestCase):
    def test_core_workflows_return_local_synthetic_outputs(self) -> None:
        symptom = symptom_checker_logic("fever")
        triage = emergency_triage_logic("chest pain and shortness of breath")
        bmi = bmi_calculator_logic(72, 175)
        medicine = medicine_info_logic("ibuprofen")

        self.assertEqual(symptom["confidence_score"], 0.92)
        self.assertEqual(triage["urgency_level"], "critical")
        self.assertEqual(bmi["bmi"], 23.5)
        self.assertEqual(medicine["medicine_name"], "Ibuprofen")
        self.assertIn("does not diagnose", symptom["safety_note"])
        self.assertIn("does not provide dosing instructions", medicine["dosage"])

    def test_appointments_are_deterministic_without_storage(self) -> None:
        first = appointment_scheduler_logic("Aanya Patel", "2026-05-11")
        second = appointment_scheduler_logic("Aanya Patel", "2026-05-11")

        self.assertEqual(first["confirmation_id"], second["confirmation_id"])
        self.assertEqual(first["status"], "confirmed")
        self.assertIn("synthetic", first["message"])

    def test_disabled_ollama_helper_does_not_call_network(self) -> None:
        with patch.dict(os.environ, {"OLLAMA_ENABLED": "false"}), patch(
            "integrations.ollama_optional.urlopen"
        ) as urlopen:
            result = ollama_optional.summarize_with_ollama("demo prompt")

        urlopen.assert_not_called()
        self.assertIn("fully local and synthetic", result["summary"])


if __name__ == "__main__":
    unittest.main()
