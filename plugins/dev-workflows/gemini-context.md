# dev-workflows

Three independent rule sets follow, each with its own scope. Apply only the section whose scope matches the task; ignore the others.

## clarify-requirements

Applies to material ambiguities **before building or planning** — where competing answers change the main deliverable, scope, permissions, data handling, or a public contract. Ignore it for fully specified tasks, questions the code or docs already answer, and pure explanations. Judge ambiguity and impact, not request or diff length.

- If `activate_skill` is available, activate the `clarify-requirements` skill and follow it.
- Otherwise explore the repo first. Ask at most 3 questions per round, each with context and required/optional status in the user's language. Offer 2–3 options with consequences and the recommended option first labeled `(Recommended)`, or ask for free text when no sensible choices exist. Narrow vague or conflicting answers with fresh options; stop after 3 rounds.
- Required decisions materially change the main deliverable or have high impact (safety, privacy, money, permissions, destructive actions, public contracts). Until answered or explicitly delegated within stated bounds, keep affected actions `BLOCKED` and continue independent, authorized work. Only reversible, low-impact choices may default as logged assumptions. Skipped, empty, timed-out answers and "done"/"proceed" alone leave required decisions open; reaching 3 rounds does not change that.
- Use an available question tool when the mode permits it, following its schema. If it is asynchronous, a returned call or preselected option is not an answer; continue only independent work while awaiting a reply. If no usable tool exists but chat remains available, print a numbered block and end the turn before dependent work. Do not retry a denied tool. A missing tool, timeout, or empty answer alone does not establish headless mode.
- Only when the caller or runtime explicitly establishes a non-interactive run with no reply channel, never wait: apply optional defaults and list `Assumptions (headless)`; report required decisions and affected actions as `BLOCKED` in the final output. Use any caller-supplied output schema. A required-question block can be:

```text
[clarify] <N> required decisions remain. Re-run with answers, e.g. "1a 2b", or free text. Unanswered required decisions stay blocked.

1. [Header — required] <self-contained question, with one line of context>
   a) <option> (Recommended) — <consequence>
   b) <option> — <consequence>
   if unanswered: BLOCKED — <affected action>; no automatic default
```

When ready, hand off a short brief with only decision-bearing fields: Goal / user, Scope, Decisions, Assumptions, Acceptance (observable checks including the key failure path), Constraints, Approach (inline by default), Open. If required decisions remain, label it a draft and name the blocked actions. Reuse prior answers and approvals; ask only for missing authorization or a material scope change after independent preparation, not because a task is large. Continue authorized work once ready; a clarification-only request ends with the brief.

Never ask what the repo already answers, and never present a default as if the user approved it.

## debug-root-cause

Work inline on a concrete test, build, CI, runtime, or performance failure, including regressions and flakes. No subagent or special question tool is required. Handle features and healthy-diff review normally; do not automatically route to another skill.

- If `activate_skill` is available and permitted, activate `debug-root-cause`; otherwise follow this section.
- Respect scope: diagnosis-only means findings and proposals without repairs, even for a typo; keep scratch repros outside the tree and tracked files unchanged. A find-and-fix request or prior approval authorizes repair within scope; discovering the cause does not require approval again. Ask only about material unresolved decisions or actions beyond authorization.
- Inspect status and relevant diffs before edits. Preserve pre-existing changes, including in the same file; isolate bisect or destructive experiments instead of resetting, stashing, or checking out over them.
- Keep effort proportional: obvious cause → check, authorized correction, rerun. Use a ledger only for uncertain or repeated investigations.
- Reproduce when feasible; record actual input, command, environment, and result. Trace the failure through callers and boundaries; compare recent changes and relevant environment differences. Before an experiment, predict an observation that distinguishes explanations; vary one factor when practical.
- A refuted hypothesis needs contradictory evidence from a valid experiment. A failed setup or non-discriminating result is inconclusive. A failed fix is a separate outcome, not automatic refutation. A suspicious commit or green rerun alone does not confirm a cause.
- Missing repro or environment means limited evidence: state unconfirmed causes and blocked checks; propose the smallest missing input or privacy-safe instrumentation. Supported, authorized local repairs may proceed with verification limits. Check repairable config/code before escalating infrastructure or dependency trouble; deployment and production probes need their own authorization.
- Prefer an existing red check, then rerun after the causal repair and run relevant nearby tests. Add coverage only when missing and practical. Do not weaken assertions, skip failing paths, silently change contracts, or fake success. A test can be wrong; changing it requires evidence from the intended behavior.
- Bounded retries, timeouts, error handling, and fallbacks can be valid repairs or mitigations: check idempotency, cost, visible terminal failures, residual risk, and recurrence detection. Label mitigation when the underlying cause remains.
- For flakes, prefer controlled timing/seed/order, then a bounded representative sample. Set a run/time/cost budget and report all failures/N and conditions. For independent runs at stable rate `p`, no failures in `n` has probability `(1-p)^n`; `3/p` only approximates 95% detection for small `p`. Unknown/correlated rates limit that estimate; no fixed green streak proves a fix.
- After repeated failed attempts, including earlier ones, pause patching and reassess. Continue only with new evidence and a distinct affordable experiment. Stop the affected path at budget exhaustion, no information gain, missing access, or a required decision; there is no three-attempt cutoff.
- Use an available, permitted question tool or interactive plain text. Async return/preselection, timeout, empty answers, and missing tools are not approval or proof of headless mode. Do not retry a denied tool. Only explicit no-reply-channel context means headless: complete authorized independent work, report required decisions and affected actions as BLOCKED, and do not wait. A clear repair mandate still permits a headless fix.
- Report cause confidence separately from verification: actual checks and results, manual steps if applicable, or "changed, verification blocked" with the blocker and next step. Diagnosis-only ends with findings; authorized repair continues through verification. Keep reports short unless complexity warrants detail.

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
