"""Synthetic appointment scheduling tool registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.errors import InputValidationError
from core.logging import get_logger
from core.models import AppointmentResponse
from services.healthcare import appointment_scheduler_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the appointment scheduler tool."""

    @mcp.tool()
    async def appointment_scheduler(name: str, date: str) -> AppointmentResponse:
        """Create a fake appointment confirmation for a synthetic workflow."""

        try:
            result = appointment_scheduler_logic(name, date)
            logger.info("Created synthetic appointment for %s on %s", name, date)
            return AppointmentResponse(**result)
        except InputValidationError:
            raise
        except Exception as exc:
            logger.exception("appointment_scheduler failed")
            raise RuntimeError(f"Unable to create appointment confirmation: {exc}") from exc
