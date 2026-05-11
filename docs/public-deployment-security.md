# Public Deployment Security

MediAssist-MCP runs by default as an offline-first synthetic healthcare workflow demo. Optional Gemini support is server-side only, disabled by default, and limited to synthetic care brief polishing.

Use this checklist before deploying any public demo.

- [ ] `.env` not committed
- [ ] Gemini key stored only in hosting secret manager
- [ ] Gemini key not present in frontend bundle
- [ ] GitHub secret scanning enabled
- [ ] Public demo mode enabled
- [ ] Synthetic-only examples verified
- [ ] PHI safety checker enabled
- [ ] Gemini disabled unless required
- [ ] Rate limits or quota limits configured
- [ ] No real patient data in logs
- [ ] No diagnosis/treatment claims
- [ ] Demo tested without API key

## Deployment Notes

Gemini is optional and server-side only.
The public frontend must never accept or display API keys.
Care brief polishing may use Gemini only when `ENABLE_GEMINI=true`, `ALLOW_SYNTHETIC_EXTERNAL_CALLS=true`, the key is configured server-side, and the synthetic/PHI safety check passes.

Do not deploy this project with real FHIR, EHR, external healthcare database, login, token, service account, or PHI handling unless a separate security review is completed.
