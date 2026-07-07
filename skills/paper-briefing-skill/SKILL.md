---
name: paper-briefing-skill
description: "Route paper-reading requests through reading, HTML rich-text report writing, teaching, critique, or research-writing workflows."
---

# Paper Briefing Skill

Use this as the entrypoint for paper-reading work. A paper briefing is not just
a summary: it turns a paper into material that can be understood, reported,
taught, and questioned.

## Route

Choose the smallest workflow that fits the request:

- Reading: read `references/paper-reader.md` when the user wants to understand a
  paper, extract contributions, map methods, or inspect figures and experiments.
- Report: read `references/paper-report.md` when the user wants a paper
  interpretation report, lab-note, group-meeting report, Notion page, Markdown,
  or HTML-rich briefing. Unless the user explicitly asks for plain text,
  Markdown-only, or another format, default to a standalone HTML rich-text
  report.
- Teaching: read `references/paper-teacher.md` when the user wants an oral
  explanation, talk track, slide outline, Q&A prep, or a beginner-friendly
  walkthrough.
- Critique: read `references/paper-reviewer.md` when the user wants weaknesses,
  risks, rebuttal points, reviewer-style comments, or reproduction concerns.
- Writing: read `references/paper-writing.md` when the user wants to write
  related work, introduction, paper notes, summaries for a manuscript, or
  response prose.

If the request is broad, run Reading first, then add Report, Teaching, or
Critique as needed. If the user asks for everything, produce a compact bundle:
briefing, report outline, talk track, Q&A, and critique.

## Intake

Prefer concrete sources over memory. Accept PDFs, arXiv links, project pages,
OpenReview pages, GitHub repos, supplementary material, or existing notes.

For PDFs, first call the official MarkItDown MCP server named `markitdown` and
its `convert_to_markdown(uri)` tool so the reading workflow can work from a
structured Markdown artifact. Use `file:` URIs for local PDFs. If the MCP server
is unavailable, report that setup problem instead of silently switching to an
unrelated parser.

If a source is missing and cannot be inferred, ask for it. Otherwise proceed and
state the source boundary.

## Quality Rules

- Separate what the paper claims from what the evidence supports.
- Preserve terminology from the paper, but add a short glossary for recurring
  terms.
- Tie figures, tables, and ablations to the claims they support.
- Mark unsupported inferences instead of presenting them as facts.
- Prefer a stable structure over creative formatting.

## Default Bundle

When the user says "paper briefing" without more detail, automatically produce
one standalone HTML rich-text report by following `references/paper-report.md`.
The report must include:

1. One-paragraph thesis.
2. Contribution map.
3. Method walkthrough.
4. Experiment and evidence map.
5. Figure/table guide.
6. Critique and risks.
7. Talk track.
8. Questions to ask the authors or presenter.
