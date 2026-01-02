"""Research agent tools.

Tools are registered via ToolRegistry.register_all() which should be called
once at application startup. This avoids relying on import side-effects.

Usage:
    from research_agent.tools.registry import ToolRegistry
    ToolRegistry.register_all()  # Call once at startup

    # Then access tools via registry
    tools = ToolRegistry.get_tools()
"""

from research_agent.tools.registry import ToolRegistry, registered_tool

__all__ = [
    "ToolRegistry",
    "registered_tool",
]
