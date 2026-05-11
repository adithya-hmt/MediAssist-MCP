# FHIR-ready Notes

This folder exists to show how the project can grow into a FHIR-compatible healthcare integration.
MediAssist-MCP currently runs as an offline-first synthetic healthcare workflow demo. External API integration is intentionally not included in this hackathon version to preserve privacy, reliability, and easy reproducibility.

Planned FHIR touchpoints:
- `Patient`
- `Practitioner`
- `Appointment`
- `Observation`
- `Condition`
- `MedicationRequest`

Important:
- All current data in MediAssist-MCP is synthetic.
- No real patient information should be added to this project.
- FHIR readiness is documentation-only in this hackathon version.
- Do not add a real FHIR server, EHR connection, login flow, token, secret, service account, or PHI handling.
- If a real FHIR server is added in a future version, keep that code in a separate environment boundary and add proper security review.
