"""Care gap MCP tool registration."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from core.logging import get_logger
from services.care_gaps import detect_care_gaps as detect_care_gaps_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the synthetic care gap detector."""

    @mcp.tool()
    async def detect_care_gaps(patient_case: dict[str, Any]) -> dict[str, Any]:
        """Return a synthetic care-gap assessment."""

        result = detect_care_gaps_logic(patient_case)
        logger.info(
            "Detected care gaps case_id=%s priority=%s",
            result.get("case_id"),
            result.get("priority"),
        )
        return result
