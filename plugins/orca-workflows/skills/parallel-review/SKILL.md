---
name: parallel-review
description: Review one diff, branch, or PR with several supervised Orca reviewers in parallel, each with a distinct lens, then merge and dedupe findings. Use this skill whenever the user asks for a code review, PR review, security review, pre-merge check, or a second opinion on changes — "review giúp anh", "check this diff", "look for issues before we merge" — especially on changes large or risky enough that a single pass would stay shallow.
---

# Parallel review

One agent reviewing everything at once tends to skim. Splitting by lens — each reviewer in a clean context, asked to refute rather than affirm — surfaces more real issues and fewer style nits.

## Decide whether to fan out

A tiny or low-risk change — a few lines, docs or typo fixes, a mechanical rename — gets a direct single-agent review with no Run. Fan out when the change is large, touches risky ground (auth, payments, concurrency, migrations, user input), or the user asked for several perspectives.

## Pick the lenses

Default set (adapt to the change; 2–5 reviewers is the useful range):

- **security** — injection, authz, secrets, unsafe input handling
- **correctness** — logic errors, edge cases, races, error paths
- **consistency** — fits the codebase's patterns, naming, and invariants
- **simplicity/performance** — needless complexity, hot-path regressions

Drop lenses that don't apply (no security surface → skip security) rather than padding the wave.

## Recipe

Prerequisites: orca-router steps 1–2 (executable resolved, runtime ready, `ORCA skills get orchestration` loaded) and its coordinator rules — the guide's lifecycle and safety rules are authoritative. If Orca is unavailable and the user did not ask for it, review as a single agent instead. On Linux outside an Orca-managed terminal the executable is `orca-ide` — never bare `orca` (the GNOME screen reader).

1. **Pin the review target.** One exact, identical reference for every reviewer: a git range (`main...HEAD`), the working tree (`git diff HEAD` plus the untracked files `git ls-files --others --exclude-standard` lists, which `git diff` omits), or a file list. For a PR, fetch it once yourself into a local ref without switching branches (e.g. `git fetch origin pull/<n>/head:pr-<n>`) and pin `<base>...pr-<n>`. Reviewers share the user's checkout, so they read with `git diff` / `git show` only — never `checkout`, `switch`, or `gh pr checkout`. Ambiguous targets make reviewers diverge on *what* they reviewed before you can compare *what* they found.
2. **Create the Run and the report directory.**
   ```sh
   ORCA orchestration run-create --objective "Review <target>: <one-line scope>" --json
   ```
   Then create the run-scoped report directory, excluded from Git (router coordinator rules), so no reviewer sees another's report in the diff.
3. **Start the full wave before waiting**, one worker per lens:
   ```sh
   ORCA orchestration worker-start --spec "<spec for lens X>" --worktree current --agent claude --json
   ```
   A non-zero exit is never relaunched — follow the receipt (router coordinator rules). Each spec contains Target (the pinned reference), Change (a findings report written to `<report_dir>/review-<lens>.md`, absolute path), Constraints (**review-only: no edits to repository files, no commits, no checkout**), Ownership (the assigned lens; ignore off-lens observations or demote them to a "notes" section), Observable acceptance (every finding has severity, `file:line` evidence, and a one-line rationale; no issue found = a report saying so).
4. **Wait and process.**
   ```sh
   # --terminal <handle> only outside the coordinator's own Orca terminal
   ORCA orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 900000 [--terminal <handle>] --json
   ```
   Reply to questions, handle escalations per the router's coordinator rules, validate each `worker_done` (outcome + report path), release settled terminals, `check --ack <delivery_id>`, roll the wait. Three consecutive empty waits → `worker-list --run <run_id> --json` (add `--include-remote` if any remote workers) and follow `projection.nextAction`; a `none` nextAction has no argv — read `liveness.reason` and keep waiting.
5. **Merge and present.** Read the reports, then deliver one deduplicated list grouped by severity — each finding tagged with its lens and evidence — and name the report directory. When lenses disagree (e.g. simplicity vs. consistency), present both positions instead of silently picking one.

## Ownership rule — the coordinator does not fix

A review-only `worker_done` authorizes synthesizing findings, nothing more. Do not edit files "while you're in there", even for one-line fixes the reviewers made obvious. If the user wants fixes, that is a separate decision: dispatch a fix worker (or use dag-build for several), referencing the findings file. Keeping reviewer and fixer separate preserves the independence that made the review worth running.
