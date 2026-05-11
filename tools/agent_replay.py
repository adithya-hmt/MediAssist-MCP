"""Agent replay MCP tool registration."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from core.logging import get_logger
from services.agent_replay import generate_agent_team_replay as generate_agent_team_replay_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the deterministic specialist-agent replay."""

    @mcp.tool()
    async def generate_agent_team_replay(patient_case: dict[str, Any]) -> dict[str, Any]:
        """Return a deterministic replay of specialist agent collaboration."""

        result = generate_agent_team_replay_logic(patient_case)
        logger.info("Generated agent replay trace_id=%s", result.get("trace_id"))
        return result
