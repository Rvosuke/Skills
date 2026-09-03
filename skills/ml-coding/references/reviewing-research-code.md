# Reviewing research code

Load this when reviewing a diff, a PR, or a delegated agent's completed work. Beyond ordinary correctness, look for the failure modes specific to research code — the ones that do not crash, but quietly invalidate a conclusion.

## Output collision (check this first)

Before approving any change that copies a config, adds a run, or introduces new output paths: enumerate every path the change will write, and intersect that set with what already exists on disk.

This catches a class of loss that no test detects. A config cloned from a previous run inherits its `output_dir`, `save_dir`, `run_name`, and every `{step}`-templated path. If the new run's step boundaries overlap the old run's, it overwrites checkpoints that took days of GPU time and whose measured results are already cited as a baseline. The run itself succeeds; the loss is silent and unrecoverable.

The second-order effect is worse than the overwrite. Orchestrators that skip a stage when its artifact already exists will treat the *previous* run's artifact as this run's output and skip the stage entirely — so the new run proceeds on stale data and reports a plausible number.

Applies to: checkpoint and export directories, dataset plates, dataset repo ids, work and scratch roots, log paths, and W&B run names.

## Silent-wrong paths

- Collectives: every rank must hit the same `dist.*` calls in the same order; flag any collective gated by a rank-local condition.
- `.get(key, default)` / `hasattr` probes on fields that should exist, internal function defaults that shadow config values, silently swallowed exceptions — each can hide a misconfiguration as a plausible result.
- Subclassing: parent methods overridden without the parts that preserve cross-rank or accumulator state (see [distributed-training.md](distributed-training.md)).
- Framework extension points: flag monkey-patching of official methods where a callback or hook already exists.

## Ordering against the framework

When a change writes model or optimizer state around a framework's own load path, the mount point decides whether it takes effect at all. State written before the framework restores from a checkpoint is silently overwritten by that restore. Require the mount point to be named, and require numeric evidence that the write survived — a logged message proves the code ran, not that the values stuck.

Under sharded optimizers, parameter writes must also reach the fp32 master copy, or the next step restores the pre-write values.

## Experiment hygiene

- Confirm ablations change only the intended variable.
- Gradient-checkpointing-style switches are implementation details, not hyperparameters, and must not be frozen across comparisons.
- A changed refresh or checkpoint interval silently rescales anything defined in steps (EMA horizons, warmup, schedules). Recheck those constants when an interval changes.

## Leftover scaffolding and defensive code

- Prints, counters, and `--contract-only` switches left in the training path.
- Input validation and custom error messages for call sites only we control — remove in favor of natural errors.

## Reporting

Prefer measured evidence over speculation, and separate "will produce wrong data" (blocking) from style nits.

Note where a delegated agent filed its own findings. A risk raised only under "open questions" while the summary reports success still transfers the decision to the reviewer — read those sections as part of the diff, not as commentary.