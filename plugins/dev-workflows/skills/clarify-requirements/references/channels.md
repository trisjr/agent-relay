# Question channels

Take the first case that applies.

## 1. Native question tool with a person to answer it

| Harness | Tool | Limits |
| --- | --- | --- |
| Claude Code, Kimi Code, Qoder CLI | `AskUserQuestion` | 1–4 questions, 2–4 options, `header` ≤12 chars, `multiSelect` |
| Codex CLI | `request_user_input` | Plan mode only — Default mode answers "unavailable", so use case 2; ≤3 questions, 2–3 options, snake_case `id`, no multi-select |
| Gemini CLI | `ask_user` | 1–4 questions, `type` choice / text / yesno, `multiSelect` |
| Cursor, Qoder IDE | built-in ask tool | limits undocumented: stay within 3 questions and 2–3 options; Cursor's tool does not block, so end the turn after asking |

## 2. Interactive but no tool

Print the plain-text block below and end your turn before starting work that depends on the answers.

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

A follow-up round uses the same block, headed `[clarify] round 2`, and names the earlier answer it narrows.

## 3. Headless — nobody can answer

CI, `-p` / `exec`, the tool was denied or removed, a dialog timed out, or answers came back empty. Don't wait, and don't retry a denied question.

- Reversible, low-risk gaps → apply the recommended defaults, continue, and end the output with an `Assumptions (headless)` list.
- Blocking or irreversible gaps (deleting data, migrations, public API, cost, security) → stop before acting and make the numbered question block above your final output, marking the affected actions `BLOCKED`, so the caller can re-run with answers. If the caller supplied an output schema, emit the questions in it.
