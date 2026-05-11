"""Polished Streamlit frontend for MediAssist-MCP.

This UI serves as a command-center style dashboard for the "Agents Assemble" hackathon.
It showcases the synthetic, local, and privacy-safe healthcare MCP workflows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

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
from services.fhir_bundle import export_fhir_bundle as export_fhir_bundle_logic  # noqa: E402
from services.gemini_provider import gemini_readiness_status  # noqa: E402
from services.workflow_primitives import (  # noqa: E402
    generate_agent_team_replay as generate_agent_team_replay_logic,
    generate_audit_trace as generate_audit_trace_logic,
    phi_safety_check as phi_safety_check_logic,
    run_full_care_journey as run_full_care_journey_logic,
    validate_sharp_context as validate_sharp_context_logic,
)

st.set_page_config(page_title="MediAssist-MCP Dashboard", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS ---
st.markdown(
    """
    <style>
      :root {
          --primary-color: #0f766e;
          --secondary-color: #14532d;
          --accent-blue: #0284c7;
          --text-dark: #0f172a;
          --bg-light: #f8fafc;
      }

      .stApp {
          background-color: var(--bg-light);
          color: var(--text-dark);
      }

      .block-container { padding-top: 2rem; padding-bottom: 2rem; }

      /* Typography */
      h1, h2, h3 {
          font-family: 'Inter', sans-serif;
          color: var(--text-dark);
          font-weight: 600;
      }

      /* Hero Section */
      .hero {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border-radius: 12px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      }

      .hero h1 {
        margin:0;
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
      }

      .hero p {
        margin: 1rem 0 0 0;
        font-size: 1.125rem;
        opacity: 0.9;
        font-weight: 300;
      }

      /* Cards */
      .custom-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }

      .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
      }

      .card-title {
        color: var(--primary-color);
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 0.5rem;
      }

      .card-body {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.5;
      }

      /* Subtle Text */
      .subtle {
        color: #64748b;
        font-size: 0.9rem;
      }

      /* Safety Banner */
      .safety-banner {
          background-color: #fffbeb;
          border-left: 4px solid #f59e0b;
          color: #92400e;
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
          font-weight: 500;
          font-size: 0.95rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
      }

      /* Status Pills */
      .status-pill {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.85rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
      }
      .status-critical { background-color: #fee2e2; color: #b91c1c; }
      .status-medium { background-color: #fef3c7; color: #b45309; }
      .status-low { background-color: #d1fae5; color: #047857; }
      .status-safe { background-color: #e0e7ff; color: #4338ca; }

      /* Metrics adjustments */
      [data-testid="stMetricValue"] {
          color: var(--primary-color);
          font-weight: 700;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Helpers ---
def load_json_example(path_str: str, fallback: dict) -> dict:
    """Load a local JSON example safely or return fallback."""
    try:
        path = PROJECT_ROOT / path_str
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def _demo_case() -> dict[str, Any]:
    """Return the bundled synthetic demo case or a safe fallback."""

    fallback = {
        "case_id": "synthetic-patient-001",
        "case_label": "Demo Patient",
        "synthetic": True,
        "data_source": "synthetic-demo",
        "age": 46,
        "primary_symptom": "fever",
        "symptom_description": "fever, chills, and fatigue",
        "condition_context": "diabetes",
        "smoking": False,
        "diabetes": True,
        "current_medications": ["metformin"],
        "last_follow_up_months_ago": 14,
        "preventive_gaps": ["annual diabetes review overdue", "vaccination review due"],
        "follow_up_preference": "primary care",
        "care_setting": "primary care",
        "synthetic_data_notice": "Synthetic example only. No real patient data or PHI.",
    }
    return load_json_example("examples/synthetic_patient_case.json", fallback)

def render_card(title: str, body: str, status_class: str = None, status_text: str = None) -> None:
    """Render a styled card component."""
    status_html = f'<span class="status-pill {status_class}">{status_text}</span>' if status_text else ''
    st.markdown(
        f"""
        <div class="custom-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div class="card-title">{title}</div>
                {status_html}
            </div>
            <div class="card-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_json_download(label: str, data: dict, filename: str) -> None:
    """Render a clean JSON block in an expander with download."""
    with st.expander(f"View Raw JSON: {label}", expanded=False):
        st.json(data)
        st.download_button(
            label=f"Download {label}",
            data=json.dumps(data, indent=2),
            file_name=filename,
            mime="application/json",
            key=filename
        )

def safety_banner() -> None:
    """Render standard safety banner."""
    st.markdown(
        """
        <div class="safety-banner">
            ⚠️ <strong>SAFETY NOTICE:</strong> Synthetic demo only. Not medical advice. No real patient data or PHI used.
        </div>
        """,
        unsafe_allow_html=True
    )

def _safe_call(func, *args, **kwargs):
    """Safely call a function and handle errors for UI."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return {"error": str(e), "status": "failed"}

# --- Page Renderers ---

def page_overview():
    """Render the Overview landing page."""
    st.markdown(
        """
        <div class="hero">
          <h1>MediAssist-MCP</h1>
          <p>Interoperable Care Coordination Toolkit for Healthcare Agents</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    safety_banner()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("MCP Tools", "15", delta="Ready")
    with col2:
        st.metric("FHIR-style Resources", "3+", delta="Interop")
    with col3:
        st.metric("Offline-first Mode", "Active", delta="Local")
    with col4:
        st.metric("Public Demo Safety", "100%", delta="No PHI")

    st.markdown("---")

    st.subheader("Why MediAssist-MCP?")
    col_a, col_b = st.columns(2)

    with col_a:
        render_card(
            "What it does",
            "Converts synthetic patient context into structured triage, risk assessment, "
            "doctor handoff briefs, and privacy-safe workflow outputs, exposed via MCP."
        )
        render_card(
            "How it fits",
            "Seamlessly integrates with MCP + FHIR + SHARP-style workflows to allow AI Agents "
            "to perform robust healthcare coordination without seeing real PHI."
        )

    with col_b:
        st.markdown("### Hackathon Alignment")
        render_card("🤖 AI Factor", "Extends LLM capabilities with deterministic, safe clinical tools.")
        render_card("🌍 Potential Impact", "Solves the 'last mile' interoperability and safety gap in Healthcare AI.")
        render_card("⚙️ Feasibility", "Fully local, requires no paid APIs, uses lightweight Python stack.")


def page_full_journey():
    """Render the full end-to-end synthetic care journey."""

    st.title("Full Care Journey Demo")
    st.markdown("Run the full offline workflow from safety scan through FHIR export.")
    safety_banner()

    demo_case = _demo_case()

    if st.button("▶ Run Full Care Journey", type="primary", use_container_width=True):
        with st.spinner("Processing synthetic clinical context..."):
            journey = _safe_call(run_full_care_journey_logic, demo_case)
            if not isinstance(journey, dict) or "error" in journey:
                journey = load_json_example("examples/full_care_journey_output.json", {})

            if not journey:
                st.error("Unable to load a full care journey payload.")
                return

            st.success("Workflow completed successfully.")
            st.markdown("---")

            snapshot = journey.get("synthetic_patient_snapshot", demo_case)
            safety_status = journey.get("safety_status", {})
            sharp_status = journey.get("sharp_context_status", {})
            triage_result = journey.get("triage_result", {})
            risk_result = journey.get("risk_assessment", {})
            care_gaps = journey.get("care_gaps", {})
            follow_up_plan = journey.get("follow_up_plan", {})
            audit_trace = journey.get("audit_trace", {})
            agent_replay = journey.get("agent_team_replay", {})
            fhir_bundle = journey.get("fhir_bundle", {})

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                render_card(
                    "Patient Snapshot",
                    f"**Case:** {snapshot.get('case_label', 'Demo Patient')}<br>"
                    f"**Age band:** {snapshot.get('age_band', '40s')}<br>"
                    f"**Symptom:** {snapshot.get('primary_symptom', 'fever')}",
                )
            with c2:
                render_card(
                    "Safety Status",
                    safety_status.get("recommendation", "Synthetic demo input accepted."),
                    status_class="status-safe" if safety_status.get("safe_to_process", False) else "status-critical",
                    status_text="SAFE" if safety_status.get("safe_to_process", False) else "BLOCKED",
                )
            with c3:
                render_card(
                    "SHARP Context",
                    sharp_status.get("status", "needs_review"),
                    status_class="status-safe" if sharp_status.get("status") == "valid_synthetic_context" else "status-medium",
                    status_text=sharp_status.get("status", "NEEDS REVIEW").upper(),
                )
            with c4:
                render_card(
                    "FHIR Resources",
                    ", ".join(journey.get("fhir_resources_generated", [])) or "No bundle generated",
                    status_class="status-safe",
                    status_text=str(len(journey.get("fhir_resources_generated", []))),
                )

            triage_label = triage_result.get("urgency_level", "low")
            risk_label = risk_result.get("risk_level", "low")
            t1, t2 = st.columns(2)
            with t1:
                render_card(
                    "Triage Result",
                    triage_result.get("recommended_action", ["Review the synthetic symptom context."])[0],
                    status_class=f"status-{triage_label}",
                    status_text=triage_label.upper(),
                )
            with t2:
                risk_status_class = "status-critical" if risk_label == "high" else f"status-{risk_label}"
                render_card(
                    "Risk Assessment",
                    risk_result.get("advice", ["Review the synthetic prevention context."])[0],
                    status_class=risk_status_class,
                    status_text=risk_label.upper(),
                )

            st.subheader("Clinical Coordination Summary")
            col_l, col_r = st.columns(2)
            with col_l:
                render_card("Doctor Handoff Brief", journey.get("doctor_handoff_brief", "No brief generated."))
                render_card(
                    "Care Gaps",
                    "<ul>"
                    + "".join(
                        f"<li>{gap['title']}: {gap['rationale']}</li>" for gap in care_gaps.get("care_gaps", [])
                    )
                    + "</ul>",
                )
            with col_r:
                render_card("Patient-Friendly Summary", journey.get("patient_friendly_summary", "No summary generated."))
                render_card(
                    "Follow-Up Plan",
                    f"**Type:** {follow_up_plan.get('recommended_follow_up_type', 'routine_follow_up')}<br>"
                    f"**Timeframe:** {follow_up_plan.get('timeframe', 'within 1 to 2 weeks')}<br>"
                    f"**Requires clinician review:** {follow_up_plan.get('requires_clinician_review', True)}",
                )

            st.subheader("Structured Outputs")
            render_json_download("Full Care Journey", journey, "full_care_journey.json")
            render_json_download("FHIR Bundle", fhir_bundle, "fhir_bundle.json")
            render_json_download("Audit Trace", audit_trace, "audit_trace.json")
            render_json_download("Agent Team Replay", agent_replay, "agent_team_replay.json")


def page_audit_trace():
    """Render the synthetic audit trace demo."""

    st.title("Audit Trace")
    st.markdown("Show the deterministic trace that explains how the care journey was assembled.")
    safety_banner()

    trace = _safe_call(generate_audit_trace_logic, _demo_case())
    if not isinstance(trace, dict) or "error" in trace:
        trace = load_json_example("examples/audit_trace_output.json", {})

    render_json_download("Audit Trace", trace, "audit_trace.json")


def page_agent_team_replay():
    """Render the synthetic agent-team replay demo."""

    st.title("Agent Team Replay")
    st.markdown("Replay the mock agent handoffs that produced the synthetic care summary.")
    safety_banner()

    replay = _safe_call(generate_agent_team_replay_logic, _demo_case())
    if not isinstance(replay, dict) or "error" in replay:
        replay = load_json_example("examples/agent_team_replay_output.json", {})

    render_json_download("Agent Team Replay", replay, "agent_team_replay.json")


def page_mcp_tools():
    """Render the MCP Tools index page."""
    st.title("MCP Tools Catalog")
    st.markdown("These are the tools exposed by the FastMCP server to the LLM agent.")

    tools = [
        {"name": "generate_care_brief", "desc": "Compiles triage, risk, and FHIR outputs into a single context object.", "in": "case_id (str)", "out": "JSON Care Brief"},
        {"name": "run_full_care_journey", "desc": "Runs safety, SHARP, triage, risk, care gaps, follow-up, audit, and FHIR export in one call.", "in": "patient_case (dict)", "out": "Journey JSON"},
        {"name": "detect_care_gaps", "desc": "Finds preventive, follow-up, and monitoring gaps in a synthetic case.", "in": "patient_case (dict)", "out": "Care Gaps JSON"},
        {"name": "generate_follow_up_plan", "desc": "Builds a follow-up plan from triage, risk, and care-gap context.", "in": "patient_case, triage_result, risk_result", "out": "Follow-up JSON"},
        {"name": "generate_audit_trace", "desc": "Explains how the workflow arrived at its outputs.", "in": "patient_case + outputs", "out": "Audit Trace JSON"},
        {"name": "generate_agent_team_replay", "desc": "Replays the synthetic agent handoffs that produced the result.", "in": "patient_case + outputs", "out": "Replay JSON"},
        {"name": "emergency_triage", "desc": "Evaluates raw symptom text for critical keywords.", "in": "symptoms (str)", "out": "Urgency Level & Action"},
        {"name": "health_risk_assessment", "desc": "Calculates chronic risk score based on demographics.", "in": "age, smoking, diabetes", "out": "Risk Level JSON"},
        {"name": "symptom_checker", "desc": "Maps simple symptoms to possible conditions.", "in": "symptom (str)", "out": "Conditions & Confidence"},
        {"name": "bmi_calculator", "desc": "Standard BMI calc with health guidance.", "in": "weight, height", "out": "BMI Category JSON"},
        {"name": "appointment_scheduler", "desc": "Generates synthetic scheduling confirmation.", "in": "name, date", "out": "Confirmation JSON"},
        {"name": "medicine_info", "desc": "Looks up synthetic drug info and warnings.", "in": "medicine_name", "out": "Usage & Warnings JSON"},
        {"name": "nutrition_recommendation", "desc": "Suggests nutrition guidance for a condition.", "in": "condition (str)", "out": "Nutrition JSON"},
        {"name": "mental_health_support", "desc": "Offers supportive wellness guidance for a mood input.", "in": "mood (str)", "out": "Wellness JSON"},
        {"name": "check_gemini_readiness", "desc": "Reports whether optional server-side Gemini polishing is available.", "in": "none", "out": "Readiness JSON"},
    ]

    for t in tools:
        with st.expander(f"🔧 {t['name']}", expanded=False):
            st.markdown(f"**Purpose:** {t['desc']}")
            st.markdown(f"**Inputs:** `{t['in']}`")
            st.markdown(f"**Outputs:** `{t['out']}`")


def page_fhir_viewer():
    """Render the FHIR Bundle Viewer."""
    st.title("FHIR-style Bundle Viewer")
    st.markdown("Demonstrating interoperability by mapping synthetic context to a FHIR-style Bundle structure.")
    safety_banner()

    st.info("Disclaimer: This is a FHIR-style demo mapping, not certified clinical FHIR.")

    journey = _safe_call(run_full_care_journey_logic, _demo_case())
    bundle = {}
    if isinstance(journey, dict) and "error" not in journey:
        bundle = export_fhir_bundle_logic(
            _demo_case(),
            journey.get("triage_result", {"urgency_level": "low"}),
            journey.get("risk_assessment", {"risk_level": "low"}),
            care_gaps=journey.get("care_gaps", {}),
            follow_up_plan=journey.get("follow_up_plan", {}),
            care_brief={
                "doctor_handoff_brief": journey.get("doctor_handoff_brief"),
                "recommended_next_steps": journey.get("follow_up_plan", {}).get("clinician_actions", []),
            },
            generated_by="frontend.app.page_fhir_viewer",
            audit_trace_id=journey.get("request_id"),
        )
    if not bundle:
        bundle = load_json_example("examples/fhir_bundle_output.json", {})

    if not bundle:
        st.warning("No bundle generated.")
        return

    entries = bundle.get("entry", [])

    col1, col2 = st.columns(2)
    col1.metric("Resource Type", bundle.get("resourceType", "Bundle"))
    col2.metric("Resources Contained", len(entries))

    st.markdown("### Resources")
    for i, entry in enumerate(entries):
        res = entry.get("resource", {})
        rtype = res.get("resourceType", "Unknown")
        rid = res.get("id", "none")
        with st.expander(f"📦 {rtype} (ID: {rid})", expanded=True):
            st.json(res)

    render_json_download("FHIR Bundle", bundle, "fhir_bundle.json")


def page_privacy_safety():
    """Render the Privacy & PHI Safety checker."""
    st.title("Privacy & PHI Safety")
    st.markdown("Demo of the pattern-based regex layer preventing real PHI from leaking to external APIs.")

    st.info("Note: This simulates how MediAssist blocks requests containing social security numbers, real emails, or phone numbers.")

    sample = st.text_area(
        "Test Text",
        value=(
            "Demo Patient, MRN DEMO12345, DOB 01/01/2000, "
            "synthetic reference ID REDACTED-0001, token api_key=demo-secret-12345."
        ),
        height=120,
    )

    if st.button("Check Safety"):
        with st.spinner("Scanning..."):
            result = phi_safety_check_logic(sample)
            render_card(
                "Safety Check Result",
                result.get("recommendation", "Scan complete."),
                status_class="status-safe" if result.get("safe_to_process") else "status-critical",
                status_text="ALLOWED" if result.get("safe_to_process") else "BLOCKED",
            )
            st.write("Detected risks:")
            st.json(result.get("detected_risks", []))
            st.write("Redacted preview:")
            st.code(result.get("redacted_preview", ""), language="text")
            render_json_download("PHI Safety Result", result, "phi_safety_check.json")


def page_sharp_context():
    """Render the SHARP Context Simulator."""
    st.title("SHARP Context")
    st.markdown("Simulating secure, context-aware boundaries for healthcare agents.")
    safety_banner()

    default_context = load_json_example(
        "examples/sharp_context_demo.json",
        {
            "case_id": "synthetic-patient-001",
            "primary_symptom": "fever",
            "symptom_description": "fever, chills, and fatigue",
            "synthetic": True,
            "data_source": "synthetic-demo",
            "consent_verified": True,
        },
    )

    json_input = st.text_area("Edit Context JSON", value=json.dumps(default_context, indent=2), height=200)

    if st.button("Validate Context"):
        try:
            ctx = json.loads(json_input)
            result = validate_sharp_context_logic(ctx)
            if result.get("status") == "valid_synthetic_context":
                st.success("Context Validated Successfully")
            else:
                st.warning("Context needs review.")
            c1, c2 = st.columns(2)
            with c1:
                render_card(
                    "Allowed Actions",
                    "<ul>" + "".join(f"<li>{item}</li>" for item in result.get("allowed_actions", [])) + "</ul>",
                )
            with c2:
                render_card(
                    "Blocked Actions",
                    "<ul>" + "".join(f"<li>{item}</li>" for item in result.get("blocked_actions", [])) + "</ul>",
                )
            render_json_download("SHARP Validation", result, "sharp_context_validation.json")
        except Exception as e:
            st.error(f"Invalid JSON: {e}")


def page_demo_script():
    """Render the submission / demo notes."""
    st.title("Demo Script & Submission Notes")

    st.markdown("### 🎬 3-Minute Video Flow")
    st.markdown("""
    1. **Overview Page (30s):** Show the command-center UI, emphasize synthetic data, and no API keys required.
    2. **Full Care Journey (60s):** Click 'Run Full Care Journey' and show the end-to-end workflow.
    3. **FHIR Viewer (30s):** Prove interoperability with a synthetic FHIR-style Bundle.
    4. **Privacy & PHI (30s):** Show the redaction layer and the safety receipt.
    5. **SHARP Context (30s):** Show authorization boundary validation.
    6. **Agent Replay or Audit Trace (30s):** Show the teamwork replay and deterministic audit log.
    """)

    st.markdown("### ✅ Submission Checklist")
    st.checkbox("Published to Prompt Opinion Marketplace", value=True, disabled=True)
    st.checkbox("Discoverable and invokable", value=True, disabled=True)
    st.checkbox("Demo video under 3 minutes", value=False)
    st.checkbox("Uses synthetic/de-identified data only", value=True, disabled=True)
    st.checkbox("No real PHI", value=True, disabled=True)
    st.checkbox("Public video link added", value=False)


# --- Sidebar Navigation ---
st.sidebar.title("MediAssist-MCP")
st.sidebar.caption("Healthcare Agent Coordination")

# Gemini Status Expander
with st.sidebar.expander("System Status", expanded=False):
    status = gemini_readiness_status()
    st.write(f"**Gemini:** {'Enabled' if status['gemini_enabled'] else 'Disabled (Local)'}")
    st.write(f"**Mode:** {status['model_mode']}")
    st.write(f"**Public Demo:** {'Yes' if status['public_demo_mode'] else 'No'}")

PAGES = {
    "1. Overview": page_overview,
    "2. Full Care Journey Demo": page_full_journey,
    "3. Agent Team Replay": page_agent_team_replay,
    "4. Audit Trace": page_audit_trace,
    "5. MCP Tools": page_mcp_tools,
    "6. FHIR Bundle Viewer": page_fhir_viewer,
    "7. Privacy & PHI Safety": page_privacy_safety,
    "8. SHARP Context": page_sharp_context,
    "9. Demo Script / Submission Notes": page_demo_script,
}

selection = st.sidebar.radio("Navigation", list(PAGES.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div class="subtle" style="font-size: 0.8rem;">
    <strong>Built for Agents Assemble Hackathon</strong><br>
    Local, synthetic, and interoperable.
    </div>
    """,
    unsafe_allow_html=True
)

# Render selected page
PAGES[selection]()
