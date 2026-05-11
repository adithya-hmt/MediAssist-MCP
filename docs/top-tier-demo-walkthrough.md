# Top-Tier Demo Walkthrough

This walkthrough is for the synthetic, offline-first MediAssist-MCP demo.

## 3-Minute Flow

1. Open the Streamlit frontend.
2. Run **Full Care Journey** with the bundled synthetic case.
3. Show the safety receipt and SHARP validation.
4. Open the FHIR-style bundle and point out `Patient`, `Encounter`, `Observation`, `Condition`, `CarePlan`, and `Provenance`.
5. Open **Agent Team Replay** to show the coordinated handoff story.
6. Open **Audit Trace** to show the deterministic workflow evidence.
7. Open **PHI Safety** and show the redacted preview.

## What To Say

- The demo is synthetic-only and does not use real PHI.
- The workflow runs offline without Gemini.
- Optional Gemini is server-side only and limited to prose polishing when explicitly enabled.
- The outputs are structured JSON so agents and inspectors can reuse them directly.

## Best Visual Emphasis

- Safety receipt
- SHARP validation
- FHIR-style bundle
- Audit trace
- Agent replay

## Do Not Claim

- Diagnosis
- Treatment
- Prescription
- Live EHR connectivity
- Real patient data processing
