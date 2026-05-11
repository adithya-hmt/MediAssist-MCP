"""Environment-driven configuration for the MediAssist-MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean-like environment value."""

    fallback = "true" if default else "false"
    return os.getenv(name, fallback).strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    """Read an integer environment value with a safe fallback."""

    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    """Small configuration object for simple, readable access."""

    server_name: str = field(default_factory=lambda: os.getenv("MCP_SERVER_NAME", "MediAssist-MCP"))
    transport: str = field(default_factory=lambda: os.getenv("MCP_TRANSPORT", "stdio"))
    host: str = field(default_factory=lambda: os.getenv("MCP_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: _env_int("MCP_PORT", 8000))
    log_level: str = field(default_factory=lambda: os.getenv("MCP_LOG_LEVEL", "INFO"))
    mediassist_env: str = field(default_factory=lambda: os.getenv("MEDIASSIST_ENV", "development"))
    mediassist_mode: str = field(default_factory=lambda: os.getenv("MEDIASSIST_MODE", "local"))
    gemini_enabled: bool = field(default_factory=lambda: _env_bool("ENABLE_GEMINI", False))
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", ""),
        repr=False,
    )
    gemini_default_model: str = field(default_factory=lambda: os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash"))
    gemini_advanced_model: str = field(default_factory=lambda: os.getenv("GEMINI_ADVANCED_MODEL", "gemini-2.5-pro"))
    gemini_model_mode: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL_MODE", "balanced"))
    gemini_timeout_seconds: int = field(default_factory=lambda: _env_int("GEMINI_TIMEOUT_SECONDS", 20))
    allow_synthetic_external_calls: bool = field(
        default_factory=lambda: _env_bool("ALLOW_SYNTHETIC_EXTERNAL_CALLS", False)
    )
    block_external_calls_on_phi: bool = field(default_factory=lambda: _env_bool("BLOCK_EXTERNAL_CALLS_ON_PHI", True))
    public_demo_mode: bool = field(default_factory=lambda: _env_bool("PUBLIC_DEMO_MODE", True))
    ollama_enabled: bool = field(default_factory=lambda: _env_bool("OLLAMA_ENABLED", False))
    ollama_host: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2"))


config = AppConfig()
