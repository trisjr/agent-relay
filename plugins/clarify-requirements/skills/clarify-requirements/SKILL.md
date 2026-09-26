---
name: clarify-requirements
description: Pin down what the user actually wants before building — explore the repo first, ask only the few questions whose answers change the work (each with a recommended option), log low-risk assumptions, and hand off a short requirements brief. Use this skill whenever a request is vague, underspecified, or high-stakes before implementation or planning starts — "build X", "add a feature", "làm tính năng", "làm rõ yêu cầu", "clarify this", a new project, PRD, or spec that will feed a plan or DAG — or whenever two plausible readings would lead to materially different work, data loss, or a changed public contract. The skill relies on asking the user. Skip it for well-specified tasks, changes whose diff fits in one sentence, questions the code or docs already answer, and pure explanations.
---

# Clarify requirements

A wrong guess about intent costs a rewrite; an interrogation costs the user's patience. This skill sits between the two: find what can be found, default what can safely be defaulted, ask only what is genuinely the user's call, then write it down so whoever implements — you, a fresh session, or a DAG worker — builds the right thing.

## 1. Right-size first

- **Skip** when the request is fully specified, the diff fits in one sentence, or every open point is a fact the repo, docs, `AGENTS.md`/`CLAUDE.md`, or the conversation already holds. At most say "requirements are clear — proceeding", then proceed.
- **Clarify** when at least one decision has two or more plausible answers that lead to materially different user-visible behavior, effort, security/privacy, data retention, or public contract — and a wrong guess would be costly, hard to reverse, or unsafe.
- **In between** (only reversible, low-impact choices are open): pick sensible defaults, list them as assumptions, and proceed without asking.

Ceremony must stay proportional: a bug fix never needs user stories, and a brief longer than the diff is a smell.

## 2. Explore before asking

Read the relevant code, tests, docs, conventions, and earlier messages first. Sort every unknown into one of three buckets:

- **Discoverable fact** (which module owns X, what format existing exports use): find it yourself. If it is still ambiguous after looking, present the concrete candidates you found and recommend one — never hand the user your research.
- **Preference or trade-off** (scope, priority, UX, data policy, who gets access): the user's call, so it is a candidate question.
- **Expert parameter** (retry budget, page size, cache TTL): choose a value from convention and log it; ask only when it is user-visible and consequential.

## 3. Scan for gaps

Use this list to detect what is missing, not as a questionnaire. A gap is worth raising only when two plausible answers would change the implementation or how it is accepted.

| Dimension | Cue in the request |
| --- | --- |
| Goal / why | an action with no outcome ("improve onboarding") |
| Users | "users" could mean customers, admins, or API clients |
| Scope in / out | "add export" without which records or surfaces |
| Behavior / rules | trigger, cadence, or ordering unstated |
| Data / lifecycle | source, ownership, or retention unstated |
| Edge cases / errors | invalid input, duplicates, dependency down |
| Non-functional | "fast", "secure", "accessible" without a target that matters |
| Constraints | compatibility, platform, deadline, compliance |
| Integration | "sync with the CRM" without system or direction |
| Acceptance | "make it work" with no observable pass condition |
| Priority | goals that conflict or cannot all fit |

## 4. Decide: ask, assume, or block

Rate each candidate on impact-if-wrong, uncertainty, and irreversibility (1–3 each) and multiply. The score only orders the list; the rules decide:

- Safety, privacy, money, permissions, destructive or data-losing actions, and public API changes are always maximum impact.
- **Ask** the highest-scoring decisions that would change what you do next.
- **Assume and log** the reversible, local, low-impact ones, one line each, naming where the default came from: `Assumption: export = current filtered view, matching the table's existing actions.` Write `agent default` when there is no precedent. Never phrase an assumption as if the user approved it.
- **Block** an irreversible, high-impact action whose decision you cannot get: keep doing the independent work, but do not invent a default for it.

Budget: at most **3 questions per round**, usually a single round. A second round exists only when an answer opens a new blocking choice. Whatever remains becomes an assumption or an `Open` item — the user can always ask for another round. Put independent questions in the same round; hold a question that depends on another open answer for the next round.

## 5. Write questions that are cheap to answer

- **Self-contained.** Restate the decision every time, with one line of context or trade-off above the options, so the user can answer without scrolling back. Some harnesses have rendered only the options; a question that carries its own context survives that.
- **One decision per question.** No compound "should it sync, notify, and retry?".
- **2–3 concrete, mutually exclusive options** (4 only when the channel allows it), each with a one-line consequence. No filler options, and no "Other" option — every channel already accepts free text.
- **Recommended option first**, label ending in `(Recommended)`, with the reason. It is the default when unanswered.
- Ask about outcomes and constraints, not implementation details you can decide yourself.
- Use an open question only when you cannot infer a sensible option set (an unknown legal retention rule, say).
- Write in the user's language.

Handling replies:

- The user asks for context on a question → explain, then re-ask that same question. A request for context is not an answer.
- "Whatever you think" / "cứ làm đi" → adopt your recommendations and record them as decisions the user delegated.
- "done", "stop", "proceed" → stop asking, default the rest, and log them.

## 6. Ask through the right channel

Take the first case that applies.

1. **Dispatched Orca worker** (a live injected preamble with executable, handle, capability, Task ID, and Dispatch ID): ask only through the preamble's `orca orchestration ask` command, copied verbatim — never a local question UI, which nobody can answer. Ask only when the coordinator must decide; default the rest and list them in the report and `worker_done`. One question maps to `--question "<header>: <question>" --options "<label a> (Recommended),<label b>"` (labels must not contain commas). On timeout, use `--resume <message_id>` instead of asking again.
2. **A native question tool and a person to answer it:**

   | Harness | Tool | Limits |
   | --- | --- | --- |
   | Claude Code, Kimi Code, Qoder CLI | `AskUserQuestion` | 1–4 questions, 2–4 options, `header` ≤12 chars, `multiSelect` |
   | Codex CLI | `request_user_input` | Plan mode only — Default mode answers "unavailable", so use case 3; ≤3 questions, 2–3 options, snake_case `id`, no multi-select |
   | Gemini CLI | `ask_user` | 1–4 questions, `type` choice / text / yesno, `multiSelect` |
   | Cursor, Qoder IDE | built-in ask tool | limits undocumented: stay within 3 questions and 2–3 options; Cursor's tool does not block, so end the turn after asking |

   These tools do not exist inside subagents (Claude Code, Codex), so run this skill in the main conversation.
3. **Interactive but no tool:** print the plain-text block below and end your turn. Do not start work that depends on the answers.
4. **Headless — nobody can answer** (CI, `-p` / `exec`, the tool was denied or removed, a dialog timed out and auto-submitted, answers came back empty): never wait, and never retry a denied question.
   - Reversible, low-risk gaps → apply the recommended defaults, continue, and end the output with an `Assumptions (headless)` list.
   - Blocking or irreversible gaps (deleting data, migrations, public API, cost, security) → stop before acting and make the question block your final output so the caller can re-run with answers. If the caller supplied an output schema, emit the questions in it.

Plain-text format:

```text
[clarify] 2 decisions before I start. Reply in one line, e.g. "1a 2b". Anything you skip uses its default.

1. [Export] Which rows should the CSV contain? The table already supports filters.
   a) Current filtered view (Recommended) — matches the existing table actions
   b) All records — needs a background job for large tenants
   default: a

2. [Access] Who may export?
   a) Anyone who can see the table (Recommended) — no new permission
   b) Admins only — adds a permission check and a settings toggle
   default: a

Free text works too, e.g. "2: finance team only".
```

## 7. Stop when it is clear enough

Stop asking and write the brief once all four hold:

1. You can state the user, the outcome, and the in-scope change in one or two sentences.
2. Every material behavior and failure path has an observable acceptance check, or inherits existing behavior you can point to.
3. No open choice could change safety, data loss, permissions, the public contract, or the main deliverable; everything else is a logged assumption.
4. The implementer could start and verify the work without asking another question.

Do not chase certainty on every edge case.

## 8. Hand off a requirements brief

Write only fields that carry a decision — 120–200 words, never more than 250. Do not paste the interview.

```markdown
## Requirements brief
Goal / user: <outcome, for whom>
Scope: <in scope; an explicit exclusion only if it prevents scope creep>
Decisions: <answers that change behavior — cite the user or repo evidence>
Assumptions: <low-risk defaults, with source or "agent default">
Acceptance: <2–5 observable checks, including the key failure path>
Constraints: <binding ones only>
Open: <none | non-blocking item | BLOCKED: decision + affected action>
```

Pick the lightest acceptance format that makes the result observable:

- **Checklist** for small edits and deliverables: `CSV has UTF-8 headers id,total; respects current filters; 0 rows → header-only file`.
- **Given / When / Then** for a user journey or rule: `Given two selected orders / When the user exports / Then the file contains exactly those two orders`.
- **EARS** for one precise system rule: `If the payment provider times out, the checkout service shall leave the order unpaid`.

Then:

- Keep the brief in chat unless the user or a downstream plan needs a file. If you write one, update it in place rather than appending copies — the brief is the single source of truth, and duplicates get re-implemented.
- For large or irreversible work, show the brief and get a yes before acting. For small work, show it and proceed.
- When the work is planned as a DAG or split across workers, each task receives only its own decisions and acceptance checks, not the whole brief.

## Anti-patterns

- Walking the gap table as a questionnaire.
- Asking what the repo, docs, or earlier messages already answer.
- "Any other requirements?" — it gives the user nothing to decide.
- Asking which library, schema, or widget before the outcome is clear.
- Making a consequential choice silently, or presenting a default as approved.
- Another round after the decisions are already actionable.
