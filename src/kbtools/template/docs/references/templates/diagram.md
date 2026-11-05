---
type: Template
title: Diagram template
description: Copy the block below into a page to add a relationship diagram with its required element description (nodes and edges, visible vs inferred).
tags: [template, diagram, mermaid]
status: stable
template_for: diagram section
---

<!--
Copy everything below this comment into the page where the diagram belongs.
Rules (docs/conventions.md#diagrams):
- every node and edge in the diagram appears in the tables
- an edge is "visible" only if the source draws it (glued connectors in slides.md
  are direct evidence); otherwise "inferred", with the evidence stated
- do not turn spatial proximity into a relationship
- draw inferred edges dashed (-.->) so the difference shows in the diagram too
-->

### <Diagram title>

```mermaid
flowchart LR
  prospect[Prospect] --> qualification[Qualification]
  qualification -.-> opportunity[Opportunity]
```

*Diagram: <what it shows>.* Source: `docs/sources/<file>`, slide <n> (figure:
[render crop](assets/<name>.png)).

**Nodes**

| Node | What it is | Source |
| --- | --- | --- |
| Prospect | <meaning> | slide <n> |
| Qualification | <meaning> | slide <n> |
| Opportunity | <meaning> | slide <n> |

**Edges**

| From | To | Relationship | Evidence |
| --- | --- | --- | --- |
| Prospect | Qualification | <leads to> | visible: arrow drawn on slide <n> |
| Qualification | Opportunity | <leads to> | inferred: <why> |
