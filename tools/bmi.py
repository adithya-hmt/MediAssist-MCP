"""BMI calculator tool registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.errors import InputValidationError
from core.logging import get_logger
from core.models import BmiResponse
from services.healthcare import bmi_calculator_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the BMI calculator tool."""

    @mcp.tool()
    async def bmi_calculator(weight: float, height: float) -> BmiResponse:
        """Calculate BMI and return a friendly health category."""

        try:
            result = bmi_calculator_logic(weight, height)
            logger.info("BMI calculated: weight=%s height=%s", weight, height)
            return BmiResponse(**result)
        except InputValidationError:
            raise
        except Exception as exc:
            logger.exception("bmi_calculator failed")
            raise RuntimeError(f"Unable to calculate BMI: {exc}") from exc
