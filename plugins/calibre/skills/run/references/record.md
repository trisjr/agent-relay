# The task record

The record is what lets a different session, or a different person, pick a task up and trust what was done. It has two homes, because a task exists before it has a branch.

## Where things live

| What | Home | Why there |
|---|---|---|
| The request, verbatim | the issue body | it is the issue |
| Triage verdict | a comment on the issue | no branch exists yet, and the requester should see it |
| A spike's answer | a comment on the issue | a spike never gets a branch |
| Closing note | a comment on the issue | visible where the task was tracked |
| Everything from `specify` on | `.calibre/tasks/<issue>/` on the task branch | travels with the code and is reviewed in the same pull request |

The task branch is `<branch_prefix><issue>-<slug>` (prefix from the config, default `task/`), cut from the default branch when the task enters `specify` — or `implement` on track `chore`.

Issue comments written by the lifecycle start with a line `**Lifecycle · <state>**` so they can be found again. With `issue_comments` set to `record` (the default) only the comments in the table above are posted. With `all`, each move also gets a one-line comment.

## Files in `.calibre/tasks/<issue>/`

| File | Written in | Holds |
|---|---|---|
| `task.md` | `specify` (`implement` on `chore`) | identity, gates, history |
| `spec.md` | `specify` | the normalized spec and criteria IDs |
| `plan.md` | `plan` | task-to-criteria map and pointers to the plan files |
| `implement.md` | `implement` | what was done, where it departed from the plan |
| `evidence.md` | `verify` | one proven result per criterion |
| `review.md` | `review` | findings and verdict |
| `handoff.md` | `handoff` | what the reviewer of the pull request needs |

Commit these on the task branch as each state finishes, following the repo's commit conventions. An uncommitted record is lost with the worktree.

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
---

## Triage
<the verdict comment, copied from the issue>

## Gates
| Gate | Decision | By | When | Commit seen |
|---|---|---|---|---|
| G1 | accept, track feature | @alice | 2026-11-13 | — |

## History
| When | From | To | Note |
|---|---|---|---|
| 2026-11-13 | triage | specify | |
```

G1 and G2 are recorded here. An accepted G3 is recorded in the closing comment on the issue instead: by then the branch is merged and there is nowhere left to commit it.

Add a history row for every move, including moves back. The row count for `verify → implement` is how the fix-round limit is enforced.

### `spec.md`

```markdown
## Problem
## In scope
## Out of scope
## Criteria
| ID | Criterion | Source |
|---|---|---|
| AC-1 | A user with the billing role can download … | specs/billing/spec.md, "Export invoices", scenario 1 |

## Sources
<paths to the provider's own spec files>
```

On track `bug`, add `## Reproduction` (exact steps and the observed result) and `## Root cause` (the cause, and the evidence that it is the cause).

### `plan.md`

```markdown
## Plan of record
<path, e.g. openspec/changes/issue-42-…/tasks.md>
## Execution plan
<path, if the implement provider needs its own format>
## Based on spec at
<commit>
## Coverage
| Criterion | Tasks | How it will be checked |
|---|---|---|
| AC-1 | 1.1, 1.3 | `npm test -- export.spec.ts` |
## Areas touched
## Risks            <!-- optional -->
```

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

## Is the evidence still current?

Evidence and review are valid for the code they were produced against. To check whether code has changed since commit `<sha>`, ignoring spec and record folders, run this from the repo root (the paths are relative to the working directory):

```bash
git diff --quiet <sha> HEAD -- . ':(exclude).calibre' ':(exclude)openspec' ':(exclude)docs/superpowers'
```

Exit status 0 means nothing relevant changed and the evidence stands. Anything else means the task must pass `verify` again before `review` or `handoff` can rely on it. This is why archiving a spec change on the branch before the pull request does not invalidate evidence: it touches only `openspec/`.

The plan is bound to the spec the same way: if the files listed under `Sources` in `spec.md` changed after the commit in `Based on spec at`, the plan needs G2 again.
