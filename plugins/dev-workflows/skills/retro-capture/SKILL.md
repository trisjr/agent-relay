---
name: retro-capture
description: Capture one durable lesson from finished work as a short structured note in the repo's solutions store (default docs/solutions/) — the problem, the cause or decision, the fix or pattern, and what to avoid next time, including lessons the user taught by correcting or rewriting agent output. Use after a hard debugging session, a real trade-off decision, a user correction that implies a convention, a repeated problem, or when the user says "lưu lại bài học", "ghi chú lại", "rút kinh nghiệm", "remember this", "note to self".
---

# Retro capture

Lessons disappear with the session transcript. Capture one reusable lesson after the work is done, in a note of about 40 body lines, so a future agent does not spend hours rediscovering it.

## 1. The durable bar

Ask: if this note vanished, could a future agent who reads the current code, tests, docs, and AGENTS.md repeat the mistake or spend substantial time rediscovering the answer? If not, write nothing and say why in one line.

Task completion, effort spent, and diff size say nothing about durability. Typos, one-off environment hiccups, and lessons already clear from the final diff or existing instructions fail the bar, because a note would only duplicate them. An explicit request to "save the lesson" does not lower the bar: capture promptly when it passes, explain briefly when it fails. If the user asked not to record, don't.

For a live failure, run `debug-root-cause` first and capture only after it finishes. For a vague request, use `clarify-requirements` before the task starts.

Signals that a lesson may be worth capturing:

| Signal | Action |
| --- | --- |
| The user rewrites agent output | Ask one sentence to confirm the intended rule before recording a convention; the edit may be taste. |
| The user says "don't do X again" or rejects a repeated pattern | Capture the correction, or update the existing note. |
| A difficult bug is resolved | Consider a `bug-lesson` after the `debug-root-cause` report. |
| A non-obvious trade-off is settled | Capture the reason as a `decision`. |
| The same problem occurs a second time | Strongest signal; update the existing note if it covers the lesson. |
| Review reveals a convention whose rationale is not in the code | Capture the rationale once its scope is clear. |

## 2. Before writing

Find the notes root with [notes-root.md](references/notes-root.md).

Scan candidate `title:`, `area:`, and `tags:` frontmatter before creating a file. If a note already has the same problem, cause, and lesson, update it in place: keep its path and frontmatter shape, refresh the body, set `last_seen` to today, and add one to `occurrences`. Increment only for a real recurrence or a newly confirmed same lesson, never for merely reading a note.

If a candidate contradicts the new lesson, don't overwrite it. Show both claims and ask the user to resolve them. Headless: write a separate note whose `## Source` says `contradicts <path>, unresolved`, and report the conflict. If the claim conflicts with AGENTS.md or current docs, report that instead of editing those files.

## 3. Compose the note

Write one lesson per file, in the language of the repo's existing docs. Pick `bug-lesson`, `convention`, `decision`, or `pitfall` and follow [note-template.md](references/note-template.md) (or the repo's own decision template). Use a flat kebab-case slug without a date prefix unless the repo has its own taxonomy. Include only the snippet needed to apply the lesson.

Before writing, scan the whole note for API tokens, private keys, `.env` values, credential-bearing connection strings, and sensitive personal paths. Remove them, or stop and tell the user if the lesson can't be recorded safely. Name a configuration key, never its value. Check referenced paths, versions, and present-tense claims against the current tree.

After a successful capture, if you actually know the session ID, sanitize it to `[A-Za-z0-9._-]` and best-effort touch `${TMPDIR:-/tmp}/compound-retros-reminded-<session_id>` so the Stop hook won't remind again. Don't invent a session-ID variable.

## 4. After writing

- **Promotion** (`occurrences` ≥ 3): draft exactly one convention line for an existing AGENTS.md or CLAUDE.md section, name the insertion point, and ask the user to approve or revise. Keep the detailed note afterwards.
- **Discoverability** (once): if the notes root exists but AGENTS.md or CLAUDE.md doesn't mention it, propose one pointer saying where the store is and when to consult it. Skip if the repo has neither file; avoid an unconditional "always check" line.

Never edit an instruction file without consent. Headless: put the proposal in the final output and leave the file untouched.

## 5. Report

Give the note path, type, and occurrence count, plus any promotion proposal or unresolved contradiction. Say when `docs/solutions/` was newly created or chosen as the headless default. `Captured nothing — <why the bar failed>` is a valid result.

A headless run or subagent can't wait for answers: use safe defaults and list unresolved decisions in the final status.

## Anti-patterns

A session journal, a task-completed report, a note longer than its lesson, a stack trace or log that may hold secrets, an AGENTS.md section added on your own, category subdirectories while the store has fewer than 10 notes, and several formatting questions the existing template already answers.
