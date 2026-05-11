"""Synthetic care brief tool registration."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from core.logging import get_logger
from services.care_brief import generate_care_brief_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the synthetic care brief tool."""

    @mcp.tool()
    async def generate_care_brief(case_id: str = "case-alpha") -> dict[str, Any]:
        """Return a synthetic care brief with optional safe Gemini prose polishing."""

        result = generate_care_brief_logic(case_id)
        logger.info(
            "Generated synthetic care brief case_id=%s provider=%s status=%s",
            result.get("case_id"),
            result.get("ai_provider"),
            result.get("ai_provider_status"),
        )
        return result
