---
description: Create an architecture diagram for the current codebase
allowed-tools: Read, Glob, Grep, Bash(mkdir:*), Write
argument-hint: [detail-level: minimal|standard|detailed]
---

Create a modern, intuitive draw.io architecture diagram for this codebase.

## Design Philosophy

Create diagrams that tell a story - showing how data flows from input to output. Use a clean, modern visual style inspired by professional infographics:

- **Top-to-bottom flow**: User/input at top, output/response at bottom
- **Dual-track layout**: Show parallel processing paths that converge
- **Icon-enhanced boxes**: Use emoji icons to make components instantly recognizable
- **Soft, modern colors**: Tailwind-inspired palette with gentle backgrounds
- **Clear visual hierarchy**: Larger boxes for major components, smaller for details

## Detail Level

Interpret $ARGUMENTS as the detail level (default to "standard" if not provided):

- **minimal**: High-level flow only (input → processing → output)
- **standard**: Components + relationships with icons and descriptions
- **detailed**: Full detail including sub-components, all connections, and annotations

## Instructions

1. **Create the diagrams folder** if it doesn't exist:
   ```bash
   mkdir -p diagrams
   ```

2. **Analyze the codebase** to understand:
   - Project type and main technologies
   - Entry points and user-facing interfaces
   - Core processing/business logic
   - Data sources and external integrations
   - Output/response generation

3. **Design the flow layout**:
   - Map the data journey from input to output
   - Identify parallel processing tracks (e.g., user queries vs tool registration)
   - Find the merge point where tracks converge
   - Plan the visual hierarchy

4. **Generate `diagrams/architecture.drawio`** using the modern flow style

5. **Report what was created**

## Modern Color Palette (Tailwind-inspired)

### Background
| Element | Color | Use |
|---------|-------|-----|
| Page background | #EDF2F7 | Soft blue-gray canvas |

### Input/Output Pills (Rounded capsules)
| Type | Fill | Stroke | Use |
|------|------|--------|-----|
| User Input | #FEF3C7 | #D97706 | Yellow - queries, user actions |
| Data Input | #D1FAE5 | #059669 | Green - tools, resources, data sources |
| Output | #D1FAE5 | #059669 | Green - responses, generated content |

### Processing Boxes
| Type | Fill | Stroke | Use |
|------|------|--------|-----|
| Core Component | #DBEAFE | #3B82F6 | Blue - main processing logic |
| Sub-component | #EFF6FF | #93C5FD | Light blue - internal details |
| Critical Path | #FEE2E2 | #EF4444 | Red - transport, critical infra |
| Example/Optional | #F3E8FF | #9333EA | Purple - examples, extensions |
| Data/Config | #DCFCE7 | #22C55E | Green - outputs, data stores |

### Text Colors
| Element | Color |
|---------|-------|
| Title | #2D3748 |
| Box titles | #1E40AF (blue boxes), #991B1B (red), #7C3AED (purple) |
| Descriptions | Match stroke color, lighter |
| Labels | #64748B (gray) |

### Arrows
| Type | Color | Style |
|------|-------|-------|
| Data flow | #6B7280 | Solid, strokeWidth=2 |
| Uses/Config | #6B7280 | Dashed |
| Highlight | Match source color | Solid |

## Draw.io XML Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="Architecture Flow" id="flow-diagram">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" page="1" pageWidth="1400" pageHeight="1000">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- BACKGROUND -->
        <mxCell id="bg" value=""
                style="rounded=20;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=none"
                vertex="1" parent="1">
          <mxGeometry x="20" y="20" width="1360" height="960" as="geometry"/>
        </mxCell>

        <!-- TITLE -->
        <mxCell id="title" value="[Project Name] - Architecture Flow"
                style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=24;fontStyle=1;fontColor=#2D3748"
                vertex="1" parent="1">
          <mxGeometry x="400" y="40" width="600" height="40" as="geometry"/>
        </mxCell>

        <!-- INPUT PILL (Yellow - User/Query) -->
        <mxCell id="user-input" value=""
                style="rounded=30;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#D97706;strokeWidth=2"
                vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="280" height="80" as="geometry"/>
        </mxCell>
        <!-- Add icons as separate text cells -->
        <mxCell id="user-icon" value="[emoji]"
                style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=28"
                vertex="1" parent="1">
          <mxGeometry x="130" y="115" width="50" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="user-label" value="Label"
                style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#92400E"
                vertex="1" parent="1">
          <mxGeometry x="130" y="155" width="50" height="20" as="geometry"/>
        </mxCell>

        <!-- PROCESSING BOX (Blue) -->
        <mxCell id="process-box" value=""
                style="rounded=15;whiteSpace=wrap;html=1;fillColor=#DBEAFE;strokeColor=#3B82F6;strokeWidth=2"
                vertex="1" parent="1">
          <mxGeometry x="100" y="220" width="280" height="120" as="geometry"/>
        </mxCell>
        <mxCell id="process-icon" value="[emoji]"
                style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=32"
                vertex="1" parent="1">
          <mxGeometry x="120" y="235" width="50" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="process-title" value="Component Name"
                style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor=#1E40AF"
                vertex="1" parent="1">
          <mxGeometry x="170" y="240" width="200" height="25" as="geometry"/>
        </mxCell>
        <mxCell id="process-desc" value="Description of what&#xa;this component does"
                style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;fontSize=11;fontColor=#3B82F6"
                vertex="1" parent="1">
          <mxGeometry x="170" y="265" width="200" height="40" as="geometry"/>
        </mxCell>

        <!-- SUB-COMPONENTS (Light blue chips inside boxes) -->
        <mxCell id="sub-comp" value="SubModule"
                style="rounded=8;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#93C5FD;fontSize=10"
                vertex="1" parent="1">
          <mxGeometry x="120" y="310" width="70" height="25" as="geometry"/>
        </mxCell>

        <!-- CRITICAL/TRANSPORT BOX (Red) -->
        <mxCell id="critical-box" value=""
                style="rounded=15;whiteSpace=wrap;html=1;fillColor=#FEE2E2;strokeColor=#EF4444;strokeWidth=2"
                vertex="1" parent="1">
          <mxGeometry x="400" y="400" width="400" height="100" as="geometry"/>
        </mxCell>

        <!-- OUTPUT PILL (Green) -->
        <mxCell id="output-pill" value=""
                style="rounded=30;whiteSpace=wrap;html=1;fillColor=#D1FAE5;strokeColor=#059669;strokeWidth=2"
                vertex="1" parent="1">
          <mxGeometry x="500" y="700" width="200" height="70" as="geometry"/>
        </mxCell>

        <!-- ARROWS -->
        <mxCell id="arrow1" value=""
                style="endArrow=classic;html=1;strokeWidth=2;strokeColor=#6B7280"
                edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="240" y="180" as="sourcePoint"/>
            <mxPoint x="240" y="220" as="targetPoint"/>
          </mxGeometry>
        </mxCell>

        <!-- CURVED MERGE ARROW -->
        <mxCell id="merge-arrow" value=""
                style="endArrow=classic;html=1;strokeWidth=2;strokeColor=#6B7280;curved=1"
                edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="200" y="340" as="sourcePoint"/>
            <mxPoint x="400" y="450" as="targetPoint"/>
            <Array as="points">
              <mxPoint x="200" y="450"/>
            </Array>
          </mxGeometry>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Recommended Emoji Icons

Use these to make components instantly recognizable:

| Concept | Emoji | Concept | Emoji |
|---------|-------|---------|-------|
| User | `👤` | Query/Search | `🔍` |
| Tools | `🔧` | Resources | `📊` |
| Documents | `📄` | Config | `⚙️` |
| API/Plugin | `🔌` | Database | `💾` |
| Cloud | `☁️` | Web | `🌐` |
| Process | `⚡` | Registry | `📋` |
| Output | `➡️` | Sync | `🔄` |
| Security | `🔒` | Compute | `🖥️` |

## Layout Patterns

### Pattern 1: Dual-Track Convergence (Recommended)
```
    [User Input]              [Data/Tools Input]
         ↓                           ↓
    [Processing A]            [Processing B]
         ↓                           ↓
         └──────────┬────────────────┘
                    ↓
              [Merge Layer]
                    ↓
            [Core Processing]
                    ↓
               [Output]
```

### Pattern 2: Linear Pipeline
```
    [Input] → [Stage 1] → [Stage 2] → [Stage 3] → [Output]
```

### Pattern 3: Hub and Spoke
```
              [Input]
                 ↓
    ┌────────[Hub]────────┐
    ↓          ↓          ↓
 [Spoke1]  [Spoke2]  [Spoke3]
    └──────────┬──────────┘
               ↓
            [Output]
```

## Best Practices

1. **Start with the story**: What journey does data take through your system?
2. **Use icons liberally**: They make components instantly scannable
3. **Keep text concise**: Title (bold), 1-2 line description, bullet points for details
4. **Color consistently**: Same color = same type of component
5. **Space generously**: Leave room for arrows to flow without crossing
6. **Show the happy path**: Primary flow should be obvious, edge cases secondary

## Shape Quick Reference

| Shape | Style | Use |
|-------|-------|-----|
| Pill/Capsule | `rounded=30` | Inputs, outputs |
| Rounded box | `rounded=15` | Main components |
| Small chip | `rounded=8` | Sub-components |
| Text | `text;html=1;strokeColor=none;fillColor=none` | Icons, labels |
| Arrow | `endArrow=classic;strokeWidth=2` | Connections |

## Notes

- Each `mxCell` needs a unique `id`
- Use `&#xa;` for line breaks in values
- Position with `<mxGeometry x="X" y="Y" width="W" height="H" as="geometry"/>`
- Icons are separate text cells positioned over the parent box
- Standard page size: 1400x1000 with 20px margin = 1360x960 usable
