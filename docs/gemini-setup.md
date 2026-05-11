# Gemini Setup

MediAssist-MCP works locally without Gemini by default. No API key, cloud account, or external call is needed for the offline demo.

MediAssist-MCP runs by default as an offline-first synthetic healthcare workflow demo. Optional Gemini support is server-side only, disabled by default, and limited to synthetic care brief polishing.

## Local No-Gemini Mode

Use the default settings:

```bash
ENABLE_GEMINI=false
ALLOW_SYNTHETIC_EXTERNAL_CALLS=false
GEMINI_MODEL_MODE=balanced
```

Run the app normally:

```bash
python server.py
streamlit run frontend/app.py
pytest
```

## Gemini Synthetic-Only Mode

Copy `.env.example` to `.env`, then set only server-side values:

```bash
ENABLE_GEMINI=true
GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
ALLOW_SYNTHETIC_EXTERNAL_CALLS=true
GEMINI_MODEL_MODE=balanced
```

Balanced mode uses `gemini-2.5-flash` for care brief prose polishing.
Gemini is never used for triage, risk levels, red flags, recommended next steps, FHIR resources, disclaimers, or safety notes.

## Advanced Mode

```bash
GEMINI_MODEL_MODE=advanced
```

Advanced mode uses `gemini-2.5-pro` only for final doctor handoff polishing.
It may cost more than balanced mode.

## Safety Rules

- Do not use real patient data.
- Do not send PHI to Gemini.
- Keep the key server-side only.
- Do not expose the key in frontend code, logs, readiness output, screenshots, or docs.
- Do not deploy an unrestricted public Gemini endpoint.
- Keep `PUBLIC_DEMO_MODE=true` for public demos.
- Keep Gemini disabled unless it is required for a synthetic-only demo.
