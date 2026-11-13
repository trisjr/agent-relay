---
name: close
description: Calibre lifecycle state `closed` — end a lifecycle task with a stated resolution (`done`, `answered`, `duplicate`, `rejected`, `already-done`, `superseded`, `canceled`) by swapping its state label for a `resolution:*` label and closing the issue with the matching GitHub reason; also cancels a task from any state and reopens a closed one into `triage`. Use for "đóng issue 42", "hủy task này", "cancel issue 42", "mở lại issue 42", and when another lifecycle state reaches a closing decision. The decision to close is always the user's. Skip closing or reopening issues that carry no lifecycle label.
argument-hint: "[issue number] [resolution]"
---

# closed

End the task with a reason anyone can read later. A closed issue with no stated reason looks the same whether the work shipped, was refused, or was forgotten.

**State:** `closed` has no state label: the issue is closed and carries one `resolution:*` label · **Done by:** this skill · **Gate:** none of its own; it acts on a decision already made

## Before you start

The label script is `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh` ([lifecycle.sh](../run/scripts/lifecycle.sh) in the `calibre:run` skill); the commands below write it as `lifecycle.sh`.

Follow the [shared rules](../run/references/rules.md): read the config and run `lifecycle.sh show <n>`. This skill works from any state, but each resolution is only allowed from the states in the table below.

## Resolutions

| Resolution | When | Closes from |
|---|---|---|
| `done` | the change was accepted at G3 | `handoff` |
| `answered` | a spike's question is settled | `specify` or `triage`, track `spike` |
| `duplicate` | the same request is tracked elsewhere | `triage` |
| `rejected` | decided not to do | `triage` |
| `already-done` | the behavior already exists | `triage` |
| `superseded` | split into child issues | `triage` or `plan` |
| `canceled` | stopped before completion | any state |

A resolution that only applies from `triage` means the task goes back there first (`lifecycle.sh state <n> triage`), so the verdict is recorded where verdicts live.

## Do

1. Make sure the decision is the user's: G1 for a triage verdict, G3 for `done`, an explicit instruction for `canceled`.
2. Write the closing comment: one or two lines giving the reason and the links that matter — the pull request and who accepted it for `done` (this is the record of gate G3), the other issue for `duplicate`, the child issues for `superseded`, where the behavior lives for `already-done`. Unless `issue_comments` is `record`, add the closing lines from *Issue comments* in [record.md](../run/references/record.md), so the issue ends with the result and not only the reason.
3. Run `lifecycle.sh close <n> <resolution> --comment "<text>"` (add `--duplicate-of <m>` for a duplicate). For a note of several lines, write it to a file in a temporary directory outside the repo and pass `--comment "$(cat <file>)"`. The script swaps the labels and closes the issue with the matching GitHub reason; if the close fails it puts the labels back.

## Cleaning up

**`done`.** The record was merged with the pull request and stays in the repo as the task's history. If `handoff.archive` is `after-merge`, the spec merge-back is still owed; tell the user it needs a commit on the default branch.

**Any other resolution, after a branch exists.** The work is not being delivered, so nothing is merged back:

- Do not run the spec provider's archive step. Archiving folds the change into the living specs, which would document behavior that was never shipped.
- The spec change folder and the record stay on the task branch and go wherever the branch goes.
- Ask before deleting the branch. Unmerged work is the kind of thing people want back a week later; the default is to leave it and say that it exists.

**`superseded`.** Each child issue starts its own lifecycle at `intake`. Link the parent from each child so the original request can be found.

## Reopening

`lifecycle.sh reopen <n>` reopens the issue, drops the resolution label and sets `state:triage`; the next skill is `calibre:triage`. The task is triaged again: what was true when it closed may no longer be. Earlier history stays in the record and in the issue comments; add to it, do not rewrite it.

## Do not

- Close on your own verdict or because the work "looks finished".
- Close by hand with `gh issue close`; the labels would no longer say why.
- Delete a branch, a spec change or a record without being told to.
