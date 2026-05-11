# Judging Alignment

This note maps MediAssist-MCP to the common things judges look for in an Agents Assemble submission.

## AI Factor

- More than one tool is exposed.
- The workflow is multi-step and structured.
- The system produces a full coordination artifact instead of a single answer.

## Interoperability

- The demo includes a FHIR-style Bundle.
- The demo includes SHARP-style context validation.
- The outputs are deterministic JSON, which makes them easy to inspect and reuse.

## Safety

- The repo is synthetic-only.
- The repo includes PHI safety checks and redaction.
- The repo carries clinician-review disclaimers.
- Gemini is optional and disabled by default.

## Feasibility

- No external API is required for the main demo.
- The frontend can fall back to bundled examples.
- The same logic powers the MCP server and the UI.

## Demo Quality

- The full care journey is the main story.
- Agent replay and audit trace help explain the workflow.
- The outputs are structured enough to screenshot and explain quickly.
