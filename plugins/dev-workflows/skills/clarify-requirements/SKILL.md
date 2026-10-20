---
name: clarify-requirements
description: Pin down what the user wants before building — explore the repo, ask only the questions that change the work, each with a recommended option, and hand off a short requirements brief. Use when a request is vague, underspecified, or high-stakes before implementation or planning — "build X", "add a feature", "làm tính năng", "làm rõ yêu cầu", "clarify this", a PRD or spec — or when two readings would change the work, lose data, or alter a public contract. Skip well-specified tasks, one-sentence diffs, and explanations.
---

# Clarify requirements

A wrong guess about intent costs a rewrite; an interrogation costs the user's patience. Find what can be found, default what can safely be defaulted, ask only what is genuinely the user's call, and write it down for whoever implements.

## Right-size first

- **Skip** when the request is fully specified, the diff fits in one sentence, or the repo, docs, `AGENTS.md`/`CLAUDE.md`, or the conversation already answer every open point.
- **Default and proceed** when only reversible, low-impact choices are open: list them as assumptions and start.
- **Clarify** when a decision with several plausible answers changes user-visible behavior, effort, security, data, or a public contract, and a wrong guess is costly to reverse.

A brief longer than the diff is a smell.

## Explore, then sort the unknowns

Read only deep enough to know what to ask; deep reading belongs to planning. Start inline. If several independent factual questions in separate areas still need real searching, fan them out in parallel to read-only explore subagents on a cheap tier (Claude Code: `Explore` or `haiku`, effort `low`), one question each, at most 4, returning `file:line` evidence rather than conclusions. Deciding and asking stay in the main conversation — subagents cannot reach the user.

- **Discoverable fact** (which module owns X, the existing export format): find it yourself; if still ambiguous, show the candidates and recommend one.
- **Preference or trade-off** (scope, priority, UX, data policy, access): the user's call.
- **Expert parameter** (retry budget, page size, TTL): follow convention and log it.

## Ask, assume, or block

Safety, privacy, money, permissions, destructive actions, and public API changes are always high impact.

- **Ask** the few decisions that change what you do next.
- **Assume and log** reversible, low-impact ones with their source — `Assumption: export = current filtered view, matching the table's existing actions.` — or `agent default`. Never phrase an assumption as if the user approved it.
- **Block** an irreversible action whose decision you cannot get: do the independent work and leave that action undone.

At most **3 questions per round** and **3 rounds**; a question that depends on another open answer waits for the next round. When an answer is vague, conflicts with another answer or the repo, or opens a new blocking choice, ask a narrower follow-up that names the answer it follows up and offers fresh options. After the last round, the rest becomes assumptions or `Open` items.

Each question carries one line of context (some harnesses render only the options), 2–3 concrete options with a one-line consequence, the recommended one first and labeled `(Recommended)`, written in the user's language — no "Other" option, since every channel accepts free text. Ask about outcomes and constraints, not implementation details you can decide. If the user asks for context, explain and re-ask the same question. "Whatever you think" / "cứ làm đi" adopts your recommendations as delegated decisions; "done" / "proceed" defaults the rest.

## Ask through the right channel

Read [references/channels.md](references/channels.md) before asking: it lists each harness's question tool and limits, the plain-text block for interactive sessions without one, and the headless rule — never wait; default reversible gaps, and make the question block your final output with irreversible actions marked `BLOCKED`.

## Hand off a requirements brief

Stop when the user, outcome, and scope fit in a sentence or two, every material behavior has an observable check, and no open choice touches safety, data loss, permissions, the public contract, or the main deliverable. Then write only the fields that carry a decision:

```markdown
## Requirements brief
Goal / user: <outcome, for whom>
Scope: <in scope; an exclusion only if it prevents scope creep>
Decisions: <answers that change behavior — cite the user or repo>
Assumptions: <low-risk defaults, with source or "agent default">
Acceptance: <2–5 observable checks, including the key failure path>
Constraints: <binding ones only>
Approach: <inline | subagents | workflow | DAG> — <one-line reason>; user may override
Open: <none | non-blocking item | BLOCKED: decision + affected action>
```

Acceptance uses the lightest observable form: a checklist for small edits, Given/When/Then for a user journey, EARS for one precise system rule. Approach defaults to inline; a workflow or a supervised DAG (`dag-build`) needs the user's go-ahead, so list it in `Open` unless already approved.

Keep the brief in chat unless a file is needed. Get a yes on it before large or irreversible work; for small work, show it and proceed.
