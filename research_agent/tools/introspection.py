"""Tool introspection for the Research Agent.

Provides a list_tools tool that allows the agent to report its own MCP tool capabilities.
"""

from typing import Any

from claude_agent_sdk import tool


# Tool registry - maintained centrally for introspection
TOOL_REGISTRY = [
    {
        "name": "generate_report",
        "description": "Generate a professional equity research report as a Word document (.docx)",
        "parameters": {
            "company_name": "The company name (e.g., 'DocuSign')",
            "ticker": "The stock ticker (e.g., 'DOCU')",
            "sections": "JSON string with report sections (executive_summary, key_highlights, financial_analysis, business_analysis, valuation, risks, key_takeaways)"
        }
    },
    {
        "name": "list_tools",
        "description": "List all available MCP tools and their capabilities",
        "parameters": {}
    }
]


@tool(
    "list_tools",
    "List all available MCP tools the agent can use, with descriptions and parameters",
    {},
)
async def list_tools(args: dict[str, Any]) -> dict[str, Any]:
    """Return formatted list of available MCP tools."""
    lines = ["# Available Tools\n"]

    for t in TOOL_REGISTRY:
        lines.append(f"## {t['name']}")
        lines.append(f"{t['description']}\n")
        if t['parameters']:
            lines.append("**Parameters:**")
            for param, desc in t['parameters'].items():
                lines.append(f"- `{param}`: {desc}")
        lines.append("")

    return {
        "content": [{"type": "text", "text": "\n".join(lines)}]
    }
