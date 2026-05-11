# MCP Resources and Prompt Notes

This repo is ready to expose a small set of synthetic demo resources and prompt patterns.

## Suggested Resources

- `synthetic://patients/demo-cases`
- `synthetic://care/full-care-journey`
- `synthetic://care/fhir-bundle`
- `synthetic://care/phi-safety`
- `synthetic://care/sharp-validation`

## Suggested Prompt Fragments

- "Run the full synthetic care journey for the bundled demo patient."
- "Show the PHI safety receipt before any downstream processing."
- "Generate the FHIR-style bundle and highlight Provenance."
- "Explain the SHARP validation result and the blocked actions."
- "Replay the agent handoffs for the demo case."

## Prompt Design Rules

- Keep the prompt synthetic-only.
- Keep the prompt free of PHI and secrets.
- Keep the prompt focused on coordination, not diagnosis.
- Prefer structured JSON outputs over prose-only responses.

## Frontend/Inspector Alignment

- The Streamlit app should load the same examples as the MCP demo path.
- Inspector-friendly outputs should be stable and deterministic where possible.
- Optional Gemini output should never become a dependency for the demo path.
