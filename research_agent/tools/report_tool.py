"""Report generation tool for the Investment Research Agent.

This tool generates professional equity research reports in both Word (.docx)
and HTML formats. The HTML format uses OneNote-compatible elements for future
integration compatibility.
"""

import json
from pathlib import Path
from typing import Any

from research_agent.tools.registry import registered_tool
from research_agent.tools.report_html import create_html_report
from research_agent.tools.report_builder import build_docx_report


def _get_outputs_dir() -> Path:
    """Get the outputs directory path."""
    from research_agent.config import get_outputs_dir
    return get_outputs_dir()


@registered_tool(
    name="generate_report",
    description=(
        "Generate a professional equity research report in both Word (.docx) and HTML formats. "
        "The HTML format is OneNote-compatible for future integration. "
        "Use this after analyzing a company to create a formal report the user can view and download."
    ),
    parameters={
        "company_name": "The company name (e.g., 'DocuSign')",
        "ticker": "The stock ticker (e.g., 'DOCU')",
        "sections": (
            "JSON string with report sections: executive_summary, key_highlights, "
            "financial_analysis, business_analysis, valuation, risks, key_takeaways"
        ),
    },
    parameter_types={
        "company_name": str,
        "ticker": str,
        "sections": str,
    },
)
async def generate_report(args: dict[str, Any]) -> dict[str, Any]:
    """Generate an equity research report in HTML and DOCX formats.

    Args:
        args: Dict with:
            - company_name: Company name (e.g., "DocuSign")
            - ticker: Stock ticker (e.g., "DOCU")
            - sections: JSON string with report sections:
                {
                    "executive_summary": "...",
                    "key_highlights": ["...", "..."],
                    "financial_analysis": "...",
                    "business_analysis": "...",
                    "valuation": "...",
                    "risks": [{"title": "...", "description": "..."}, ...],
                    "key_takeaways": ["...", "..."]
                }

    Returns:
        Tool result with success/failure message and paths to both files.
    """
    try:
        company_name = args.get("company_name", "")
        ticker = args.get("ticker", "")
        sections_json = args.get("sections", "{}")

        if not company_name or not ticker:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: company_name and ticker are required."
                }],
                "is_error": True,
            }

        # Parse sections JSON
        try:
            sections = json.loads(sections_json)
        except json.JSONDecodeError as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error parsing sections JSON: {e}"
                }],
                "is_error": True,
            }

        # Generate HTML report (always available)
        html_path = create_html_report(company_name, ticker, sections)

        # Try to generate DOCX report using Builder (may fail if python-docx not installed)
        docx_path = None
        docx_error = None
        try:
            docx_path = build_docx_report(
                company_name, ticker, sections, _get_outputs_dir()
            )
        except ImportError as e:
            docx_error = str(e)

        # Build response message
        if docx_path:
            return {
                "content": [{
                    "type": "text",
                    "text": (
                        f"Reports generated successfully!\n\n"
                        f"HTML (viewable): {html_path}\n"
                        f"DOCX (downloadable): {docx_path}"
                    )
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": (
                        f"HTML report generated successfully!\n\n"
                        f"Saved to: {html_path}\n\n"
                        f"Note: DOCX generation skipped - {docx_error}"
                    )
                }]
            }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error generating report: {e}"
            }],
            "is_error": True,
        }
