#!/usr/bin/env python3
"""Generate draw.io diagram of the Investment Research Agent architecture.

This developer utility introspects the agent's structure and generates a
visual diagram showing components, tools, and data flow.

Usage:
    python -m research_agent.architecture
"""

import os
from pathlib import Path


def create_shape(
    shape_id: str,
    text: str,
    x: int,
    y: int,
    width: int,
    height: int,
    shape_type: str = "rectangle",
    fill_color: str = "#dae8fc",
    stroke_color: str = "#6c8ebf",
    font_size: int = 12,
    font_style: int = 0,
) -> str:
    """Generate XML for a shape."""
    style_map = {
        "rectangle": "rounded=0;whiteSpace=wrap;html=1",
        "rounded": "rounded=1;whiteSpace=wrap;html=1;arcSize=10",
        "ellipse": "ellipse;whiteSpace=wrap;html=1",
        "diamond": "rhombus;whiteSpace=wrap;html=1",
        "cylinder": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15",
        "cloud": "ellipse;shape=cloud;whiteSpace=wrap;html=1",
        "document": "shape=document;whiteSpace=wrap;html=1;boundedLbl=1",
        "swimlane": "swimlane;whiteSpace=wrap;html=1;startSize=30",
    }

    base_style = style_map.get(shape_type, "rounded=0;whiteSpace=wrap;html=1")
    style = f"{base_style};fillColor={fill_color};strokeColor={stroke_color};fontSize={font_size};fontStyle={font_style}"

    return f'''        <mxCell id="{shape_id}" value="{text}"
                style="{style}"
                vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry"/>
        </mxCell>'''


def create_connector(
    conn_id: str,
    source_id: str,
    target_id: str,
    label: str = "",
    dashed: bool = False,
) -> str:
    """Generate XML for a connector."""
    dash_style = ";dashed=1;dashPattern=8 8" if dashed else ""
    label_attr = f' value="{label}"' if label else ""

    return f'''        <mxCell id="{conn_id}"{label_attr}
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2{dash_style}"
                edge="1" parent="1" source="{source_id}" target="{target_id}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>'''


def create_diagram_wrapper(content: str, diagram_name: str = "Diagram") -> str:
    """Wrap diagram content in proper XML structure."""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="{diagram_name}" id="diagram-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageWidth="1100" pageHeight="850">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

{content}

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''


def generate_agent_diagram() -> str:
    """Generate the Investment Research Agent architecture diagram."""
    shapes = []
    connectors = []

    # Title
    shapes.append(create_shape(
        "title", "Investment Research Agent Architecture",
        300, 20, 400, 40, "rectangle",
        "#f5f5f5", "#333333", 16, 1
    ))

    # === User Layer ===
    shapes.append(create_shape(
        "user", "User",
        475, 100, 80, 50, "ellipse",
        "#e1d5e7", "#9673a6", 12, 1
    ))

    # === Input Layer ===
    shapes.append(create_shape(
        "cli", "CLI Interface&#xa;(Interactive / One-shot)",
        420, 180, 180, 50, "rounded",
        "#dae8fc", "#6c8ebf"
    ))

    # === Agent Core ===
    shapes.append(create_shape(
        "agent-box", "Agent Core",
        250, 270, 520, 200, "swimlane",
        "#fff2cc", "#d6b656", 14, 1
    ))

    shapes.append(create_shape(
        "client", "ClaudeSDKClient&#xa;(Multi-turn with Memory)",
        280, 310, 180, 60, "rounded",
        "#dae8fc", "#6c8ebf"
    ))

    shapes.append(create_shape(
        "system-prompt", "SYSTEM_PROMPT&#xa;Investment Analyst Persona",
        500, 310, 180, 60, "document",
        "#d5e8d4", "#82b366"
    ))

    shapes.append(create_shape(
        "mcp-server", "MCP Server&#xa;(research-tools)",
        280, 400, 180, 50, "rounded",
        "#f8cecc", "#b85450"
    ))

    shapes.append(create_shape(
        "options", "ClaudeAgentOptions&#xa;max_turns, tools, prompts",
        500, 400, 180, 50, "rectangle",
        "#f5f5f5", "#666666", 11
    ))

    # === Tools Layer ===
    shapes.append(create_shape(
        "tools-box", "Tools",
        250, 510, 520, 100, "swimlane",
        "#e1d5e7", "#9673a6", 14, 1
    ))

    shapes.append(create_shape(
        "report-tool", "@tool&#xa;generate_report",
        290, 550, 140, 50, "rounded",
        "#dae8fc", "#6c8ebf", 11
    ))

    shapes.append(create_shape(
        "future-tools", "Future Tools&#xa;(extensible)",
        460, 550, 140, 50, "rounded",
        "#f5f5f5", "#999999", 11
    ))

    # === Output Layer ===
    shapes.append(create_shape(
        "outputs-box", "Outputs",
        250, 650, 520, 80, "swimlane",
        "#d5e8d4", "#82b366", 14, 1
    ))

    shapes.append(create_shape(
        "console", "Console&#xa;Response",
        290, 685, 100, 40, "rectangle",
        "#dae8fc", "#6c8ebf", 10
    ))

    shapes.append(create_shape(
        "docx", ".docx&#xa;Reports",
        420, 685, 100, 40, "document",
        "#fff2cc", "#d6b656", 10
    ))

    shapes.append(create_shape(
        "drawio", ".drawio&#xa;Diagrams",
        550, 685, 100, 40, "document",
        "#e1d5e7", "#9673a6", 10
    ))

    # === Connectors ===
    connectors.append(create_connector("c1", "user", "cli"))
    connectors.append(create_connector("c2", "cli", "client"))
    connectors.append(create_connector("c3", "system-prompt", "client", "", True))
    connectors.append(create_connector("c4", "options", "client", "", True))
    connectors.append(create_connector("c5", "client", "mcp-server"))
    connectors.append(create_connector("c6", "mcp-server", "report-tool"))
    connectors.append(create_connector("c7", "report-tool", "docx"))
    connectors.append(create_connector("c8", "client", "console"))

    # Combine all elements
    content = "\n".join(shapes + connectors)
    return create_diagram_wrapper(content, "Research Agent Architecture")


def main() -> None:
    """Generate and save the architecture diagram."""
    from research_agent.config import get_outputs_dir
    outputs_dir = get_outputs_dir()

    # Generate diagram
    diagram_xml = generate_agent_diagram()

    # Save to file
    output_path = outputs_dir / "agent_architecture.drawio"
    output_path.write_text(diagram_xml)

    print(f"Architecture diagram saved to: {output_path}")
    print("\nOpen with draw.io (diagrams.net) to view and edit.")


if __name__ == "__main__":
    main()
