# Instruction block for the repo's instruction file

Add this to `CLAUDE.md`, `AGENTS.md` or the equivalent file the harness reads. Keep the two marker comments: a later re-check replaces what is between them.

Include the base section always, and the section for each provider that the config actually uses. Leave the others out; instructions about a library that is not installed are noise.

## Base

```markdown
<!-- calibre:start -->
## Task lifecycle

Work tracked on a GitHub issue with a `state:*` label follows the task lifecycle (`calibre` plugin). For such work:

- The issue's `state:*` label is the task's state. Only the lifecycle's script changes `state:`, `wait:`, `track:` and `resolution:` labels; never edit them by hand.
- The plugin's skills (`calibre:run`, and one `calibre:<state>` skill per state) decide which state runs next. Other workflow skills are invoked by them, for one state, and hand control back when that state's output exists.
- No skill merges, pushes, opens a pull request, closes an issue or deletes a branch for lifecycle work on its own. Those happen in the lifecycle's `handoff` and `closed` states.
- "Done" means the lifecycle's `verify` state recorded evidence for every acceptance criterion, not that a skill reported success.
<!-- calibre:end -->
```

## When `openspec` is configured

Insert before the end marker:

```markdown
- Specifications live in `openspec/changes/<change>/`. When a change exists for a task, it is the only spec: do not write a second one elsewhere.
- An OpenSpec change is archived only by the lifecycle's `handoff` state, and only for a task that is being delivered.
```

## When `superpowers` is configured

Insert before the end marker:

```markdown
- For lifecycle work, the lifecycle chooses which superpowers skill runs and when. Do not start `superpowers:brainstorming` for a task that already has a spec, and do not start a superpowers skill merely because it could apply.
- `superpowers:writing-plans` writes the execution plan from the approved spec and plan of record; its review pause is the lifecycle's plan approval, not an extra one.
- `superpowers:subagent-driven-development` and `superpowers:executing-plans` stop when the plan's tasks are committed. Do not continue into `superpowers:finishing-a-development-branch`.
- `superpowers:systematic-debugging` stops at a confirmed root cause when the lifecycle state is `specify`; the fix is made in `implement`.
```

## Why a block and not just the skill

superpowers states that user instruction files take precedence over its skills, and that skills override default behavior. The lifecycle's own skill is only another skill, so on its own it cannot stop a provider from following its built-in next step. Text in the instruction file can.
