---
name: retro-recall
description: Make past lessons compound before starting non-trivial work — locate the repo's solutions store (default docs/solutions/), shortlist notes by frontmatter (tags, area, title) and file paths the task will touch, read only the few relevant notes in full, cite and apply them, and update recurrence fields when the same situation repeats. Use this skill at the start of any non-trivial task in an area with captured lessons, when the user says "lần sau nhớ", "nhớ bài học", "check the notes", "đã gặp vụ này chưa", "have we seen this before", or when a problem feels familiar; also use it when the user asks to review or clean up the notes store. Skip it when no solutions store exists, for trivial one-line changes, and never bulk-read every note into context.
---

# Retro recall

Start similar work with the lessons the repo has already earned.
Context is scarce: shortlist cheaply, then read only what can change this task.

## 1. When to consult

Consult at the start of non-trivial work when a notes store exists, the user asks to check past lessons, the problem feels familiar, or planned file paths match a note's area or tags. Skip a trivial one-line change. If no store exists, proceed with the task normally; do not create or suggest a store unless the user asks.

Recall supplies past context; use `debug-root-cause` to investigate a live failure and `clarify-requirements` to resolve a vague request. Do not treat a note as a diagnosis or a requirements decision.

## 2. Locate the notes root

Choose the notes root by the first matching rule:

1. The user named a location this session, or AGENTS.md/CLAUDE.md points to a solutions/notes path.
2. The repo already has a directory with note-shaped files (candidates: docs/solutions/, docs/retros/, docs/notes/, docs/adr/, docs/decisions/, .agent/notes/ …; shape check: frontmatter with type/tags) — use it as is, including its own template for `decision` notes.
3. The repo has docs/ → docs/solutions/ (create it with the first note and say so in the report).
4. No docs/ → still default to docs/solutions/, but interactively ask one quick question ("docs/solutions/ or elsewhere?") before the first creation; headless → use docs/solutions/ and state it in the final output. Never write notes outside the user's repo, never into the plugin directory.

For recall, rules 3–4 identify a possible future root; do not create it just to search. Use the existing repo's note shape and decision template when present. See [the note format](../retro-capture/references/note-template.md) for the shared fields.

## 3. Cheap-first lookup

1. Infer a few keywords from the task, the area, and file paths about to change. List note filenames, then search only frontmatter fields: `grep -liE '^(tags|area|title):.*<kw>' <root>/*.md`. Replace `<root>` and `<kw>` with the actual root and an escaped keyword or short alternation. Inspect only the first 12 lines of each candidate with `head -n 12 <candidate>` before deciding which full notes matter.
2. If more than eight files match, narrow by `area:` and the paths the task will touch. If none match, run one broad full-content grep for the keyword (`grep -liE '<kw>' <root>/*.md`), then inspect the returned candidates' frontmatter.
3. Read at most three notes in full for this task. Rank by matching area, task terms, and current file paths. If nothing relevant remains, continue the task and mention the empty result in at most one line. Never dump or bulk-read the store.

## 4. Apply and attribute

Apply a relevant lesson before changing code and cite its path when explaining the choice: “According to `docs/solutions/<slug>.md`, …”. Check its claim against current code and docs. If the note conflicts with the current repo, follow the current evidence and flag the note as stale for curation instead of silently following it. Keep any note update in the language of the target repo's existing documentation.

## 5. Recurrence update

Increment `occurrences` by exactly one and set `last_seen` to today's `YYYY-MM-DD` only when the same situation has actually recurred and the note's lesson still applies. A lookup, citation, or unrelated use of the pattern is not a recurrence. Preserve the note's path and other frontmatter. At `occurrences` ≥ 3, hand the one-line AGENTS.md/CLAUDE.md promotion proposal to [retro-capture's promotion path](../retro-capture/SKILL.md); wait for user consent before editing an instruction file. In headless mode, propose the line and leave the instruction file untouched.

## 6. Curate on request

When asked to clean the store, first show a path-by-path list: **keep** for still-useful lessons; **merge** for notes with the same lesson; **stale** when a verified `retire_when` happened or a note with `occurrences: 1` has not recurred for over six months; **contradiction** for incompatible claims needing the user's decision. Check current code before asserting that a retirement condition happened. Distinguish correcting drift from deep pruning: a still-true note stays, even if code now expresses the rule.

Show the list to the user before any merge or deletion, and act only after the user decides. A stale candidate is a proposal to shorten or retire, not automatic deletion. In headless mode, report the classifications and delete or merge nothing. Keep the full-read limit from section 3; mark any classification that needs more evidence as provisional.

## 7. Anti-patterns

Do not bulk-read the store, consult it for a one-line change, obey a note over changed code, create a store no one requested, or increment `occurrences` merely because a note was read. In a headless run or subagent that cannot ask, use safe defaults and put unresolved decisions or blocked actions in the final status rather than waiting.
