---
name: paper-reader
description: Produce source-grounded research-paper readings with contribution maps, method walkthroughs, experiment evidence, figure guides, glossary, and uncertainty notes.
---

# Paper Reader

Use for understanding a paper from source material. Stay grounded in the
provided paper and distinguish direct content from inference.

## Workflow

1. Identify the paper: title, authors, venue/date when available, source URL or
   file, and any companion code/data.
2. For PDF sources, call the official MarkItDown MCP server named `markitdown`
   and its `convert_to_markdown(uri)` tool to create a Markdown artifact. Use
   `file:` URIs for local PDFs. If the MCP server is unavailable, report the
   setup problem instead of silently switching to an unrelated parser.
3. Extract the central problem, thesis, and claimed contributions.
4. Build a method map: inputs, outputs, modules, training/inference pipeline,
   losses/objectives, and dependencies.
5. Build an evidence map: datasets, metrics, baselines, ablations, figures,
   tables, and what each result supports.
6. Note limits: assumptions, missing comparisons, fragile evaluations, unclear
   details, and reproduction blockers.
7. Create a glossary of key terms and notation.

## Output

Use this structure unless the user asks otherwise:

- Thesis
- Contributions
- Method
- Evidence
- Figures and tables
- Key terms
- Limitations and open questions
- What to read next

## Source Discipline

- Do not invent experiments, claims, citations, or implementation details.
- If citing page/section/figure numbers is possible, include them.
- If the paper is unavailable or partially available, say what was inspected.
- Keep speculative interpretation in a clearly labeled "Inference" section.
