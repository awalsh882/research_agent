---
description: Update the architecture diagram with recent codebase changes
allowed-tools: Read, Glob, Grep, Write, Bash(git log:*), Bash(git diff:*), Bash(git status:*)
argument-hint: [instructions or detail-level]
---

Update the existing `diagrams/architecture.drawio` to reflect the current state of the codebase while maintaining the modern flow-based design style.

## User Instructions

$ARGUMENTS

Interpret the arguments as either:
- A detail level: "minimal", "standard", or "detailed"
- Custom instructions: e.g., "Focus on the new authentication module", "Add more detail to the API layer"
- Empty: Just sync the diagram with current codebase state

## Steps

### 1. Check for existing diagram

First, verify `diagrams/architecture.drawio` exists. If it doesn't exist, inform the user:
> "No existing diagram found at `diagrams/architecture.drawio`. Run `/diagram_create` first to create an initial diagram."

### 2. Read the existing diagram

Parse the current `diagrams/architecture.drawio` to understand:
- The current visual style (modern flow vs legacy swimlane)
- What components are currently documented
- The existing layout and flow direction
- Current relationships/connectors

### 3. Analyze recent changes

Check what has changed in the codebase:

```bash
# Recent commits (if git repo)
git log --oneline -20 2>/dev/null || echo "Not a git repo"

# Current status
git status --short 2>/dev/null || echo ""
```

### 4. Scan current codebase structure

Compare the diagram against the actual codebase:
- Identify new files/modules not in the diagram
- Find components in the diagram that no longer exist
- Detect renamed modules or restructured code
- Discover new dependencies or relationships

### 5. Update the diagram

Make necessary changes while **preserving the modern flow style**:
- **Add** new components with appropriate styling and positioning
- **Remove** components that no longer exist
- **Update** labels for renamed items
- **Add** new connectors for new relationships
- **Maintain** the visual hierarchy and flow direction

### 6. Save and report

Write the updated diagram to `diagrams/architecture.drawio` and report:
- Components added (list them)
- Components removed (list them)
- Relationships updated
- Any areas that may need manual review

## Modern Design Style Guidelines

### Visual Hierarchy (Top to Bottom)

```
    [Input Pills - Yellow/Green]     <- User/data entry points
              ↓
    [Processing Boxes - Blue]        <- Core logic components
              ↓
    [Critical Layer - Red]           <- Transport/infrastructure
              ↓
    [Output Pills - Green]           <- Results/responses
```

### Color Palette (Tailwind-inspired)

**Background:**
| Element | Color |
|---------|-------|
| Page background | #EDF2F7 |

**Input/Output Pills (rounded=30):**
| Type | Fill | Stroke |
|------|------|--------|
| User Input | #FEF3C7 | #D97706 |
| Data/Tools Input | #D1FAE5 | #059669 |
| Output | #D1FAE5 | #059669 |

**Processing Boxes (rounded=15):**
| Type | Fill | Stroke | Text Color |
|------|------|--------|------------|
| Core Component | #DBEAFE | #3B82F6 | #1E40AF |
| Sub-component | #EFF6FF | #93C5FD | #3B82F6 |
| Critical Path | #FEE2E2 | #EF4444 | #991B1B |
| Example/Optional | #F3E8FF | #9333EA | #7C3AED |
| Data/Config | #DCFCE7 | #22C55E | #065F46 |

**Arrows:**
| Type | Color | Style |
|------|-------|-------|
| Data flow | #6B7280 | Solid, strokeWidth=2 |
| Uses/Config | #6B7280 | Dashed |
| Highlight | Match source color | Solid |

### Component Structure

Each major component should have:
1. **Container box** (rounded=15, colored background)
2. **Icon** (emoji as separate text cell, fontSize=28-32)
3. **Title** (bold, fontSize=14, colored to match box)
4. **Description** (1-2 lines, fontSize=11, lighter color)
5. **Sub-components** (optional, rounded=8 chips at bottom)

Example structure:
```xml
<!-- Container -->
<mxCell id="comp-box" value=""
        style="rounded=15;whiteSpace=wrap;html=1;fillColor=#DBEAFE;strokeColor=#3B82F6;strokeWidth=2"
        vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="280" height="120" as="geometry"/>
</mxCell>

<!-- Icon -->
<mxCell id="comp-icon" value="⚡"
        style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=32"
        vertex="1" parent="1">
  <mxGeometry x="120" y="215" width="50" height="50" as="geometry"/>
</mxCell>

<!-- Title -->
<mxCell id="comp-title" value="Component Name"
        style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor=#1E40AF"
        vertex="1" parent="1">
  <mxGeometry x="170" y="220" width="200" height="25" as="geometry"/>
</mxCell>

<!-- Description -->
<mxCell id="comp-desc" value="What this component does"
        style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;fontSize=11;fontColor=#3B82F6"
        vertex="1" parent="1">
  <mxGeometry x="170" y="245" width="200" height="40" as="geometry"/>
</mxCell>
```

### Recommended Emoji Icons

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
| Research | `🔬` | Build | `🏗️` |

### Layout Preservation Rules

When updating:
- **Keep the flow direction** (top-to-bottom)
- **Maintain track alignment** (left track, right track, center merge)
- **Preserve spacing** between components
- **Add new components** near related existing ones
- **Use consistent sizing** for similar component types

### When to Add vs Skip Components

**Add** a component if:
- It's a new module with significant functionality
- It represents a new entry point or API
- It's a new external integration
- It's explicitly mentioned in user instructions

**Skip** a component if:
- It's a minor utility/helper file
- It's a test file (unless diagram focuses on testing)
- It's auto-generated code
- It's configuration that doesn't affect architecture

### Arrow Routing

**Straight down (adjacent components):**
```xml
<mxCell id="arrow1" value=""
        style="endArrow=classic;html=1;strokeWidth=2;strokeColor=#6B7280"
        edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="240" y="350" as="sourcePoint"/>
    <mxPoint x="240" y="400" as="targetPoint"/>
  </mxGeometry>
</mxCell>
```

**Curved merge (converging tracks):**
```xml
<mxCell id="merge-arrow" value=""
        style="endArrow=classic;html=1;strokeWidth=2;strokeColor=#6B7280;curved=1"
        edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="200" y="540" as="sourcePoint"/>
    <mxPoint x="440" y="640" as="targetPoint"/>
    <Array as="points">
      <mxPoint x="200" y="640"/>
    </Array>
  </mxGeometry>
</mxCell>
```

**Dashed (optional/config relationship):**
```xml
<mxCell id="config-arrow" value=""
        style="endArrow=classic;html=1;strokeWidth=2;strokeColor=#9333EA;dashed=1"
        edge="1" parent="1">
  ...
</mxCell>
```

## Migrating Legacy Diagrams

If the existing diagram uses the old swimlane style, consider these updates:
- Replace swimlanes with the new pill/box hierarchy
- Add emoji icons to each component
- Update colors to the Tailwind palette
- Restructure to show flow rather than layers
- Add a soft background rectangle

## Example Output

After updating, report like this:

```
## Diagram Updated

### Added Components
- `auth/` module (new authentication system) - Blue processing box with 🔒
- `RateLimiter` service - Added as sub-component chip
- Redis cache - Added to critical layer with 💾

### Removed Components
- `legacy_auth.py` (deleted from codebase)

### Updated Relationships
- Added arrow: API Gateway → Rate Limiter
- Added dashed arrow: Rate Limiter → Redis config

### Visual Updates
- Repositioned auth components to right track
- Added merge arrow to transport layer

### Notes
- Consider adding more detail to the new auth flow
- The Redis connection may need manual positioning

Diagram saved to: diagrams/architecture.drawio
Open with draw.io (https://app.diagrams.net) to view and fine-tune.
```
