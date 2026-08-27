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

- Blocking conclusions ("data is untrustworthy / must fix first / cannot proceed") require a real measurement, not code reading or reasoning. Before making one, run the smallest experiment that could falsify it.
- Run the controlled comparison before constructing a mechanism explanation. Isolate, snapshot-diff, statically enumerate — each takes minutes. Once a hypothesis exists, evidence tends to be used to support it rather than test it.
- Simulation is not measurement. Tables produced with assumed parameters have no evidential value. Numbers used as evidence must come from observing the real thing; label each as measured or inferred.
- An order-of-magnitude deviation is itself a signal — question the explanatory model, do not use it to explain the deviation away.
- Be extra wary when a ready theory is in hand. Existing docs/experience make you skip verification; confirm the theory's preconditions actually hold here.
- Read code through to its side effects. If a branch omits something, check whether it is compensated elsewhere (a variable mutated, a later loop completing it) before concluding it is missing.
- Distinguish hypothesis from conclusion in tone. Mark unverified candidates as such; after falsification, retract explicitly and leave a "falsified, do not revert" note.
- State the scope of every conclusion: "X verified" becomes "part A of X verified, part B not checked." Treating a local check as global is harder to self-catch than speculation.
- Identifying a root cause is not fixing it. Write it down, then change the plan immediately — otherwise all subsequent data rests on a known-wrong premise.
- Distinguish hyperparameters from implementation details. Numerically transparent switches (e.g. gradient checkpointing recomputes activations, does not change gradients) are not hyperparameters. "Align with baseline" must not freeze implementation details, or it rejects the change that actually fixes the problem.

## Reviewing research code

When reviewing a diff or PR, in addition to correctness, check the failure modes specific to research code — the ones that do not crash but invalidate conclusions:

- Collectives: every rank must hit the same `dist.*` calls in the same order; flag any collective gated by a rank-local condition.
- Silent-wrong paths: `.get(key, default)` / `hasattr` probes on fields that should exist, internal function defaults that shadow config values, silently swallowed exceptions — each can hide a misconfiguration as a plausible result.
- Subclassing: parent methods overridden without the parts that preserve cross-rank or accumulator state (see [references/distributed-training.md](references/distributed-training.md)).
- Framework extension points: flag monkey-patching of official methods where a callback/hook exists.
- Leftover debug scaffolding: prints, counters, `--contract-only` switches left in the training path.
- Defensive code: input validation / custom error messages for paths only we call — remove in favor of natural errors.
- Experiments: confirm ablations change only the intended variable; gradient-checkpointing-style switches are implementation details, not hyperparameters, and must not be frozen across comparisons.

Report findings with measured evidence over speculation, and distinguish "will produce wrong data" (blocking) from style nits.

## Documentation for long-running projects

- Docs are external memory, not a status report. Once a conclusion is confirmed, mark it "(已定)" with supporting reasoning; context is lost, docs are not. Read docs before asserting something is undecided.
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
