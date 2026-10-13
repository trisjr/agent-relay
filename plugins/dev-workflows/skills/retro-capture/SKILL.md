---
name: retro-capture
description: Capture one durable lesson from finished work as a short structured note in the repo's solutions store (default docs/solutions/, honoring existing conventions) — the problem hit, the cause or key decision, the fix or pattern applied, and what to avoid next time, including lessons the user taught by correcting, rejecting, or rewriting agent output. Use this skill after meaningful work worth remembering, when the user says "lưu lại bài học", "ghi chú lại", "rút kinh nghiệm", "remember this", "note to self", when they corrected or rewrote agent code with an implicit convention, after a hard debugging session or real trade-off decision, or when the same problem appears for the second time. Skip it for trivial tasks (typo, one-off environment hiccup), anything already explained by the final code, tests, docs, or AGENTS.md, and anything the user asked not to record; never write secrets, credentials, or sensitive values into notes.
---

# Retro capture

Lessons can disappear with the session transcript.
Capture one reusable lesson after the work is done.
Keep a good note to about 40 body lines so it saves a future agent hours of rediscovery.

## 1. The durable bar

Ask: if this note vanished, could a future agent who reads the current code, tests, docs, and AGENTS.md repeat the mistake or spend substantial time rediscovering the answer? If not, do not write a note; say why in one line if capture was raised.

Do not treat task completion, effort spent, or diff size as evidence of durability. Skip typos, one-off environment hiccups, and lessons already clear in the final diff or existing instructions. An explicit request to "save the lesson" does not lower this bar: capture promptly when it passes, and explain briefly when it fails. Respect a request not to record.

For a live failure, use `debug-root-cause` first; capture only a durable lesson after that work is finished. Use `clarify-requirements` for a vague request before the task begins.

## 2. When to capture — signals

| Signal | Action |
| --- | --- |
| The user manually corrects or rewrites agent output | Ask one sentence to confirm the intended rule before recording a convention; the edit may reflect taste. |
| The user says "don't do X again" or rejects a repeated pattern | Capture the durable correction, or update an existing note. |
| A difficult bug is resolved | Consider a `bug-lesson` after the `debug-root-cause` Phase 5 report; apply the durable bar again. |
| A non-obvious trade-off is settled | Capture the reason as a `decision`. |
| The same problem occurs a second time | Treat recurrence as the strongest signal; update the existing note if it covers the lesson. |
| Review reveals a convention whose rationale is absent from code | Capture the rationale once its intended scope is clear. |
| The user explicitly asks to remember a lesson | Apply the durable bar, then capture immediately if it passes. |

## 3. Write-time curation (before writing)

Choose the notes root by the first matching rule:

1. The user named a location this session, or AGENTS.md/CLAUDE.md points to a solutions/notes path.
2. The repo already has a directory with note-shaped files (candidates: docs/solutions/, docs/retros/, docs/notes/, docs/adr/, docs/decisions/, .agent/notes/ …; shape check: frontmatter with type/tags) — use it as is, including its own template for `decision` notes.
3. The repo has docs/ → docs/solutions/ (create it with the first note and say so in the report).
4. No docs/ → still default to docs/solutions/, but interactively ask one quick question ("docs/solutions/ or elsewhere?") before the first creation; headless → use docs/solutions/ and state it in the final output. Never write notes outside the user's repo, never into the plugin directory.

Scan candidate `title:`, `area:`, and `tags:` frontmatter before creating a file. If a note already has the same problem, cause, and lesson, update it in place: preserve its path and frontmatter shape, refresh its body, set `last_seen` to today, and increment `occurrences` by one. Do not create a duplicate. Increment only for a real recurrence or newly confirmed same lesson, not for merely reading a note.

If a candidate contradicts the new lesson, do not overwrite it. Show both claims and ask the user to resolve them. In headless mode, write a separate note with `## Source` saying `contradicts <path>, unresolved`, and report the conflict. If the claim conflicts with AGENTS.md or current docs, report that conflict instead of editing those files.

## 4. Compose the note

Write one lesson per file, in the language used by the target repo's existing documentation. Choose `bug-lesson`, `convention`, `decision`, or `pitfall`; follow [the note template](references/note-template.md) and any existing repo template for decisions. Use a flat kebab-case slug without a date prefix unless the repo already has its own taxonomy. Keep the body near or below 40 lines and include only the snippet needed to apply the lesson.

Compact fallback if the template is unavailable: YAML frontmatter must contain `title`, `type`, `area`, `tags` (at most 8 lower-hyphen tags), `created`, `last_seen` (both `YYYY-MM-DD`), and integer `occurrences` (start at 1); `retire_when` is optional. Follow with `## Context`, `## Lesson`, `## Apply`, and optional `## Source`; add `## Problem` and a one-sentence `## Cause` for `bug-lesson`, or `## Options considered` for `decision`. Quote YAML values containing `: ` or ` #`.

Before writing, scan the entire proposed note for API tokens, private keys, `.env` values, credential-bearing connection strings, and sensitive personal paths. Remove those values or stop and tell the user if the lesson cannot be recorded safely. Name a configuration key, never its value. Verify referenced paths, versions, and present-tense claims against the current tree.

After a successful capture, if you actually know the session ID, sanitize it to `[A-Za-z0-9._-]` and best-effort touch `${TMPDIR:-/tmp}/compound-retros-reminded-<session_id>` so the Stop hook will not remind again. Never invent a session-ID environment variable.

## 5. Promotion path (`occurrences` ≥ 3)

When an in-place update reaches three occurrences, draft exactly one convention line for an existing AGENTS.md or CLAUDE.md section and name the insertion point. Ask the user to approve or revise it; never edit either instruction file without consent. Do not rewrite a section or add a heading for a single line. In headless mode, propose the line in the final output and leave the file untouched. Keep the detailed note after promotion unless the user chooses otherwise.

## 6. Discoverability (once)

If the notes root exists but AGENTS.md or CLAUDE.md does not mention it, propose one descriptive pointer stating where the store is and when to consult it. Wait for consent before adding it; in headless mode, report the gap only. Skip this step if the repo has neither instruction file. Avoid an unconditional "always check" instruction.

## 7. Report

Report the new or updated note path, type, and occurrence count; include any promotion proposal or unresolved contradiction. `Captured nothing — <reason the durable bar failed>` is a valid result. State when `docs/solutions/` was newly created or chosen as the headless default.

In a headless run or subagent that cannot ask, use safe defaults, do not wait for answers, and put unresolved decisions or blocked actions in the final status. The only root-location question is the one before first creation when `docs/` is absent; headless runs default as stated above.

## 8. Anti-patterns

Do not write a session journal, a task-completed report, a note longer than its lesson needs, or a full stack trace or log that may hold secrets. Do not add an AGENTS.md section on your own. Do not create category subdirectories while the store has fewer than 10 notes. Do not ask several formatting questions when the existing template already answers them.
