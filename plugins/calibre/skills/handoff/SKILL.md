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

1. **Re-check currency.** `evidence.md` and, off the `chore` track, `review.md` must both name the current code (see *Is the evidence still current?* in [record.md](../run/references/record.md)). If not, return to `verify`. The plan of record must also read as it was approved at G2, ticked tasks aside (same section). If it was edited since, do not archive it: go back to `implement` and from there to `plan`, so the edit is approved before it is delivered.
2. **Merge the spec back**, when the task has a spec change to merge (`change` in `task.md`; a `chore` has none) that an earlier handoff has not archived already, following `handoff.archive` in the config:
   - `before-pr` (default): run the spec provider's archive step on the task branch now, point the `Sources` rows of `task.md` at where the files moved, and commit both together, so the pull request carries the updated specs. The [OpenSpec adapter](../run/references/providers/openspec.md) describes it. This touches only spec and record folders, so the evidence stays valid.
   - `after-merge`: leave it; after the merge it needs its own commit on the default branch, which you will have to raise with the user.
   - `never`, or no spec provider with an archive step: skip.
3. **Drop the scaffolding.** When `Sources` in `task.md` lists a derived plan that is a file of its own — an execution plan, a fix plan — delete each file, add `(removed at handoff)` to its row and commit. The row keeps the path, which is what lets the file be restored if the task comes back. A derived plan restates the plan of record or a fix list and is not part of what is delivered. A derived plan inside the spec provider's change folder stays with the change. The evidence stays valid here too: the currency check ignores the folder the plan lived in.
4. **Write `handoff.md`** in the record: a summary, the criteria with the evidence for each, departures from the plan, what was not done and the follow-ups, and how to try the change. A criterion whose result in `evidence.md` is `post-deploy` is not proven yet: say so in its evidence cell, and list the check under `Not done / follow-ups` with its exact steps and who runs them. Commit it.
5. **Open the pull request.** Show the title and body first (the body is `handoff.md`), and on a yes push the branch and run `gh pr create`. Reference the issue as `Refs #<n>`, not `Closes #<n>`: an auto-close on merge would close the issue behind the lifecycle's back, without its resolution label.
6. Post the pull request link on the issue under `**Lifecycle · handoff**` — with the handoff lines from *Issue comments* in [record.md](../run/references/record.md) unless `issue_comments` is `record` — then `lifecycle.sh wait <n> approval`.

## Gate G3

What counts as accepted is `handoff.accepted_when` in the config:

- `merged` (default): the pull request is merged. Check with `gh pr view <pr> --json state,mergedAt`.
- `approved`: the pull request has an approving review, or the user says it is accepted.

**Post-deploy checks.** A task with a `post-deploy` row in `evidence.md` is not accepted until every such check has been run and its result reported, whatever `handoff.accepted_when` says. The merge is usually what lets the check run, so the task stays in `handoff` with `wait:approval` after it: give the user the steps again and ask for the result.

| Outcome | Do |
|---|---|
| accepted | close as `done` through `calibre:close`; its closing comment records G3 — who accepted, the pull request, and the result of each post-deploy check as `manual, reported by <who>` — because once the branch is merged there is no task branch left to commit the record to |
| a post-deploy check fails | `lifecycle.sh state <n> implement --comment "G3: post-deploy check for <ID> failed. <what was observed>"` (omit `--comment` when `issue_comments` is `record`), and note the failure under G3 in `task.md`; the fix comes back through `calibre:verify` and `calibre:review`. See *A return after the merge* when the pull request is already merged |
| changes requested | note it under G3 in `task.md`, `lifecycle.sh state <n> implement --comment "G3: changes requested by <who>. <what>"` (omit `--comment` when `issue_comments` is `record`); the fix comes back through `calibre:verify` and `calibre:review` |
| the wrong thing was built | `lifecycle.sh state <n> specify`, then `calibre:specify` |
| abandoned | close as `canceled` through `calibre:close` |

**A return after the merge.** When the task goes back and its pull request is already merged, the task branch is spent and the record sits on the default branch. Cut a new task branch from the default branch; if the old name is still taken, add a suffix and update `branch` in `task.md`. The record continues there: note the G3 outcome in `task.md`, and the fix round ends in a new pull request. On the second handoff the spec change is already archived, so step 2 has nothing to merge, and `handoff.md` is rewritten for the new pull request rather than started over.

## Exit when

- `handoff.md` maps every criterion to its evidence and names what was left out.
- The pull request exists and is linked on the issue.
- The outcome at G3 is recorded: in the closing comment when accepted, in `task.md` when the task goes back.
- No `post-deploy` check is left unreported when the task closes as `done`.

## Do not

- Merge the pull request yourself. Acceptance is the one decision this lifecycle never takes for the user.
- Force-push over a branch someone is reviewing.
- Describe the change as complete when `Not done / follow-ups` is not empty; say what is missing in the summary.
- Treat a merged pull request as acceptance while a post-deploy check is still owed.
