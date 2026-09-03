# Diagnosis discipline

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