"""HTML report generation for equity research reports.

Generates OneNote-compatible HTML using only supported elements:
- <h1>-<h6>, <p>, <ul>, <ol>, <li>, <table>, <tr>, <td>, <th>
- <b>, <i>, <em>, <strong> for text formatting
- Inline <style> for viewer display (OneNote ignores CSS)
"""

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any


def _get_outputs_dir() -> Path:
    """Get the outputs directory path."""
    from research_agent.config import get_outputs_dir

    return get_outputs_dir()


def _escape(text: str) -> str:
    """Escape HTML special characters."""
    return escape(str(text)) if text else ""


def _render_bullets(items: list[str]) -> str:
    """Render a list of items as HTML bullet points."""
    if not items:
        return ""
    bullets = "\n".join(f"        <li>{_escape(item)}</li>" for item in items)
    return f"    <ul>\n{bullets}\n    </ul>"


def _render_risks(risks: list[dict[str, str] | str]) -> str:
    """Render risk items with titles and descriptions."""
    if not risks:
        return ""

    html_parts = []
    for i, risk in enumerate(risks, 1):
        if isinstance(risk, dict):
            title = _escape(risk.get("title", f"Risk {i}"))
            description = _escape(risk.get("description", ""))
            html_parts.append(f"""    <h3>{i}. {title}</h3>
    <p style="text-align: justify;">{description}</p>""")
        else:
            html_parts.append(f"    <p><strong>{i}.</strong> {_escape(risk)}</p>")

    return "\n".join(html_parts)


def generate_html_report(
    company_name: str,
    ticker: str,
    sections: dict[str, Any],
) -> str:
    """Generate an HTML equity research report.

    Uses only OneNote-compatible HTML elements to ensure future
    integration compatibility.

    Args:
        company_name: Company name (e.g., "DocuSign")
        ticker: Stock ticker (e.g., "DOCU")
        sections: Dict with report sections:
            - executive_summary: str
            - key_highlights: list[str]
            - financial_analysis: str
            - business_analysis: str
            - valuation: str
            - risks: list[dict] with 'title' and 'description'
            - key_takeaways: list[str]

    Returns:
        Complete HTML document as a string.
    """
    report_date = datetime.now().strftime("%B %d, %Y")

    # Build sections
    executive_summary = ""
    if sections.get("executive_summary"):
        executive_summary = f"""
    <h2>EXECUTIVE SUMMARY</h2>
    <p style="text-align: justify;">{_escape(sections["executive_summary"])}</p>
"""

    key_highlights = ""
    if sections.get("key_highlights"):
        key_highlights = f"""
    <h2>KEY HIGHLIGHTS</h2>
{_render_bullets(sections["key_highlights"])}
"""

    financial_analysis = ""
    if sections.get("financial_analysis"):
        financial_analysis = f"""
    <h2>FINANCIAL ANALYSIS</h2>
    <p style="text-align: justify;">{_escape(sections["financial_analysis"])}</p>
"""

    business_analysis = ""
    if sections.get("business_analysis"):
        business_analysis = f"""
    <h2>BUSINESS ANALYSIS</h2>
    <p style="text-align: justify;">{_escape(sections["business_analysis"])}</p>
"""

    valuation = ""
    if sections.get("valuation"):
        valuation = f"""
    <h2>VALUATION ANALYSIS</h2>
    <p style="text-align: justify;">{_escape(sections["valuation"])}</p>
"""

    risks = ""
    if sections.get("risks"):
        risks = f"""
    <h2>KEY RISKS</h2>
{_render_risks(sections["risks"])}
"""

    key_takeaways = ""
    if sections.get("key_takeaways"):
        key_takeaways = f"""
    <h2>KEY TAKEAWAYS</h2>
{_render_bullets(sections["key_takeaways"])}
"""

    # Assemble complete HTML document
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{_escape(company_name)} ({_escape(ticker)}) - Equity Research Report</title>
    <style>
        body {{
            font-family: Calibri, Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #1a202c;
        }}
        h1 {{
            color: #1a365d;
            border-bottom: 2px solid #3182ce;
            padding-bottom: 10px;
            text-align: center;
        }}
        h2 {{
            color: #2c5282;
            margin-top: 30px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #2d3748;
            margin-top: 20px;
        }}
        p {{
            margin: 10px 0;
        }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f7fafc;
            font-weight: bold;
        }}
        .subtitle {{
            text-align: center;
            color: #4a5568;
            margin-bottom: 20px;
        }}
        .meta {{
            margin-bottom: 30px;
        }}
        .disclaimer {{
            font-style: italic;
            color: #718096;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <h1>{_escape(company_name)} ({_escape(ticker)})</h1>
    <p class="subtitle">Equity Research Report</p>

    <p class="meta"><strong>Report Date:</strong> {report_date}</p>
{executive_summary}{key_highlights}{financial_analysis}{business_analysis}{valuation}{risks}{key_takeaways}
    <p class="disclaimer">
        <strong>DISCLAIMER:</strong> This analysis is for informational purposes only
        and does not constitute investment advice. Always conduct independent due
        diligence before making investment decisions. Past performance is not
        indicative of future results.
    </p>
</body>
</html>"""

    return html


def create_html_report(
    company_name: str,
    ticker: str,
    sections: dict[str, Any],
) -> Path:
    """Create an HTML report file and save it to the outputs directory.

    Args:
        company_name: Company name (e.g., "DocuSign")
        ticker: Stock ticker (e.g., "DOCU")
        sections: Dict with report sections

    Returns:
        Path to the saved HTML file.
    """
    html_content = generate_html_report(company_name, ticker, sections)

    filename = f"{company_name.replace(' ', '_')}_{ticker}_Analysis.html"
    output_path = _get_outputs_dir() / filename
    output_path.write_text(html_content, encoding="utf-8")

    return output_path
