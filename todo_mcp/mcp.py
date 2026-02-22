"""Minimal Model Context Protocol (MCP) tool registry & runner.

This lightweight implementation allows registering named tools with simple
schemas and invoking them programmatically or via a JSON stdin/stdout server.
The design is intentionally minimal so we can "eat our own dogfood" without
pulling in an external dependency.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Any]


# registry holds all tools registered via register_tool
_registry: Dict[str, ToolSpec] = {}


class ToolNotFoundError(KeyError):
    pass


def register_tool(name: str, description: str, input_schema: Dict[str, Any]):
    """Decorator to register a function as an MCP tool.

    The decorated function must accept a single dict argument and return any
    JSON-serializable result.
    """

    def _decorator(func: Callable[[Dict[str, Any]], Any]):
        spec = ToolSpec(name=name, description=description, input_schema=input_schema, handler=func)
        _registry[name] = spec
        return func

    return _decorator


def list_tools() -> List[ToolSpec]:
    """Return metadata for all registered tools."""
    return list(_registry.values())


def call_tool(name: str, args: Dict[str, Any]) -> Any:
    """Invoke a registered tool by name with arguments.

    Raises ToolNotFoundError if the tool is unknown.
    """
    if name not in _registry:
        raise ToolNotFoundError(name)
    return _registry[name].handler(args)


def serve_stdin(stdout=sys.stdout, stdin=sys.stdin):
    """A very small loop reading JSON commands from stdin and writing results.

    Each incoming line is expected to be a JSON object with keys:
        {"tool": "tool_name", "input": { ... }}

    The response is written as a single-line JSON object with either
    {"result": ...} or {"error": "..."}.
    """
    # debug output: list available tools at startup
    stdout.write(json.dumps({"info": "tools", "names": [t.name for t in list_tools()]}) + "\n")
    stdout.flush()
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            tool = req.get("tool")
            args = req.get("input", {})
            result = call_tool(tool, args)
            stdout.write(json.dumps({"result": result}) + "\n")
        except Exception as e:
            stdout.write(json.dumps({"error": str(e)}) + "\n")
        stdout.flush()


# ensure the built-in tools are registered during import
# importing the module has side effects of registering via decorator
from . import mcp_tools  # noqa: F401

if __name__ == "__main__":
    serve_stdin()
