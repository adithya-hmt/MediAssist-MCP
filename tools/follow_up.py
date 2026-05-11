"""Follow-up MCP tool registration."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from core.logging import get_logger
from services.follow_up import generate_follow_up_plan as generate_follow_up_plan_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the synthetic follow-up planner."""

    @mcp.tool()
    async def generate_follow_up_plan(
        patient_case: dict[str, Any],
        care_brief: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a synthetic follow-up plan."""

        result = generate_follow_up_plan_logic(patient_case, care_brief)
        logger.info(
            "Generated follow-up plan case_id=%s type=%s",
            result.get("case_id"),
            result.get("recommended_follow_up_type"),
        )
        return result
