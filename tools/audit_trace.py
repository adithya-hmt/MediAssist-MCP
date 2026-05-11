"""Audit trace MCP tool registration."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from core.logging import get_logger
from services.audit_trace import generate_audit_trace as generate_audit_trace_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the workflow audit trace generator."""

    @mcp.tool()
    async def generate_audit_trace(workflow_result: dict[str, Any]) -> dict[str, Any]:
        """Return a synthetic audit trace."""

        result = generate_audit_trace_logic(workflow_result)
        logger.info("Generated audit trace trace_id=%s", result.get("trace_id"))
        return result
