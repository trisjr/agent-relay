---
name: plan
description: Calibre lifecycle state `plan` — for an issue labeled `state:plan`, decide how each acceptance criterion will be met and checked by delegating to the configured plan provider, build the criterion-to-task coverage table, then stop at gate G2 so the user approves spec and plan together. Use for "lên plan cho issue 42", "plan #42", "duyệt plan issue này", or when a plan was revised and needs approval again. It edits no code and does not start implementing. Skip issues with no `state:*` label and ordinary planning requests that do not involve the lifecycle.
argument-hint: "[issue number]"
---

# plan

Decide how the criteria will be met and how each will be checked, then get a person to approve spec and plan together. This is the last cheap point to change direction.

**State:** `state:plan` · **Done by:** provider role `plan` · **Gate:** G2 · **Next:** `calibre:implement`

## Before you start

The label script is `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh` ([lifecycle.sh](../run/scripts/lifecycle.sh) in the `calibre:run` skill); the commands below write it as `lifecycle.sh`.

Follow the [shared rules](../run/references/rules.md): read the config, run `lifecycle.sh show <n>`, and continue only if the task is in `plan`.

## Do

1. Read the adapter for the configured `plan` provider — [openspec.md](../run/references/providers/openspec.md), [superpowers.md](../run/references/providers/superpowers.md) or [builtin.md](../run/references/providers/builtin.md) — and produce the plan. If the provider already wrote plan files while specifying (OpenSpec's proposal step writes design and tasks in the same call), review and correct those instead of regenerating them.
2. **Execution plan, when needed.** Some `implement` providers only work from a plan in their own format (superpowers is one; its adapter says how). If the `implement` provider differs from the `plan` provider and needs that, produce the execution plan now, from the plan of record, so that one approval covers both. `plan.record` in the config says which of the two is the plan of record (default: the `plan` provider's); the other is derived from it and is regenerated whenever the record changes.
3. Build the coverage table: for every criterion in `spec.md`, the tasks that deliver it and the check that will prove it. A criterion with no task is unplanned work; a criterion with no check cannot be verified later.

## Produce

`plan.md` in the record ([record.md](../run/references/record.md)):

- **Plan of record** and **Execution plan**: paths.
- **Based on spec at**: the commit the spec was at.
- **Coverage**: criterion → tasks → how it will be checked.
- **Areas touched**: the parts of the codebase the plan expects to change.
- **Risks**: optional; include when there is something a reviewer should weigh.

Commit the plan files and the record on the task branch.

## Gate G2

Present, in this order: the criteria, the approach in a few lines, the coverage table, and anything you are unsure about. Then `lifecycle.sh wait <n> approval` and stop.

If the execution-plan provider pauses on its own to ask for plan approval, that pause is this gate, not a second one: bring its question and yours to the user together.

| Decision | Do |
|---|---|
| approved | record the gate in `task.md` with the commit approved, then `lifecycle.sh state <n> implement` |
| change the plan | `lifecycle.sh resume <n>`, revise through the provider's own revise step (see the adapter), stay in `plan`, present again |
| a requirement is wrong | `lifecycle.sh state <n> specify`, then `calibre:specify` |
| too big | show the child issues, create them on a yes, close as `superseded` through `calibre:close` |

## Exit when

- Every criterion has at least one task and a named check.
- The plan files and `plan.md` are committed.
- G2 is recorded with the commit the user approved.

## Do not

- Edit code. A plan that needed a code change to be written is a spike in disguise.
- Start implementing because approval seems certain.
- Carry an approval across a change. Revised after G2 means G2 again, for the revised part.
