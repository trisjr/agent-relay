---
name: clarify-requirements
description: Pin down what the user actually wants before building — explore the repo first, ask only the few questions whose answers change the work, each with a recommended option, and hand off a short requirements brief. Use this skill whenever a request is vague, underspecified, or high-stakes before implementation or planning starts — "build X", "add a feature", "làm tính năng", "làm rõ yêu cầu", "clarify this", a new project, PRD, or spec that will feed a plan or DAG — or whenever two plausible readings would lead to materially different work, data loss, or a changed public contract. The skill relies on asking the user. Skip it for well-specified tasks, changes whose diff fits in one sentence, questions the code or docs already answer, and pure explanations.
---

# Clarify requirements

A wrong guess about intent costs a rewrite; an interrogation costs the user's patience. Find what can be found, default what can safely be defaulted, ask only what is genuinely the user's call, then write it down so whoever implements — you, a fresh session, or a DAG worker — builds the right thing.

## Right-size first

- **Skip** when the request is fully specified, the diff fits in one sentence, or every open point is a fact the repo, docs, `AGENTS.md`/`CLAUDE.md`, or the conversation already holds. At most say "requirements are clear — proceeding".
- **Default and proceed** when only reversible, low-impact choices are open: list them as assumptions and start.
- **Clarify** when a decision has two or more plausible answers that change user-visible behavior, effort, security or privacy, data retention, or a public contract, and a wrong guess would be costly or hard to reverse.

Keep ceremony proportional: a bug fix never needs user stories, and a brief longer than the diff is a smell.

## Explore, then sort the unknowns

Read the relevant code, tests, docs, conventions, and earlier messages before asking anything. Delegating wide reads to subagents is fine, but keep the deciding and the asking in the main conversation — question tools don't exist inside subagents. Sort each unknown:

- **Discoverable fact** (which module owns X, what format existing exports use): find it yourself. If it is still ambiguous, show the candidates you found and recommend one rather than handing the user your research.
- **Preference or trade-off** (scope, priority, UX, data policy, who gets access): the user's call, so a candidate question.
- **Expert parameter** (retry budget, page size, cache TTL): choose from convention and log it; ask only when it is user-visible and consequential.

A gap is worth raising only when two plausible answers would change the implementation or how it is accepted — typically the goal, which users, scope, rules, data lifecycle, failure paths, non-functional targets, integrations, or the acceptance condition.

## Ask, assume, or block

Weigh each candidate by impact if wrong, uncertainty, and irreversibility. Safety, privacy, money, permissions, destructive or data-losing actions, and public API changes are always top impact.

- **Ask** the few decisions that would change what you do next.
- **Assume and log** the reversible, low-impact ones, one line each, naming the source: `Assumption: export = current filtered view, matching the table's existing actions.` Write `agent default` when there is no precedent. An assumption is never phrased as if the user approved it.
- **Block** an irreversible, high-impact action whose decision you cannot get: keep doing the independent work, and leave that action undone rather than inventing a default.

Ask at most **3 questions per round**, usually one round; a second round only when an answer opens a new blocking choice. Independent questions share a round; one that depends on another open answer waits. Whatever remains becomes an assumption or an `Open` item.

## Write questions that are cheap to answer

Each question restates its decision with one line of context, because some harnesses render only the options. It covers one decision, offers 2–3 concrete, mutually exclusive options (4 only where the channel allows) with a one-line consequence each, and puts the recommended option first with a label ending in `(Recommended)` — the default when unanswered. Leave out filler and "Other"; every channel already accepts free text. Ask about outcomes and constraints, not implementation details you can decide, and write in the user's language. Use an open question only when no sensible option set exists.

If the user asks for context, explain and re-ask the same question. "Whatever you think" / "cứ làm đi" means adopt your recommendations, recorded as delegated decisions. "done", "stop", or "proceed" means stop asking and default the rest.

## Ask through the right channel

Take the first case that applies.

1. **Dispatched Orca worker** (a live injected preamble with executable, handle, capability, Task ID, and Dispatch ID): ask only through the preamble's `orca orchestration ask` command, copied verbatim — a local question UI would go unanswered. Ask only what the coordinator must decide; default the rest and list them in the report and `worker_done`. One question maps to `--question "<header>: <question>" --options "<label a> (Recommended),<label b>"` (labels must not contain commas). On timeout, use `--resume <message_id>` instead of asking again.
2. **A native question tool and a person to answer it:**

   | Harness | Tool | Limits |
   | --- | --- | --- |
   | Claude Code, Kimi Code, Qoder CLI | `AskUserQuestion` | 1–4 questions, 2–4 options, `header` ≤12 chars, `multiSelect` |
   | Codex CLI | `request_user_input` | Plan mode only — Default mode answers "unavailable", so use case 3; ≤3 questions, 2–3 options, snake_case `id`, no multi-select |
   | Gemini CLI | `ask_user` | 1–4 questions, `type` choice / text / yesno, `multiSelect` |
   | Cursor, Qoder IDE | built-in ask tool | limits undocumented: stay within 3 questions and 2–3 options; Cursor's tool does not block, so end the turn after asking |

3. **Interactive but no tool:** print the plain-text block below and end your turn before starting work that depends on the answers.
4. **Headless — nobody can answer** (CI, `-p` / `exec`, the tool was denied or removed, a dialog timed out, answers came back empty): don't wait, and don't retry a denied question.
   - Reversible, low-risk gaps → apply the recommended defaults, continue, and end the output with an `Assumptions (headless)` list.
   - Blocking or irreversible gaps (deleting data, migrations, public API, cost, security) → stop before acting and make the question block your final output so the caller can re-run with answers. If the caller supplied an output schema, emit the questions in it.

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

## Hand off a requirements brief

Stop asking once you can state the user, outcome, and scope in a sentence or two; every material behavior and failure path has an observable check; no open choice touches safety, data loss, permissions, the public contract, or the main deliverable; and the implementer could start without another question. Then write a brief with only the fields that carry a decision — short enough to read at a glance, never the interview:

```markdown
## Requirements brief
Goal / user: <outcome, for whom>
Scope: <in scope; an explicit exclusion only if it prevents scope creep>
Decisions: <answers that change behavior — cite the user or repo evidence>
Assumptions: <low-risk defaults, with source or "agent default">
Acceptance: <2–5 observable checks, including the key failure path>
Constraints: <binding ones only>
Approach: <inline | subagents | workflow | DAG> — <one-line reason>; recommended, user may override
Open: <none | non-blocking item | BLOCKED: decision + affected action>
```

Write acceptance in the lightest format that makes the result observable: a checklist for small edits, Given/When/Then for a user journey, EARS for one precise system rule.

For **Approach**, default to inline. Recommend subagents when a few independent areas or a large read would flood one context, a workflow for many similar items that get the same check, and a supervised DAG for a multi-part feature across modules that needs decision gates. Workflows and DAGs multiply cost and coordination, so put the user's go-ahead for them in `Open` unless they already approved it.

Keep the brief in chat unless the user or a downstream plan needs a file; if you write one, update it in place so it stays the single source of truth. For large or irreversible work, get a yes on the brief before acting; for small work, show it and proceed. When the work is split across workers, each task receives only its own decisions and acceptance checks.
