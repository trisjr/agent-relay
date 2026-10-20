---
name: clarify-requirements
description: Clarify material ambiguities before implementation or planning — explore the repo, ask only decisions that change the work, and produce a short requirements brief. Use for "làm rõ yêu cầu", "clarify this", an underspecified feature or spec, or competing interpretations that change scope, permissions, data handling, or a public contract. Skip fully specified tasks and pure explanations.
---

# Clarify requirements

A wrong guess about intent costs a rewrite; an interrogation costs the user's patience. Find what can be found, default what can safely be defaulted, ask only what is genuinely the user's call, and write it down for whoever implements.

## Right-size first

- **Skip** when the request is fully specified or the repo, docs, `AGENTS.md`/`CLAUDE.md`, or the conversation already answer every material open point. No brief ceremony is needed for routine, fully specified work.
- **Default and proceed** when only reversible, low-impact choices are open: list them as assumptions and continue the authorized task.
- **Clarify** when competing answers materially change the main deliverable, scope, security, data, permissions, or a public contract, or a wrong guess is costly to reverse.

Judge ambiguity and impact, not request or diff length. A one-line deletion can still need clarification. If the user asked only to clarify, stop at the brief; clarification does not authorize implementation.

## Explore, then sort the unknowns

Read only deep enough to know what to ask; deep reading belongs to planning. Start inline. If several independent factual questions in separate areas still need real searching, use native read-only subagents when available and permitted: at most 4, one question each, returning `file:line` evidence. Prefer a low-cost model and low effort when the harness exposes those controls. Otherwise explore inline; no external orchestration setup is needed. Deciding and asking stay in the main conversation.

- **Discoverable fact** (which module owns X, the existing export format): find it yourself; if still ambiguous, show the candidates and recommend one.
- **Preference or trade-off** (scope, priority, UX, data policy, access): the user's call.
- **Expert parameter** (retry budget, page size, TTL): follow convention and log it.

## Ask, assume, or block

Safety, privacy, money, permissions, destructive actions, and public API changes are always high impact.

- **Required decision:** ask when an unresolved choice materially changes the main deliverable or has high impact. Keep the affected action `BLOCKED` until the user answers or explicitly delegates that decision within stated bounds. Continue independent, authorized work.
- **Optional choice:** assume and log only reversible, low-impact defaults with their source — `Assumption: CSV delimiter = comma, matching existing exports.` — or `agent default`. Never phrase an assumption as if the user approved it.

At most **3 questions per round** and **3 rounds** per clarification pass; a question that depends on another open answer waits for the next round. When an answer is vague, conflicts with another answer or the repo, or opens a new blocking choice, ask a narrower follow-up that names the answer it follows up and offers fresh options. After the last round, default only optional choices and report unresolved required decisions as `Open: BLOCKED`, with the affected actions.

Each question states its context and whether it is required or optional, in the user's language. Offer 2–3 concrete options with a one-line consequence, the recommended one first and labeled `(Recommended)`; use a free-text question when no sensible option set exists. Avoid an "Other" option when the channel already accepts free text. Ask about outcomes and constraints, not implementation details you can decide. If the user asks for context, explain and re-ask the same question.

A recommendation is not approval. Skipped, empty, or timed-out answers leave required decisions open; "done" / "proceed" alone defaults only optional choices. Explicit delegation such as "choose the access policy you recommended" settles that decision; record it as delegated. Reuse prior answers and approvals instead of asking again.

## Ask through the right channel

Read [references/channels.md](references/channels.md) before asking: choose an available question tool or a plain-text block from the actual session capabilities. In confirmed headless runs, default only optional choices and report required decisions with affected actions marked `BLOCKED`.

## Hand off a requirements brief

A brief is ready when the user, outcome, and scope fit in a sentence or two, every material behavior has an observable check, and no required decision remains open. If clarification ends with blockers, label the brief as a draft and name the blocked actions. Write only fields that carry a decision:

```markdown
## Requirements brief
Goal / user: <outcome, for whom>
Scope: <in scope; an exclusion only if it prevents scope creep>
Decisions: <answers that change behavior — cite the user or repo>
Assumptions: <low-risk defaults, with source or "agent default">
Acceptance: <2–5 observable checks, including the key failure path>
Constraints: <binding ones only>
Approach: <inline | native subagents> — <one-line reason, only when relevant>
Open: <none | non-blocking item | BLOCKED: decision + affected action>
```

Acceptance uses the lightest observable form: a checklist for small edits, Given/When/Then for a user journey, EARS for one precise system rule. Approach defaults to inline and follows the user's execution preferences and available capabilities.

Keep the brief in chat unless a file is needed. Once requirements are ready, continue work already authorized. Ask for approval only for an action that still needs authorization or a material scope change, after completing independent preparation; task size alone is not a reason to ask again. A clarification-only request ends with the brief.
