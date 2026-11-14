---
name: implement
description: Calibre lifecycle state `implement` — for an issue labeled `state:implement`, build what the approved plan describes on the task branch by delegating to the configured implement provider, and record which tasks were done and where the work departed from the plan. Use for "implement issue 42", "code issue này theo plan", "làm tiếp phần code của issue 42", and after `verify` or `review` sent the task back for fixes. It stops when the plan's tasks are committed and does not verify, review, push or open a pull request. Skip issues with no `state:*` label and ordinary coding requests that do not involve the lifecycle.
argument-hint: "[issue number]"
---

# implement

Build what the approved plan describes, on the task branch, and write down where reality departed from the plan.

**State:** `state:implement` · **Done by:** provider role `implement` · **Gate:** none · **Next:** `calibre:verify`

## Before you start

The label script is `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh` ([lifecycle.sh](../run/scripts/lifecycle.sh) in the `calibre:run` skill); the commands below write it as `lifecycle.sh`.

Follow the [shared rules](../run/references/rules.md): read the config, run `lifecycle.sh show <n>`, and continue only if the task is in `implement`.

## On entry

- Tracks `feature` and `bug`: confirm G2 is recorded in `task.md` and that neither the spec nor the plan of record has changed since, ticked tasks aside (see *Is the evidence still current?* in [record.md](../run/references/record.md)). An unapproved or stale plan goes back to `plan`.
- Track `chore`: create the task branch and the record now. `task.md` links the triage verdict; copy its criteria into the criteria index, each with its check, so `verify` has something to prove.

## Do

Read the adapter for the configured `implement` provider — [openspec.md](../run/references/providers/openspec.md), [superpowers.md](../run/references/providers/superpowers.md) or [builtin.md](../run/references/providers/builtin.md) — and invoke it with the approved plan as input. On track `chore` there is no plan: build directly against the criteria, using the provider's coding discipline if it has one (the `builtin` adapter covers the minimum).

Tell the provider where to stop: when the plan's tasks are done and committed on the task branch. No merging, pushing, opening a pull request, or cleaning up the branch from inside this state; those belong to `handoff`.

Reviews a provider runs on its own tasks while building are part of building. They do not replace the `review` state, which looks at the final commit after `verify`.

### A fix round

When the task came back from `verify`, `review` or gate G3, the planned tasks are already done and the plan is not the input. The input is what sent the task back: the failing criteria in `evidence.md`, the blocking findings in `review.md`, or the changes requested at G3 in `task.md`.

1. List them under `## Fix rounds` in `implement.md`, one row per item, each naming the criterion ID or the finding it answers. They do not go into the plan of record: adding tasks there would revise an approved plan.
2. Run that list through the configured `implement` provider, the same as planned work; each adapter says how it takes a fix list. On track `chore`, build against the list with the provider's coding discipline, as on the first pass.
3. If you would run the fixes any other way, including fixing them yourself inline, tell the user and wait for the answer before starting. Skipping the configured provider is the user's choice, not a detail to report afterwards.

A fix that only works by changing an approved decision is not a fix round: leave for `plan` (see *Leave differently when*).

## Produce

`implement.md` in the record:

- **Commits**: the range this state added; a fix round adds its own range.
- **Tasks**: each task from the plan, done or not, and tick them off in the plan of record as well.
- **Fix rounds**: each item that sent the task back, where it came from, and what was done about it.
- **Departures from the plan**: what changed and why. Ask the provider for these before its scratch files are cleaned up; most keep them only for the length of the run.
- **Follow-ups noticed**: work that turned up and is outside this task.

## Exit when

- Every planned task is done, or listed as a departure with a reason.
- In a fix round, every item that sent the task back has a committed fix, or a stated reason why it has none.
- The project builds and its test suite runs (use the repo's own commands).
- The working tree is clean: everything is committed on the task branch.
- The state's summary is on the issue, unless `issue_comments` is `record`.

Then `lifecycle.sh state <n> verify`; the next skill is `calibre:verify`.

## Leave differently when

- The plan cannot work as approved: `lifecycle.sh state <n> plan`, then `calibre:plan`. A small departure is recorded in `implement.md`, and the plan of record keeps its approved text. A change to an approved decision is a revision and gets G2 again; *What counts as revised* in the [shared rules](../run/references/rules.md) draws the line.
- A requirement is wrong or missing: `lifecycle.sh state <n> specify`, then `calibre:specify`.
- Something outside the task is in the way: `lifecycle.sh wait <n> blocked`, and say what would unblock it.

## Do not

- Report criteria as met. Tests passing during the build are encouraging; proof is `verify`'s output.
- Widen the scope. Extra work becomes a follow-up, not a surprise in the diff.
- Weaken a test to make it pass.
- Edit the plan of record beyond ticking its tasks. Making the plan match the code afterwards is a revision nobody approved.
