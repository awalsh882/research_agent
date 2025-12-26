"""Tool introspection for the Research Agent.

Provides a list_tools tool that allows the agent to report its own MCP tool capabilities.
This tool reads from the ToolRegistry, ensuring a single source of truth.
"""

from typing import Any

from research_agent.tools.registry import registered_tool, ToolRegistry


@registered_tool(
    name="list_tools",
    description="List all available MCP tools the agent can use, with descriptions and parameters",
    parameters={},
    parameter_types={},
)
async def list_tools(args: dict[str, Any]) -> dict[str, Any]:
    """Return formatted list of available MCP tools.

    Reads directly from the ToolRegistry to ensure the response
    always matches the actually registered tools.
    """
    return {
        "content": [{"type": "text", "text": ToolRegistry.get_introspection_text()}]
    }
