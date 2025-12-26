"""Research agent tools.

Tools are self-registering via the @registered_tool decorator.
Import this module to ensure all tools are registered.
"""

from research_agent.tools.registry import ToolRegistry, registered_tool

# Import tools to trigger registration
from research_agent.tools.report_tool import generate_report
from research_agent.tools.introspection import list_tools

__all__ = [
    "ToolRegistry",
    "registered_tool",
    "generate_report",
    "list_tools",
]
