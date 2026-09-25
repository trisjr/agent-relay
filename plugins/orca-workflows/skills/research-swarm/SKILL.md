---
name: research-swarm
description: Fan out a broad research, analysis, or investigation question across parallel supervised Orca workers, then synthesize their findings. Use this skill whenever the user wants something researched, compared, investigated, or explored along several independent angles at once — "research X", "phân tích giúp anh", "compare our options", codebase deep-dives too large for one context, market or technology surveys, and multi-part questions — even if they don't mention agents or Orca. Workers each write findings to a report file; the coordinator synthesizes from those files instead of passing large outputs through messages. Not for root-causing one specific failure, which stays depth-first with a single agent.
---

# Research swarm

Breadth-first research is the workload where multi-agent pays off most: each worker gets a clean context, digs deep into one angle, and returns a compressed reference. But it costs roughly an order of magnitude more tokens than a single agent, so the first decision is whether a swarm is warranted at all.

## Scale the swarm to the question

| Question shape | Swarm |
|---|---|
| Single-fact lookup, one-file question, quick explanation | No swarm — just answer directly |
| Root cause of one specific failure ("why does X crash?") | No swarm — chase it sequentially; hypothesis pursuit is depth-first |
| Comparison, or 2–4 independent angles | 2–4 workers |
| Complex, multi-direction investigation; more ground than one context covers | 5–8 workers, decomposed by subsystem or angle |

Scale down generously. Ten workers on a shallow question produce ten shallow reports and a synthesis problem.

## Recipe

Prerequisites: orca-router steps 1–2 (executable resolved, runtime ready, `ORCA skills get orchestration` loaded) and its coordinator rules. The guide's lifecycle and safety rules are authoritative — this recipe only encodes the shape of the work. If Orca is unavailable and the user did not ask for it, research as a single agent instead. On Linux outside an Orca-managed terminal the executable is `orca-ide` — never bare `orca` (the GNOME screen reader).

1. **Decompose.** Split the question into N independent, non-overlapping sub-questions. Overlap between workers means duplicated effort and contradictory findings; give each worker explicit boundaries against its siblings.
2. **Create the Run and the report directory.**
   ```sh
   ORCA orchestration run-create --objective "<the research question>" --json
   ```
   Then create the run-scoped report directory, excluded from Git (router coordinator rules).
3. **Start the whole wave before waiting.** One call per sub-question:
   ```sh
   ORCA orchestration worker-start --spec "<self-contained spec>" --worktree current --agent codex --json
   ```
   A non-zero exit is never relaunched — follow the receipt (router coordinator rules). Vary agents across the wave (codex, claude, …) when perspective diversity helps. Each spec must contain:
   - **Target** — the exact code, docs, or resources to investigate.
   - **Change** — the findings expected, written to `<report_dir>/findings-<angle>.md` (absolute path).
   - **Constraints** — no edits to repository files; the report is the only file it writes; stay inside the assigned angle.
   - **Ownership** — what it may read/use; coordination boundary (no contacting other workers).
   - **Observable acceptance** — the report file exists and covers the listed questions, with evidence (file:line citations, command output).
4. **Wait and process.**
   ```sh
   # --terminal <handle> only outside the coordinator's own Orca terminal
   ORCA orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 900000 [--terminal <handle>] --json
   ```
   Per batch: `reply` to questions, handle escalations per the router's coordinator rules, note each `worker_done`'s outcome and `--report-path`, decide each settled terminal's next owner (usually `worker-release`), then `check --ack <delivery_id>` and roll the wait again. A timeout or empty wait is a checkpoint, not a failure — after three consecutive empties, run `worker-list --run <run_id> --json` (add `--include-remote` if any remote workers) and follow each row's `projection.nextAction` (a `none` nextAction has no argv — read `liveness.reason` and keep waiting).
5. **Synthesize.** Read the report files (or `worker-read --dispatch <id>` for archived output). Merge into one answer: dedupe overlaps, reconcile contradictions explicitly, and attribute key findings to the worker/angle that produced them.

## Guarantees to keep

- **References, not transcripts.** Workers write files; messages carry paths. Pasting large findings into mailbox messages degrades fidelity and burns coordinator context.
- **End only when settled.** The final report names, per sub-question: outcome, evidence, and any unresolved blocker, plus the report directory — and `worker-list --run <run_id> --terminal-state reclaimable` returns none.
- **No repository edits.** A research wave that edits code is a build, not research — route that to dag-build or a plain implementation task.
