---
name: retro-recall
description: Apply past lessons before starting non-trivial work — locate the repo's solutions store (default docs/solutions/), shortlist notes by frontmatter and the file paths the task will touch, read only the few relevant ones, cite and apply them, and update recurrence fields when the same situation repeats. Use at the start of non-trivial work in an area with captured lessons, when a problem feels familiar, when the user says "lần sau nhớ", "nhớ bài học", "check the notes", "đã gặp vụ này chưa", "have we seen this before", or asks to review or clean up the notes store.
---

# Retro recall

Start similar work with the lessons the repo has already earned. Context is scarce: shortlist cheaply, then read only what can change this task.

## 1. When to consult

Consult at the start of non-trivial work when a notes store exists, the user asks to check past lessons, the problem feels familiar, or planned file paths match a note's area or tags. Skip one-line changes. If no store exists, proceed normally and don't create or suggest one unless asked.

Recall supplies past context, not a diagnosis or a requirements decision: use `debug-root-cause` for a live failure and `clarify-requirements` for a vague request.

## 2. Locate the notes root

Use [notes-root.md](../retro-capture/references/notes-root.md). For recall, rules 3–4 only identify a possible future root; don't create it just to search. Shared note fields are in [note-template.md](../retro-capture/references/note-template.md).

## 3. Cheap-first lookup

1. Infer a few keywords from the task, the area, and the file paths about to change. List note filenames, then search only frontmatter: `grep -liE '^(tags|area|title):.*<kw>' <root>/*.md` (substitute the real root and an escaped keyword or short alternation). Inspect candidates with `head -n 12 <candidate>` before deciding which to read in full.
2. If more than eight files match, narrow by `area:` and the paths the task will touch. If none match, run one broad grep (`grep -liE '<kw>' <root>/*.md`), then inspect the returned candidates' frontmatter.
3. Read at most three notes in full, ranked by matching area, task terms, and current file paths. If nothing relevant remains, continue and mention the empty result in one line.

Reading the whole store would crowd out the task itself, so never dump or bulk-read it.

## 4. Apply and attribute

Apply a relevant lesson before changing code and cite its path when explaining the choice: "According to `docs/solutions/<slug>.md`, …". Check its claim against current code and docs. If the note conflicts with the repo, follow the current evidence and flag the note as stale for curation instead of silently following it. Write any note update in the language of the repo's existing docs.

## 5. Recurrence update

Add one to `occurrences` and set `last_seen` to today (`YYYY-MM-DD`) only when the same situation has actually recurred and the lesson still applies. A lookup, a citation, or an unrelated use of the pattern is not a recurrence. Keep the note's path and other frontmatter. At `occurrences` ≥ 3, hand the one-line AGENTS.md/CLAUDE.md proposal to [retro-capture's promotion step](../retro-capture/SKILL.md#4-after-writing) and wait for consent before editing an instruction file.

## 6. Curate on request

When asked to clean the store, first show a path-by-path list:

- **keep**: still-useful lessons.
- **merge**: notes with the same lesson.
- **stale**: a verified `retire_when` happened, or an `occurrences: 1` note hasn't recurred for over six months.
- **contradiction**: incompatible claims that need the user's decision.

Check current code before asserting that a retirement condition happened. A still-true note stays even if the code now expresses the rule. A stale candidate is a proposal to shorten or retire, not automatic deletion. Act on merges and deletions only after the user decides. The full-read limit from section 3 still applies; mark classifications that need more evidence as provisional.

## Headless mode

A headless run or subagent can't wait for answers: use safe defaults, report classifications without deleting or merging anything, leave instruction files untouched, and list unresolved decisions in the final status.
