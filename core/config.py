"""Environment-driven configuration for the MediAssist-MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Small configuration object for simple, readable access."""

    server_name: str = os.getenv("MCP_SERVER_NAME", "MediAssist-MCP")
    transport: str = os.getenv("MCP_TRANSPORT", "stdio")
    host: str = os.getenv("MCP_HOST", "127.0.0.1")
    port: int = int(os.getenv("MCP_PORT", "8000"))
    log_level: str = os.getenv("MCP_LOG_LEVEL", "INFO")
    ollama_enabled: bool = os.getenv("OLLAMA_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")


config = AppConfig()
