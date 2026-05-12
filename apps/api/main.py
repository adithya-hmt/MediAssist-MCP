import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, privacy, sharp, workflow, fhir, audit, demo, mcp_info, gemini

app = FastAPI(title="Cerelytic MediAssist API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(privacy.router)
app.include_router(sharp.router)
app.include_router(workflow.router)
app.include_router(fhir.router)
app.include_router(audit.router)
app.include_router(demo.router)
app.include_router(mcp_info.router)
app.include_router(gemini.router)
