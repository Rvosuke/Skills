# Translation Guide

## Natural Chinese

The goal is natural academic Chinese, not word-by-word calques. Naturalize the syntax while keeping a formal academic register — do not colloquialize.

- Prefer the subject–method–condition–result information order; avoid chains of long attributives and English-inversion residue.
- Let real verbs carry the sentence. English "conduct/perform/achieve/make + noun" comes out as 进行/作出/实现/完成 + 名词 in translationese; restore the action verb ("对方案进行讨论" → "讨论方案").
- Chinese repeats nouns for cohesion; it does not use English-style pronoun back-reference. Replace 前者/后者, 上述/该/此 with the repeated noun, and avoid calque frames: 当……时 (just state it), sentence-initial 在……, 作为……, the 是……的 judgment construction, and 被 overuse — Chinese has a notional passive ("糖吃光了"), so use 被 only for genuine adversity or unknown agent.
- For a breathless long sentence, first add a comma at a natural pause rather than splitting; academic prose may stay long, it just must not run out of air. Split only when one sentence packs several independent ideas chained by 的/从而/进而/基于.
- Keep one Chinese rendering for one source concept throughout. Chinese tolerates repetition; do not rename the same term just to avoid repeating it.
- Do not coin neologisms. If a term has no standard Chinese rendering, keep the English (see Proper nouns) rather than inventing a clever translation. Use em-dashes (——) sparingly; a comma or period almost always reads better.
- Long sentences may be split and adjacent short ones merged, but causality, contrast, condition, and scope must survive. Resolve pronouns explicitly; repeat a subject name when needed rather than inventing an explanation.
- Match the source's exact hedge and strength — translate "significantly" as 显著 only because the source says so, and never add intensifiers (至关重要/毫无疑问/显著) that are not in the source. Preserve negations, comparatives, hedges, confidence intervals, units, and numeric precision.
- Use full-width punctuation in Chinese prose; keep formulas, code, labels, and English abbreviations in their original form, with one space between Chinese and English.
- First occurrence of an abbreviation follows the source. If written as "Chinese (English, ABBR)", the English and abbreviation must come from the official source.

## Structure preservation

- Replace only text nodes or explicitly allowed presentation containers; do not regenerate the page, and do not change IDs or link relations.
- Do not touch MathML, LaTeX annotations, equation numbers, or citation targets. Natural-language comments in algorithms may be translated; identifiers, function names, and pseudocode semantics may not.
- Preserve `<table>` cell order, `rowspan`/`colspan`, header semantics, and values. Image alt text may be translated; the embedded `src` bytes must not change because of translation.
- Bibliographic entries stay in their original language by default, to avoid making papers hard to retrieve.

## Proper nouns

- Keep these in English: datasets and versions, benchmarks/task suites/splits, models/methods/baselines/policies/architectures, robots/arms/sensors/hardware platforms, simulation environments/worlds, repos/orgs/packages/commands/URL handles, metric abbreviations/axis and legend labels, class and action labels.
- A capitalized word is not necessarily a proper noun (it may just start a sentence); judge from type, position, and defining context. The same English word may be a proper noun in one place and a common word in another.
- No global replace. When a homograph has a common meaning, edit case by case by context; do not force a common word in a reference title to match this paper's proper noun; do not touch formula, code, or URL bytes.

## Final pass

- Search for residual navigation text, placeholders, and untranslated body English (legitimate English proper nouns and references do not count), plus mixed punctuation, runs of spaces, and orphaned brackets.
- Spot-check high-risk paragraphs: abstract, conclusion, number-dense passages, table captions, limitation statements.
- Numbers, percentages, units, variables, citations, footnotes, and equation numbers match the original item by item; "reads well" is not a substitute for checking.
