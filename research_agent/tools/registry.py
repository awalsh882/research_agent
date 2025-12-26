"""Tool registry for the Research Agent.

Provides a single source of truth for all MCP tools. Tools self-register
using the @registered_tool decorator, eliminating the need to maintain
tool metadata in multiple places.

Usage:
    from research_agent.tools.registry import registered_tool, ToolRegistry

    @registered_tool(
        name="my_tool",
        description="Does something useful",
        parameters={"param1": "Description of param1"},
    )
    async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
        ...

    # Get all registered tools
    tools = ToolRegistry.get_tools()

    # Get tool metadata for introspection
    metadata = ToolRegistry.get_metadata()

    # Generate system prompt section
    prompt_section = ToolRegistry.get_system_prompt_section()
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from claude_agent_sdk import tool


@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    name: str
    description: str
    parameters: dict[str, str] = field(default_factory=dict)
    parameter_types: dict[str, type] = field(default_factory=dict)


class ToolRegistry:
    """Central registry for all MCP tools.

    Maintains a single source of truth for:
    - Tool functions (for create_sdk_mcp_server)
    - Tool metadata (for introspection)
    - System prompt generation (for SYSTEM_PROMPT)
    """

    _tools: dict[str, Callable[..., Awaitable[dict[str, Any]]]] = {}
    _metadata: dict[str, ToolMetadata] = {}

    @classmethod
    def register(
        cls,
        name: str,
        description: str,
        parameters: dict[str, str],
        parameter_types: dict[str, type],
        func: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Register a tool with the registry.

        Args:
            name: Tool name (e.g., "generate_report")
            description: Human-readable description
            parameters: Dict mapping param names to descriptions
            parameter_types: Dict mapping param names to types (for @tool decorator)
            func: The decorated tool function
        """
        cls._tools[name] = func
        cls._metadata[name] = ToolMetadata(
            name=name,
            description=description,
            parameters=parameters,
            parameter_types=parameter_types,
        )

    @classmethod
    def get_tools(cls) -> list[Callable[..., Awaitable[dict[str, Any]]]]:
        """Get all registered tool functions.

        Returns:
            List of tool functions for create_sdk_mcp_server.
        """
        return list(cls._tools.values())

    @classmethod
    def get_tool_names(cls) -> list[str]:
        """Get all registered tool names.

        Returns:
            List of tool names for allowed_tools configuration.
        """
        return list(cls._tools.keys())

    @classmethod
    def get_allowed_tools(cls, server_name: str = "research-tools") -> list[str]:
        """Get allowed_tools list for ClaudeAgentOptions.

        Args:
            server_name: The MCP server name.

        Returns:
            List of fully-qualified tool names (e.g., "mcp__research-tools__generate_report")
        """
        return [f"mcp__{server_name}__{name}" for name in cls._tools.keys()]

    @classmethod
    def get_metadata(cls) -> list[ToolMetadata]:
        """Get metadata for all registered tools.

        Returns:
            List of ToolMetadata for introspection.
        """
        return list(cls._metadata.values())

    @classmethod
    def get_system_prompt_section(cls) -> str:
        """Generate the tools section for SYSTEM_PROMPT.

        Returns:
            Formatted markdown string describing all tools.
        """
        lines = ["## Available Tools", "", "You have access to the following tools:", ""]

        for meta in cls._metadata.values():
            lines.append(f"**{meta.name}**: {meta.description}")
            if meta.parameters:
                lines.append("Parameters:")
                for param, desc in meta.parameters.items():
                    lines.append(f"- {param}: {desc}")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def get_introspection_text(cls) -> str:
        """Generate formatted text for the list_tools tool.

        Returns:
            Markdown-formatted list of tools with parameters.
        """
        lines = ["# Available Tools\n"]

        for meta in cls._metadata.values():
            lines.append(f"## {meta.name}")
            lines.append(f"{meta.description}\n")
            if meta.parameters:
                lines.append("**Parameters:**")
                for param, desc in meta.parameters.items():
                    lines.append(f"- `{param}`: {desc}")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools. Useful for testing."""
        cls._tools.clear()
        cls._metadata.clear()


def registered_tool(
    name: str,
    description: str,
    parameters: dict[str, str] | None = None,
    parameter_types: dict[str, type] | None = None,
):
    """Decorator that registers a tool with both the SDK and the registry.

    This replaces the need to:
    1. Use @tool decorator
    2. Add to TOOL_REGISTRY manually
    3. Add to create_sdk_mcp_server manually
    4. Add to allowed_tools manually
    5. Update SYSTEM_PROMPT manually

    Args:
        name: Tool name
        description: Human-readable description
        parameters: Dict mapping param names to human descriptions
        parameter_types: Dict mapping param names to types (defaults to str for all)

    Example:
        @registered_tool(
            name="generate_report",
            description="Generate a professional equity research report",
            parameters={
                "company_name": "The company name (e.g., 'DocuSign')",
                "ticker": "The stock ticker (e.g., 'DOCU')",
            },
            parameter_types={
                "company_name": str,
                "ticker": str,
            },
        )
        async def generate_report(args: dict[str, Any]) -> dict[str, Any]:
            ...
    """
    params = parameters or {}
    types = parameter_types or {k: str for k in params.keys()}

    def decorator(func: Callable[..., Awaitable[dict[str, Any]]]):
        # Apply the SDK's @tool decorator
        decorated = tool(name, description, types)(func)

        # Register with our registry
        ToolRegistry.register(
            name=name,
            description=description,
            parameters=params,
            parameter_types=types,
            func=decorated,
        )

        return decorated

    return decorator
