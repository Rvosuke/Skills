# Distributed training pitfalls

Concrete traps that look like something else. Read when writing or debugging multi-rank (DDP/FSDP/DeepSpeed) training.

## Collective communication deadlocks

Any collective whose entry condition depends on local state is a deadlock source.

- `if self.some_dict:` followed by `all_gather` — ranks where the dict is empty skip the collective while others enter; the job hangs.
- The same applies to any rank-conditional `dist.*` call, a conditional log that masks a collective, or an early return before a barrier.
- All ranks must hit the same sequence of collectives in the same order; branch conditions that gate a collective must be identical across ranks.

## Do not judge progress by GPU utilization

NCCL spin-wait pegs the GPU at 99–100% while ranks are stalled waiting on each other. A hung job can look fully utilized.

Judge progress by:

- the step counter advancing,
- log lines growing over time,
- expected checkpoints/files appearing.

Not by `nvidia-smi`.

## War story: a missing accumulator as a silent hang

A single missed call to `_accumulate_loss_outputs` made 6 ranks deadlock for 2 hours, and was first misdiagnosed as "just a missing curve in the logs." The symptom was a hang; the cause was one rank taking a code path that skipped a collective.

Lesson: when a hang appears, first enumerate every collective in the step and confirm every rank executes the same set, before speculating about NCCL or the network.

## Prefer callbacks over monkey-patching

A custom trace launcher that monkey-patches official methods is in the same failure class: it creates divergent rank behavior that is hard to see. The framework already provides a callback/hook mechanism; use it.
