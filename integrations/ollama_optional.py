"""Optional local Ollama helper.

This module is intentionally kept outside the main MCP flow.
It is free to use when Ollama is already installed on the same machine, and
it is safe to ignore entirely if the hackathon demo does not need it.
"""

from __future__ import annotations

import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def ollama_available() -> bool:
    """Check whether an Ollama host has been configured."""

    return os.getenv("OLLAMA_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}


def summarize_with_ollama(prompt: str, model: str | None = None) -> dict[str, str]:
    """Generate a tiny local summary using Ollama if it is available.

    The function returns a fallback message instead of failing hard, so it
    never blocks the core hackathon demo.
    """

    if not ollama_available():
        return {
            "model": model or os.getenv("OLLAMA_MODEL", "llama3.2"),
            "summary": "Ollama is disabled, so this result stayed fully local and synthetic.",
        }

    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    selected_model = model or os.getenv("OLLAMA_MODEL", "llama3.2")

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        request = Request(
            f"{host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
            return {
                "model": selected_model,
                "summary": body.get("response", ""),
            }
    except (URLError, TimeoutError, OSError):
        return {
            "model": selected_model,
            "summary": "Ollama is not available, so this result stayed fully local and synthetic.",
        }
