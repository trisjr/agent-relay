# Hypothesis ledger

Use for uncertain causes, interacting failures, or repeated attempts. A short list is enough; do not create a table for an obvious correction. Record the starting state and any run/time/cost budget. Fill the prediction before the experiment.

| Hypothesis | Supporting evidence | Discriminating experiment | Expected if true | Observed result | Conclusion / next step |
| --- | --- | --- | --- | --- | --- |
| Host timezone changes a date required to be UTC | CI and local disagree near midnight | Hold input and version fixed; vary `TZ` | Output changes with `TZ`, reproducing the CI mismatch | Recorded outputs under both zones match the prediction | Mechanism supported; check nearby dates before repair |
| A resolved dependency version differs between passing and failing installs | Failure began after install | Compare resolved versions from both lockfiles/environments | Versions differ | Same versions | Version drift refuted; other dependency or artifact differences (build cache, platform wheels, postinstall output) remain untested |
| Concurrent claims race | Two workers report the same job | Force overlapping claims against the test DB | Both claim the job | DB unavailable; harness failed before either claim | Inconclusive; restore the fixture or obtain a trace |

Use **confirmed** only when the mechanism explains the relevant observations and plausible alternatives have been tested as needed. Record evidence, not just a status word.

## Repairs are a separate record

| Attempt | Why it should help | Check and actual result | What it establishes |
| --- | --- | --- | --- |
| Increase TTL (earlier user attempt) | Suspected premature expiration | Original assertion still fails | Failed fix; alone it neither confirms nor refutes expiration |

A failed fix may be incomplete, based on the wrong cause, or expose another fault. A test harness failure may leave its effectiveness unknown. Preserve earlier evidence; remove only your own unsuccessful experimental edits when safe, without reverting pre-existing work.

Repeated failures trigger reassessment, not an automatic count-based stop or permission to keep guessing. Continue only with a distinct experiment justified by new evidence and within budget. At a stop, record what is known, what remains unconfirmed, the blocker, and what would permit progress.

## Flaky checks: choose a budget, not a magic pass count

Prefer a controlled reproducer (barrier, clock, seed, ordering) over brute-force reruns. State the environment, baseline failure estimate and its source, purpose of the sample, and run/time budget before sampling. An expensive suite with a five-minute budget may justify fewer runs and an explicit verification limit.

For independent runs with a stable failure probability `p`, the chance of seeing no failures in `n` runs is `(1-p)^n`. To have at least `1-alpha` probability of observing a failure if that rate persists, choose:

```text
n >= ceil(log(alpha) / log(1-p)), for 0 < p < 1
```

At `p = 0.2`, 14 runs reach a 95% detection chance; 21 reach 99%. The common `3/p` estimate approximates the 95% target for small `p`; it is not a minimum or a verification guarantee. Unknown rates, correlated runs, cached state, and changed load invalidate a confident use of this calculation.

After a repair, zero failures in a preselected sample of `n` independent, representative runs gives a one-sided 95% upper bound `1 - 0.05^(1/n)` on the failure probability, approximately `3/n` for large `n`. Zero in 20 still permits about 14%; it does not mean a 99% chance the fix is correct. A causal reproducer plus representative checks is stronger evidence than a streak alone.

This zero-failure bound follows by solving `(1-p)^n = 0.05`, the one-sided case of [exact binomial confidence limits](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm).

Report all failures and total runs before/after, not only the latest green streak. Do not reset the count at a failure or rerun until green. If the original failure recurs, reassess the repair; when the budget ends, report the remaining uncertainty rather than extending indefinitely or declaring success.
