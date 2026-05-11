"""Mental health support tool registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.errors import InputValidationError
from core.logging import get_logger
from core.models import MentalHealthResponse
from services.healthcare import mental_health_support_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the mental health support tool."""

    @mcp.tool()
    async def mental_health_support(mood: str) -> MentalHealthResponse:
        """Return encouraging synthetic wellness guidance."""

        try:
            result = mental_health_support_logic(mood)
            logger.info("Mental health guidance generated for mood=%s", mood)
            return MentalHealthResponse(**result)
        except InputValidationError:
            raise
        except Exception as exc:
            logger.exception("mental_health_support failed")
            raise RuntimeError(f"Unable to generate wellness guidance: {exc}") from exc
