---
name: triage
description: Calibre lifecycle state `triage` — for an issue labeled `state:triage`, decide whether the request is worth doing and on which track (feature, bug, chore, spike) by checking for duplicates, behavior that already exists and earlier rejections, and by quickly confirming a reported bug is real; then stop at gate G1 for the user's decision. Use for "triage issue 42", "issue này có đáng làm không", "phân loại issue này", a deferred task being resumed, or a task whose scope changed. It proposes a verdict; it never closes an issue or starts work on its own judgment. Skip issues with no lifecycle label unless the user wants them on the lifecycle (`calibre:intake` comes first), and skip triaging pasted feedback that is not an issue.
argument-hint: "[issue number]"
---

# triage

Decide whether the request is worth doing and on which track, before anyone spends effort specifying it. A request that is a duplicate, already built, or out of scope should end here, cheaply.

**State:** `state:triage` · **Done by:** this skill · **Gate:** G1 · **Next:** `calibre:specify`, or `calibre:implement` on track `chore`

## Before you start

The label script is `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh` ([lifecycle.sh](../run/scripts/lifecycle.sh) in the `calibre:run` skill); the commands below write it as `lifecycle.sh`.

Follow the [shared rules](../run/references/rules.md): read the config and run `lifecycle.sh show <n>`. Triage is also where a task returns to, so two cases bring it here from another state:

- **The scope changed**, and the user wants the task judged again: `lifecycle.sh state <n> triage`.
- **The task was deferred** (`wait:deferred`) and is being picked up: `lifecycle.sh resume <n>`, which also returns it to `triage`.

Otherwise continue only if the task is already in `triage`.

## Do

1. **Classify the track**: `feature`, `bug`, `chore` or `spike`. [tracks.md](../run/references/tracks.md) has the tests for each; when torn between `feature` and `chore`, it is a `feature`.
2. **Size it**: `small`, `medium` or `large`. A `large` task, or one that bundles separable outcomes, is a candidate for splitting.
3. **Already there?** Search the code and docs for the behavior itself, not the requester's wording. For a bug, "already there" means already fixed. Note where you looked.
4. **Duplicate?** Search open and closed issues (`gh issue list --state all --search "<concept>"`).
5. **Decided before?** Check documented scope and conventions (README, `AGENTS.md`, ADRs, earlier issues closed as `resolution:rejected`).
6. **Bug only: is it real?** Try the reported steps without changing code and without commands that have effects outside the repo. Record `reproduced`, `not reproduced` or `not attempted: <reason>`. Stop at "is it real"; finding the cause is the `specify` state's job.
7. **Reach a verdict** — one of `accept`, `reject`, `duplicate`, `already-done`, `defer`, `split`, `needs-info` — and point to the evidence for it: the file where the behavior lives, the issue it duplicates, the document it contradicts.
8. **Track `chore` only:** write the acceptance criteria now, since no `specify` state will. Give each an ID (`AC-1`, …) and say how it will be checked.

## Produce

Post the verdict as an issue comment; it is the record for this state.

```markdown
**Lifecycle · triage**

Customers cannot get their invoices out as a file today; this proposes building a CSV export.

- Track: feature
- Size: medium
- Verdict: accept
- Evidence: no export code exists (searched `src/billing/` and docs for "export", "csv"); no matching issue
- Bug check: n/a

<for `chore`>
Acceptance:
- AC-1: … — checked by …
```

Open with one sentence a product manager can read without the code: what is being asked and what you propose. The evidence below it is where file paths and symbols belong.

## Gate G1

Present the verdict and its evidence, run `lifecycle.sh wait <n> approval`, and stop. The decision is the user's; act on what they decide, not on what you proposed.

| Decision | Do |
|---|---|
| accept | `lifecycle.sh track <n> <track>`, then `lifecycle.sh state <n> specify --comment "G1: accepted by <who>, track <track>"` — or `state <n> implement` on track `chore`. Omit `--comment` when `issue_comments` is `record` |
| reject, duplicate, already-done | close through `calibre:close` with the reason |
| defer | `lifecycle.sh wait <n> deferred`; note in the comment what would make it worth revisiting |
| split | show the child issues you would create, create them on a yes, then close as `superseded` through `calibre:close` |
| needs-info | post the specific questions, `lifecycle.sh wait <n> needs-info` |

Moving to the next state clears the `wait:approval` label on its own.

## Exit when

- The verdict comment exists and cites evidence a reader can follow.
- The user decided at G1, and the decision is what you acted on.
- For `accept`: the track label is set.

## Do not

- Design a solution or suggest a fix. Triage answers whether, not how; a guessed cause passed along as a finding sends the next state the wrong way.
- Close the issue on your own verdict. Until G1 it is a proposal.
- Treat "not now" as a rejection. That is `defer`.
