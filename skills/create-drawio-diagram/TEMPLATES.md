# Draw.io Diagram Templates Library

This file contains ready-to-use templates for common diagram types. Copy and customize these templates for quick diagram creation.

## Table of Contents

1. [Basic Flowchart](#basic-flowchart)
2. [System Architecture](#system-architecture)
3. [Network Diagram](#network-diagram)
4. [UML Class Diagram](#uml-class-diagram)
5. [Sequence Diagram](#sequence-diagram)
6. [Entity Relationship Diagram](#entity-relationship-diagram)
7. [Mind Map](#mind-map)
8. [Gantt Chart](#gantt-chart)
9. [AWS Architecture](#aws-architecture)
10. [Decision Tree](#decision-tree)

---

## Basic Flowchart

Simple process flow with start, process, decision, and end nodes.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="Basic Flowchart" id="flowchart-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- Start -->
        <mxCell id="start" value="Start" 
                style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;" 
                vertex="1" parent="1">
          <mxGeometry x="375" y="40" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Process 1 -->
        <mxCell id="process1" value="Initialize System" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="1">
          <mxGeometry x="350" y="140" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Decision -->
        <mxCell id="decision1" value="Ready?" 
                style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;fontStyle=1;" 
                vertex="1" parent="1">
          <mxGeometry x="365" y="240" width="120" height="80" as="geometry"/>
        </mxCell>
        
        <!-- Process 2 -->
        <mxCell id="process2" value="Execute Task" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="1">
          <mxGeometry x="550" y="250" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Error -->
        <mxCell id="error" value="Handle Error" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;" 
                vertex="1" parent="1">
          <mxGeometry x="150" y="250" width="150" height="60" as="geometry"/>
        </mxCell>
        
        <!-- End -->
        <mxCell id="end" value="End" 
                style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;" 
                vertex="1" parent="1">
          <mxGeometry x="375" y="380" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Connectors -->
        <mxCell id="c1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="start" target="process1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="process1" target="decision1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c3" value="Yes" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;fontStyle=1;fontSize=11;" 
                edge="1" parent="1" source="decision1" target="process2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c4" value="No" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;fontStyle=1;fontSize=11;" 
                edge="1" parent="1" source="decision1" target="error">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="process2" target="end">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="error" target="end">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## System Architecture

3-tier architecture with client, application server, and database.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="System Architecture" id="arch-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- Client Layer Container -->
        <mxCell id="client-layer" value="Presentation Layer" 
                style="swimlane;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=14;fontStyle=1;" 
                vertex="1" parent="1">
          <mxGeometry x="80" y="80" width="690" height="150" as="geometry"/>
        </mxCell>
        
        <!-- Web Client -->
        <mxCell id="web-client" value="Web Browser" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="client-layer">
          <mxGeometry x="40" y="50" width="120" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Mobile Client -->
        <mxCell id="mobile-client" value="Mobile App" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="client-layer">
          <mxGeometry x="200" y="50" width="120" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Desktop Client -->
        <mxCell id="desktop-client" value="Desktop App" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="client-layer">
          <mxGeometry x="360" y="50" width="120" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Application Layer Container -->
        <mxCell id="app-layer" value="Application Layer" 
                style="swimlane;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;fontStyle=1;" 
                vertex="1" parent="1">
          <mxGeometry x="80" y="280" width="690" height="200" as="geometry"/>
        </mxCell>
        
        <!-- API Gateway -->
        <mxCell id="api-gateway" value="API Gateway" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="app-layer">
          <mxGeometry x="40" y="50" width="120" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Service 1 -->
        <mxCell id="service1" value="User Service" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="app-layer">
          <mxGeometry x="200" y="50" width="120" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Service 2 -->
        <mxCell id="service2" value="Order Service" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="app-layer">
          <mxGeometry x="360" y="50" width="120" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Cache -->
        <mxCell id="cache" value="Redis Cache" 
                style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#f5f5f5;strokeColor=#666666;fontSize=12;" 
                vertex="1" parent="app-layer">
          <mxGeometry x="530" y="40" width="100" height="80" as="geometry"/>
        </mxCell>
        
        <!-- Data Layer Container -->
        <mxCell id="data-layer" value="Data Layer" 
                style="swimlane;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;" 
                vertex="1" parent="1">
          <mxGeometry x="80" y="530" width="690" height="150" as="geometry"/>
        </mxCell>
        
        <!-- Database -->
        <mxCell id="database" value="PostgreSQL" 
                style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="data-layer">
          <mxGeometry x="170" y="40" width="100" height="80" as="geometry"/>
        </mxCell>
        
        <!-- File Storage -->
        <mxCell id="storage" value="S3 Storage" 
                style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" 
                vertex="1" parent="data-layer">
          <mxGeometry x="330" y="40" width="100" height="80" as="geometry"/>
        </mxCell>
        
        <!-- Connectors -->
        <mxCell id="c1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;dashed=1;" 
                edge="1" parent="1" source="web-client" target="api-gateway">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;dashed=1;" 
                edge="1" parent="1" source="mobile-client" target="api-gateway">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="api-gateway" target="service1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="api-gateway" target="service2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="service1" target="database">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="service2" target="database">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## Decision Tree

Hierarchical decision-making flow.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="Decision Tree" id="tree-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- Root Decision -->
        <mxCell id="root" value="Customer Type?" 
                style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;fontStyle=1;" 
                vertex="1" parent="1">
          <mxGeometry x="350" y="40" width="150" height="100" as="geometry"/>
        </mxCell>
        
        <!-- Branch 1 Decision -->
        <mxCell id="branch1" value="Order Value?" 
                style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" 
                vertex="1" parent="1">
          <mxGeometry x="150" y="200" width="130" height="90" as="geometry"/>
        </mxCell>
        
        <!-- Branch 2 Decision -->
        <mxCell id="branch2" value="Region?" 
                style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" 
                vertex="1" parent="1">
          <mxGeometry x="570" y="200" width="130" height="90" as="geometry"/>
        </mxCell>
        
        <!-- Outcomes -->
        <mxCell id="outcome1" value="Standard&#xa;Shipping" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" 
                vertex="1" parent="1">
          <mxGeometry x="40" y="350" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="outcome2" value="Express&#xa;Shipping" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" 
                vertex="1" parent="1">
          <mxGeometry x="165" y="350" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="outcome3" value="Premium&#xa;Service" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" 
                vertex="1" parent="1">
          <mxGeometry x="290" y="350" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="outcome4" value="Local&#xa;Delivery" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" 
                vertex="1" parent="1">
          <mxGeometry x="510" y="350" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="outcome5" value="International&#xa;Shipping" 
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" 
                vertex="1" parent="1">
          <mxGeometry x="635" y="350" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Connectors from root -->
        <mxCell id="c1" value="New" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;fontStyle=1;fontSize=11;" 
                edge="1" parent="1" source="root" target="branch1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c2" value="Existing" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;fontStyle=1;fontSize=11;" 
                edge="1" parent="1" source="root" target="branch2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <!-- Connectors from branch1 -->
        <mxCell id="c3" value="&lt;$50" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;fontSize=10;" 
                edge="1" parent="1" source="branch1" target="outcome1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c4" value="$50-$200" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;fontSize=10;" 
                edge="1" parent="1" source="branch1" target="outcome2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c5" value="&gt;$200" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;fontSize=10;" 
                edge="1" parent="1" source="branch1" target="outcome3">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <!-- Connectors from branch2 -->
        <mxCell id="c6" value="Domestic" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;fontSize=10;" 
                edge="1" parent="1" source="branch2" target="outcome4">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c7" value="Foreign" 
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;fontSize=10;" 
                edge="1" parent="1" source="branch2" target="outcome5">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## Swimlane Diagram

Process flow across different departments/actors.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="Swimlane Process" id="swim-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageWidth="1100" pageHeight="850">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- Customer Lane -->
        <mxCell id="customer-lane" value="Customer" 
                style="swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontStyle=1;startSize=50;" 
                vertex="1" parent="1">
          <mxGeometry x="80" y="80" width="940" height="150" as="geometry"/>
        </mxCell>
        
        <mxCell id="cust1" value="Place Order" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" 
                vertex="1" parent="customer-lane">
          <mxGeometry x="70" y="45" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="cust2" value="Receive&#xa;Confirmation" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" 
                vertex="1" parent="customer-lane">
          <mxGeometry x="470" y="45" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="cust3" value="Receive&#xa;Product" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" 
                vertex="1" parent="customer-lane">
          <mxGeometry x="770" y="45" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Sales Lane -->
        <mxCell id="sales-lane" value="Sales Team" 
                style="swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;fontStyle=1;startSize=50;" 
                vertex="1" parent="1">
          <mxGeometry x="80" y="230" width="940" height="150" as="geometry"/>
        </mxCell>
        
        <mxCell id="sales1" value="Review Order" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" 
                vertex="1" parent="sales-lane">
          <mxGeometry x="220" y="45" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="sales2" value="Approve Order" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" 
                vertex="1" parent="sales-lane">
          <mxGeometry x="370" y="45" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Warehouse Lane -->
        <mxCell id="warehouse-lane" value="Warehouse" 
                style="swimlane;horizontal=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=14;fontStyle=1;startSize=50;" 
                vertex="1" parent="1">
          <mxGeometry x="80" y="380" width="940" height="150" as="geometry"/>
        </mxCell>
        
        <mxCell id="ware1" value="Pick Items" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" 
                vertex="1" parent="warehouse-lane">
          <mxGeometry x="520" y="45" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <mxCell id="ware2" value="Pack Items" 
                style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" 
                vertex="1" parent="warehouse-lane">
          <mxGeometry x="670" y="45" width="100" height="60" as="geometry"/>
        </mxCell>
        
        <!-- Connectors -->
        <mxCell id="c1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="cust1" target="sales1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="sales1" target="sales2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="sales2" target="cust2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="sales2" target="ware1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="ware1" target="ware2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="c6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;" 
                edge="1" parent="1" source="ware2" target="cust3">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## Quick Reference: Common Shapes

```xml
<!-- Rectangle (Process) -->
<mxCell id="rect" value="Text" 
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>

<!-- Rounded Rectangle -->
<mxCell id="round" value="Text" 
        style="rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#e1d5e7;strokeColor=#9673a6;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>

<!-- Ellipse (Start/End) -->
<mxCell id="ellipse" value="Text" 
        style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="100" height="60" as="geometry"/>
</mxCell>

<!-- Diamond (Decision) -->
<mxCell id="diamond" value="Text?" 
        style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="80" as="geometry"/>
</mxCell>

<!-- Parallelogram (Input/Output) -->
<mxCell id="para" value="Text" 
        style="shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>

<!-- Cylinder (Database) -->
<mxCell id="cylinder" value="Text" 
        style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#dae8fc;strokeColor=#6c8ebf;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="80" height="100" as="geometry"/>
</mxCell>

<!-- Cloud -->
<mxCell id="cloud" value="Text" 
        style="ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="80" as="geometry"/>
</mxCell>

<!-- Document -->
<mxCell id="doc" value="Text" 
        style="shape=document;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#f5f5f5;strokeColor=#666666;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="80" as="geometry"/>
</mxCell>

<!-- Actor (Person) -->
<mxCell id="actor" value="Text" 
        style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#d5e8d4;strokeColor=#82b366;" 
        vertex="1" parent="1">
  <mxGeometry x="115" y="100" width="30" height="60" as="geometry"/>
</mxCell>

<!-- Hexagon -->
<mxCell id="hex" value="Text" 
        style="shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;" 
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

## Python Helper Functions

```python
def create_shape(shape_id, text, x, y, width, height, shape_type="rectangle", 
                 fill_color="#dae8fc", stroke_color="#6c8ebf"):
    """Generate XML for a shape."""
    
    style_map = {
        "rectangle": "rounded=0;whiteSpace=wrap;html=1",
        "rounded": "rounded=1;whiteSpace=wrap;html=1;arcSize=10",
        "ellipse": "ellipse;whiteSpace=wrap;html=1",
        "diamond": "rhombus;whiteSpace=wrap;html=1",
        "parallelogram": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1",
        "cylinder": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15",
        "cloud": "ellipse;shape=cloud;whiteSpace=wrap;html=1",
        "document": "shape=document;whiteSpace=wrap;html=1;boundedLbl=1",
        "actor": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0",
    }
    
    base_style = style_map.get(shape_type, "rounded=0;whiteSpace=wrap;html=1")
    style = f"{base_style};fillColor={fill_color};strokeColor={stroke_color}"
    
    return f'''<mxCell id="{shape_id}" value="{text}" 
        style="{style}" 
        vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry"/>
</mxCell>'''


def create_connector(conn_id, source_id, target_id, label="", dashed=False):
    """Generate XML for a connector."""
    
    dash_style = ";dashed=1;dashPattern=8 8" if dashed else ""
    label_attr = f' value="{label}"' if label else ''
    
    return f'''<mxCell id="{conn_id}"{label_attr} 
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2{dash_style}" 
        edge="1" parent="1" source="{source_id}" target="{target_id}">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>'''


def create_diagram_wrapper(content, diagram_name="Diagram"):
    """Wrap diagram content in proper XML structure."""
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" version="24.0.0">
  <diagram name="{diagram_name}" id="diagram-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" page="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
{content}
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
```

## Usage Example

```python
# Create shapes
shapes = []
shapes.append(create_shape("start", "Start", 375, 40, 100, 60, "ellipse", "#d5e8d4", "#82b366"))
shapes.append(create_shape("process", "Process Data", 350, 140, 150, 60, "rectangle", "#dae8fc", "#6c8ebf"))
shapes.append(create_shape("end", "End", 375, 240, 100, 60, "ellipse", "#d5e8d4", "#82b366"))

# Create connectors
connectors = []
connectors.append(create_connector("c1", "start", "process"))
connectors.append(create_connector("c2", "process", "end"))

# Combine and wrap
content = "\n".join(shapes + connectors)
diagram = create_diagram_wrapper(content, "Simple Flow")

# Save
with open('/mnt/user-data/outputs/diagram.drawio', 'w') as f:
    f.write(diagram)
```
