# dev-workflows

Three independent rule sets follow, each with its own scope. Apply only the section whose scope matches the task; ignore the others.

## clarify-requirements

Applies only to a request that is vague, underspecified, or high-stakes **before building or planning** — where two plausible readings would lead to materially different work, data loss, or a changed public contract. Ignore it for well-specified tasks, changes whose diff fits in one sentence, questions the code or docs already answer, and pure explanations.

- If `activate_skill` is available, activate the `clarify-requirements` skill and follow it.
- If only `ask_user` is available: explore the repo first, then ask at most 3 questions — each self-contained, one decision, 2–3 options with the recommended option first and labeled `(Recommended)` — and log low-risk defaults as assumptions.
- If `ask_user` is not available, you are headless (`-p`, CI, no TTY): nobody can answer, so never wait and never retry a denied question.
  - Reversible, low-risk gaps → apply the recommended defaults, continue, and end the output with an `Assumptions (headless)` list.
  - Blocking or irreversible gaps (deleting data, migrations, public API, cost, security) → stop before acting and make this question block your final output so the caller can re-run with answers:

```text
[clarify] <N> decisions before I start. Re-run with answers, e.g. "1a 2b". Anything skipped uses its default.

1. [Header] <self-contained question, with one line of context>
   a) <option> (Recommended) — <consequence>
   b) <option> — <consequence>
   default: a
```

Never ask what the repo already answers, and never present a default as if the user approved it.

## debug-root-cause

Apply to one concrete, existing test, build, CI, or runtime failure; keep one agent on the failure and investigate depth-first.
Ignore for new features, healthy-diff review, vague requirements, and open-ended research; route those to ordinary work, `parallel-review`, `clarify-requirements`, or `research-swarm` as appropriate, or handle them as a single agent when that skill is missing.

- If `activate_skill` is available, activate the `debug-root-cause` skill and follow it.
- Right-size first: an obvious error can take minutes; uncertain failures need recorded evidence and a hypothesis ledger.
- Phase 1 — Reproduce & isolate: run the failing path, minimize it, or collect targeted boundary data when it cannot be reproduced.
- Phase 2 — Gather evidence: inspect traces backward, recent changes, environment, dependencies, and component boundaries before changing behavior.
- Phase 3 — Hypothesis ledger: rank testable causes; predict and run the smallest one-variable experiment, then record `confirmed`, `refuted`, or `inconclusive`.
- Phase 4 — Fix & regression: prove the bug with a failing test or automated repro script, repair the root cause, then run it green and run the related suite.
- Phase 5 — Aftermath: report Symptom, Root cause, Fix, and Prevention in chat; flag `unverified by automated test` if only manual verification was possible.
- Rule 1 — No fix before failing test: do not change production logic before a red check, except a one-step-obvious error named by its message; rerun that command afterward.
- Rule 2 — Never claim "fixed" without verification: require the original check and related suite green, plus a one-sentence root cause.
- Stop at 3 refuted hypotheses or 3 failed fixes: summarize the ledger and ask the user or question the architecture; never silently try a fourth.
- Escalate without force-fixing unpatchable dependency bugs; infra, vendor, quota, DNS, or CI-runner trouble; unapproved public-contract changes or data migrations; or races outside your control.
- In a headless run, a stop or escalation ends with a final status block containing the ledger summary, evidence, unresolved cause, and proposal.

## compound-retros

Apply to durable project lessons after meaningful work and to similar non-trivial work when a solutions store already exists.
Skip trivial changes, one-off environment hiccups, and recall when no store exists.

- Capture: write one short structured lesson after a hard fix, meaningful decision, repeated issue, or confirmed user correction.
- Recall: shortlist notes by title, area, tags, and affected paths before similar work; read only the few relevant notes in full and cite them.
- If `activate_skill` is available, activate `retro-capture` or `retro-recall` for the relevant phase.
- Apply the durable bar: would losing the note let a future agent repeat the mistake despite current code, tests, docs, and `AGENTS.md`? If not, do not write it.
- A request to remember something does not waive that bar.
- Never record secrets, credentials, or sensitive values; use configuration key names without values.
- Select the notes root in order: a user-named path or `AGENTS.md`/`CLAUDE.md` pointer, then an existing note-shaped directory and template, then `docs/solutions/`.
- If the repo lacks `docs/`, ask once before the first note when interactive; headless use `docs/solutions/` and report the choice.
- Keep notes inside the user's repo, never inside the plugin.
- Update duplicate lessons in place; surface contradictions instead of silently overwriting them.
- At `occurrences >= 3`, propose one line for `AGENTS.md` or `CLAUDE.md` and wait for user consent; headless only propose.
- Do not create a store merely to perform recall.
