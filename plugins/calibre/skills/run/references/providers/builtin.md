# Provider: builtin

The fallback for any role whose configured provider is missing, and the provider for a repo that has no library installed. It is deliberately minimal: enough to satisfy the state's exit criteria, with no workflow of its own. It has no folder of its own, so the files it writes live in the task's record folder, `.calibre/tasks/<issue>/`, and `task.md` points to them like any other provider's.

## Roles

### `specify`

1. Read the request and the code it touches. Resolve from the repo whatever the repo can answer.
2. Ask the user only what changes the outcome: at most three questions a round, each with the options and your recommended one.
3. Write `spec.md`: the problem, what is in scope, what is out, and the criteria. Phrase each criterion as an observable result — given a situation, when something happens, then this is true — and include at least one failure path. This file is the spec: list it in the `Spec` row of `Sources` and index its criteria in `task.md`.

### `plan`

1. Read the spec and the code. Choose the simplest approach that meets every criterion; name the alternative you rejected if there was a real one.
2. Write `plan.md`: the approach in a few lines, an ordered list of small tasks, each naming the files it touches and the command or action that shows it worked, and any risk a reviewer should weigh. This file is the plan of record.
3. Fill the `Tasks` and `Check` columns of the criteria index in `task.md`.

### `implement`

1. Work through the tasks in order on the task branch.
2. For each task that changes behavior, write the test first and see it fail for the right reason, then make it pass. A test written after the code tends to test what the code does rather than what was asked.
3. Commit per task. Tick the task off in the plan of record.
4. When a task cannot be done as planned, decide whether it is a small departure (do it, and note what and why) or a different approach (stop; this goes back to `plan`).

### `review`

1. Dispatch a fresh subagent if the session has them. Give it the diff from the merge-base to the head, the spec and plan files listed under `Sources` in `task.md`, the criteria index and `evidence.md` — not the conversation.
2. Ask it for findings with a file and line, a severity of `blocking` or `non-blocking`, and a verdict. Ask it to look for: criteria the change does not actually meet, behavior changed outside the scope, missing failure handling, and tests that would pass without the change.
3. With no subagents, review it yourself and record the review as `self-review`. Tell the user it was not independent.

### `diagnose`

1. Reproduce the bug and write down the exact steps and what was observed.
2. Form one hypothesis at a time and design a check that would tell it apart from the alternatives. Change one thing per check.
3. Stop when a hypothesis is confirmed by evidence. Record the reproduction, the cause and that evidence in `diagnosis.md`. Write no fix.

### `explore`

1. Restate the question and what a useful answer would let the user decide.
2. Investigate read-only: code, docs, and experiments in a scratch directory outside the tree.
3. Report the answer, the evidence, what remains uncertain, and any work it implies.
