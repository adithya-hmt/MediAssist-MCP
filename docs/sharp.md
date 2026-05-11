# SHARP Context Placeholders

SHARP-style integration placeholders are intentionally left here for future expansion.
MediAssist-MCP currently runs as an offline-first synthetic healthcare workflow demo. External API integration is intentionally not included in this hackathon version to preserve privacy, reliability, and easy reproducibility.

You can use this folder for:
- secure healthcare partner context
- authorization metadata
- organization-specific configuration
- server-side policy notes

Suggested placeholder variables:
- `SHARP_BASE_URL`
- `SHARP_CLIENT_ID`
- `SHARP_CLIENT_SECRET`
- `SHARP_AUDIENCE`
- `SHARP_SCOPES`

Important:
- Do not place secrets in this repository.
- Keep the current build synthetic-only unless a future project explicitly adds real healthcare connectivity.
- Treat any future SHARP or API notes here as documentation-only until the project deliberately opts into external connectivity.
- Do not add real FHIR, EHR, login, token, service-account, or PHI handling to this hackathon version.
