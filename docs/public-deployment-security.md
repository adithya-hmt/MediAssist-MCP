# Public Deployment Security

MediAssist-MCP is synthetic-only and offline-first by default.
Optional Gemini support is server-side only, disabled by default, and limited to prose polishing for synthetic care briefs.

## Before Public Deployment

- [ ] `.env` is not committed
- [ ] `.env.example` contains placeholders only
- [ ] Gemini key is stored only in a secret manager
- [ ] Gemini key is not present in the frontend bundle
- [ ] GitHub secret scanning is enabled
- [ ] Public demo mode is enabled
- [ ] Synthetic examples are verified
- [ ] PHI safety checks are enabled
- [ ] Gemini remains disabled unless explicitly required
- [ ] No real patient data appears in logs
- [ ] No diagnosis/treatment/prescription claims are made
- [ ] The demo works without an API key

## Deployment Notes

- The frontend should never display secrets.
- The server must stay usable with no Gemini key at all.
- Gemini may only polish prose and may not alter triage, risk, red flags, bundle content, or disclaimers.
- Keep all demo data synthetic and de-identified.
- Do not deploy real FHIR, EHR, login, token, service-account, or PHI handling in this hackathon version.
