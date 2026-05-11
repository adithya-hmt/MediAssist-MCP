"""Nutrition recommendation tool registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.errors import InputValidationError
from core.logging import get_logger
from core.models import NutritionResponse
from services.healthcare import nutrition_recommendation_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the nutrition recommendation tool."""

    @mcp.tool()
    async def nutrition_recommendation(condition: str) -> NutritionResponse:
        """Suggest a synthetic diet pattern based on a health condition."""

        try:
            result = nutrition_recommendation_logic(condition)
            logger.info("Nutrition suggestions created for %s", condition)
            return NutritionResponse(**result)
        except InputValidationError:
            raise
        except Exception as exc:
            logger.exception("nutrition_recommendation failed")
            raise RuntimeError(f"Unable to generate nutrition guidance: {exc}") from exc
