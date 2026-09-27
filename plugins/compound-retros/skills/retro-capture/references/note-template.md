# Solution note template

Write one durable lesson per file. Keep the body near or below 40 lines. Use the language of the target repo's existing documentation. If that repo already has a decision/ADR template, use it for `decision` notes.

## Frontmatter

Start every note with YAML frontmatter:

```yaml
---
title: Human-readable one-line lesson
type: bug-lesson
area: billing
tags: [billing, rounding, user-correction]
created: 2026-09-27
last_seen: 2026-09-27
occurrences: 1
retire_when: Remove after the old billing path is deleted and verified unused
---
```

| Field | Rule |
| --- | --- |
| `title` | Required, one line naming the lesson, not the session. |
| `type` | Required; exactly `bug-lesson`, `convention`, `decision`, or `pitfall`. |
| `area` | Required; a stable kebab-case repo area such as `billing`, `auth`, or `ci`. |
| `tags` | Required YAML list; at most 8 lower-hyphen tags. Search the existing corpus and reuse its spellings before adding a tag. Prefer area/module, technology, lesson topic, or `user-correction` tags that help lookup. Do not invent synonyms. |
| `created` | Required `YYYY-MM-DD` calendar date of the original note; keep it on updates. |
| `last_seen` | Required `YYYY-MM-DD` calendar date when the lesson last recurred or was confirmed; set to today on creation and real recurrence. |
| `occurrences` | Required integer, starting at `1`; increment only when the same situation recurs or the same lesson is newly confirmed, not when a note is merely read. |
| `retire_when` | Optional concrete condition and check for when the note stops applying. Omit when there is no known expiry. |

Quote any YAML scalar containing `: ` or ` #` (and escape quotes as YAML requires). Never place credentials, API token values, private keys, `.env` values, credential-bearing connection strings, or sensitive personal paths in frontmatter or body. Mention a config key by name only.

## File naming and updates

Use a descriptive kebab-case slug such as `ci-date-uses-utc.md`, with no date prefix. Keep notes flat in the chosen notes root unless the repo already has a taxonomy. Before writing, search candidate `title:`, `area:`, and `tags:` fields. When a note teaches the same problem, cause, and lesson, update that file in place, keep its path and frontmatter shape, refresh the concise body, set `last_seen` to today, and increment `occurrences`. Do not replace a contradictory note: present both claims for resolution; in headless mode, use a separate note with `## Source` stating `contradicts <path>, unresolved`.

## Type templates

Use the frontmatter above with the chosen `type`, `area`, tags, and dates. Keep `## Source` only when it adds useful provenance.

### `bug-lesson`

```markdown
## Context
Where the failure appeared and why a future agent may encounter it.

## Problem
The observed wrong behavior, in one or two sentences.

## Cause
One sentence naming the verified root cause.

## Lesson
The reusable rule that the code alone does not make obvious.

## Apply
The fix or check to repeat, with only a short snippet if necessary.

## Source
Issue, commit, or debugging report, if useful.
```

### `convention`

```markdown
## Context
Where the convention applies.

## Lesson
The agreed repo practice and its reason.

## Apply
What to use or avoid next time.

## Source
User correction, review, or decision, if useful.
```

### `decision`

```markdown
## Context
The constraint or trade-off that required a choice.

## Options considered
- Option A: relevant benefit and cost.
- Option B: relevant benefit and cost.

## Lesson
The choice and why it won.

## Apply
Where this decision governs future work and when to revisit it.

## Source
Issue or discussion, if useful.
```

### `pitfall`

```markdown
## Context
The workflow or component where the mistake is tempting.

## Lesson
The failure mode and why it matters.

## Apply
The safe action and the action to avoid.

## Source
User correction or incident, if useful.
```

## Filled examples

These illustrate the format; verify paths and claims against the actual target repo before adapting them.

### CI date failure — `ci-date-uses-utc.md`

```markdown
---
title: Pin the timezone in date assertions used by CI
type: bug-lesson
area: ci
tags: [ci, timezone, date-tests]
created: 2026-09-27
last_seen: 2026-09-27
occurrences: 1
retire_when: Remove if date assertions no longer depend on local timezone; verify under two TZ settings
---

## Context
A date assertion passed locally in Asia/Ho_Chi_Minh but failed on a CI runner using UTC.

## Problem
The expected calendar day changed between local and CI runs.

## Cause
The test formatted an instant using the machine's default timezone.

## Lesson
An instant has no stable local calendar date until the timezone is explicit.

## Apply
Set the timezone explicitly in the formatter or assertion, then verify under `TZ=UTC` and `TZ=Asia/Ho_Chi_Minh`.

## Source
Timezone-only CI failure investigation.
```

### User correction — `prices-use-format-vnd.md`

```markdown
---
title: Format displayed VND amounts with the repo helper
type: convention
area: billing
tags: [billing, money, user-correction]
created: 2026-09-27
last_seen: 2026-09-27
occurrences: 1
---

## Context
The agent formatted a displayed amount with `toLocaleString`; the user changed it to the existing `formatVnd` helper in `lib/money.ts` and confirmed this is the repo convention.

## Lesson
Reuse `formatVnd` for displayed VND amounts so formatting stays consistent across the app.

## Apply
Import the existing helper rather than calling `toLocaleString` at each display site.

## Source
Confirmed user correction to agent output.
```
