"""Clean MCP server wiring for Cerelytic MediAssist."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.server.fastmcp import FastMCP
from mcp.tools import TOOL_REGISTRY
from mcp.resources import RESOURCES
from mcp.prompts import PROMPTS

mcp = FastMCP("Cerelytic MediAssist-MCP", json_response=True, stateless_http=True)

# Register all tools
for name, fn in TOOL_REGISTRY.items():
    mcp.tool(name=name)(fn)

# Register resources
for resource in RESOURCES:
    uri = resource["uri"]
    name = resource["name"]
    description = resource["description"]
    mime_type = resource["mimeType"]
    content = resource["content"]

    def make_resource_fn(c: str):
        def resource_fn() -> str:
            return c
        return resource_fn

    mcp.resource(uri, name=name, description=description, mime_type=mime_type)(
        make_resource_fn(content)
    )

# Register prompts
for prompt in PROMPTS:
    pname = prompt["name"]
    pdesc = prompt["description"]
    ptemplate = prompt["template"]

    def make_prompt_fn(t: str):
        def prompt_fn(**kwargs) -> str:
            result = t
            for k, v in kwargs.items():
                result = result.replace(f"{{{{{k}}}}}", str(v))
            return result
        return prompt_fn

    mcp.prompt(name=pname, description=pdesc)(make_prompt_fn(ptemplate))


if __name__ == "__main__":
    mcp.run(transport="stdio")
