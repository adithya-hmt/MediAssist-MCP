"""Health risk assessment tool registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.errors import InputValidationError
from core.logging import get_logger
from core.models import RiskAssessmentResponse
from services.healthcare import health_risk_assessment_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the health risk assessment tool."""

    @mcp.tool()
    async def health_risk_assessment(age: int, smoking: bool, diabetes: bool) -> RiskAssessmentResponse:
        """Return a simple synthetic risk score based on three inputs."""

        try:
            result = health_risk_assessment_logic(age, smoking, diabetes)
            logger.info("Risk assessment complete age=%s smoking=%s diabetes=%s", age, smoking, diabetes)
            return RiskAssessmentResponse(**result)
        except InputValidationError:
            raise
        except Exception as exc:
            logger.exception("health_risk_assessment failed")
            raise RuntimeError(f"Unable to assess risk: {exc}") from exc
