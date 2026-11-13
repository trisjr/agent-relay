---
name: run
description: Drive a task through the whole Calibre task lifecycle — intake, triage, specify, plan, implement, verify, review, handoff, closed — by reading the `state:*` label on its GitHub issue and running the skill for that state, one state after another, until a human gate or a wait. Use whenever the user wants to continue or advance a tracked task without naming the state ("chạy calibre cho issue 42", "chạy lifecycle cho issue 42", "làm tiếp issue này", "next step for issue 42"), resume one after an approval or an answer, or ask where it stands ("issue này đang ở bước nào"). For a single named state, the state's own skill (`calibre:triage`, `calibre:verify`, …) can be used directly. Skip one-off edits with no issue, and repos where the user declined to set the lifecycle up.
argument-hint: "[issue number | new request]"
---

# Task lifecycle

A task moves through nine states. Libraries such as OpenSpec and superpowers are good at the work inside a state, and bad at telling you where a task stands, whether it was ever worth doing, or whether "done" was proven. The lifecycle supplies that missing layer.

The issue is the task. Its single `state:*` label is the state, visible to everyone without opening a session. Each state has its own skill; this one reads the label, runs the matching skill, and keeps going.

## Run a task

1. **Config.** Read `.calibre/config.json` at the repo root. If it is missing, the repo has not been set up: say so, offer `calibre:setup`, and stop.
2. **Find the task.** With an issue number, run `scripts/lifecycle.sh show <n>` (the script sits in this skill's directory; in Claude Code that is `${CLAUDE_SKILL_DIR}/scripts/lifecycle.sh`). Call it by path and stay in the task's repo: `gh` acts on the repository of the working directory, and `show` prints which one that is. A new request with no issue, or an issue with no state label, starts at `intake`.
3. **Run the state's skill** from the table below. Invoke it as a skill; where skills cannot be invoked from here, read its `SKILL.md` and follow it. It checks its own preconditions against the [shared rules](references/rules.md), does that one state, and moves the label when its exit criteria hold.
4. **Repeat** with the new state. Stop at a gate, at a wait, or when the next state deserves a fresh session (a long implementation). Say in one line what state the task is in now and what happens next.

Never do a state's work from memory of how it usually goes, and never move a label yourself to "catch up": the state skills carry the exit criteria, and the script refuses moves the lifecycle does not allow.

## The states

| State | Label | Skill | Who does the work | Gate |
|---|---|---|---|---|
| `intake` | `state:intake` | [`calibre:intake`](../intake/SKILL.md) | the skill | |
| `triage` | `state:triage` | [`calibre:triage`](../triage/SKILL.md) | the skill | G1 |
| `specify` | `state:specify` | [`calibre:specify`](../specify/SKILL.md) | provider: `specify`, `diagnose` or `explore` | |
| `plan` | `state:plan` | [`calibre:plan`](../plan/SKILL.md) | provider: `plan` | G2 |
| `implement` | `state:implement` | [`calibre:implement`](../implement/SKILL.md) | provider: `implement` | |
| `verify` | `state:verify` | [`calibre:verify`](../verify/SKILL.md) | the skill | |
| `review` | `state:review` | [`calibre:review`](../review/SKILL.md) | provider: `review` | |
| `handoff` | `state:handoff` | [`calibre:handoff`](../handoff/SKILL.md) | the skill | G3 |
| `closed` | `resolution:*`, issue closed | [`calibre:close`](../close/SKILL.md) | the skill | |

Not every task visits every state: [references/tracks.md](references/tracks.md) gives the path for `feature`, `bug`, `chore` and `spike`. Every allowed move, forward and back, is in [references/transitions.md](references/transitions.md).

## What every state skill shares

These live in one place so the nine skills cannot drift apart:

- [references/rules.md](references/rules.md) — the checks before and after a state, the rules that hold in every state, providers, gates, waits, and which actions need a yes.
- [references/record.md](references/record.md) — where each state's output is kept and how to tell whether evidence is still current.
- [references/providers/](references/providers/openspec.md) — one adapter per library: [OpenSpec](references/providers/openspec.md), [superpowers](references/providers/superpowers.md), [builtin](references/providers/builtin.md).
- `scripts/lifecycle.sh` — the only writer of lifecycle labels.

## A waiting task

If `show` reports a wait, the task is paused. Confirm with the user that the thing waited for has happened, then follow the *Waiting* table in the shared rules: `resume`, and act on the decision or answer through the state's skill. A `wait:deferred` task returns to `triage` when resumed.

## Cancelling, reopening, status

- **Cancel**, or **reopen** a closed task: [`calibre:close`](../close/SKILL.md).
- **Scope changed mid-flight**: `scripts/lifecycle.sh state <n> triage`, then `calibre:triage`. A different request deserves a fresh verdict.
- **Status only** ("where is #42?"): run `show`, read the record, and report state, wait, track, what the last state produced and what is needed next. Change nothing.
- **A lifecycle skill misbehaved** (skipped a step, ran past a gate, got in the way): [`calibre:audit`](../audit/SKILL.md), in the same session while the conversation still shows what happened.
