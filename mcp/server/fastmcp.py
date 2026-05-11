"""Lightweight FastMCP-compatible server used by MediAssist-MCP.

This compatibility layer keeps the project runnable on Python 3.9 in the
current MacBook environment without installing the external MCP package.
It supports the small subset of the API this project needs:

- `FastMCP(name, json_response=True, stateless_http=True)`
- `@mcp.tool()`
- `mcp.run(transport="stdio" | "streamable-http", host=..., port=...)`

The implementation speaks basic JSON-RPC over stdio and HTTP so the project
remains demo-friendly and MCP-shaped.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import sys
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Callable, get_args, get_origin, get_type_hints

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn


JSONRPC_VERSION = "2.0"
DEFAULT_PROTOCOL_VERSION = "2025-03-26"


def _jsonable(value: Any) -> Any:
    """Convert return values into plain JSON-friendly data."""

    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict") and callable(value.dict):
        return value.dict()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    return value


def _type_to_schema(annotation: Any) -> dict[str, Any]:
    """Convert a Python type annotation into a tiny JSON schema fragment."""

    origin = get_origin(annotation)
    args = get_args(annotation)

    if annotation in (str, inspect._empty):
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    if annotation in (date, datetime):
        return {"type": "string", "format": "date-time" if annotation is datetime else "date"}
    if origin in (list, list[str]):
        return {"type": "array", "items": _type_to_schema(args[0] if args else str)}
    if origin is dict:
        return {"type": "object"}
    if origin is tuple:
        return {"type": "array"}
    return {"type": "string"}


@dataclass
class RegisteredTool:
    """Simple tool registry entry."""

    name: str
    description: str
    func: Callable[..., Any]
    schema: dict[str, Any]


class FastMCP:
    """A small, local FastMCP-compatible server."""

    def __init__(self, name: str, json_response: bool = True, stateless_http: bool = True):
        self.name = name
        self.json_response = json_response
        self.stateless_http = stateless_http
        self._logger = logging.getLogger(f"mcp.fastmcp.{name}")
        self._tools: dict[str, RegisteredTool] = {}

    def tool(self, func: Callable[..., Any] | None = None):
        """Register a tool function with or without decorator parentheses."""

        def decorator(inner: Callable[..., Any]) -> Callable[..., Any]:
            signature = inspect.signature(inner)
            type_hints = get_type_hints(inner)
            properties: dict[str, Any] = {}
            required: list[str] = []

            for param_name, param in signature.parameters.items():
                annotation = type_hints.get(param_name, param.annotation)
                properties[param_name] = _type_to_schema(annotation)
                if param.default is inspect._empty:
                    required.append(param_name)

            schema = {
                "type": "object",
                "properties": properties,
                "additionalProperties": False,
            }
            if required:
                schema["required"] = required

            self._tools[inner.__name__] = RegisteredTool(
                name=inner.__name__,
                description=(inner.__doc__ or "").strip(),
                func=inner,
                schema=schema,
            )
            return inner

        if func is not None:
            return decorator(func)
        return decorator

    @property
    def tools(self) -> dict[str, RegisteredTool]:
        """Expose the tool registry."""

        return self._tools

    def _tool_list(self) -> list[dict[str, Any]]:
        """Return tools in MCP-compatible list format."""

        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.schema,
            }
            for tool in self._tools.values()
        ]

    async def _invoke_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Invoke a registered tool and normalize its output."""

        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool: {name}")

        result = tool.func(**arguments)
        if inspect.isawaitable(result):
            result = await result
        return _jsonable(result)

    async def _handle_rpc(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        """Handle a single JSON-RPC request."""

        method = payload.get("method")
        request_id = payload.get("id")
        params = payload.get("params") or {}

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": params.get("protocolVersion", DEFAULT_PROTOCOL_VERSION),
                    "serverInfo": {
                        "name": self.name,
                        "version": "0.1.0",
                    },
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                }
                return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}

            if method == "notifications/initialized":
                return None

            if method == "ping":
                return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": {}}

            if method == "tools/list":
                return {
                    "jsonrpc": JSONRPC_VERSION,
                    "id": request_id,
                    "result": {"tools": self._tool_list()},
                }

            if method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments") or {}
                tool_result = await self._invoke_tool(name, arguments)
                return {
                    "jsonrpc": JSONRPC_VERSION,
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(tool_result, indent=2, ensure_ascii=False),
                            }
                        ],
                        "structuredContent": tool_result,
                    },
                }

            if method == "resources/list":
                return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": {"resources": []}}

            return {
                "jsonrpc": JSONRPC_VERSION,
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        except Exception as exc:
            self._logger.exception("RPC handling failed for %s", method)
            return {
                "jsonrpc": JSONRPC_VERSION,
                "id": request_id,
                "error": {"code": -32000, "message": str(exc)},
            }

    async def _handle_payload(self, payload: Any) -> Any:
        """Handle a JSON-RPC payload or batch."""

        if isinstance(payload, list):
            responses = []
            for item in payload:
                response = await self._handle_rpc(item)
                if response is not None:
                    responses.append(response)
            return responses
        return await self._handle_rpc(payload)

    def _build_app(self) -> FastAPI:
        """Build the HTTP app used for the streamable transport."""

        app = FastAPI(title=self.name)

        @app.get("/")
        async def root() -> dict[str, Any]:
            return {
                "name": self.name,
                "transport": "streamable-http",
                "tools": [tool.name for tool in self._tools.values()],
            }

        @app.get("/health")
        async def health() -> dict[str, Any]:
            return {"status": "ok", "name": self.name, "tool_count": len(self._tools)}

        @app.get("/mcp")
        async def mcp_get() -> dict[str, Any]:
            return {
                "message": "MediAssist-MCP is running.",
                "name": self.name,
                "transport": "streamable-http",
                "tools": [tool.name for tool in self._tools.values()],
            }

        @app.post("/mcp")
        async def mcp_post(request: Request) -> JSONResponse:
            payload = await request.json()
            response = await self._handle_payload(payload)
            if response is None:
                return JSONResponse(status_code=204, content=None)
            return JSONResponse(response)

        return app

    def _log_startup(self, transport: str, host: str | None = None, port: int | None = None) -> None:
        """Print a compact startup summary."""

        tool_names = ", ".join(self._tools) if self._tools else "no tools"
        if transport == "streamable-http":
            self._logger.info(
                "Starting %s on http://%s:%s/mcp with %d tools",
                self.name,
                host,
                port,
                len(self._tools),
            )
            self._logger.info("Tools: %s", tool_names)
            return

        self._logger.info("Starting %s in stdio mode with %d tools", self.name, len(self._tools))
        self._logger.info("Tools: %s", tool_names)
        self._logger.info("Send JSON-RPC requests on stdin; responses are written to stdout.")

    def _run_stdio(self) -> None:
        """Run a simple line-delimited JSON-RPC loop over stdio."""

        self._log_startup("stdio")

        for raw_line in sys.stdin:
            line = raw_line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                error = {
                    "jsonrpc": JSONRPC_VERSION,
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {exc}"},
                }
                sys.stdout.write(json.dumps(error) + "\n")
                sys.stdout.flush()
                continue

            response = asyncio.run(self._handle_payload(payload))
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

    def run(self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000) -> None:
        """Run the server using the selected transport."""

        if transport == "streamable-http":
            self._log_startup(transport, host=host, port=port)
            uvicorn.run(self._build_app(), host=host, port=port, log_level="info")
            return

        if transport == "stdio":
            self._run_stdio()
            return

        raise ValueError(f"Unsupported transport: {transport}")

