---
name: create-drawio-diagram
description: "Create, export, validate, and manage draw.io diagrams programmatically. Supports flowcharts, architecture diagrams, network diagrams, UML, and more with professional styling, animations, and multi-format exports (PNG, SVG, PDF, GIF, MP4). Use when users need to create technical diagrams, visualize workflows, document system architectures, or generate professional diagram exports."
license: MIT
---

# Draw.io Diagram Creation & Export Skill

## Overview

This skill enables Claude to create professional draw.io diagrams programmatically and export them to various formats. Draw.io (also known as diagrams.net) is a powerful, open-source diagramming tool that supports flowcharts, UML diagrams, network diagrams, architecture diagrams, and more.

**Key Capabilities:**
- 🎨 Create diagrams from scratch using XML format
- 📤 Export to multiple formats (PNG, JPG, SVG, PDF, GIF, MP4)
- ✨ Add animations and interactivity
- 🔍 Validate diagram consistency and standards
- 🎯 Batch process multiple diagrams
- 📊 Support for all major diagram types

## When to Use This Skill

Use this skill when users ask for:
- Creating flowcharts, process diagrams, or workflows
- System architecture or network diagrams
- UML diagrams (class, sequence, activity, etc.)
- Mind maps or organizational charts
- Database schemas or ER diagrams
- Cloud architecture diagrams (AWS, Azure, GCP)
- Timeline or Gantt charts
- Converting descriptions into visual diagrams
- Exporting diagrams to images, PDFs, or animated formats
- Validating diagram consistency

## File Structure

The skill includes:
- `drawio.py` - Main CLI tool for diagram export and validation
- `DRAWIO_CLI_GUIDE.md` - Comprehensive usage documentation
- This SKILL.md file - Integration guide for Claude

## Quick Start

### 1. Setup (First Time Only)

```bash
# The drawio.py script should be in /home/claude or copied from uploads
# Ensure it's executable
chmod +x drawio.py

# Install dependencies (already included in base image)
pip install click pillow --break-system-packages
```

### 2. Create a Simple Diagram

```python
# Create a basic flowchart
diagram_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Claude" version="24.0.0">
  <diagram name="Page-1" id="1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- Start Node -->
        <mxCell id="2" value="Start" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="375" y="40" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Process Node -->
        <mxCell id="3" value="Process Data" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="350" y="140" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Decision Node -->
        <mxCell id="4" value="Valid?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="365" y="240" width="120" height="80" as="geometry"/>
        </mxCell>
        
        <!-- End Node -->
        <mxCell id="5" value="End" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="375" y="360" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Connectors -->
        <mxCell id="6" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="7" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="3" target="4">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="8" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="4" target="5">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

# Save the diagram
with open('flowchart.drawio', 'w') as f:
    f.write(diagram_xml)
```

### 3. Export the Diagram

```bash
# Export to PNG
python drawio.py export flowchart.drawio --format png --size large

# Export to high-quality PDF
python drawio.py export flowchart.drawio --format pdf --size print

# Export animated GIF
python drawio.py export flowchart.drawio --format gif --animated
```

## Diagram Creation Guide

### XML Structure Basics

Every draw.io diagram follows this structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="Page-1" id="unique-id">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageScale="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- Your shapes and connectors go here -->
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Common Shape Types

#### 1. Rectangle (Process Box)
```xml
<mxCell id="2" value="Process Name" 
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

#### 2. Rounded Rectangle (Subprocess)
```xml
<mxCell id="3" value="Subprocess" 
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;arcSize=10;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="120" height="60" as="geometry"/>
</mxCell>
```

#### 3. Ellipse (Start/End)
```xml
<mxCell id="4" value="Start" 
        style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="300" width="100" height="60" as="geometry"/>
</mxCell>
```

#### 4. Diamond (Decision)
```xml
<mxCell id="5" value="Decision?" 
        style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" 
        vertex="1" parent="1">
  <mxGeometry x="90" y="400" width="120" height="80" as="geometry"/>
</mxCell>
```

#### 5. Parallelogram (Input/Output)
```xml
<mxCell id="6" value="Input Data" 
        style="shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="500" width="140" height="60" as="geometry"/>
</mxCell>
```

#### 6. Cylinder (Database)
```xml
<mxCell id="7" value="Database" 
        style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#dae8fc;strokeColor=#6c8ebf;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="600" width="80" height="100" as="geometry"/>
</mxCell>
```

#### 7. Cloud (Cloud Service)
```xml
<mxCell id="8" value="Cloud" 
        style="ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="720" width="120" height="80" as="geometry"/>
</mxCell>
```

#### 8. Actor (Person)
```xml
<mxCell id="9" value="User" 
        style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#d5e8d4;strokeColor=#82b366;" 
        vertex="1" parent="1">
  <mxGeometry x="115" y="820" width="30" height="60" as="geometry"/>
</mxCell>
```

### Connectors (Arrows)

#### Simple Arrow
```xml
<mxCell id="10" value="" 
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
        edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

#### Labeled Arrow
```xml
<mxCell id="11" value="Yes" 
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;fontStyle=1;" 
        edge="1" parent="1" source="5" target="6">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

#### Dashed Arrow
```xml
<mxCell id="12" value="Optional" 
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;dashPattern=8 8;" 
        edge="1" parent="1" source="6" target="7">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### Color Schemes

**Professional Color Palette:**

| Color Name | Fill Color | Stroke Color | Use Case |
|------------|-----------|--------------|----------|
| Blue | `#dae8fc` | `#6c8ebf` | Processes, normal flow |
| Green | `#d5e8d4` | `#82b366` | Start, success, positive |
| Yellow | `#fff2cc` | `#d6b656` | Decisions, warnings |
| Red | `#f8cecc` | `#b85450` | End, errors, critical |
| Purple | `#e1d5e7` | `#9673a6` | Special processes, external |
| Gray | `#f5f5f5` | `#666666` | Data, storage, neutral |
| Orange | `#ffe6cc` | `#d79b00` | Highlights, important |

### Style Properties Reference

**Common Style Properties:**

```
fillColor=#hexcolor       - Background color
strokeColor=#hexcolor     - Border color
strokeWidth=2             - Border thickness
fontColor=#hexcolor       - Text color
fontSize=14               - Text size
fontStyle=1               - Bold (0=normal, 1=bold, 2=italic, 4=underline)
rounded=1                 - Rounded corners (0 or 1)
dashed=1                  - Dashed border (0 or 1)
dashPattern=8 8          - Dash pattern if dashed=1
opacity=80               - Transparency (0-100)
shadow=1                 - Drop shadow (0 or 1)
whiteSpace=wrap          - Text wrapping
html=1                   - Enable HTML formatting
align=center             - Text alignment (left, center, right)
verticalAlign=middle     - Vertical alignment (top, middle, bottom)
```

## Common Diagram Types

### 1. Flowchart Template

```python
def create_flowchart(title, steps):
    """
    Create a flowchart from a list of steps.
    
    Args:
        title: Diagram title
        steps: List of dicts with 'type' and 'text' keys
               type can be: 'start', 'process', 'decision', 'end'
    """
    # Template implementation
    pass
```

### 2. System Architecture Template

```python
def create_architecture_diagram(components):
    """
    Create a system architecture diagram.
    
    Args:
        components: List of dicts with 'name', 'type', 'connections'
                   type can be: 'server', 'database', 'service', 'client'
    """
    # Template implementation
    pass
```

### 3. Sequence Diagram Template

```python
def create_sequence_diagram(actors, messages):
    """
    Create a UML sequence diagram.
    
    Args:
        actors: List of actor names
        messages: List of dicts with 'from', 'to', 'message'
    """
    # Template implementation
    pass
```

## Export Options Guide

### Format Selection

**Static Formats:**
- **PNG** - Best for web, presentations, general use
- **JPG** - Smaller file size, no transparency
- **SVG** - Scalable, perfect quality, editable
- **PDF** - Print quality, professional documents

**Animated Formats:**
- **GIF** - Universal animation support
- **MP4** - High-quality video with audio support
- **WebM** - Modern web video format
- **HTML** - Interactive web animations

### Size Presets

```bash
# Quick reference
--size thumbnail  # 400×300   - Small previews
--size small      # 800×600   - Web thumbnails
--size medium     # 1200×900  - Standard display
--size large      # 1920×1080 - HD presentations
--size xlarge     # 2560×1440 - 4K displays
--size print      # 3508×2480 - A4 print (300 DPI)
```

### Quality Presets

```bash
# Quick reference
--quality-preset low       # 60 - Quick previews
--quality-preset medium    # 80 - Web display
--quality-preset high      # 90 - Professional
--quality-preset very-high # 95 - Print quality
--quality-preset maximum   # 100 - Archival
```

### Export Examples

```bash
# Basic exports
python drawio.py export diagram.drawio --format png
python drawio.py export diagram.drawio --format svg
python drawio.py export diagram.drawio --format pdf --size print

# Custom sizing
python drawio.py export diagram.drawio --format png --width 2000 --height 1500
python drawio.py export diagram.drawio --format png --scale 2.0

# High quality
python drawio.py export diagram.drawio --format png --quality-preset very-high --size large

# Transparent background
python drawio.py export diagram.drawio --format png --transparent

# Custom background
python drawio.py export diagram.drawio --format png --background "#ffffff"

# Animated exports
python drawio.py export diagram.drawio --format gif --animated
python drawio.py export diagram.drawio --format gif --animated --animation-speed 1.5
python drawio.py export diagram.drawio --format mp4 --animated --quality-preset high

# Batch export
python drawio.py batch "*.drawio" --format png --size large --output-dir exports/
```

## Advanced Features

### 1. Animations

Add animations to your diagrams using the `flowAnimation` attribute:

```xml
<mxCell id="2" value="Animated" 
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;flowAnimation=1;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### 2. Multi-Page Diagrams

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile>
  <diagram name="Page 1" id="page1">
    <!-- First page content -->
  </diagram>
  <diagram name="Page 2" id="page2">
    <!-- Second page content -->
  </diagram>
</mxfile>
```

Export specific page:
```bash
python drawio.py export multipage.drawio --page 2 --format png
python drawio.py export multipage.drawio --all-pages --format png
```

### 3. Layers

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    
    <!-- Layer 1: Background -->
    <mxCell id="layer1" value="Background" parent="1"/>
    <mxCell id="shape1" parent="layer1" .../>
    
    <!-- Layer 2: Foreground -->
    <mxCell id="layer2" value="Foreground" parent="1"/>
    <mxCell id="shape2" parent="layer2" .../>
  </root>
</mxGraphModel>
```

## Validation Features

The tool includes powerful validation capabilities:

### 1. Diagram Information

```bash
python drawio.py info diagram.drawio
```

Shows:
- File size and format
- Number of pages
- Animation detection
- Element counts
- Diagram dimensions

### 2. Style Validation

```bash
python drawio.py validate-style diagram.drawio
```

Checks for:
- Inconsistent fonts and colors
- Mixed connector styles
- Improper text formatting
- Color scheme violations

### 3. Overlap Detection

```bash
python drawio.py validate-overlaps diagram.drawio --min-spacing 20
```

Detects overlapping elements and suggests fixes.

### 4. Connector Validation

```bash
python drawio.py validate-routing diagram.drawio
```

Validates:
- Orthogonal vs diagonal routing
- Proper connector anchoring
- Consistent arrow styles

### 5. Decision Flow Validation

```bash
python drawio.py validate-decisions diagram.drawio
```

Checks decision diamond conventions:
- YES paths go right
- NO paths go down
- Proper labeling

## Best Practices

### 1. Diagram Organization

**DO:**
- Use consistent spacing (20-40px between elements)
- Align elements to grid (10px grid recommended)
- Group related elements using containers
- Use layers for complex diagrams
- Add clear labels to all connectors
- Use standard shapes for standard concepts

**DON'T:**
- Overlap elements without intention
- Use inconsistent colors for same element types
- Mix orthogonal and diagonal connectors
- Create overly complex diagrams (split into multiple pages)
- Use unclear or ambiguous labels

### 2. Color Usage

**Semantic Colors:**
- **Green** - Start, success, go, positive outcomes
- **Red** - Stop, error, danger, negative outcomes
- **Yellow** - Caution, decisions, important notices
- **Blue** - Normal processes, information, neutral
- **Purple** - External systems, third-party services
- **Gray** - Data, passive elements, infrastructure

### 3. Text Formatting

```xml
<!-- Good: Clear, concise, well-formatted -->
<mxCell id="2" value="Validate User Input" 
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;fontStyle=1;" 
        vertex="1" parent="1">

<!-- Avoid: Too much text, poor formatting -->
<mxCell id="3" value="This is a very long description that should probably be broken into multiple lines or simplified to be more concise" 
        style="rounded=0;whiteSpace=wrap;html=1;" 
        vertex="1" parent="1">
```

### 4. Layout Principles

**Top-to-Bottom Flow:**
- Start at top
- Process flows downward
- End at bottom
- Decisions branch right (YES) and down (NO)

**Left-to-Right Flow:**
- Start at left
- Process flows rightward
- End at right
- Use for timeline/sequence diagrams

**Grid Alignment:**
```python
# Calculate grid-aligned positions
def align_to_grid(value, grid_size=10):
    return round(value / grid_size) * grid_size

x = align_to_grid(157)  # Returns 160
y = align_to_grid(243)  # Returns 240
```

## Workflow Examples

### Example 1: Create Simple Flowchart

```python
# Step 1: Define the workflow
workflow = """
1. Start
2. Receive Request
3. Validate Data
4. Is Valid?
   - Yes: Process Request
   - No: Return Error
5. Save to Database
6. Send Response
7. End
"""

# Step 2: Create diagram XML
diagram_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="Request Flow" id="1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <mxCell id="start" value="Start" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="375" y="40" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="receive" value="Receive Request" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="350" y="130" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="validate" value="Validate Data" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="350" y="220" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="decision" value="Is Valid?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="365" y="310" width="120" height="80" as="geometry"/>
        </mxCell>
        
        <mxCell id="process" value="Process Request" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="550" y="320" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="error" value="Return Error" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="150" y="320" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="save" value="Save to Database" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="565" y="420" width="120" height="80" as="geometry"/>
        </mxCell>
        
        <mxCell id="respond" value="Send Response" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="550" y="540" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="end" value="End" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="375" y="640" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Connectors -->
        <mxCell id="c1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="start" target="receive">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="c2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="receive" target="validate">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="c3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="validate" target="decision">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="c4" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;fontStyle=1;" edge="1" parent="1" source="decision" target="process">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="c5" value="No" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;fontStyle=1;" edge="1" parent="1" source="decision" target="error">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="c6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="process" target="save">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="c7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="save" target="respond">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="c8" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="respond" target="end">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="c9" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="error" target="end">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

# Step 3: Save and export
with open('/mnt/user-data/outputs/request_flow.drawio', 'w') as f:
    f.write(diagram_xml)

# Step 4: Export to PNG
import subprocess
result = subprocess.run([
    'python', 'drawio.py', 'export', 
    '/mnt/user-data/outputs/request_flow.drawio',
    '--format', 'png',
    '--size', 'large',
    '--output', '/mnt/user-data/outputs/request_flow.png'
], capture_output=True, text=True)

print(result.stdout)
```

### Example 2: Batch Process Multiple Diagrams

```bash
# Export all diagrams in a directory
python drawio.py batch "/mnt/user-data/uploads/*.drawio" \
  --format png \
  --size large \
  --output-dir /mnt/user-data/outputs/diagrams/

# Export with animation
python drawio.py batch "*.drawio" \
  --format gif \
  --animated \
  --animation-preset fast \
  --output-dir /mnt/user-data/outputs/animated/
```

## Troubleshooting

### Common Issues

**1. Export fails with "Draw.io desktop application not found"**

The tool requires the draw.io desktop application for exports. On macOS, it looks for:
- `/Applications/draw.io.app/Contents/MacOS/draw.io`

If not found, the tool will show an error. You can install draw.io desktop from:
https://github.com/jgraph/drawio-desktop/releases

**2. Invalid XML format**

Ensure your XML is well-formed:
- All tags are properly closed
- Special characters are escaped (`&lt;`, `&gt;`, `&amp;`, `&quot;`)
- ID attributes are unique
- Required attributes are present

**3. Shapes not displaying correctly**

Check that:
- The `style` attribute includes all required properties
- Colors are in hex format with # prefix
- Geometry coordinates are within page bounds
- Parent relationships are correct

**4. Connectors not connecting**

Ensure:
- `source` and `target` attributes reference valid cell IDs
- Source and target cells exist before creating connector
- Edge has `edge="1"` attribute
- Parent is correct (usually "1")

## Performance Tips

1. **Optimize diagram complexity**: Keep diagrams under 100 elements
2. **Use batch export**: Process multiple files in one command
3. **Choose appropriate formats**: SVG for web, PNG for presentations
4. **Set reasonable sizes**: Don't export at 4K unless needed
5. **Cache exports**: Don't re-export unchanged diagrams

## Integration with Other Skills

This skill works well with:

- **docx skill**: Export diagrams and embed in Word documents
- **pptx skill**: Export diagrams and add to presentations
- **pdf skill**: Create PDF reports with embedded diagrams
- **xlsx skill**: Document data flows and processes

## Additional Resources

- Draw.io Documentation: https://www.diagrams.net/doc/
- Draw.io GitHub: https://github.com/jgraph/drawio
- Draw.io Desktop: https://github.com/jgraph/drawio-desktop
- Shape Libraries: Available in the draw.io app under More Shapes

## Summary

This skill enables comprehensive diagram creation and export capabilities. When users ask for diagrams:

1. **Understand requirements**: What type of diagram? What elements?
2. **Create XML**: Build the draw.io XML structure
3. **Save file**: Write to .drawio file
4. **Export**: Use drawio.py to export to desired format
5. **Validate** (optional): Check consistency and standards
6. **Deliver**: Move to outputs directory and provide link

Always start simple and iterate based on feedback!
