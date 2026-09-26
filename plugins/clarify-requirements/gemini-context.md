# clarify-requirements

Applies only to a request that is vague, underspecified, or high-stakes **before building or planning** — where two plausible readings would lead to materially different work, data loss, or a changed public contract. Ignore it for well-specified tasks, changes whose diff fits in one sentence, questions the code or docs already answer, and pure explanations.

- If `activate_skill` is available, activate the `clarify-requirements` skill and follow it.
- If only `ask_user` is available: explore the repo first, then ask at most 3 questions — each self-contained, one decision, 2–3 options with the recommended option first and labeled `(Recommended)` — and log low-risk defaults as assumptions.
- If `ask_user` is not available, you are headless (`-p`, CI, no TTY): nobody can answer, so never wait and never retry a denied question.
  - Reversible, low-risk gaps → apply the recommended defaults, continue, and end the output with an `Assumptions (headless)` list.
  - Blocking or irreversible gaps (deleting data, migrations, public API, cost, security) → stop before acting and make this question block your final output so the caller can re-run with answers:

```text
[clarify] <N> decisions before I start. Re-run with answers, e.g. "1a 2b". Anything skipped uses its default.

1. [Header] <self-contained question, with one line of context>
   a) <option> (Recommended) — <consequence>
   b) <option> — <consequence>
   default: a
```

Never ask what the repo already answers, and never present a default as if the user approved it.
