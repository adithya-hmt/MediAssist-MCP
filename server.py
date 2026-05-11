"""MediAssist-MCP main entrypoint.

This file creates the FastMCP server, registers every healthcare tool module,
and starts the server using the transport selected in the environment.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from core.logging import configure_logging, get_logger
from tools.appointment_scheduler import register_tools as register_appointment_tools
from tools.bmi import register_tools as register_bmi_tools
from tools.care_brief import register_tools as register_care_brief_tools
from tools.care_coordination import register_tools as register_care_coordination_tools
from tools.gemini_readiness import register_tools as register_gemini_readiness_tools
from tools.mental_health_support import register_tools as register_mental_health_tools
from tools.medicine_info import register_tools as register_medicine_tools
from tools.nutrition_recommendation import register_tools as register_nutrition_tools
from tools.health_risk_assessment import register_tools as register_risk_tools
from tools.symptom_checker import register_tools as register_symptom_tools
from tools.triage import register_tools as register_triage_tools


# Load environment variables from a local .env file if present.
load_dotenv()


# Make sure the project root is importable when the file is launched directly.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Configure logging before any tool code starts logging messages.
configure_logging()
logger = get_logger(__name__)


# Create the MCP server with JSON responses enabled for structured outputs.
mcp = FastMCP(
    os.getenv("MCP_SERVER_NAME", "MediAssist-MCP"),
    json_response=True,
    stateless_http=True,
)


# Register each tool module in one place so the server stays easy to navigate.
register_symptom_tools(mcp)
register_medicine_tools(mcp)
register_bmi_tools(mcp)
register_appointment_tools(mcp)
register_risk_tools(mcp)
register_triage_tools(mcp)
register_nutrition_tools(mcp)
register_mental_health_tools(mcp)
register_care_brief_tools(mcp)
register_care_coordination_tools(mcp)
register_gemini_readiness_tools(mcp)


def main() -> None:
    """Start the MCP server with the chosen transport."""

    # The default transport is Streamable HTTP so the project is easy to demo in a browser.
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))

    logger.info("Starting %s with transport=%s", mcp.name, transport)
    logger.info("Project root: %s", Path(__file__).resolve().parent)

    # Streamable HTTP is useful for browser-based inspection and production use.
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host=host, port=port)
        return

    # Stdio is ideal for local MCP clients and the MCP Inspector command flow.
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
