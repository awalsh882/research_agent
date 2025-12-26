# Equity Research Report Formatting Reference

This document provides detailed formatting guidelines and code examples for creating professional equity research reports using docx-js.

## Complete Document Template

```javascript
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle } = require("docx");
const fs = require("fs");

const doc = new Document({
    sections: [{
        properties: {},
        children: [
            // Title page elements
            // Body sections
            // Tables
            // Disclaimer
        ]
    }]
});

Packer.toBuffer(doc).then((buffer) => {
    fs.writeFileSync("/mnt/user-data/outputs/Company_Ticker_Analysis.docx", buffer);
});
```

## Section Templates

### Title and Header

```javascript
new Paragraph({
    text: "COMPANY NAME (TICKER)",
    heading: HeadingLevel.TITLE,
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 }
}),
new Paragraph({
    text: "Equity Research Report",
    alignment: AlignmentType.CENTER,
    spacing: { after: 400 }
}),
new Paragraph({
    children: [
        new TextRun({ text: "Report Date: ", bold: true }),
        new TextRun("October 21, 2025")
    ],
    spacing: { after: 100 }
}),
new Paragraph({
    children: [
        new TextRun({ text: "Current Price: ", bold: true }),
        new TextRun("$XX.XX")
    ],
    spacing: { after: 400 }
})
```

### Executive Summary (WITH JUSTIFIED ALIGNMENT)

```javascript
new Paragraph({
    text: "EXECUTIVE SUMMARY",
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 }
}),
// Use JUSTIFIED alignment for body paragraphs
new Paragraph({
    text: "Roblox reports Q3 2025 earnings on October 30, 2025, following a blowout Q2 that saw the platform reach 111.8 million daily active users (up 41% YoY) and bookings surge 51% to $1.44 billion. The company significantly raised full-year guidance, now expecting FY25 bookings of $5.87-$5.97 billion (up from $5.29-$5.36 billion), driven by viral experiences like \"Grow a Garden\" that attracted over 10 million daily users. Management attributed the momentum to strategic investments in infrastructure, discovery, and the virtual economy, positioning Roblox to capture 10% of the $180 billion global gaming content market.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
}),
new Paragraph({
    text: "For Q3, Roblox guides to bookings of $1.59-$1.64 billion (41-45% growth), well above the prior consensus of $1.33 billion. While analysts expect continued strong user engagement and bookings growth, investor focus will center on whether recent viral hits sustain momentum, how the platform navigates mounting child safety lawsuits, and management's confidence in achieving long-term profitability targets while maintaining rapid growth investments.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
}),
new Paragraph({
    children: [
        new TextRun({ text: "Business Analysis: ", bold: true }),
        new TextRun("Following the company's exceptional Q2 performance, management's ability to drive viral user engagement through strategic platform enhancements demonstrates the scalability of Roblox's ecosystem and indicates that the company is capturing an increasing share of the global gaming content market.")
    ],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 400 }
})
```

### Key Highlights Section (Bullets Use LEFT Alignment)

```javascript
new Paragraph({
    text: "KEY HIGHLIGHTS",
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 }
}),
new Paragraph({
    text: "Recent Financial Performance:",
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 }
}),
// Bullet points use default LEFT alignment, NOT justified
new Paragraph({
    children: [
        new TextRun({ text: "Revenue: ", bold: true }),
        new TextRun("$1,081M (+21% YoY growth)")
    ],
    bullet: { level: 0 },
    spacing: { after: 50 }
}),
new Paragraph({
    children: [
        new TextRun({ text: "Bookings: ", bold: true }),
        new TextRun("$1,438M (+51% YoY) - significantly above consensus")
    ],
    bullet: { level: 0 },
    spacing: { after: 50 }
}),
new Paragraph({
    children: [
        new TextRun({ text: "DAUs: ", bold: true }),
        new TextRun("111.8M (+41% YoY) - platform reaching new scale")
    ],
    bullet: { level: 0 },
    spacing: { after: 300 }
})
```

### Major Section Heading with Justified Body

```javascript
new Paragraph({
    text: "REVENUE ANALYSIS & GROWTH TRAJECTORY",
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 }
}),
// Use JUSTIFIED alignment for analytical paragraphs
new Paragraph({
    text: "Roblox delivered exceptional revenue performance in Q2 2025, with reported revenue of $1.08 billion representing 21% year-over-year growth. More importantly, bookings—a more relevant metric for the platform's health as it reflects user spending before deferrals—surged 51% to $1.44 billion, significantly outpacing both Street expectations and the company's own guidance. This outperformance was driven by a combination of robust user growth, higher engagement per user, and improved monetization of the platform's virtual economy.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
}),
new Paragraph({
    text: "The bookings acceleration reflects the network effects inherent in Roblox's platform model. As the user base expanded to 111.8 million daily active users, creators responded by developing more engaging experiences, which in turn attracted more users and drove higher spending. The viral success of experiences like \"Grow a Garden,\" which attracted over 10 million daily users at its peak, demonstrates the platform's ability to generate cultural moments that transcend traditional gaming boundaries.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
})
```

### Subsection Heading with Justified Analysis

```javascript
new Paragraph({
    text: "Quarterly Revenue Trends:",
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 }
}),
// Analysis paragraphs use JUSTIFIED alignment
new Paragraph({
    text: "Over the past eight quarters, Roblox has demonstrated consistent acceleration in both revenue and bookings growth. The company's revenue CAGR has improved from low-teens percentages in early 2024 to over 20% currently, while bookings growth has accelerated even more dramatically, reaching the 40-50% range. This divergence between revenue and bookings reflects the company's increasing focus on expanding its user base and engagement before optimizing for revenue recognition, a strategy that prioritizes long-term platform health over near-term financial metrics.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
})
```

### Risk Section with Justified Paragraphs

```javascript
new Paragraph({
    text: "KEY RISKS TO RATING",
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 }
}),
new Paragraph({
    text: "1. Child Safety and Regulatory Risk",
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 }
}),
// Risk descriptions use JUSTIFIED alignment
new Paragraph({
    text: "Roblox faces mounting legal and regulatory scrutiny regarding child safety on its platform. The company currently faces multiple lawsuits from families alleging inadequate protection of minors from inappropriate content and predatory behavior. These lawsuits could result in significant financial penalties, mandatory platform changes that reduce user engagement, or reputational damage that impacts user acquisition. Additionally, regulators in multiple jurisdictions are considering legislation that would impose stricter requirements on platforms serving children, which could increase compliance costs and limit certain monetization strategies.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 300 }
}),
new Paragraph({
    text: "2. Viral Content Sustainability",
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 100 }
}),
new Paragraph({
    text: "The company's recent bookings acceleration was significantly driven by viral experiences like \"Grow a Garden,\" which attracted over 10 million daily users. However, viral phenomena are inherently unpredictable and temporary. If Roblox fails to generate new viral hits at a similar cadence, or if user attention shifts away from the platform to competing entertainment options, growth could decelerate rapidly. The sustainability of viral-driven growth remains a key uncertainty, particularly as the platform matures and faces increased competition for users' time and spending.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 300 }
})
```

### Key Takeaways with Justified Text

```javascript
new Paragraph({
    text: "KEY TAKEAWAYS",
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 }
}),
// Use JUSTIFIED alignment for summary narrative
new Paragraph({
    text: "The company's exceptional Q2 performance demonstrates that Roblox is capturing an increasing share of the global gaming content market through its unique user-generated content model. While near-term volatility around viral content sustainability and child safety litigation presents risks, the platform's network effects and expanding global reach position it for continued growth opportunities. The long-term value proposition centers on Roblox's 80 million monthly creators and the compounding benefits of its investments in infrastructure and discovery algorithms.",
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
}),
new Paragraph({
    children: [
        new TextRun({ text: "Key Catalysts: ", bold: true }),
        new TextRun("Q3 earnings results on October 30, 2025; continued user and engagement growth; successful international expansion; new creator monetization tools; and potential inclusion in major market indices as the company matures.")
    ],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 400 }
})
```

## Alignment Guidelines Summary

**Use AlignmentType.JUSTIFIED for:**
- Executive summary paragraphs
- Business analysis sections
- Business overview narratives
- Financial analysis prose
- Risk description paragraphs
- Market analysis sections
- Key takeaways text
- Any multi-sentence body paragraph in main sections

**Use AlignmentType.CENTER for:**
- Document title
- Subtitle/report type

**Use AlignmentType.LEFT (default) for:**
- All section headings (HEADING_1, HEADING_2)
- Bullet points and lists
- Single-line metadata (dates, ratings, etc.)
- Table content
- Labels and short captions

**Do NOT use justified alignment for:**
- Any heading or subheading
- Bullet point lists
- Tables
- Single-line items
- Metadata fields

## Financial Tables

### Simple Financial Summary Table

```javascript
new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
        top: { style: BorderStyle.SINGLE, size: 1 },
        bottom: { style: BorderStyle.SINGLE, size: 1 },
        left: { style: BorderStyle.SINGLE, size: 1 },
        right: { style: BorderStyle.SINGLE, size: 1 },
        insideHorizontal: { style: BorderStyle.SINGLE, size: 1 },
        insideVertical: { style: BorderStyle.SINGLE, size: 1 }
    },
    rows: [
        new TableRow({
            children: [
                new TableCell({
                    children: [new Paragraph({ text: "Metric", bold: true })],
                    width: { size: 40, type: WidthType.PERCENTAGE }
                }),
                new TableCell({
                    children: [new Paragraph({ text: "Q2 2025 Actual", bold: true })],
                    width: { size: 20, type: WidthType.PERCENTAGE }
                }),
                new TableCell({
                    children: [new Paragraph({ text: "Q3 2025E (Consensus)", bold: true })],
                    width: { size: 20, type: WidthType.PERCENTAGE }
                }),
                new TableCell({
                    children: [new Paragraph({ text: "Company Guidance", bold: true })],
                    width: { size: 20, type: WidthType.PERCENTAGE }
                })
            ]
        }),
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph("Revenue")] }),
                new TableCell({ children: [new Paragraph("$1,081M (+21% YoY)")] }),
                new TableCell({ children: [new Paragraph("$1,691M")] }),
                new TableCell({ children: [new Paragraph("$1,110-$1,160M")] })
            ]
        }),
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph("Bookings")] }),
                new TableCell({ children: [new Paragraph("$1,438M (+51% YoY)")] }),
                new TableCell({ children: [new Paragraph("$1,691M")] }),
                new TableCell({ children: [new Paragraph("$1,590-$1,640M")] })
            ]
        }),
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph("DAUs")] }),
                new TableCell({ children: [new Paragraph("111.8M (+41% YoY)")] }),
                new TableCell({ children: [new Paragraph("~115-120M (est.)")] }),
                new TableCell({ children: [new Paragraph("—")] })
            ]
        })
    ]
})
```

### Quarterly Trends Table

```javascript
new Paragraph({
    text: "Quarterly Financial Trends:",
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 100 }
}),
new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph({ text: "Quarter", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Q1 2024", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Q2 2024", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Q3 2024", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Q4 2024", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Q1 2025", bold: true })] })
            ]
        }),
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph("Revenue ($M)")] }),
                new TableCell({ children: [new Paragraph("801")] }),
                new TableCell({ children: [new Paragraph("894")] }),
                new TableCell({ children: [new Paragraph("919")] }),
                new TableCell({ children: [new Paragraph("1,023")] }),
                new TableCell({ children: [new Paragraph("1,081")] })
            ]
        }),
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph("YoY Growth")] }),
                new TableCell({ children: [new Paragraph("22.0%")] }),
                new TableCell({ children: [new Paragraph("31.0%")] }),
                new TableCell({ children: [new Paragraph("29.0%")] }),
                new TableCell({ children: [new Paragraph("30.0%")] }),
                new TableCell({ children: [new Paragraph("21.0%")] })
            ]
        })
    ]
})
```

### Valuation Comparison Table

```javascript
new Paragraph({
    text: "Valuation Metrics:",
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 100 }
}),
new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph({ text: "Metric", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Current", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Historical Avg", bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: "Peer Median", bold: true })] })
            ]
        }),
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph("P/E (FWD)")] }),
                new TableCell({ children: [new Paragraph("18.5x")] }),
                new TableCell({ children: [new Paragraph("21.2x")] }),
                new TableCell({ children: [new Paragraph("19.8x")] })
            ]
        }),
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph("EV/EBITDA")] }),
                new TableCell({ children: [new Paragraph("12.3x")] }),
                new TableCell({ children: [new Paragraph("14.5x")] }),
                new TableCell({ children: [new Paragraph("13.2x")] })
            ]
        }),
        new TableRow({
            children: [
                new TableCell({ children: [new Paragraph("P/S")] }),
                new TableCell({ children: [new Paragraph("3.2x")] }),
                new TableCell({ children: [new Paragraph("4.1x")] }),
                new TableCell({ children: [new Paragraph("3.8x")] })
            ]
        })
    ]
})
```

## Spacing Guidelines

Standard spacing values to maintain consistency:

```javascript
// After title elements
spacing: { after: 400 }

// After major section headings (HEADING_1)
spacing: { before: 400, after: 200 }

// After subsection headings (HEADING_2)  
spacing: { before: 200, after: 100 }

// After regular paragraphs
spacing: { after: 200 }

// After bullet points
spacing: { after: 50 }

// After final bullet in a series
spacing: { after: 300 }

// Between data rows
spacing: { after: 100 }
```

## Text Formatting

### Bold Key Terms

```javascript
new Paragraph({
    children: [
        new TextRun({ text: "Key Metric: ", bold: true }),
        new TextRun("Regular text follows the bold label")
    ],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
})
```

### Italic Emphasis

```javascript
new Paragraph({
    children: [
        new TextRun("Regular text with "),
        new TextRun({ text: "italicized emphasis", italics: true }),
        new TextRun(" continuing.")
    ],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
})
```

### Combined Formatting

```javascript
new Paragraph({
    children: [
        new TextRun({ text: "Important Note: ", bold: true, italics: true }),
        new TextRun("Critical information that requires attention")
    ],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
})
```

## Disclaimer Section

Always include at the end:

```javascript
new Paragraph({
    text: "DISCLAIMER",
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 }
}),
new Paragraph({
    text: "This report is for informational purposes only and should not be construed as investment advice. Past performance does not guarantee future results. Investors should conduct their own research and consult with financial advisors before making investment decisions. All data sourced from public filings, earnings reports, and third-party analyst research as of October 21, 2025.",
    italics: true,
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 }
})
```

## Complete Example with Justified Text

Here's a complete example showing proper use of justified alignment:

```javascript
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = require("docx");
const fs = require("fs");

const doc = new Document({
    sections: [{
        properties: {},
        children: [
            // Title - CENTERED
            new Paragraph({
                text: "ROBLOX CORPORATION (RBLX)",
                heading: HeadingLevel.TITLE,
                alignment: AlignmentType.CENTER,
                spacing: { after: 200 }
            }),
            new Paragraph({
                text: "Q3 2025 Earnings Preview",
                alignment: AlignmentType.CENTER,
                spacing: { after: 400 }
            }),
            
            // Section heading - LEFT (default)
            new Paragraph({
                text: "EXECUTIVE SUMMARY",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            
            // Body paragraphs - JUSTIFIED
            new Paragraph({
                text: "Roblox reports Q3 2025 earnings on October 30, 2025, following a blowout Q2 that saw the platform reach 111.8 million daily active users (up 41% YoY) and bookings surge 51% to $1.44 billion. The company significantly raised full-year guidance, now expecting FY25 bookings of $5.87-$5.97 billion.",
                alignment: AlignmentType.JUSTIFIED,
                spacing: { after: 200 }
            }),
            
            // Section heading - LEFT (default)
            new Paragraph({
                text: "KEY HIGHLIGHTS",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),

            // Bullet points - LEFT (default)
            new Paragraph({
                children: [
                    new TextRun({ text: "Revenue: ", bold: true }),
                    new TextRun("$1,081M (+21% YoY)")
                ],
                bullet: { level: 0 },
                spacing: { after: 50 }
            }),

            // Disclaimer - JUSTIFIED
            new Paragraph({
                text: "DISCLAIMER",
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 400, after: 200 }
            }),
            new Paragraph({
                text: "This report is for informational purposes only and should not be construed as investment advice.",
                italics: true,
                alignment: AlignmentType.JUSTIFIED
            })
        ]
    }]
});

Packer.toBuffer(doc).then((buffer) => {
    fs.writeFileSync("/mnt/user-data/outputs/Roblox_RBLX_Analysis.docx", buffer);
});
```

## Best Practices

1. **Consistent spacing**: Use the standard spacing values throughout
2. **Bold sparingly**: Only for key terms, metrics, and labels
3. **Table formatting**: Always include borders and clear headers
4. **Section breaks**: Use 400-point spacing before major sections
5. **Bullet points**: Use for lists of 3+ items, not for paragraphs
6. **Alignment rules**: 
   - CENTER for titles only
   - LEFT for all headings and bullets
   - JUSTIFIED for all body paragraphs
7. **Headings**: Use HEADING_1 for major sections, HEADING_2 for subsections
8. **Professional tone**: Maintain formal, objective language throughout
9. **Justified text**: Apply to ALL multi-sentence analytical paragraphs for institutional quality
