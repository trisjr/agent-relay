# Notes root

Shared by `retro-capture` and `retro-recall`. Choose the notes root by the first matching rule:

1. The user named a location this session, or AGENTS.md/CLAUDE.md points to a solutions/notes path.
2. The repo already has a directory with note-shaped files (candidates: docs/solutions/, docs/retros/, docs/notes/, docs/adr/, docs/decisions/, .agent/notes/ …; shape check: frontmatter with type/tags) — use it as is, including its own template for `decision` notes.
3. The repo has docs/ → docs/solutions/ (create it with the first note and say so in the report).
4. No docs/ → still default to docs/solutions/, but interactively ask one quick question ("docs/solutions/ or elsewhere?") before the first creation; headless → use docs/solutions/ and state it in the final output.

Notes live in the user's repo, never outside it and never in the plugin directory, so they stay versioned with the code they describe.
