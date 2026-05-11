# MediAssist-MCP

MediAssist-MCP is an interoperable care coordination toolkit for healthcare agents.
It is offline-first, synthetic-only, and designed for hackathon demos where safety, structured outputs, and MCP interoperability matter more than raw model calls.

## 30-Second Summary

Use MediAssist-MCP to turn a synthetic patient case into a full care-coordination artifact:
triage, risk assessment, care gaps, follow-up planning, a FHIR-style bundle, a deterministic audit trace, and an agent-team replay.

The server works without Gemini. Optional Gemini polishing is server-side only, disabled by default, and limited to prose polishing for synthetic care briefs.

## Why It Fits Agents Assemble

- It demonstrates a practical multi-tool agent workflow instead of a single prompt demo.
- It keeps the entire judge path synthetic, offline-first, and reproducible.
- It exposes structured MCP outputs that are easy for agents and inspectors to consume.
- It includes interoperability storytelling through a FHIR-style bundle and SHARP-style context validation.
- It includes explicit PHI safety checks and human-review disclaimers.

## Architecture Overview

- `server.py` registers the MCP tool surface.
- `services/` contains the deterministic offline logic.
- `tools/` exposes the logic through FastMCP tool wrappers.
- `frontend/` provides a Streamlit command-center view.
- `examples/` contains synthetic fallback JSON payloads for demos.
- `docs/` contains the walkthrough, alignment, security, and marketplace notes.

## MCP Tool Surface

### Original tools

- `symptom_checker`
- `emergency_triage`
- `bmi_calculator`
- `medicine_info`
- `nutrition_recommendation`
- `appointment_scheduler`
- `mental_health_support`
- `health_risk_assessment`

### New top-tier tools

- `run_full_care_journey`
- `detect_care_gaps`
- `generate_follow_up_plan`
- `generate_audit_trace`
- `generate_agent_team_replay`
- `export_fhir_bundle`
- `validate_sharp_context`
- `phi_safety_check`

### Optional if present

- `generate_care_brief`
- `check_gemini_readiness`

## Full Care Journey Workflow

`run_full_care_journey(patient_case: dict)` is the primary demo path.

It returns one structured artifact with:

- `request_id`
- `synthetic_patient_snapshot`
- `safety_status`
- `sharp_context_status`
- `triage_result`
- `risk_assessment`
- `care_gaps`
- `follow_up_plan`
- `doctor_handoff_brief`
- `patient_friendly_summary`
- `fhir_resources_generated`
- `audit_trace`
- `disclaimers`
- `synthetic_data_notice`

The workflow is synthetic-only, requires no internet, and does not require Gemini.
It must never claim diagnosis, treatment, or prescription advice.
It always includes a clinician-review disclaimer.

## Agent Team Replay

`generate_agent_team_replay` shows the synthetic handoff sequence used in the demo.
It is a storytelling artifact, not a real autonomous care workflow.
Use it to explain how the safety, triage, risk, gap detection, and follow-up steps fit together.

## FHIR-Style Bundle

`export_fhir_bundle` produces a demo Bundle with:

- `Patient`
- `Encounter`
- `Observation`
- `Condition`
- `MedicationRequest` when medication context exists
- `Appointment` when follow-up context exists
- `CarePlan`
- `Provenance`

Required metadata is included:

- `synthetic_only: true`
- `contains_phi: false`
- `demo_use_only: true`
- `disclaimer`

This is a FHIR-style demo mapping only, not a certified clinical integration.

## SHARP-Style Context Validation

`validate_sharp_context` checks whether the supplied context is suitable for the synthetic care-coordination demo.
It flags missing fields and keeps the allowed/blocked actions explicit so judges can see the access boundary.

## PHI Safety

`phi_safety_check` detects common PHI-like patterns, including:

- email addresses
- phone numbers
- Aadhaar-like 12-digit numbers
- credit-card-like 13-19 digit numbers
- URLs
- token/key-like strings

The output includes:

- `safe_to_process`
- `detected_risks`
- `redacted_preview`
- `recommendation`
- `synthetic_only_policy`
- `disclaimer`

## Optional Gemini Polishing

Gemini is disabled by default.
If enabled, it is used only for safe prose polishing of synthetic care briefs.
It must not change triage, risk, red-flag logic, the FHIR bundle, or any disclaimer.

The project runs fully offline without Gemini.

## Run Locally

```bash
cd /home/wk/MediAssist-MCP
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

### Streamlit frontend

```bash
streamlit run frontend/app.py
```

## Test

Run the offline verification suite:

```bash
python -m compileall .
python -m pytest
```

## Inspect MCP Tools

Use the local MCP server with stdio or Streamable HTTP.

```bash
MCP_TRANSPORT=stdio python server.py
```

or

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 MCP_PORT=8000 python server.py
```

Then connect your inspector or client to the `/mcp` endpoint on the configured host and port.

## Streamlit Frontend

The frontend is a safe demo dashboard that can display or load:

- Full Care Journey output
- FHIR bundle output
- PHI safety output
- SHARP context output
- Agent Team Replay output

It falls back to the bundled `examples/*.json` files when live execution is not available.

## Prompt Opinion Marketplace Checklist

- Synthetic data only
- No real PHI
- No hardcoded API keys
- No `.env` committed
- No diagnosis, treatment, or prescription claims
- Stable tool names and structured JSON outputs
- Clear safety disclaimer
- Offline demo path works without Gemini
- Example payloads are bundled for reviewers

See `docs/prompt-opinion-marketplace-checklist.md` for the fuller submission checklist.

## Safety Disclaimer

This project is for synthetic demonstration and workflow prototyping only.
It does not diagnose, treat, prescribe, or replace professional care.
Any real-world deployment should be reviewed by qualified security, privacy, and clinical stakeholders.
