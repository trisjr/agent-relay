# Provider: OpenSpec

OpenSpec keeps specifications as files in the repo: a proposed change lives in its own folder until it is archived into the living specs. It is strong at fixing what is to be built and at recording why; it does not run checks, review code, or touch git.

Written against **OpenSpec 2.0** (skills named `openspec-*`). Nothing here has been exercised end to end by this plugin; treat the skill names as the thing to confirm first.

## Is it available?

- In the repo: `openspec/config.yaml`, with `openspec/specs/` and `openspec/changes/`.
- On the machine: `openspec list --json` succeeds and its `root` is not `null`.
- In the session: skills named `openspec-propose`, `openspec-update-change`, `openspec-archive-change`, `openspec-explore`.
- A repo with `.claude/commands/opsx/` and no `openspec-*` skills is on OpenSpec 1.x, whose commands were `/opsx:*`. Tell the user this adapter targets 2.0 and that OpenSpec's upgrade guide maps the old commands to the new skills; do not guess the mapping.

If the skills are missing, use `builtin` for the role and say so.

Which skills are installed depends on the user's OpenSpec profile. The standard `core` profile includes propose, explore, apply, update, sync and archive. Two steps below are not roles, so they have their own fallback when their skill is absent:

- No `openspec-update-change`: edit the change's files directly, keeping their structure, and run `openspec validate`.
- No `openspec-archive-change`: use the CLI's `openspec archive`, which does the same move and spec update. Read `openspec archive --help` first; this plugin has not run it.

## Naming the change

Use `issue-<n>-<slug>` as the change name so the folder can be traced to its issue: `openspec/changes/issue-42-export-invoices-csv/`. Record it as `change` in `task.md`.

## Roles

### `specify`

Invoke `openspec-propose` with the request and the triage verdict. It writes, under `openspec/changes/<name>/`:

- `proposal.md` — why, what changes, capabilities, impact.
- `specs/<capability>/spec.md` — delta specs: requirements, each with scenarios in WHEN/THEN form.
- `design.md` (optional) and `tasks.md` — these belong to the `plan` role; see below.

These files are the spec. Index them in `task.md` and copy nothing out of them:

- `Sources`, `Spec` row: `proposal.md` and the `specs/` folder of the change.
- `Criteria`: one row per scenario, with the requirement and scenario name as its source, written relative to the change folder so the pointer survives archiving. OpenSpec does not number scenarios, which is why the lifecycle assigns the `AC-n` IDs.
- Out of scope: `proposal.md` has no such section. When the change has a `design.md`, its non-goals are the statement; confirm with the user that they are complete. When it has none, get the boundary from the user and record it under `## Out of scope` in `task.md`.

Run `openspec validate` on the change before accepting it.

**Where it stops:** `openspec-propose` writes planning files only and does not write code, even when asked to.

**It spans two states.** One call produces the spec and the plan. The label still moves one state at a time: check the `specify` exit criteria against `proposal.md` and the delta specs, move to `plan`, and only then assess `design.md` and `tasks.md`.

### `plan`

The plan is `design.md` (context, goals and non-goals, decisions, risks) and `tasks.md` (numbered checkbox tasks, each expected to say how it is verified). They normally exist already from the `specify` call; review them rather than regenerating. `tasks.md` is the plan of record; list it, with `design.md`, in the `Plan of record` row of `Sources`.

Tasks are not linked to requirements in OpenSpec's format, so the `Tasks` and `Check` columns of the criteria index are yours to fill: for each criterion, the task numbers that deliver it and the check that proves it. A criterion with no task means `tasks.md` is incomplete. Risks belong in `design.md`.

**To revise** after feedback at G2, or when implementation shows the spec or plan is wrong: `openspec-update-change`, run in the `plan` state (`specify` for the spec) and never from inside `implement`. It edits the change's files and does not touch code.

### `explore`

`openspec-explore` is a thinking-partner conversation that investigates and does not edit code. Use it for a spike. It writes no file, so capture the findings and the answer yourself, into the issue comment.

### `implement`

`openspec-apply-change` works through `tasks.md`, changes code and ticks each task. It runs until the tasks are done or it is blocked. It creates no branch and makes no commits, so be on the task branch before invoking it and commit when it returns. It does not record where it departed from the plan; ask, and write the answer into `implement.md`.

**Where it runs on.** When implementation reveals a design issue, it pauses and suggests updating the change's artifacts. Do not take that up inside `implement`: editing `design.md` or `tasks.md` is a revision, which belongs to `plan` and gate G2.

**A fix round** (the task came back from `verify`, `review` or G3). `openspec-apply-change` takes its tasks only from `tasks.md` and reports nothing to do once they are all ticked. Adding the fixes there would revise the plan of record, so it cannot run a fix list. Tell the user before starting, then work through the fix list in `implement.md` with the `builtin` implement steps.

When another provider implements instead, that provider still ticks tasks off in `tasks.md` so the plan of record shows progress.

### Not provided

`diagnose` and `review`. OpenSpec has an optional `openspec-verify-change`, but it searches the code for keywords and runs nothing, so it is neither the lifecycle's `verify` nor a review. Use it, if at all, as an extra completeness check on the spec.

## Merging the spec back (`handoff`)

`openspec-archive-change` moves the change folder to `openspec/changes/archive/<date>-<name>/` and merges its delta specs into `openspec/specs/`. It asks before syncing. Run it on the task branch when `handoff.archive` is `before-pr`, point the `Sources` rows of `task.md` at the archived folder, and commit both together.

Archive only a task closing as `done`. A change that is rejected, canceled or superseded is never archived: its folder stays on the unmerged branch.
