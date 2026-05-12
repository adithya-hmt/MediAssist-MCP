from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from apps.api.routes.health import router as health_router
from apps.api.routes.cases import router as cases_router
from apps.api.routes.workflows import router as workflows_router
from apps.api.routes.fhir import router as fhir_router
from apps.api.routes.safety import router as safety_router
from apps.api.routes.audit import router as audit_router
from apps.api.routes.mcp import router as mcp_router
from apps.api.services.demo_case import get_synthetic_patient_case
from apps.api.services.persistence import save_case, save_run, save_audit
from services.workflow_primitives import run_full_care_journey, generate_agent_team_replay, generate_audit_trace, phi_safety_check, validate_sharp_context
from services.fhir_bundle import export_fhir_bundle


def create_app() -> FastAPI:
    app = FastAPI(title="MediAssist", version="2.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(cases_router, prefix="/api/cases", tags=["cases"])
    app.include_router(workflows_router, prefix="/api/workflows", tags=["workflows"])
    app.include_router(fhir_router, prefix="/api/fhir", tags=["fhir"])
    app.include_router(safety_router, prefix="/api/safety", tags=["safety"])
    app.include_router(audit_router, prefix="/api/audit", tags=["audit"])
    app.include_router(mcp_router, prefix="/mcp", tags=["mcp"])

    @app.get("/", response_class=HTMLResponse)
    def home() -> str:
        return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>MediAssist</title><style>body{margin:0;font-family:Inter,system-ui,sans-serif;background:#f6f1e8;color:#0f172a} .wrap{display:grid;grid-template-columns:280px 1fr;min-height:100vh} .side{background:#111827;color:#fff;padding:28px} .main{padding:32px} .card{background:rgba(255,255,255,.8);border:1px solid rgba(15,23,42,.08);border-radius:20px;padding:20px;box-shadow:0 18px 50px rgba(15,23,42,.08);margin-bottom:16px} button{background:#111827;color:#fff;border:0;border-radius:12px;padding:12px 16px;font-weight:700;cursor:pointer} pre{white-space:pre-wrap;word-break:break-word;background:#fff;border-radius:16px;padding:16px;overflow:auto} .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}@media(max-width:900px){.wrap{grid-template-columns:1fr}.grid{grid-template-columns:1fr}} .pill{display:inline-block;padding:4px 10px;border-radius:999px;background:rgba(24,168,184,.14);color:#18a8b8;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.08em}</style></head><body><div class='wrap'><aside class='side'><h1>MediAssist-MCP</h1><p>Synthetic-only healthcare workflow platform.</p><div class='card' style='background:#1f2937;color:#fff;border-color:#374151'><strong>System Status</strong><p>FastAPI + MCP + FHIR + Safety</p></div><div><div>Overview</div><div>Full Journey</div><div>FHIR Bundle</div><div>Safety</div><div>Audit</div></div></aside><main class='main'><div class='pill'>Healthcare Command Center</div><h2>Full-stack rebuild in progress</h2><p>This product now uses a real backend API and a clean web shell for the hackathon demo.</p><div class='card'><button onclick='runJourney()'>Run full journey</button><div id='out'></div></div><div class='grid'><div class='card'><h3>Care Journey</h3><pre id='journey'>Click the button above.</pre></div><div class='card'><h3>FHIR / Safety / Audit</h3><pre id='meta'>Waiting...</pre></div></div><script>async function runJourney(){const caseRes=await fetch('/api/cases'); const caseData=await caseRes.json(); const journey=await (await fetch('/api/workflows/journey', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(caseData.items[0])})).json(); const fhir=await (await fetch('/api/fhir/bundle',{method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(caseData.items[0])})).json(); const phi=await (await fetch('/api/safety/phi',{method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(caseData.items[0])})).json(); const audit=await (await fetch('/api/audit',{method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(journey)})).json(); document.getElementById('journey').textContent=JSON.stringify(journey,null,2); document.getElementById('meta').textContent=JSON.stringify({fhir_resources:fhir.entry?.length||0, phi_status:phi.status, audit_trace:audit.request_id},null,2);}</script></main></div></body></html>"""

    return app
