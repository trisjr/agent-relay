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

- Tracks `feature` and `bug`: confirm G2 is recorded in `task.md` and that the spec has not changed since (see *Is the evidence still current?* in [record.md](../run/references/record.md)). An unapproved or stale plan goes back to `plan`.
- Track `chore`: create the task branch and the record now. `task.md` carries the triage verdict; write the triage criteria into `spec.md` so `verify` has something to prove.

## Do

Read the adapter for the configured `implement` provider — [openspec.md](../run/references/providers/openspec.md), [superpowers.md](../run/references/providers/superpowers.md) or [builtin.md](../run/references/providers/builtin.md) — and invoke it with the approved plan as input. On track `chore` there is no plan: build directly against the criteria, using the provider's coding discipline if it has one (the `builtin` adapter covers the minimum).

Tell the provider where to stop: when the plan's tasks are done and committed on the task branch. No merging, pushing, opening a pull request, or cleaning up the branch from inside this state; those belong to `handoff`.

Reviews a provider runs on its own tasks while building are part of building. They do not replace the `review` state, which looks at the final commit after `verify`.

## Produce

`implement.md` in the record:

- **Commits**: the range this state added.
- **Tasks**: each task from the plan, done or not, and tick them off in the plan of record as well.
- **Departures from the plan**: what changed and why. Ask the provider for these before its scratch files are cleaned up; most keep them only for the length of the run.
- **Follow-ups noticed**: work that turned up and is outside this task.

## Exit when

- Every planned task is done, or listed as a departure with a reason.
- The project builds and its test suite runs (use the repo's own commands).
- The working tree is clean: everything is committed on the task branch.

Then `lifecycle.sh state <n> verify`; the next skill is `calibre:verify`.

## Leave differently when

- The plan cannot work as approved: `lifecycle.sh state <n> plan`, then `calibre:plan`. Small departures are recorded; a different approach is re-approved.
- A requirement is wrong or missing: `lifecycle.sh state <n> specify`, then `calibre:specify`.
- Something outside the task is in the way: `lifecycle.sh wait <n> blocked`, and say what would unblock it.

## Do not

- Report criteria as met. Tests passing during the build are encouraging; proof is `verify`'s output.
- Widen the scope. Extra work becomes a follow-up, not a surprise in the diff.
- Weaken a test to make it pass.
