# Prompt Opinion Marketplace Checklist

Use this checklist before publishing the demo or sharing a marketplace listing.

## Must-Have

- [ ] Synthetic data only
- [ ] No real PHI
- [ ] No hardcoded API keys
- [ ] No committed `.env`
- [ ] The server runs without Gemini
- [ ] The frontend runs without Gemini
- [ ] MCP tool names are stable
- [ ] Outputs are structured JSON
- [ ] Safety disclaimer is visible
- [ ] No diagnosis/treatment/prescription claim

## Strongly Recommended

- [ ] Full Care Journey demo path works from a single synthetic example
- [ ] FHIR-style bundle is easy to inspect
- [ ] PHI safety checker is easy to show live
- [ ] SHARP validation is visible in the UI
- [ ] Agent Team Replay is available for storytelling
- [ ] Audit Trace is available for reviewer confidence

## Listing Copy

Keep the catalog description short and accurate:

> MediAssist-MCP is a synthetic healthcare MCP server for care coordination demos, with triage, risk, follow-up, FHIR-style output, PHI safety, and audit trace tooling.

## What Not To Do

- Do not claim clinical decision support.
- Do not imply that the tool diagnoses or prescribes.
- Do not expose a real Gemini key.
- Do not make Gemini mandatory.
