---
name: arxiv2zhtml
description: Translate an arXiv/official HTML paper into Simplified Chinese and output a fully offline single-file HTML. Use when 翻译论文/arXiv HTML 为中文, inlining images and resources, or producing a self-contained Chinese HTML that preserves the original structure. Requires file access and Python 3; do not start an HTTP server.
---

# Arxiv to Chinese HTML

Translate a paper's official HTML into natural, faithful Simplified Chinese and output a single self-contained HTML file with no external dependencies, for offline reading. Structural and resource integrity comes before visual polish.

## Sources and boundaries

- Prefer official HTML (`https://arxiv.org/html/<id>`; a bare id resolves to the latest version). Use official TeX to verify formulas or structure when the HTML is broken; PDF only for what neither source confirms.
- Do not add facts, explanations, or citations absent from the paper. Sentences may be split, merged, or reordered, but facts, numbers, negations, comparisons, and claim strength must not drift.
- Preserve the section tree, formulas/MathML, tables (cell order, `rowspan`/`colspan`, values), figures and captions, algorithms, footnotes, appendices, references, and link relations. Replace only text nodes; do not regenerate the page or change IDs.
- Keep dataset, benchmark, task suite, model, robot/arm platform, simulation environment, repo/handle, metric label, and class label **names in English** — do not translate them mechanically. Keep field-convention English terms such as token and embedding as well. Do not translate formulas, code, URLs, or labels.
- Never start an HTTP server or listen on a port; preview locally with `file://` only.

## Workflow

1. **Translate** section by section in natural academic Chinese word order (subject–method–condition–result), avoiding word-by-word mapping and English inversion. Use full-width punctuation in Chinese; keep formulas, code, and English abbreviations in their original form. Treat tables, captions, footnotes, and appendices as first-class content, not optional. Keep the proper nouns listed above in English as you encounter them; do not pre-scan the whole paper to build a glossary.
2. **Inline resources**: inline CSS into `<style>` and any necessary JS into `<script>` (prefer CSS over script); download paper images and encode them as `data:` URIs with the real MIME type; do not reference external fonts. Check every `src`/`srcset`/`href`/CSS `url()`/`@import` — rendering resources must not hit the network (`#fragment` and `data:` are fine). Remove site navigation, feedback, and telemetry controls, but not internal paper navigation, footnote backlinks, or reference links.
3. **Save** to a new file; do not overwrite the original HTML (a `_zh` or version suffix is enough — no hashes or baseline ceremony).
4. **Structure audit**: run the deterministic script to verify structure and resources are conserved:

```bash
python3 scripts/audit_html.py original.html translated.html --json audit.json
```

   It checks DOM/IDs, MathML hashes, table grids, image data URIs and decoded hashes, bibliography/footnote/citation edges, internal link targets, and external dependencies. If an unauthorized structural change appears, stop and fix it rather than widening an allowlist to hide the diff. In translation mode a large visible-text diff is expected; focus on the structural items.
5. **Spot-check**: open the file with Chromium/Chrome via `file://` at desktop width once: formulas/MathML render readably, images show offline, tables do not overflow the page, and there is no clipped or low-contrast text. If Chromium is unavailable, state that visual checking was not done rather than passing off static parsing as a visual pass.

## Optional (only when asked)

- **Numbered citations**: when converting author-year citations to `[n]`, assign stable numbers by bibliography order; keep every number as an internal link to its entry. Runs may render as ranges but all member links must remain reachable.
- **Proper-noun fix-up / layout-only mode**: for an existing Chinese draft, change only mistranslations confirmed against the original, no drive-by polishing. In layout-only mode freeze all visible text and touch only containers, CSS, and accessibility attributes.

Translation details are in [references/translation-guide.md](references/translation-guide.md).
