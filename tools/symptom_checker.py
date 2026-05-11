"""Symptom checker tool registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.errors import InputValidationError
from core.logging import get_logger
from core.models import SymptomCheckerResponse
from services.healthcare import symptom_checker_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the symptom checker tool on the provided MCP server."""

    @mcp.tool()
    async def symptom_checker(symptom: str) -> SymptomCheckerResponse:
        """Return synthetic possible conditions, a confidence score, and a recommendation."""

        try:
            result = symptom_checker_logic(symptom)
            logger.info("Symptom check complete for %s", symptom)
            return SymptomCheckerResponse(symptom=symptom, **result)
        except InputValidationError:
            raise
        except Exception as exc:
            logger.exception("symptom_checker failed")
            raise RuntimeError(f"Unable to process symptom checker request: {exc}") from exc
