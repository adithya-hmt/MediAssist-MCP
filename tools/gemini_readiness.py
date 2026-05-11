"""Gemini readiness tool registration."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from services.gemini_provider import gemini_readiness_status


def register_tools(mcp: FastMCP) -> None:
    """Register the public-safe Gemini readiness tool."""

    @mcp.tool()
    async def check_gemini_readiness() -> dict[str, Any]:
        """Return Gemini readiness without exposing secrets or raw environment values."""

        return gemini_readiness_status()
