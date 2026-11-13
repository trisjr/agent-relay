---
name: verify
description: Calibre lifecycle state `verify` — for an issue labeled `state:verify`, prove every acceptance criterion against the current code by running its check now and recording the command, what it actually showed, and the commit; plus one full regression run. Use for "verify issue 42", "kiểm chứng issue này", "chứng minh #42 đã xong", and whenever code changed after an earlier verification. Always done by this skill, never delegated to a provider; it changes no code and no tests. Skip issues with no `state:*` label and ordinary requests to run tests that do not involve the lifecycle.
argument-hint: "[issue number]"
---

# verify

Prove each acceptance criterion against the code as it now stands. The most expensive failure in agent-assisted work is "done" reported without having been checked; this state exists so that "done" always comes with what was run and what it showed.

**State:** `state:verify` · **Done by:** this skill, always. A provider's own verification step is welcome extra signal but never replaces this record · **Gate:** none · **Next:** `calibre:review`, or `calibre:handoff` on track `chore`

## Before you start

The label script is `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh` ([lifecycle.sh](../run/scripts/lifecycle.sh) in the `calibre:run` skill); the commands below write it as `lifecycle.sh`.

Follow the [shared rules](../run/references/rules.md): read the config, run `lifecycle.sh show <n>`, and continue only if the task is in `verify`.

## Do

1. Note the current commit. Everything below is evidence about that commit.
2. For each criterion in `spec.md`, run the check named for it in `plan.md` (on track `chore`, the check written at triage). Run it now: a result remembered from the build, or reported by the provider, is not evidence.
3. Record what the run actually printed or showed, trimmed to the lines that decide pass or fail.
4. Run the repo's full test suite once and record the result, to catch what the change broke elsewhere.
5. A check that needs a person (a device, a visual judgment, a production-only system): describe exactly what to do, ask the user to do it, and record the result as `manual, reported by <who>`.

## Produce

`evidence.md` in the record ([record.md](../run/references/record.md)), committed:

```markdown
## Verified at
3f2a91c, 2026-11-13
## Criteria
| ID | Check run | Observed | Result |
|---|---|---|---|
| AC-1 | `npm test -- export.spec.ts` | 12 passed, 0 failed | pass |
| AC-2 | `curl -s localhost:3000/invoices.csv \| head -1` | `id,date,total` | pass |
## Regression
`npm test` → 418 passed, 0 failed
```

"Works as expected" is not an observation. If you cannot say what you saw, the check did not happen.

## Exit when

- Every criterion has a row with a check that was run in this state and a `pass`.
- The regression run is recorded.
- `evidence.md` is committed, and the code has not changed since the commit it names.

Then `lifecycle.sh state <n> review` and `calibre:review` — or, on track `chore`, `lifecycle.sh state <n> handoff` and `calibre:handoff`.

## When a criterion fails

List the failing IDs with what was observed, then `lifecycle.sh state <n> implement` and `calibre:implement`. Count the `verify → implement` rows in the `task.md` history: once they reach `verify.max_loops` (default 3), repeated fixing is not converging. Run `lifecycle.sh wait <n> blocked` and bring the pattern to the user instead of trying again.

A criterion that turns out to be untestable or wrong is a spec problem: return to `implement` and from there to `specify`, rather than quietly rewording it here.

## Do not

- Change code or tests in this state. Fixing and judging in the same step is how a failing check becomes a passing one without the behavior changing.
- Mark a criterion as passed because a neighbouring test passed.
- Skip the fresh run because nothing "should" have changed.
