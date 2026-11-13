# The task record

The record is what lets a different session, or a different person, pick a task up and trust what was done. It is an index and a ledger, not a second copy of the spec or the plan.

## Where things live

| What | Home | Why there |
|---|---|---|
| The request, verbatim | the issue body | it is the issue |
| Triage verdict | a comment on the issue | no branch exists yet, and the requester should see it |
| A spike's answer | a comment on the issue | a spike never gets a branch |
| The pull request link | a comment on the issue | the issue is where people look for it |
| Closing note | a comment on the issue | visible where the task was tracked |
| The spec and the plan | the provider's own files | the library that wrote them keeps them current |
| Everything else from `specify` on | `.calibre/tasks/<issue>/` on the task branch | travels with the code and is reviewed in the same pull request |

The task branch is `<branch_prefix><issue>-<slug>` (prefix from the config, default `task/`), cut from the default branch when the task enters `specify` — or `implement` on track `chore`.

## One home

**Point, do not copy.** What a provider commits to a file — a proposal, requirements, a design, a task list — stays in that file, and the record points to it. A second copy in the record goes stale the first time the provider's file is revised, and leaves the reader to guess which one was approved.

The record holds what has no other home:

- the task's identity, its gates and its history;
- the criteria index, which gives each criterion an ID and ties it to its source, its tasks and its check;
- what a provider says only in the conversation or in scratch files it deletes: a diagnosis, departures from the plan, review findings;
- the evidence.

**No home in the provider's files?** Something a state must produce — what is out of scope, a risk, a decision a person made along the way — goes in the provider's file when its format has a place for it, and otherwise in a section of `task.md`.

## Files in `.calibre/tasks/<issue>/`

| File | Written in | Holds |
|---|---|---|
| `task.md` | `specify` (`implement` on `chore`), then updated by each state | identity, sources, criteria index, gates, decisions, history |
| `diagnosis.md` | `specify`, track `bug` | the reproduction and the root cause |
| `implement.md` | `implement` | what was done, where it departed from the plan |
| `evidence.md` | `verify` | one proven result per criterion |
| `review.md` | `review` | findings and verdict |
| `handoff.md` | `handoff` | what the reviewer of the pull request needs |

When `builtin` is the `specify` or `plan` provider, its `spec.md` and `plan.md` sit in this folder too. They are that provider's files — the only copy of the spec and the plan — and `task.md` points to them like any other source.

Commit these on the task branch as each state finishes, following the repo's commit conventions. An uncommitted record is lost with the worktree.

A record written by an earlier version of the lifecycle keeps its criteria in `spec.md` and its coverage in `plan.md`. Read them there and leave that task's layout alone until it closes.

### `task.md`

```markdown
---
issue: 42
title: Export invoices as CSV
track: feature
size: medium
branch: task/42-export-invoices-csv
base: main
change: issue-42-export-invoices-csv   # provider's own name for the work, if any
triage: https://github.com/acme/billing/issues/42#issuecomment-123456
---

## Sources
| What | Where |
|---|---|
| Spec | openspec/changes/issue-42-export-invoices-csv/proposal.md, openspec/changes/issue-42-export-invoices-csv/specs/ |
| Plan of record | openspec/changes/issue-42-export-invoices-csv/tasks.md (with design.md) |
| Execution plan (derived) | docs/superpowers/plans/2026-11-13-export-invoices-csv.md |

## Criteria
| ID | Criterion | Source | Tasks | Check |
|---|---|---|---|---|
| AC-1 | A user with the billing role downloads invoices as CSV | specs/billing/spec.md, "Export invoices", scenario 1 | 1.1, 1.3 | `npm test -- export.spec.ts` |

## Gates
| Gate | Decision | By | When | Commit seen |
|---|---|---|---|---|
| G1 | accept, track feature | @alice | 2026-11-13 | — |
| G2 | approved spec and plan | @alice | 2026-11-14 | 3f2a91c |

## Decisions
| Question | Decision | By | When |
|---|---|---|---|
| May a viewer export too? | No, billing role only | @alice | 2026-11-13 |

## History
| When | From | To | Note |
|---|---|---|---|
| 2026-11-13 | triage | specify | |
```

- **Sources.** The `Spec` row names the files that define what is to be built, and nothing an implementer edits: the task list is ticked off during `implement`, so it belongs in the `Plan of record` row. The `Execution plan (derived)` row exists only when the `implement` provider needed its own plan format. A bug fixed without a provider spec has `diagnosis.md` in its `Spec` row. A `chore` has no `Sources` rows: its criteria come from the triage comment.
- **Criteria.** `specify` fills `ID`, `Criterion` and `Source`; `plan` fills `Tasks` and `Check`. `Criterion` is one line that names the criterion; its full wording stays at the source. On track `chore`, `implement` fills the rows from the triage comment, with `—` under `Tasks`.
- **Gates.** G1 and G2 are recorded here. An accepted G3 is recorded in the closing comment on the issue instead: by then the branch is merged and there is nowhere left to commit it.
- **Decisions.** Answers a person gave between gates that shaped the spec or the plan.
- **History.** One row for every move, including moves back. The row count for `verify → implement` is how the fix-round limit is enforced.
- **`## Out of scope`, `## Risks`.** Optional sections, used only under the fallback in *One home*.

### `diagnosis.md`

```markdown
## Reproduction
<exact steps, and what was observed>
## Root cause
<the cause, and the evidence that it is the cause and not merely nearby>
## Criteria
<only when no provider spec was written for the fix: the full wording of each criterion>
```

When the criteria come from the bug itself and no provider wrote a spec, this file is their source: the `Spec` row of `Sources` and the `Source` cells of the criteria index point here.

### `implement.md`

```markdown
## Commits
<first>..<last>
## Tasks
| Task | Status | Note |
## Departures from the plan
| Task | What changed | Why |
## Follow-ups noticed
```

### `evidence.md`

```markdown
## Verified at
<commit>, <date>
## Criteria
| ID | Check run | Observed | Result |
|---|---|---|---|
| AC-1 | `npm test -- export.spec.ts` | 12 passed, 0 failed | pass |
## Regression
<command> → <result>
```

`Observed` is what the run printed or showed, trimmed; "works as expected" is not an observation. A check a person had to perform is recorded as `manual, reported by <who>`.

### `review.md`

```markdown
## Reviewed at
<commit>, by <provider or reviewer>
## Findings
| Severity | Location | Finding | Status |
|---|---|---|---|
| blocking | src/export.ts:88 | … | open |
## Verdict
pass | changes requested
```

### `handoff.md`

```markdown
## Summary
## Criteria and evidence
| ID | Criterion | Evidence |
## Departures from the plan
## Not done / follow-ups
## How to try it
## Pull request
<url>
```

## Issue comments

The issue is where people who never open the branch follow the task. Every comment the lifecycle posts starts with a `**Lifecycle · …**` line so it can be found again.

| Kind | First line | Posted | With `issue_comments` |
|---|---|---|---|
| Record comment | `**Lifecycle · <state>**` | the triage verdict, a spike's answer, the pull request link, the closing note | always |
| Summary | `**Lifecycle · <state>**` | when a state from `specify` on has produced its output | `summary`, `all` |
| Move note | `**Lifecycle · <from> → <to>**` | when a person decides at a gate, and when a task moves back | `summary`, `all` |

With `all`, every move gets a move note, not only decisions and moves back. With `record`, post neither summaries nor move notes.

### Summary

A summary tells a product manager what the state concluded. The task branch is not pushed until `handoff`, so a summary carries the content itself and never links to a file on the branch.

```markdown
**Lifecycle · plan**

<One sentence in plain words: what this state concluded.>

- <the lines for this state, from the table below>
- Next: <the state that follows, or the decision the task waits for>
```

| State | Lines |
|---|---|
| `specify` | each criterion's ID and one line; what is out of scope; decisions people made; on track `bug`, the root cause in a sentence and whether it was reproduced |
| `plan` | the approach in two or three lines; the areas of the codebase it touches; risks; that it waits for approval at G2 |
| `implement` | tasks done out of planned; each departure from the plan and why, or "none"; follow-ups noticed |
| `verify` | criteria proven out of total, and at which commit; the regression result; checks a person performed |
| `review` | the verdict; each blocking finding and its status; non-blocking findings left as follow-ups |
| `handoff` | added under the pull request link: criteria proven out of total, and what was not done |
| closed | added to the closing note: what was delivered or why it was not, the pull request and who accepted it, follow-ups left open |

- **Derive it** from the record and the files it points to. Three to eight lines; a fact found in neither does not belong in the summary.
- **Plain words first.** Lead with what changes for a user or the product; file paths and symbols come after, if at all.
- **Post it** with `gh issue comment <n> --body-file <file>`, with the file in a temporary directory outside the repo: text in backticks breaks inside a quoted argument, and the task branch must stay clean.
- **It is written for people.** No lifecycle skill reads a summary or a move note back; the record files are the authority. Record comments are the exception, because the issue is their home.

### Move note

Pass the reason with the move, and the script posts it under the right heading:

```bash
lifecycle.sh state 42 implement --comment "G2: approved by @alice at 3f2a91c"
lifecycle.sh state 42 implement --comment "AC-2 failed: the CSV has no header row. Fix round 1 of 3."
```

A gate decision names who decided and, for G2, the commit they saw. A move back names what sent it back. Keep the text plain; for anything longer or with backticks, pass `--comment "$(cat <file>)"`.

## Is the evidence still current?

Evidence and review are valid for the code they were produced against. To check whether code has changed since commit `<sha>`, ignoring spec and record folders, run this from the repo root (the paths are relative to the working directory):

```bash
git diff --quiet <sha> HEAD -- . ':(exclude).calibre' ':(exclude)openspec' ':(exclude)docs/superpowers'
```

Exit status 0 means nothing relevant changed and the evidence stands. Anything else means the task must pass `verify` again before `review` or `handoff` can rely on it. This is why archiving a spec change on the branch before the pull request does not invalidate evidence: it touches only `openspec/`.

The plan is bound to the spec the same way. G2 approved the spec as it stood at the commit in its `Commit seen` cell, so check the paths in the `Spec` row of `Sources` against that commit:

```bash
git diff --quiet <G2 commit> HEAD -- <spec paths>
```

Anything but exit status 0 means the spec changed after it was approved, and the plan needs G2 again.

After `handoff` has archived a spec change, the files sit at a path that did not exist at the G2 commit, so the command above always reports a change. Compare the old location at that commit with the new one at the head instead; the old location is the change folder named by `change` in `task.md`:

```bash
git diff --quiet <G2 commit>:<old path> HEAD:<new path>
```
