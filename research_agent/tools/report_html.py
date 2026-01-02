"""HTML report generation for equity research reports.

Generates professional sellside-style HTML reports with:
- Clean typography and responsive design
- Proper markdown-to-HTML conversion (bold, lists, headers)
- Styled sections for executive summary, highlights, risks, takeaways
- Print-friendly styling
"""

import re
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


def _markdown_to_html(text: str) -> str:
    """Convert markdown formatting to HTML.

    Handles:
    - **bold** -> <strong>bold</strong>
    - *italic* -> <em>italic</em>
    - Preserves already-escaped HTML
    """
    if not text:
        return ""

    # First escape HTML special chars
    text = _escape(text)

    # Convert **bold** to <strong>
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # Convert *italic* to <em> (but not if it's part of **)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', text)

    return text


def _render_bullets(items: list[str]) -> str:
    """Render a list of items as HTML bullet points."""
    if not items:
        return ""

    bullets = []
    for item in items:
        item = str(item).strip()
        if item:
            # Convert markdown in list items
            item_html = _markdown_to_html(item)
            bullets.append(f"                <li>{item_html}</li>")

    return "\n".join(bullets)


def _render_risks(risks: list[dict[str, str] | str]) -> str:
    """Render risk items with titles and descriptions."""
    if not risks:
        return ""

    html_parts = []
    for i, risk in enumerate(risks, 1):
        if isinstance(risk, dict):
            title = _escape(risk.get("title", f"Risk {i}"))
            description = _markdown_to_html(risk.get("description", ""))
            html_parts.append(f"""            <div class="risk-item">
                <h3>{i}. {title}</h3>
                <p>{description}</p>
            </div>""")
        else:
            # String risk - try to split on colon for title/description
            risk_str = str(risk).strip()
            if ':' in risk_str:
                parts = risk_str.split(':', 1)
                title = _escape(parts[0].strip())
                desc = _markdown_to_html(parts[1].strip())
            else:
                title = f"Risk {i}"
                desc = _markdown_to_html(risk_str)

            html_parts.append(f"""            <div class="risk-item">
                <h3>{i}. {title}</h3>
                <p>{desc}</p>
            </div>""")

    return "\n".join(html_parts)


def _render_analysis_section(text: str, title: str) -> str:
    """Render an analysis section with proper markdown handling.

    Handles:
    - Paragraphs separated by blank lines
    - Bullet lists (lines starting with - or •)
    - Bold text (**text**)
    - Section subheaders (**Header:**)
    """
    if not text:
        return ""

    lines = []
    lines.append(f"        <h2>{_escape(title)}</h2>")

    # Split into paragraphs
    paragraphs = text.split('\n\n')

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Check if this paragraph is a bullet list
        para_lines = para.split('\n')
        is_list = all(
            line.strip().startswith(('-', '•', '*')) or not line.strip()
            for line in para_lines
            if line.strip()
        )

        if is_list:
            # Render as a list
            lines.append("        <ul>")
            for line in para_lines:
                line = line.strip()
                if line:
                    # Remove bullet marker
                    line = re.sub(r'^[-•*]\s*', '', line)
                    lines.append(f"            <li>{_markdown_to_html(line)}</li>")
            lines.append("        </ul>")
        else:
            # Check if it's a subheader (starts with **Something:**)
            if re.match(r'^\*\*[^*]+:\*\*', para):
                # It's a subheader, render with line breaks
                html_content = _markdown_to_html(para)
                # Replace newlines with <br>
                html_content = html_content.replace('\n', '<br>\n            ')
                lines.append(f"        <p>{html_content}</p>")
            else:
                # Regular paragraph
                html_content = _markdown_to_html(para)
                lines.append(f"        <p>{html_content}</p>")

    return "\n".join(lines)


def generate_html_report(
    company_name: str,
    ticker: str,
    sections: dict[str, Any],
) -> str:
    """Generate a professional HTML equity research report.

    Args:
        company_name: Company name (e.g., "DocuSign")
        ticker: Stock ticker (e.g., "DOCU")
        sections: Dict with report sections:
            - executive_summary: str
            - key_highlights: list[str]
            - financial_analysis: str
            - business_analysis: str
            - valuation: str
            - risks: list[dict] with 'title' and 'description', or list[str]
            - key_takeaways: list[str]

    Returns:
        Complete HTML document as a string.
    """
    report_date = datetime.now().strftime("%B %d, %Y")

    # Start building HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_escape(company_name)} ({_escape(ticker)}) - Equity Research Report</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Calibri, Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            line-height: 1.7;
            color: #1a202c;
            background: #fafbfc;
        }}
        .report-container {{
            background: white;
            padding: 50px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .report-header {{
            text-align: center;
            border-bottom: 3px solid #1a365d;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        .report-header h1 {{
            color: #1a365d;
            font-size: 2.5rem;
            margin: 0 0 10px 0;
            font-weight: 700;
        }}
        .report-header .subtitle {{
            color: #4a5568;
            font-size: 1.2rem;
            margin: 0 0 15px 0;
        }}
        .report-header .meta {{ color: #718096; font-size: 0.95rem; }}
        h2 {{
            color: #1a365d;
            font-size: 1.3rem;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        h3 {{ color: #2d3748; font-size: 1.1rem; margin: 25px 0 10px 0; }}
        p {{ margin: 15px 0; text-align: justify; color: #2d3748; }}
        ul, ol {{ margin: 15px 0; padding-left: 25px; }}
        li {{ margin: 10px 0; color: #2d3748; line-height: 1.6; }}
        strong {{ color: #2c5282; }}
        .executive-summary {{
            background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%);
            border-left: 4px solid #3182ce;
            padding: 25px 30px;
            margin: 30px 0;
            border-radius: 0 8px 8px 0;
        }}
        .executive-summary h2 {{ color: #2c5282; margin-top: 0; border-bottom: none; }}
        .executive-summary p {{ font-size: 1.05rem; margin-bottom: 0; }}
        .highlights {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 25px 30px;
            margin: 30px 0;
        }}
        .highlights h2 {{ color: #2c5282; margin-top: 0; }}
        .highlights ul {{ list-style: none; padding: 0; }}
        .highlights li {{
            padding: 12px 0 12px 35px;
            position: relative;
            border-bottom: 1px solid #e2e8f0;
        }}
        .highlights li:last-child {{ border-bottom: none; }}
        .highlights li::before {{
            content: "\\2713";
            position: absolute;
            left: 0;
            color: #38a169;
            font-weight: bold;
        }}
        .risk-item {{
            margin: 20px 0;
            padding: 20px;
            background: #fff5f5;
            border-left: 4px solid #e53e3e;
            border-radius: 0 8px 8px 0;
        }}
        .risk-item h3 {{ color: #c53030; margin: 0 0 10px 0; }}
        .risk-item p {{ margin: 0; color: #4a5568; }}
        .takeaways {{
            background: linear-gradient(135deg, #f0fff4 0%, #e6ffed 100%);
            border-radius: 8px;
            padding: 25px 30px;
            margin: 30px 0;
        }}
        .takeaways h2 {{ color: #276749; margin-top: 0; }}
        .takeaways ul {{ list-style: none; padding: 0; }}
        .takeaways li {{
            padding: 10px 0 10px 30px;
            position: relative;
        }}
        .takeaways li::before {{
            content: "\\2794";
            position: absolute;
            left: 0;
            color: #38a169;
        }}
        .disclaimer {{
            margin-top: 50px;
            padding: 25px;
            background: #f7fafc;
            border-radius: 8px;
            font-size: 0.85rem;
            color: #718096;
            border: 1px solid #e2e8f0;
        }}
        .analysis-section {{ margin: 30px 0; }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .report-container {{ box-shadow: none; padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1>{_escape(company_name)} ({_escape(ticker)})</h1>
            <p class="subtitle">Equity Research Report</p>
            <p class="meta"><strong>Report Date:</strong> {report_date}</p>
        </div>
"""

    # Executive Summary
    if sections.get("executive_summary"):
        summary = _markdown_to_html(sections["executive_summary"])
        html += f"""
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <p>{summary}</p>
        </div>
"""

    # Key Highlights
    if sections.get("key_highlights"):
        html += f"""
        <div class="highlights">
            <h2>Key Highlights</h2>
            <ul>
{_render_bullets(sections["key_highlights"])}
            </ul>
        </div>
"""

    # Financial Analysis
    if sections.get("financial_analysis"):
        html += f"""
        <div class="analysis-section">
{_render_analysis_section(sections["financial_analysis"], "Financial Analysis")}
        </div>
"""

    # Business Analysis
    if sections.get("business_analysis"):
        html += f"""
        <div class="analysis-section">
{_render_analysis_section(sections["business_analysis"], "Business Analysis")}
        </div>
"""

    # Valuation Analysis
    valuation = sections.get("valuation") or sections.get("valuation_analysis")
    if valuation:
        html += f"""
        <div class="analysis-section">
{_render_analysis_section(valuation, "Valuation Analysis")}
        </div>
"""

    # Key Risks
    if sections.get("risks"):
        html += f"""
        <div class="risks-section">
            <h2>Key Risks</h2>
{_render_risks(sections["risks"])}
        </div>
"""

    # Key Takeaways
    if sections.get("key_takeaways"):
        html += f"""
        <div class="takeaways">
            <h2>Key Takeaways</h2>
            <ul>
{_render_bullets(sections["key_takeaways"])}
            </ul>
        </div>
"""

    # Disclaimer and close
    html += """
        <div class="disclaimer">
            <strong>DISCLAIMER:</strong> This analysis is for informational purposes only
            and does not constitute investment advice. Always conduct independent due
            diligence before making investment decisions. Past performance is not
            indicative of future results.
        </div>
    </div>
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
