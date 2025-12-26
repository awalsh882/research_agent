# Create Draw.io Diagram Skill

A comprehensive skill for creating, exporting, and managing draw.io diagrams programmatically.

## Installation

This skill is ready to use. Simply upload the entire folder to your Claude skills directory.

## Files Included

- **SKILL.md** - Complete skill documentation and integration guide (3,000+ lines)
- **TEMPLATES.md** - Ready-to-use diagram templates and Python helpers
- **drawio.py** - CLI tool for exporting and validating diagrams (1,600+ lines)
- **README.md** - This file
- **requirements.txt** - Python dependencies

## What This Skill Does

### Creation
- Build draw.io diagrams from XML
- Support all major diagram types (flowcharts, UML, architecture, etc.)
- Apply professional styling and colors
- Add animations and interactivity

### Export
- Export to PNG, JPG, SVG, PDF
- Create animated GIFs and MP4 videos
- Batch process multiple diagrams
- Customize size, quality, and appearance

### Validation
- Check diagram consistency
- Validate connector routing
- Detect overlapping elements
- Enforce style standards

## Quick Start

1. **Read SKILL.md** - Comprehensive guide on using this skill
2. **Browse TEMPLATES.md** - Pre-built templates for common diagram types
3. **Use drawio.py** - Export diagrams to various formats

### Example: Create a Simple Flowchart

```python
diagram_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="Process Flow" id="1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <mxCell id="start" value="Start" 
                style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" 
                vertex="1" parent="1">
          <mxGeometry x="375" y="40" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="process" value="Process Data" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" 
                vertex="1" parent="1">
          <mxGeometry x="350" y="140" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="c1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="start" target="process">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

# Save to file
with open('flowchart.drawio', 'w') as f:
    f.write(diagram_xml)

# Export to PNG
import subprocess
subprocess.run(['python', 'drawio.py', 'export', 'flowchart.drawio', 
                '--format', 'png', '--size', 'large'])
```

## Common Use Cases

1. **Flowcharts** - Process flows, decision trees, workflows
2. **Architecture Diagrams** - System design, cloud infrastructure, 3-tier architectures
3. **UML Diagrams** - Class, sequence, activity diagrams for software documentation
4. **Network Diagrams** - Infrastructure, topology, connectivity
5. **Organizational Charts** - Hierarchies, reporting structures
6. **Mind Maps** - Brainstorming, concept mapping
7. **Data Flow Diagrams** - Information flow, ETL processes

## Export Commands

```bash
# Basic export to PNG
python drawio.py export diagram.drawio --format png --size large

# High quality export
python drawio.py export diagram.drawio --format png --quality-preset very-high

# Print quality PDF
python drawio.py export diagram.drawio --format pdf --size print

# Animated GIF
python drawio.py export diagram.drawio --format gif --animated

# Batch export all diagrams
python drawio.py batch "*.drawio" --format png --size large --output-dir exports/

# Get diagram information
python drawio.py info diagram.drawio

# Validate diagram
python drawio.py validate-style diagram.drawio
```

## Professional Color Scheme

| Purpose | Fill Color | Stroke Color | Usage |
|---------|-----------|--------------|--------|
| Start/Success | `#d5e8d4` | `#82b366` | Green - positive outcomes |
| Process | `#dae8fc` | `#6c8ebf` | Blue - normal operations |
| Decision | `#fff2cc` | `#d6b656` | Yellow - choice points |
| Error/End | `#f8cecc` | `#b85450` | Red - negative outcomes |
| External | `#e1d5e7` | `#9673a6` | Purple - third-party services |
| Data/Storage | `#f5f5f5` | `#666666` | Gray - databases, files |

## Requirements

- Python 3.7+
- draw.io desktop application (for exports)
- PIL/Pillow (for image processing)
- click (for CLI)

Install dependencies:
```bash
pip install -r requirements.txt --break-system-packages
```

## Key Features

✅ Professional styling with semantic colors
✅ Multiple export formats (static & animated)
✅ Comprehensive validation tools
✅ Batch processing support
✅ Template library for quick starts
✅ Integration with other skills (docx, pptx, pdf)
✅ 3,000+ lines of documentation
✅ Python helper functions included

## Documentation Structure

### SKILL.md
- Overview and when to use
- XML structure and diagram creation
- All shape types with examples
- Color schemes and styling
- Export options guide
- Advanced features (animations, multi-page, layers)
- Validation features
- Best practices
- Workflow examples
- Troubleshooting

### TEMPLATES.md
- Basic flowchart template
- System architecture (3-tier)
- Decision tree
- Swimlane diagram
- Network diagram
- UML templates
- Python helper functions
- Quick reference guide

## Support

For detailed documentation, see **SKILL.md**
For templates, see **TEMPLATES.md**
For CLI help, run: `python drawio.py --help`

## License

MIT License

## Version

1.0 - October 2025
