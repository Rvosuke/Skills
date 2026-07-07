---
name: paper-report
description: Write polished research-paper reports for lab notes, Notion pages, group meetings, or experiment logs using source-grounded evidence and clear structure.
---

# Paper Report

Use when the user needs a durable written report from a paper briefing.

## Default Output

Unless the user explicitly requests plain text, Markdown-only, Notion-only, or
another format, produce a standalone HTML rich-text report. Do not return a
pure-text report as the default.

The HTML report should be self-contained and readable when opened directly in a
browser:

- Include `<!doctype html>`, `<html>`, `<head>`, and `<body>`.
- Put all CSS in a `<style>` block in the same file; do not rely on external
  assets unless the user provides them.
- Use semantic sections, headings, tables, callout boxes, and concise lists to
  make the report scannable.
- Preserve source-grounded wording: every major claim should be tied to the
  paper's stated evidence, figure, table, ablation, or experiment when possible.
- If the paper source or evidence is incomplete, mark the boundary clearly
  inside the report instead of filling gaps with confident guesses.

## Report Shape

Default to a concise research note:

1. Metadata: title, authors, venue/date, links, code/data.
2. Why it matters: one short paragraph.
3. Main idea: the paper's core mechanism or insight.
4. Method details: enough for a reader to reconstruct the pipeline.
5. Experiments: datasets, metrics, baselines, ablations, and key numbers.
6. Strengths: claims that are well supported.
7. Weaknesses: unsupported or fragile claims.
8. Relevance: how it relates to the user's project.
9. Follow-ups: experiments, code checks, or papers to read next.

## Style

- Default visual style: clean academic briefing page, with a readable max-width,
  clear hierarchy, subtle borders, highlighted key takeaways, and print-friendly
  colors.
- Prefer dense, scannable prose over marketing language.
- Use tables only when comparison is the clearest form.
- Avoid filler like "this paper presents a novel approach" unless the novelty is
  stated precisely.
- Make figure references useful: explain what the figure proves or fails to
  prove.

## Notion-Oriented Reports

When writing for Notion, use Markdown that converts cleanly:

- Short headings.
- Flat lists.
- No huge tables unless necessary.
- Put action items and open questions near the top or bottom as requested.
