# Synthetic subject: stop rules for a batch compiler

This file is a synthetic subject, written for this repository, so that
`tools/run_loop_harness.py` has a source to compile that carries no third-party
rights and no acquisition provenance. It is deliberately small and deliberately
boring. It is not a retained source and it is not evidence about the world.

## Section 1 — a round budget stops the wrong thing

A batch compiler that stops after N rounds stops on a property of the operator's
patience rather than a property of the work. The observed failure is that the
last round of a truncated run looks exactly like the last round of a finished
run: both end with a state object, both end with a registry, and neither says
which one it was. The batch is then described as complete because the process
exited zero.

## Section 2 — a stall is not the same as a budget

A run that emits an identical registry and an identical cursor twice in a row
has stopped doing work, and no further round will change that. Detecting the
repeat costs one comparison against the previous round. A round budget cannot
tell a stalled run from a slow one; a repeat check can, and it never truncates a
run that is still moving.

## Section 3 — the completion contract has to be checked by something else

Any completion signal produced by the same process that produces the work is a
self-report. If the compiler says DONE and the harness merely records DONE, the
word carries no information. The cheap check is to re-run the deterministic part
of the pipeline against its own output: if reconciling the finished batch a
second time is not byte-identical, the batch was never finished.
