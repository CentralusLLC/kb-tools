---
type: Template
title: Concept page template
description: Copy this file to create a new knowledge page. Replace type, title, description, tags and the body.
tags: [template]
status: draft
template_for: any
---

<!--
Copy to the right section, then:
- set `type` from docs/conventions.md (Domain Concept, Guide, Policy, Process, ...)
- set generated.by to yourself (human:<name> or <tool>/<version>) and generated.at to now
- list sources and cite them with footnotes [^id]
- status: stable when complete, draft while not; never add verified entries for your own work
- figures go in an assets/ folder beside the page (use `tools/kb figure`), each with an
  element table; diagrams follow references/templates/diagram.md
- link the new page from its section index.md and add a line to docs/log.md
- delete this comment and `template_for`
-->
---
type: Domain Concept
title: <Title>
description: <One sentence an agent can use to decide whether to read this page.>
tags: []
status: <stable | draft>
generated:
  by: <human:name | tool/version>
  at: <YYYY-MM-DDTHH:MM:SSZ>
sources:
  - id: <id>
    resource: <relative path or URL>
---

# <Title>

<Summary first: two or three sentences.>

## <Section>

<Details. One concept per page. Link related pages rather than repeating them.>

> Open question: <anything unresolved>

[^id]: <citation>
