---
name: paper-reviewer
description: Critique research papers with reviewer-style evidence checks, weakness analysis, reproduction risks, missing comparisons, and actionable questions.
---

# Paper Reviewer

Use when the user wants to challenge a paper's claims.

## Review Axes

Evaluate:

- Problem framing: is the problem important and well scoped?
- Novelty: what is new versus recombined?
- Technical soundness: are assumptions, objectives, and implementation details
  clear enough?
- Evidence: do experiments support the claimed contributions?
- Comparisons: are baselines, metrics, datasets, and ablations adequate?
- Reproducibility: are code, data, hyperparameters, checkpoints, and compute
  requirements available or inferable?
- Impact: what project decisions could this paper change?

## Output

Use:

1. Verdict in one paragraph.
2. Strong points.
3. Major concerns.
4. Minor concerns.
5. Missing experiments or checks.
6. Questions for authors or presenter.
7. Risk to adoption or reproduction.

## Evidence Labels

Label each concern:

- Supported: directly grounded in paper content.
- Weakly supported: inferred from partial evidence.
- Not assessable: source does not contain enough information.

Do not invent reviewer identities or external evidence unless the user asks for
external literature comparison.
