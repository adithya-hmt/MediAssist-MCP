"""Full care journey MCP tool registration."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from core.logging import get_logger
from services.care_journey import run_full_care_journey as run_full_care_journey_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the full synthetic care journey workflow."""

    @mcp.tool()
    async def run_full_care_journey(patient_case: dict[str, Any]) -> dict[str, Any]:
        """Run the full synthetic care-coordination journey."""

        result = run_full_care_journey_logic(patient_case)
        logger.info(
            "Ran care journey case_id=%s status=%s",
            result.get("case_id"),
            result.get("workflow_status"),
        )
        return result
