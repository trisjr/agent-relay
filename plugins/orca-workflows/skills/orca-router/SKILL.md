---
name: orca-router
description: Entry point and router for any Orca multi-agent request. Use this skill whenever a request involves coordinating several agents, supervising or monitoring agent work, waiting for results, task DAGs or decision gates, handing work off to another agent or worktree, checking worker status or mail, or anything Orca — even if the user only says "relay this", "spawn a team", "have another agent look at it", "giao việc cho agent khác", "không cần theo dõi đâu", "nhắc anh khi xong", or asks for one of this plugin's workflows without naming Orca. The router classifies the request, picks supervised orchestration vs. fire-and-forget handoff vs. plain terminal work, then loads the version-matched guide from the live binary before any command runs.
---

# Orca router

Orca behavior changes between versions, and the authoritative documentation is bundled with the binary the user actually runs. So this skill's first job is always to resolve the executable and pull the version-matched guide, and only then act. Command shapes in this plugin match Orca 1.4.211; when one disagrees with the loaded guide or a command's `--help`, the guide wins.

## Step 1 — Resolve the executable (once per session)

1. `ORCA_CLI_COMMAND` env var → use it verbatim (Orca exports it for managed sessions).
2. `ORCA_DEV_REPO_ROOT` set → use `orca-dev`.
3. Linux, outside an Orca-managed terminal → use `orca-ide`. Bare `orca` there is the GNOME screen reader and starts speech on the user's machine.
4. Otherwise → `orca`.

Substitute the resolved path everywhere below. Never silently switch executables after one fails — that could target a different Orca build.

## Step 2 — Confirm runtime, load guides

```sh
ORCA status --json
```

If the executable is missing, `status` fails, or the app is not running:

- **The user explicitly asked for Orca or multi-agent work** → if the app is simply not running, start it with `ORCA open --json` and retry once; otherwise report the exact error and stop.
- **Otherwise** (a recipe matched a plain request such as "research X" or "review this") → do the task as a single agent and say in one line that Orca was unavailable. Never launch the desktop app for a request that did not ask for it.

Prefer `--json` on every command.

The guides are served by the binary:

```sh
ORCA skills get orchestration                 # supervised coordination
ORCA skills get orchestration --references    # list deep-dive references
ORCA skills get orca-cli                      # terminals, worktrees, handoffs, browser
```

Load the one your classification selects before running workflow commands. For a gated topic (remote placement, recovery, DAG depth), load only the named reference with `--reference references/<file>.md`. If the binary rejects `--reference`, run `ORCA skills get orchestration --full` once instead; if an older binary also rejects `--full`, keep this skill's safety floor, read that command's `--help`, and never guess newer flags.

## Step 3 — Classify before doing anything

| Situation | Route | Never |
|---|---|---|
| User asks to supervise, monitor, wait for results, track completion, coordinate a DAG, use decision gates, or answer blocking worker questions | **Orchestration**: `ORCA skills get orchestration`, then the coordinator loop (Run → `worker-start` waves → `check --wait`) | — |
| Handoff without supervision: "hand off", "handover", "give this to another agent / another worktree" | **orca-cli**: `ORCA worktree create --name <task> --no-parent --agent <id> --prompt "<brief>" --json`; when the user names a model or effort, use [Handoff with a model](#handoff-with-a-model). Done when the worktree id and agent handle are reported and the send receipt shows `accepted: true` | No Run/Task/Dispatch, no `check --wait` — handoff is fire-and-forget by design |
| A live injected preamble is present: the exact executable, handle, capability, Task ID, and Dispatch ID | **You are a dispatched worker**: follow the worker contract in the orchestration guide, copying the preamble's commands verbatim; send `worker_done` exactly once from the dispatched terminal | Do not create a Run; do not act as coordinator. Task/Dispatch IDs without the executable, handle, and capability are not a live preamble — never rebuild lifecycle commands from them; treat it as the last row and say which parts are missing |
| A message carries a legacy authority label (`[LEGACY ...]`) | **Compatibility operator**: load `ORCA skills get orchestration --reference references/legacy-contract-migration.md` before any lifecycle mutation | Never guess legacy semantics from memory |
| None of the above | **Ordinary terminal agent** | Emit no Orca lifecycle messages |

The boundary between the first two rows: "giao việc rồi nhắc anh khi xong" (hand off and notify me when done) contains a wait-for-results request, so it is supervision — the orchestration row, not the handoff row.

Model or effort choice never makes a handoff supervised. And when Orca provenance was requested, never substitute a non-Orca subagent tool — Orca runtime state is what makes the coordination real.

### Handoff with a model

`worktree create --agent` uses Orca's configured launcher and has no per-call model or effort flags. When the user names a model or effort, launch the agent yourself — still a handoff, still no Run:

```sh
ORCA worktree create --name <task> --no-parent --json
ORCA terminal create --worktree id:<repoId>::<newWorktreePath> --title <task> --command '<agent> <its own model/effort flags>' --json
ORCA terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
ORCA terminal send --terminal <handle> --text "<brief>" --enter --json
```

The `--command` quoting is POSIX; in PowerShell or `cmd.exe`, quote by that shell's rules. Resolve a vague request ("the strongest model") to a concrete model ID — ask when unsure — and report the model actually launched. Send only when the wait reports `satisfied: true`; on `false`, wait once more with a larger timeout, then report the handoff as not started. `ORCA skills get orca-cli` covers the rest (the extra fallback shell, handle rules).

## Step 4 — Prefer an encoded workflow

This plugin ships three recipes on top of orchestration; when the request matches one, follow that skill instead of improvising:

- **research-swarm** — fan out a broad question across parallel workers that write findings to files.
- **parallel-review** — review one diff/branch with several lens-specific reviewers, then dedupe.
- **dag-build** — build a multi-part feature as a task DAG with decision gates.

All three assume steps 1–2 here and follow the coordinator rules below.

### Chaining recipes

A request spanning plan → code → docs chains the recipes; each stage is its own Run, linked by report paths in specs, never pasted content:

1. **research-swarm** — only when the ground is broad; its reports feed the plan.
2. **dag-build** — the spec cites those report paths; the gate is where the user approves the plan (planning-only requests stop after the gate). Docs are ordinary DAG tasks with file ownership: a docs task depends on the code tasks it describes, and drift-fixing over independent doc files skips the gate.
3. **parallel-review** — on the resulting diff; for docs, swap lenses to accuracy (docs vs. code), completeness, and consistency with repo conventions.
4. **Fixes** — a fresh fix worker or another dag-build wave, never the coordinator.

Reports are Git-excluded and deleted afterward; a plan or doc the user keeps must be written into the repo by a task. Any stage that is small or sequential runs as a single agent instead.

## Coordinator rules shared by the recipes

- **`check` names its caller.** Omit `--terminal` inside the coordinator's own Orca terminal, where Orca resolves the caller; from anywhere else pass `--terminal <handle>` explicitly (`references/messaging-and-gates.md`).
- **A failed start is never relaunched.** If `worker-start` exits non-zero, read the receipt's `failedStage` and `residualResources`, load `references/recovery-and-cleanup.md`, and release what the receipt names with its `worker-release` — a failed start still owns its terminal and shows as `reclaimable`.
- **An escalation means blocked, not done.** Unblock the worker with `ORCA orchestration send --to dispatch:<dispatch_id> --subject "Follow-up" --body "<guidance>" --json`, or take the blocker to the user. Never release, stop, or retry because of an escalation.
- **Reports stay out of the diff.** Before the wave, create `<checkout>/.orca-reports/<run_id>/`; in a Git checkout, add `.orca-reports/` to the file `git rev-parse --git-path info/exclude` prints (local, never committed), so reports never show in `git status` or `git diff`. Put the directory's absolute path in every spec — it sits inside every worker's writable workspace. Workers write only their report there — no edits to repository files. The final report names the directory; delete it once the user no longer needs the files.
