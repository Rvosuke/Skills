---
name: ml-coding
description: Write, debug, and review ML research code. Use for Research/Training Code — training loops, distributed training, experiments, ablations, and diagnosing silent-wrong results.
---

# ML Coding

Write and diagnose machine learning research the way a lab does: let errors surface, make every experiment trustworthy, and prefer the framework's existing extension point over a custom shim.

## Research code is not product code

- Accept natural errors: missing attributes raise AttributeError, shape mismatches raise from PyTorch, bad configs crash. Do not wrap these with custom messages.
- No defensive programming for ourselves: code and configs are written by us. Correct values live in yaml/docs, not in runtime checks. Do not validate caller inputs (e.g. `training_mode` legality, hyperparameter ranges).
- The only checks worth keeping are those whose absence fails silently — it does not crash but produces wrong data or wrong conclusions. When keeping one, comment what silent failure it prevents.
- One-off debug/verification code (prints, counters, comparisons, `--contract-only` switches) is deleted once the conclusion is written up.
- No `hasattr`/`getattr` probe chains for structures you know. Access the real path; a missing field should raise KeyError naturally. Avoid `.get(key, default)` for fields that must exist, and never stack fallbacks — they turn a missing field into a silently wrong value.
- No default parameter values inside functions. Defaults live only in config, passed explicitly from outside. Internal defaults hide the effective value, and a missed config update silently uses the wrong one.
- Design decisions go in docs and comments, not runtime assertions.
- Research code is still for humans to read (collaborators, future you). Name things for what they mean and keep interfaces ordered; let comments carry the design intent that the deliberate absence of assertions would otherwise leave undocumented. Comments explain why a non-obvious choice exists, not what the next line literally does.

## Reuse before building

- Match existing code: style, call patterns, structure. The official precedent in the same repo is the best spec — copy how it is done, do not reinvent it.
- When subclassing, verify the parent's full capability stays online, not just that your new code works. One missed parent method is a missing feature in single process; in distributed training it can break cross-rank consistency.
- Prefer the framework's official extension point (callbacks, hooks) over monkey-patching internal methods. Custom trace launchers are a recurring source of the hard-to-diagnose failures the framework already has a slot for.

For distributed deadlocks and silent stalls, see [references/distributed-training.md](references/distributed-training.md).

## Diagnosis discipline

When diagnosing silent-wrong results or debugging complex failures, load [references/diagnosis-discipline.md](references/diagnosis-discipline.md).

## Reviewing research code

When reviewing a diff, a PR, or a delegated agent's completed work, load [references/reviewing-research-code.md](references/reviewing-research-code.md).

## Documentation for long-running projects

- Docs are external memory, not a status report. Once a conclusion is confirmed, mark it "(Confirmed)" with supporting reasoning; context is lost, docs are not. Read docs before asserting something is undecided.
- When adding a conclusion, simultaneously fix old content: scan the same doc for stale values/"TBD", check other docs that repeat it, update indexes/maps. Add-without-fix makes the doc self-contradictory.
- Verify cross-references; section numbers drift. After edits, script-check "existing sections vs referenced sections" and link targets.
- Move decided items out of the open-questions list immediately.
- When delegating, agree on filenames first; on collision, merge before continuing, judging each item for staleness rather than concatenating.
- Maintain a HANDOFF.md as the single entry point so a zero-context handoff (new machine, new agent) works by reading docs/ alone: current approach, what is decided (with evidence), what is open, which files, how to run, pitfalls. Handoff relies on docs, not code reading — especially in research code that deliberately avoids assertions.

## Delegation

- When having something rewritten, hand over every non-trivial design choice and what it guards against; a rewrite otherwise loses the implicit semantics.
- Frame the problem narrowly, then add one open-ended requirement (e.g. "trace this field end-to-end and report any branch that depends on its value").
- "Verify my judgment, don't just trust my conclusion" has standalone value, especially when the judgment is wrong.
- The validator itself must be validated: positive-only self-tests miss checks that never fire; craft a wrong sample to confirm it catches it.
