"""Medicine information tool registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from core.errors import InputValidationError
from core.logging import get_logger
from core.models import MedicineInfoResponse
from services.healthcare import medicine_info_logic


logger = get_logger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register the medicine info tool."""

    @mcp.tool()
    async def medicine_info(medicine_name: str) -> MedicineInfoResponse:
        """Return synthetic medicine usage, dosage, and warning details."""

        try:
            result = medicine_info_logic(medicine_name)
            logger.info("Medicine lookup succeeded for %s", medicine_name)
            return MedicineInfoResponse(**result)
        except InputValidationError:
            raise
        except Exception as exc:
            logger.exception("medicine_info failed")
            raise RuntimeError(f"Unable to process medicine lookup: {exc}") from exc
