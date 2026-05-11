"""Simple Streamlit frontend for MediAssist-MCP.

The UI is intentionally plain and fast to demo.
It uses the same pure local logic as the MCP tools, which keeps the server and
the frontend aligned without extra moving parts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st


# Make sure the project root is importable when Streamlit starts this file.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.healthcare import (  # noqa: E402
    appointment_scheduler_logic,
    bmi_calculator_logic,
    emergency_triage_logic,
    health_risk_assessment_logic,
    mental_health_support_logic,
    medicine_info_logic,
    nutrition_recommendation_logic,
    symptom_checker_logic,
)
from services.gemini_provider import gemini_readiness_status  # noqa: E402


st.set_page_config(page_title="MediAssist-MCP", page_icon="🏥", layout="wide")


st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; }
      .hero {
        background: linear-gradient(135deg, #0f766e 0%, #14532d 100%);
        color: white;
        border-radius: 18px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 1rem;
      }
      .subtle {
        color: #475569;
        font-size: 0.95rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


TOOL_OPTIONS = [
    "Symptom checker",
    "Emergency triage",
    "BMI calculator",
    "Medicine info",
    "Nutrition recommendation",
    "Appointment scheduler",
    "Mental health support",
    "Health risk assessment",
]


def render_json_result(title: str, payload: dict[str, object]) -> None:
    """Show a clean result block with a JSON payload and download option."""

    st.subheader(title)
    st.json(payload)
    st.download_button(
        label="Download JSON",
        data=json.dumps(payload, indent=2),
        file_name=f"{title.lower().replace(' ', '_')}.json",
        mime="application/json",
    )


def render_home() -> None:
    """Render the landing area for the Streamlit demo."""

    st.markdown(
        """
        <div class="hero">
          <h1 style="margin:0;">MediAssist-MCP</h1>
          <p style="margin:0.35rem 0 0 0;">
            A synthetic-only healthcare MCP demo for hackathon judges, built to be simple, fast, and local.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns(3)
    left.metric("MCP Tools", "10")
    middle.metric("Data Mode", "Synthetic")
    right.metric("Paid APIs", "None")

    st.markdown(
        """
        <div class="subtle">
        Pick a tool in the sidebar, enter a sample input, and test the healthcare workflow visually.
        The same logic powers the MCP server, so the demo stays consistent for inspectors and judges.
        </div>
        """,
        unsafe_allow_html=True,
    )


def symptom_page() -> None:
    """Render the symptom checker demo."""

    st.subheader("Symptom checker")
    with st.form("symptom_form"):
        symptom = st.text_input("Symptom", value="fever")
        submitted = st.form_submit_button("Run symptom checker")

    if submitted:
        result = symptom_checker_logic(symptom)
        render_json_result("Symptom checker result", result)


def triage_page() -> None:
    """Render the emergency triage demo."""

    st.subheader("Emergency triage")
    with st.form("triage_form"):
        symptoms = st.text_area("Symptoms", value="chest pain and shortness of breath")
        submitted = st.form_submit_button("Run triage")

    if submitted:
        result = emergency_triage_logic(symptoms)
        render_json_result("Emergency triage result", result)


def bmi_page() -> None:
    """Render the BMI calculator demo."""

    st.subheader("BMI calculator")
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=1.0, value=72.0, step=0.5)
    with col2:
        height = st.number_input("Height (cm)", min_value=1.0, value=175.0, step=1.0)

    if st.button("Calculate BMI"):
        result = bmi_calculator_logic(weight, height)
        render_json_result("BMI result", result)


def medicine_page() -> None:
    """Render the medicine info demo."""

    st.subheader("Medicine info")
    with st.form("medicine_form"):
        medicine_name = st.text_input("Medicine name", value="ibuprofen")
        submitted = st.form_submit_button("Look up medicine")

    if submitted:
        result = medicine_info_logic(medicine_name)
        render_json_result("Medicine result", result)


def nutrition_page() -> None:
    """Render the nutrition recommendation demo."""

    st.subheader("Nutrition recommendation")
    with st.form("nutrition_form"):
        condition = st.text_input("Condition", value="diabetes")
        submitted = st.form_submit_button("Get nutrition suggestions")

    if submitted:
        result = nutrition_recommendation_logic(condition)
        render_json_result("Nutrition result", result)


def appointment_page() -> None:
    """Render the fake appointment demo."""

    st.subheader("Appointment scheduler")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", value="Aanya Patel")
    with col2:
        appointment_date = st.date_input("Date")

    if st.button("Create fake confirmation"):
        result = appointment_scheduler_logic(name, appointment_date)
        render_json_result("Appointment result", result)


def mental_health_page() -> None:
    """Render the mental health support demo."""

    st.subheader("Mental health support")
    with st.form("mental_form"):
        mood = st.text_input("Mood", value="stressed")
        submitted = st.form_submit_button("Get wellness guidance")

    if submitted:
        result = mental_health_support_logic(mood)
        render_json_result("Mental health result", result)


def risk_page() -> None:
    """Render the health risk assessment demo."""

    st.subheader("Health risk assessment")
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=46, step=1)
    with col2:
        smoking = st.selectbox("Smoking", [False, True], index=0)
    with col3:
        diabetes = st.selectbox("Diabetes", [False, True], index=1)

    if st.button("Assess risk"):
        result = health_risk_assessment_logic(int(age), smoking, diabetes)
        render_json_result("Risk result", result)


PAGE_RENDERERS = {
    "Symptom checker": symptom_page,
    "Emergency triage": triage_page,
    "BMI calculator": bmi_page,
    "Medicine info": medicine_page,
    "Nutrition recommendation": nutrition_page,
    "Appointment scheduler": appointment_page,
    "Mental health support": mental_health_page,
    "Health risk assessment": risk_page,
}


def render_gemini_status() -> None:
    """Render public-safe Gemini status without exposing any key details."""

    status = gemini_readiness_status()
    with st.sidebar.expander("Gemini status", expanded=False):
        st.write(f"Gemini enabled: {'yes' if status['gemini_enabled'] else 'no'}")
        st.write(f"Gemini configured: {'yes' if status['gemini_configured'] else 'no'}")
        st.write(f"Model mode: {status['model_mode']}")
        st.write(f"Default model: {status['default_model']}")
        st.write(f"Advanced model: {status['advanced_model']}")
        st.write(f"External calls allowed: {'yes' if status['allow_synthetic_external_calls'] else 'no'}")
        st.write(f"Public demo mode: {'yes' if status['public_demo_mode'] else 'no'}")


st.sidebar.title("MediAssist-MCP")
st.sidebar.caption("Synthetic healthcare MCP server")
render_gemini_status()
page = st.sidebar.radio("Choose a tool", TOOL_OPTIONS)
st.sidebar.markdown(
    """
    <div class="subtle">
    Tips for judges:
    <br>- Start with Symptom checker or Emergency triage.
    <br>- Then show Medicine info and BMI calculator.
    <br>- Finish with Appointment scheduler and Mental health support.
    </div>
    """,
    unsafe_allow_html=True,
)


render_home()
PAGE_RENDERERS[page]()
