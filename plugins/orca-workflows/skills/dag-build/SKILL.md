---
name: dag-build
description: Build a multi-part feature or migration as a supervised Orca task DAG with decision gates — plan, gate the spec for user approval, run independent components in parallel waves, then integrate and verify. Use this skill whenever the user asks to implement, build, or develop something spanning several modules or services with controlled checkpoints — "build feature X", "xây tính năng", cross-service migrations, "split this across agents", or any implementation where they want to approve the approach before code lands. Not for sequential bug-fix chains, which stay with a single agent.
---

# DAG build

Multi-agent shines on genuinely parallel implementation; it burns tokens on sequential work. Gate this workflow at the door: if the task is one dependency-heavy chain (edit → build → test → fix), do it as a single agent or a short chain instead. A DAG earns its cost when several components can proceed independently once the plan is fixed.

## Recipe

Prerequisites: orca-router steps 1–2 (executable resolved, runtime ready, `ORCA skills get orchestration` loaded) and its coordinator rules. The guide's lifecycle, safety, and recovery rules (retries, circuit breaker, release boundaries) are authoritative; this recipe encodes shape only. If Orca is unavailable and the user did not ask for it, build as a single agent instead. On Linux outside an Orca-managed terminal the executable is `orca-ide` — never bare `orca` (the GNOME screen reader).

### 1. Plan, then gate the spec

Produce an implementation spec: the component split, each component's acceptance criteria, and the dependency graph. Then make the user's approval an explicit gate instead of a shrug in chat:

```sh
ORCA orchestration run-create --objective "Build <feature>" --json
ORCA orchestration task-create --spec "Implementation spec: <summary>" --json
ORCA orchestration gate-create --task <spec_task_id> --question "Approve this implementation plan?" --options '["approve","revise","abort"]' --json
```

The JSON arrays here and in `--deps` use POSIX single quotes; in PowerShell or `cmd.exe`, quote them by that shell's rules instead.

The spec task is coordinator bookkeeping: it carries the gate and never gets a worker. Present the spec and the gate options to the user, run `gate-resolve --id <gate_id> --resolution "<choice>" --json`, then act on the choice before anything else:

- **approve** → `ORCA orchestration task-update --id <spec_task_id> --status completed --json`, then create the DAG.
- **revise** → rework the spec with the user's feedback and gate the same spec task again; create no component tasks yet.
- **abort** → `ORCA orchestration task-update --id <spec_task_id> --status failed --json`, report, and stop.

`task-update` is how a Task with no Dispatch gets its outcome; the guide's "no `task-update` after `worker_done`" rule covers dispatched Tasks only. Gates exist for coordinator-owned DAG decisions like this one — a worker's blocking question is answered with `reply`, never with a gate.

Skip the gate and the spec task when the user's instruction already fixes the plan decisively — e.g. a migration over N independent, homogeneous modules — and no cross-cutting decision is left to approve.

### 2. Create the DAG

One task per component, dependencies only for **real** ordering:

```sh
ORCA orchestration task-create --spec "<component spec>" --deps '["<dep_task_id>"]' --json
```

Prefer parallel waves over deep chains — anything beyond three or four dependent levels usually means the decomposition, not the code, needs rethinking. Every component spec carries the full contract: Target, Change, Constraints (invariants, do-not-touch files), Ownership (exactly what this worker may edit — other components belong to other workers), and Observable acceptance as a command that must pass, scoped to the component: its own tests, typecheck, or lint path. Components share one checkout by default, so a whole-tree build or test run would see siblings' half-finished edits; the full suite belongs to the integration task (step 5).

### 3. Run wave by wave

```sh
ORCA orchestration task-list --ready --brief --json     # what is startable now
ORCA orchestration worker-start --task <task_id> --worktree current --agent codex --json
```

Shadow routing: when the jev-dispatch `ask` tool is available, call it once per task before its first new-agent `worker-start` (not on `--terminal` reuse or `--retry-of`), following the `dispatch-routing` skill in shadow mode. Send `task` as a 1–3 sentence summary, never the component spec. Keep `--agent codex` and do not pass routing's `model`/`effort` through — its `sol`/`luna` are shorthand, not provider ids. `routing.requires_approval=true` → ask the user before starting that worker. Log the routing at start and append the worker outcome when it settles; that pair is the golden set.

Start every ready task in the wave **before** waiting; a fresh worker already means a fresh terminal. Give a component its own worktree (`--worktree new-child --name <component> --setup run`) only when the user asked for one, components edit the same files, or its acceptance cannot be scoped away from sibling edits — then the integration task must merge that branch first (step 5). Then:

```sh
# --terminal <handle> only outside the coordinator's own Orca terminal
ORCA orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 900000 [--terminal <handle>] --json
```

Per batch: reply to questions, handle escalations per the router's coordinator rules, validate `worker_done` (**including running or checking the acceptance command's evidence**), and decide each settled terminal's next owner. Reuse it only when the same exact agent has immediate follow-up work:

```sh
ORCA orchestration worker-show --dispatch <dispatch_id> --json     # the proven handle
ORCA orchestration worker-start --task <next_task_id> --worktree <that terminal's workspace: current, or its exact id:<repoId>::<path>> --terminal <handle> --json
```

`--terminal` never combines with `--agent`, `--model`, or `--effort`. Otherwise `worker-release`. Then `check --ack <delivery_id>`, re-list ready tasks, and start the next wave.

### 4. Failures and recovery

- A `worker-start` that exits non-zero is never relaunched — follow its receipt per the router's coordinator rules.
- Retry a failed task only with positive proof and explicit placement: `worker-start --task <failed_task_id> --retry-of <dispatch_id> --worktree <explicit> --agent <agent> --json`.
- Three consecutive failures for one task trip Orca's circuit breaker and fail the task. Stop there and escalate to the user with the evidence — do not route around the breaker with a new Run or an unrelated dispatch.
- `unverifiable` liveness or a lost response authorizes nothing: inspect (`worker-list`, `worker-show --dispatch <id>`, `worker-read --dispatch <id>`), and use `request-show --request <id>` before replaying any mutation with `--retry-request`.

### 5. Integrate and verify

The last task in the DAG is integration, depending on every component; its observable acceptance is the full verification suite (build, all tests). If any component ran in its own worktree, the integration spec names those branches and merges them into the integration workspace first — otherwise the suite verifies a tree without their work. Fan-in merges verified work, not hopeful work.

### 6. Report

End the run with a per-task table: outcome, the evidence behind it, unresolved blockers. Finish only when `worker-list --run <run_id> --terminal-state reclaimable --json` returns none.
