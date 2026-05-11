# Marketplace Publishing Notes

Use these notes if you later publish MediAssist-MCP to an MCP marketplace or catalog.
MediAssist-MCP runs by default as an offline-first synthetic healthcare workflow demo. Optional Gemini support is server-side only, disabled by default, and limited to synthetic care brief polishing.

Recommended checklist:
- Keep the server name short and recognizable.
- Mention clearly that all bundled examples use synthetic data only.
- Document the supported tools and their argument types.
- Include the transport mode you support for the inspector and for real clients.
- Add a short privacy note explaining that no PHI is stored or transmitted by default.
- Provide a sample `mcp.json` or launcher command for each supported client.
- Keep future API references at the documentation level only unless the offline-first rule is explicitly lifted.
- Do not require accounts, keys, tokens, cloud services, or external healthcare databases for local testing.

Suggested marketplace description:
> MediAssist-MCP is a synthetic healthcare MCP server that exposes symptom, medication, triage, nutrition, mental-health, BMI, risk, and appointment tools for demo, hackathon, and prototype workflows.
