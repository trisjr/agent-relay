# Question channels

Choose from the actual session capabilities. Tool schemas and session instructions take precedence over remembered harness names or limits.

## 1. Confirmed headless — nobody can answer

Use this case when the caller or runtime explicitly establishes a non-interactive run, such as a CI job with no reply channel. A missing or denied tool, a timeout, or an empty answer alone does not establish that nobody can answer.

- Optional, reversible, low-impact gaps → apply defaults, continue authorized work, and list `Assumptions (headless)` in the final output.
- Required decisions → complete independent work, leave dependent actions `BLOCKED`, and end with the numbered question block below so the caller can re-run with answers. Recommend options without making them automatic defaults. Use the caller's output schema when supplied.

Never wait for interactive input in this case.

## 2. Available question tool with a person to answer it

Use the available tool that the current mode permits. Follow its schema, keeping at most 3 questions per round and normally 2–3 options. Put context and required/optional status inside each question. Use a text response when the tool supports one and choices would be artificial.

For an asynchronous tool, a returned call or a preselected option is not an answer. Continue only independent work while the question is pending; wait or end the turn as the session requires. For any tool, process partial answers per question: optional choices may default, required decisions remain open.

If the tool is unavailable in the current mode, denied, or unable to express the question, use case 3 when chat remains available. Do not retry a denied tool or infer approval from a timeout or empty response.

## 3. Interactive chat without a usable question tool

Print a numbered block and end your turn before starting dependent work. Explain which choices may default and which require an answer. For example:

```text
[clarify] Reply in one line, e.g. "1a 2b", or use free text. Question 1 may default; question 2 needs an answer before export access is implemented.

1. [Format — optional] Which CSV delimiter? Existing exports use commas.
   a) Comma (Recommended) — matches existing exports
   b) Semicolon — convenient for spreadsheet locales that expect it
   default if skipped: a (recorded as an assumption)

2. [Access — required] Who may export? The app has no export policy yet.
   a) Admins only (Recommended) — limits bulk extraction to admins
   b) Anyone who can see the table — allows all table viewers to download its data
   if unanswered: BLOCKED — export access policy; no automatic default

Free text works too, e.g. "2: finance team only".
```

A follow-up round names the earlier answer it narrows and asks only unresolved decisions. If the user replies only `1a`, keep question 2 open. After 3 rounds, end with a draft brief listing the remaining required decisions and blocked actions; do not silently default them.
