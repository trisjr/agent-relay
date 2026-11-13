# Provider: superpowers

superpowers is a set of skills that impose engineering discipline on how an agent works: test-first implementation, a fresh subagent per task, review by a subagent that has not seen the author's reasoning. It is strong at execution and review. It keeps almost nothing durable, and it is built to run its own whole workflow, so the lifecycle has to fence it.

Written against **superpowers 7.0.2**. The hand-off from another provider's plan into superpowers execution has not been exercised end to end by this plugin.

## Is it available?

superpowers installs per user, not per repo, so nothing in the repo proves it is there. Check the session: skills named `superpowers:writing-plans`, `superpowers:subagent-driven-development`, `superpowers:requesting-code-review` and so on. If they are missing, use `builtin` for the role and say so.

## Keeping it inside one state

Left alone, superpowers chains: brainstorming hands to planning, planning to execution, and execution ends by finishing the branch. It also asks to be invoked before any response. Its own text says user instruction files take precedence over its skills, and that is the lever: `calibre:setup` offers a block for the repo's `CLAUDE.md` or `AGENTS.md` that states the boundaries below. A skill cannot outrank another skill, so if that block is absent, tell the user the fences are only as strong as this conversation.

For any role, say explicitly when invoking the skill: which lifecycle state this is, what the input is, and that control returns to the lifecycle when the role's output exists.

## Roles

### `implement`

superpowers executes a plan in its own format: a file with an ordered list of tasks, each naming files, steps, and the command that proves the step.

**If the plan of record is not a superpowers plan** (for example OpenSpec's `tasks.md`), produce the execution plan during the `plan` state with `superpowers:writing-plans`, giving it the spec and the plan of record as its requirements. It saves to `docs/superpowers/plans/<date>-<feature>.md`. Tell it up front which execution method will be used; it then pauses once to have the plan reviewed, and that pause is gate G2. The plan of record stays the approved one; the execution plan is derived and is regenerated if the record changes.

**The derived execution plan is scaffolding.** It restates the plan of record in another format, so it is not delivered: list it in `task.md` under `Sources` as `Execution plan (derived)`, and `handoff` deletes it from the task branch before the pull request opens. Its row stays in `Sources`, marked as removed. If the task comes back to `implement` after that, restore the file from the branch history (`git log --diff-filter=D -- <path>` finds the commit that removed it) or write a new one covering the fix.

**To execute**, invoke `superpowers:subagent-driven-development` with the execution plan — or `superpowers:executing-plans` when the session has no subagents. Both apply `superpowers:test-driven-development` to each task and run without pausing between tasks.

**Where it runs on.** After the last task, both run a whole-branch review and then invoke `superpowers:finishing-a-development-branch`, which offers to merge or push. Stop before that: the lifecycle owns `verify`, `review` and `handoff`. State this when you invoke the skill.

**Capture before it is gone.** Progress and every decision the executor made on its own are kept in a ledger under `.superpowers/sdd/`, which is deleted when the run finishes. Before that, copy into `implement.md` the tasks completed and every ruling where the executor departed from the plan. Tick the same tasks off in the plan of record.

### `review`

Invoke `superpowers:requesting-code-review` for the whole change: base is the merge-base with the default branch, head is the task branch's head. It dispatches a fresh subagent that receives a description, the requirements and the two commits, and never the session's history, which is exactly the independence the `review` state wants. Give it, as the requirements, the spec and plan files listed under `Sources` in `task.md` and the criteria index.

The reviewer returns strengths, issues graded Critical, Important and Minor, and an assessment of whether the change is ready to merge. Nothing is written to a file, so copy the issues into `review.md`. Map Critical and Important to `blocking`, Minor to `non-blocking`.

If the session has no subagents, superpowers falls back to self-review. That is not independent; record the review as `self-review` in `review.md` and tell the user.

### `diagnose`

Invoke `superpowers:systematic-debugging` for a bug. Its first three phases — root-cause investigation, pattern analysis, hypothesis and testing — are the `diagnose` role. Its fourth phase implements the fix; stop before it and say so when invoking, because fixing belongs to `implement`, after the plan is approved.

It writes no file. Record the reproduction, the root cause and the evidence in `diagnosis.md` yourself.

### `specify`

`superpowers:brainstorming` asks questions and writes a design document to `docs/superpowers/specs/<date>-<topic>-design.md`, covering intent, goals and non-goals, constraints and approaches. That document is the spec: list it in the `Spec` row of `Sources`. It does not produce numbered or individually testable acceptance criteria, so derive them from the design, confirm them with the user, add them to the design document under an `Acceptance criteria` heading, and index them in `task.md`. After the design is approved it invokes `superpowers:writing-plans` on its own; return to the lifecycle first so the `specify` exit is checked.

When another provider owns `specify`, do not run brainstorming for the same task: two specs in two places is the conflict this lifecycle exists to prevent.

### `plan`

`superpowers:writing-plans`, as described under `implement`. When superpowers is the `plan` provider, its plan file is the plan of record. The format does not link tasks to criteria, so fill the `Tasks` and `Check` columns of the criteria index yourself. It has no risks section either: a risk a reviewer should weigh goes under `## Risks` in `task.md`.

### Not provided

`explore`. Use `builtin`, or another provider.
