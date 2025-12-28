---
name: equity-research-report
description: "Generate professional equity research reports in institutional analyst format. Use when the user requests financial analysis, stock analysis, investment reports, or equity research on publicly traded companies. Creates comprehensive reports with business analysis, valuation analysis, financial forecasts, risk assessment, and formatted tables following institutional research standards. Reports provide objective analysis without buy/hold/sell ratings or investment recommendations."
---

# Equity Research Report Generator

Generate institutional-quality equity research reports following professional analyst report format. This skill creates comprehensive financial analyses with proper structure, formatting, and professional presentation without providing investment ratings or recommendations.

## When to Use This Skill

Use this skill when users request:
- Financial analysis of publicly traded companies
- Investment research reports or equity analysis
- Stock analysis and performance assessment
- Comparative analysis with sector peers
- Valuation assessments and financial modeling

## Report Structure

Professional equity research reports follow this standard structure:

### 1. Cover Page & Summary
- Company name and ticker
- Report date and analyst information
- Current stock price and market data
- Executive summary (2-3 paragraphs)
- Key highlights (bullet points)

### 2. Financial Performance Analysis
- Recent quarterly/annual results
- Revenue analysis and growth trends
- Margin analysis (gross, operating, net)
- Profitability metrics and trends
- Cash flow generation
- Performance vs. consensus expectations

### 3. Business Analysis
- Strategic positioning and competitive advantages
- Growth drivers and catalysts
- Market opportunity and TAM analysis
- Key strengths and opportunities

### 4. Valuation Analysis
- Current valuation multiples (P/E, EV/EBITDA, P/S, etc.)
- Historical valuation comparison
- Peer group comparison
- DCF or other valuation methodologies
- Valuation range analysis
- Scenario analysis if applicable

### 5. Business Overview
- Company description
- Business segments
- Products/services
- Market position and competitive landscape
- Recent strategic initiatives

### 6. Financial Forecasts
- Revenue projections (quarterly and annual)
- Earnings estimates (EPS)
- Margin forecasts
- Key assumptions driving forecasts
- Comparison to consensus estimates

### 7. Risk Assessment
- Business and operational risks
- Key sensitivities
- Regulatory/legal risks
- Competitive threats
- Execution risks
- Macro risks

### 8. Key Takeaways
- Summary of financial position
- Notable opportunities and challenges
- Important catalysts to watch
- Key metrics to monitor
- Valuation considerations

### 9. Financial Tables
- Income statement summary
- Balance sheet highlights
- Cash flow statement
- Key metrics and ratios
- Quarterly trends

## Document Creation Workflow

Always follow these steps:

### Step 1: Research & Data Gathering

Collect comprehensive information using available tools:

```markdown
1. Use web_search to find:
   - Latest earnings reports and financial results
   - Recent news and company announcements
   - Analyst consensus estimates
   - Industry trends and competitive landscape
   - Management commentary

2. Use web_fetch to retrieve:
   - Investor relations presentations
   - SEC filings (10-K, 10-Q, 8-K)
   - Earnings transcripts
   - Company guidance

3. Gather quantitative data:
   - Historical financials (3-5 years)
   - Quarterly trends
   - Valuation multiples
   - Peer comparisons
   - Market data
```

### Step 2: Analysis & Synthesis

Analyze the data systematically:

1. **Financial Analysis**:
   - Calculate growth rates and margins
   - Identify trends and inflection points
   - Compare to historical performance
   - Benchmark against peers

2. **Qualitative Assessment**:
   - Evaluate management strategy
   - Assess competitive position
   - Analyze industry dynamics
   - Identify key risks and opportunities

3. **Valuation Work**:
   - Calculate current multiples
   - Compare to historical ranges
   - Develop valuation range methodology
   - Create scenarios (bull/base/bear)

### Step 3: Report Creation

**CRITICAL**: Before creating the document, read the docx skill:

```bash
# MANDATORY: Read the docx skill documentation
view /mnt/skills/public/docx/SKILL.md
```

Then create the Word document using docx-js:

1. Create a comprehensive JavaScript file using the Document library
2. Follow professional formatting standards:
   - Use proper headings hierarchy (HEADING_1, HEADING_2)
   - Apply consistent spacing (before/after paragraphs)
   - Use justified alignment for body paragraphs (see formatting section below)
   - Use bullet points appropriately
   - Bold key metrics and important data
   - Create professional tables for financial data
   - Maintain clean, scannable layout

3. Structure sections clearly:
   - Executive summary at the top
   - Logical flow from summary → analysis → key takeaways
   - Clear section breaks
   - Professional typography

### Step 4: Quality Checks

Before delivering, verify:
- All financial data is accurate and sourced
- Calculations are correct
- Analysis is objective and balanced
- Risk factors are comprehensive
- Citations are included where appropriate
- Document formatting is professional
- Tables are properly formatted
- No placeholder text remains

## Document Formatting Standards

### Typography
- Title: Large, bold, centered
- Headers: HEADING_1 for major sections, HEADING_2 for subsections
- Body text: Standard paragraph formatting with justified alignment for professional reports
- Key metrics: Bold for emphasis
- Spacing: Consistent before/after spacing for readability

### Paragraph Alignment

**IMPORTANT**: Use justified alignment (AlignmentType.JUSTIFIED) for professional body paragraphs to create clean, aligned edges on both left and right sides.

**Use justified alignment for:**
- Executive summary paragraphs
- Investment thesis sections
- Business overview narrative
- Risk analysis paragraphs
- All multi-sentence body paragraphs in main report sections
- Financial analysis prose
- Market analysis sections
- Company description paragraphs

**Do NOT use justified alignment for:**
- Titles and headers (use CENTER for titles, LEFT for section headers)
- Bullet points (use default LEFT alignment)
- Single-line metadata (dates, tickers, ratings, etc.)
- Table content
- Short labels or captions
- Lists or enumerated items

**Example formatting:**

```javascript
// Executive Summary - JUSTIFIED
new Paragraph({
    text: "Roblox reports Q3 2025 earnings on October 30, 2025, following a blowout Q2 that saw the platform reach 111.8 million daily active users (up 41% YoY) and bookings surge 51% to $1.44 billion. The company significantly raised full-year guidance, now expecting FY25 bookings of $5.87-$5.97 billion (up from $5.29-$5.36 billion), driven by viral experiences like \"Grow a Garden\" that attracted over 10 million daily users.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
}),

// Headers - LEFT aligned (default)
new Paragraph({
    text: "INVESTMENT THESIS",
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 }
}),

// Body paragraphs - JUSTIFIED
new Paragraph({
    text: "We maintain our Overweight rating with increased conviction following the company's exceptional Q2 performance. Management's ability to drive viral user engagement through strategic platform enhancements demonstrates the scalability of Roblox's ecosystem and validates our thesis that the company is capturing an increasing share of the global gaming content market.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
}),

// Bullet points - LEFT aligned (default)
new Paragraph({
    children: [
        new TextRun({ text: "User Growth: ", bold: true }),
        new TextRun("DAUs reached 111.8M (+41% YoY), significantly above consensus estimates")
    ],
    bullet: { level: 0 },
    spacing: { after: 50 }
})
```

### Tables
Create professional financial tables:
- Clear column headers
- Aligned data (numbers right-aligned)
- Borders for structure
- Alternating row colors optional
- Units clearly indicated ($M, %, etc.)

### Content Style
- **Executive summary**: Concise, 2-3 paragraphs maximum with justified alignment
- **Bullet points**: Use for key highlights, not full paragraphs (left-aligned)
- **Body paragraphs**: 3-5 sentences each, justified alignment, focused on single topic
- **Data presentation**: Always include context (growth rates, comparisons)
- **Citations**: Use  tags when based on web search results

## Analysis Framework

Provide objective analysis covering:

**Valuation Assessment:**
- Current valuation vs. historical ranges
- Peer comparison analysis
- Multiple valuation methodologies
- Scenario-based valuation ranges

Always include:
- Clear methodology for valuation analysis
- Historical context and trends
- Comparative analysis with peers
- Key catalysts and uncertainties

## Key Metrics to Include

### Valuation Metrics
- P/E ratio (trailing and forward)
- EV/EBITDA
- Price/Sales
- Price/Book
- EV/Sales
- PEG ratio
- Dividend yield (if applicable)

### Profitability Metrics
- Gross margin
- Operating margin
- Net margin
- EBITDA margin
- ROIC
- ROE
- ROA

### Growth Metrics
- Revenue growth (YoY, QoQ)
- EPS growth
- EBITDA growth
- User/customer growth (if applicable)
- Market share trends

### Financial Health
- Debt/Equity ratio
- Net Debt/EBITDA
- Current ratio
- Interest coverage
- Free cash flow
- Free cash flow yield

## Common Pitfalls to Avoid

1. **Insufficient data**: Always gather comprehensive financial data before starting
2. **Missing risks**: Include both company-specific and macro risks
3. **Biased analysis**: Maintain objectivity without making investment recommendations
4. **Poor formatting**: Maintain professional, clean document structure with proper alignment
5. **Lack of peer comparison**: Always benchmark against competitors
6. **Omitting sources**: Cite data sources appropriately
7. **Ignoring recent news**: Include latest developments and their impact
8. **Inconsistent alignment**: Use justified text for body paragraphs, not for headers or bullets

## Example Report Sections

### Example: Business Analysis (Good)

```
Business Analysis

[Company] is executing on its strategic transformation, with strong momentum in [key growth driver]. The company's [competitive advantage] positions it to compete effectively in the growing [market] opportunity, projected to reach $XXB by 2028.

Key business highlights:

• Revenue Growth: [Company] delivered X% organic growth in QX, driven by [specific drivers]
• Margin Expansion: Operating margins improved XXX bps YoY to XX% through [cost initiatives]
• Market Position: Leading XX% share in [market segment], with clear differentiation via [advantage]
• Valuation: Trading at XX.Xx forward P/E vs. XX.Xx historical average and XX.Xx peer median

Near-term catalysts to monitor include [specific catalysts], which may significantly impact the company's trajectory.
```

**Formatting Note**: The narrative paragraphs should use JUSTIFIED alignment. The bullet points should use default LEFT alignment.

### Example: Risk Assessment (Good)

```
Risk Assessment

1. Competitive Intensity: Increasing competition from [competitors] could pressure pricing and market share. [Company]'s XX% market share faces threats from [specific competitive dynamics].

2. Execution Risk: The company's strategic transformation depends on successful [initiative]. Delays or challenges could impact growth trajectory and operational performance.

3. Macro Headwinds: [Company] derives XX% of revenue from [segment/geography] which remains exposed to [macro factor]. Continued weakness could pressure near-term results.

4. Valuation Sensitivity: At XX.Xx forward P/E, the stock trades above its historical average of XX.Xx. Multiple compression could occur if growth disappoints or sector sentiment shifts.

5. Regulatory Risk: [Specific regulatory developments] could impact [aspect of business], creating uncertainty around [financial impact].
```

**Formatting Note**: All the risk description paragraphs should use JUSTIFIED alignment for professional presentation.

## Output Location & Formats

Reports are generated in **two formats** for flexibility and future OneNote integration:

### Primary Format: HTML (OneNote-Compatible)
```
outputs/[CompanyName]_[Ticker]_Analysis.html
```
- Viewable directly in the web UI
- Uses only OneNote-compatible HTML elements
- Ready for future Microsoft Graph API integration

### Secondary Format: DOCX (Downloadable)
```
outputs/[CompanyName]_[Ticker]_Analysis.docx
```
- Professional Word document for offline use
- Institutional formatting with justified paragraphs
- Suitable for sharing and printing

Example files:
- `outputs/Dropbox_DBX_Analysis.html` (view in browser)
- `outputs/Dropbox_DBX_Analysis.docx` (download)

## Best Practices

1. **Start with research**: Gather all data before writing
2. **Be objective**: Present balanced view with both opportunities and risks
3. **Use specific data**: Include actual numbers, growth rates, and comparisons
4. **Cite sources**: Use  tags for data from web searches
5. **Professional tone**: Maintain institutional-quality writing
6. **Balanced analysis**: Provide objective assessment without investment recommendations
7. **Visual hierarchy**: Use formatting to guide reader through report
8. **Proper alignment**: Use justified text for body paragraphs to match institutional report standards
9. **Quality over speed**: Take time to create comprehensive analysis

## Example Usage

**User request**: "Analyze Microsoft's latest earnings and provide a comprehensive financial report"

**Workflow**:
1. Search for Microsoft's latest earnings report
2. Gather financial data, analyst estimates, and recent news
3. Analyze performance vs. expectations and historical trends
4. Assess competitive position and growth drivers
5. Calculate valuation metrics and compare to peers
6. Develop comprehensive business and valuation analysis
7. Call the `generate_report` tool with structured sections
8. Reports saved in both HTML and DOCX formats
9. HTML viewable immediately in UI, DOCX available for download

## OneNote Integration Roadmap

The HTML output format is designed for future OneNote integration:

### Supported HTML Elements
| Element | Usage |
|---------|-------|
| `<h1>` - `<h3>` | Section headers |
| `<p>` | Body paragraphs (with `text-align: justify`) |
| `<ul>`, `<ol>`, `<li>` | Bullet and numbered lists |
| `<table>`, `<tr>`, `<td>`, `<th>` | Financial data tables |
| `<strong>`, `<b>` | Bold text for labels |
| `<em>`, `<i>` | Italic text for emphasis |

### Elements NOT Used (OneNote incompatible)
- `<div>`, `<span>` with complex styling
- Custom JavaScript
- External CSS files
- HTML5 semantic elements (`<section>`, `<article>`, etc.)

## Notes

- This skill creates institutional-quality research reports suitable for professional analysis
- Reports should be comprehensive (typically 8-15 pages)
- Always base analysis on current, factual data from reliable sources
- Include disclaimers that report is for informational purposes only
- Maintain objective, analytical tone throughout
- Focus on thorough analysis and balanced assessment
- Do not provide buy/hold/sell ratings or specific investment recommendations
- HTML format uses inline styles for viewer display while remaining OneNote-compatible
