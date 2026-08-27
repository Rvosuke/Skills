---
name: arxiv-blog-skill
description: "Read an arXiv paper and write a Chinese popular-science blog that explains the topic and method in depth. Use for 解读/精读/讲解论文."
---

# Arxiv Blog Skill

Turn a paper into a Chinese popular-science / paper-reading blog (Zhihu, CSDN style). The center of gravity is explaining the topic and the method deeply and accessibly, not summarizing the abstract or translating it.

## Source

- Accept an arXiv id or link; prefer the HTML version at `https://arxiv.org/html/<id>`. A bare id resolves to the latest version. HTML is easier than PDF for both text and figures.
- Ground everything in the paper itself; never invent numbers, results, or terms. State the boundary if something was not read.

## Writing

- Write in Chinese with full-width punctuation（，。：；！？""''——）; keep English terms, numbers, and code half-width, with one space between Chinese and English.
- Write for a curious beginner or hobbyist with no specialized background: build up intuition with analogies before introducing any terminology, and explain why the design is the way it is. The method is still the core of the post — just make it accessible rather than assuming prior knowledge.
- Around five sections works well (e.g. one-sentence overview / background and motivation / method / experiments / takeaways), with subsections inside the method as needed — adjust the count and titles to the paper rather than forcing the template.
- Keep it tight, no padding. Use footnotes or blockquotes for side notes.
- Output Markdown; if the user wants it in Feishu/Lark, Notion, etc., import it there with the appropriate tool.

## Figures

Use the paper's original figures alongside the explanation. In arXiv HTML the image paths are relative, so turn them into absolute links of the form:

`https://arxiv.org/html/<id>v<n>/<filename>.png`

To list every figure with its caption at once:

```bash
python3 scripts/fetch_arxiv_figures.py <arxiv-id> --inline
```

You can also parse the HTML directly. Prefer the method overview, architecture, and key result figures, with one Chinese sentence per figure explaining what it shows.
