---
name: handoff
description: Calibre lifecycle state `handoff` — for an issue labeled `state:handoff`, put the verified and reviewed change in front of the person who accepts it by merging the spec back, writing the handoff summary with each criterion mapped to its evidence, opening the pull request after the user confirms, and waiting at gate G3. Use for "bàn giao issue 42", "mở PR cho issue 42", "handoff issue 42", and to check whether the pull request was accepted. It never merges the pull request itself. Skip issues with no `state:*` label and ordinary requests to open a pull request that do not involve the lifecycle.
argument-hint: "[issue number]"
---

# handoff

Put the finished change in front of the person who accepts it, with everything they need to decide quickly: what was asked, what was built, and the proof for each criterion.

**State:** `state:handoff` · **Done by:** this skill; a provider only merges its spec back · **Gate:** G3 · **Next:** `calibre:close`

## Before you start

The label script is `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh` ([lifecycle.sh](../run/scripts/lifecycle.sh) in the `calibre:run` skill); the commands below write it as `lifecycle.sh`.

Follow the [shared rules](../run/references/rules.md): read the config, run `lifecycle.sh show <n>`, and continue only if the task is in `handoff`. If it is already waiting with `wait:approval`, the pull request is open: go to *Gate G3*.

## Do

1. **Re-check currency.** `evidence.md` and, off the `chore` track, `review.md` must both name the current code (see *Is the evidence still current?* in [record.md](../run/references/record.md)). If not, return to `verify`.
2. **Merge the spec back**, when the task has a spec change to merge (`change` in `task.md`; a `chore` has none), following `handoff.archive` in the config:
   - `before-pr` (default): run the spec provider's archive step on the task branch now and commit it, so the pull request carries the updated specs. The [OpenSpec adapter](../run/references/providers/openspec.md) describes it. This touches only spec folders, so the evidence stays valid.
   - `after-merge`: leave it; after the merge it needs its own commit on the default branch, which you will have to raise with the user.
   - `never`, or no spec provider with an archive step: skip.
3. **Write `handoff.md`** in the record: a summary, the criteria with the evidence for each, departures from the plan, what was not done and the follow-ups, and how to try the change. Commit it.
4. **Open the pull request.** Show the title and body first (the body is `handoff.md`), and on a yes push the branch and run `gh pr create`. Reference the issue as `Refs #<n>`, not `Closes #<n>`: an auto-close on merge would close the issue behind the lifecycle's back, without its resolution label.
5. Post the pull request link on the issue under `**Lifecycle · handoff**`, then `lifecycle.sh wait <n> approval`.

## Gate G3

What counts as accepted is `handoff.accepted_when` in the config:

- `merged` (default): the pull request is merged. Check with `gh pr view <pr> --json state,mergedAt`.
- `approved`: the pull request has an approving review, or the user says it is accepted.

| Outcome | Do |
|---|---|
| accepted | close as `done` through `calibre:close`; its closing comment records G3 — who accepted, and the pull request — because once the branch is merged there is no task branch left to commit the record to |
| changes requested | note it under G3 in `task.md`, `lifecycle.sh state <n> implement`; the fix comes back through `calibre:verify` and `calibre:review` |
| the wrong thing was built | `lifecycle.sh state <n> specify`, then `calibre:specify` |
| abandoned | close as `canceled` through `calibre:close` |

## Exit when

- `handoff.md` maps every criterion to its evidence and names what was left out.
- The pull request exists and is linked on the issue.
- The outcome at G3 is recorded: in the closing comment when accepted, in `task.md` when the task goes back.

## Do not

- Merge the pull request yourself. Acceptance is the one decision this lifecycle never takes for the user.
- Force-push over a branch someone is reviewing.
- Describe the change as complete when `Not done / follow-ups` is not empty; say what is missing in the summary.
