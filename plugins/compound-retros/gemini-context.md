# compound-retros

Apply to durable project lessons after meaningful work and to similar non-trivial work when a solutions store already exists.
Skip trivial changes, one-off environment hiccups, and recall when no store exists.

- Capture: write one short structured lesson after a hard fix, meaningful decision, repeated issue, or confirmed user correction.
- Recall: shortlist notes by title, area, tags, and affected paths before similar work; read only the few relevant notes in full and cite them.
- If `activate_skill` is available, activate `retro-capture` or `retro-recall` for the relevant phase.
- Apply the durable bar: would losing the note let a future agent repeat the mistake despite current code, tests, docs, and `AGENTS.md`? If not, do not write it.
- A request to remember something does not waive that bar.
- Never record secrets, credentials, or sensitive values; use configuration key names without values.
- Select the notes root in order: a user-named path or `AGENTS.md`/`CLAUDE.md` pointer, then an existing note-shaped directory and template, then `docs/solutions/`.
- If the repo lacks `docs/`, ask once before the first note when interactive; headless use `docs/solutions/` and report the choice.
- Keep notes inside the user's repo, never inside the plugin.
- Update duplicate lessons in place; surface contradictions instead of silently overwriting them.
- At `occurrences >= 3`, propose one line for `AGENTS.md` or `CLAUDE.md` and wait for user consent; headless only propose.
- Do not create a store merely to perform recall.
