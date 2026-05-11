"""Emergency triage tool registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.errors import InputValidationError
from core.logging import get_logger
from core.models import TriageResponse
from services.healthcare import emergency_triage_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the emergency triage tool."""

    @mcp.tool()
    async def emergency_triage(symptoms: str) -> TriageResponse:
        """Return a synthetic urgency level for a symptom description."""

        try:
            result = emergency_triage_logic(symptoms)
            logger.info("Triage result=%s for symptoms=%s", result["urgency_level"], symptoms)
            return TriageResponse(symptoms=symptoms, **result)
        except InputValidationError:
            raise
        except Exception as exc:
            logger.exception("emergency_triage failed")
            raise RuntimeError(f"Unable to triage symptoms: {exc}") from exc
