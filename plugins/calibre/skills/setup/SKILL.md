---
name: setup
description: Set up or re-check the Calibre task lifecycle in a repo — detect which workflow libraries are installed (OpenSpec, superpowers), map each lifecycle role to one of them or to the built-in fallback, record the policies, create the lifecycle's issue labels, and offer the instruction block that keeps those libraries inside one state at a time. Use for "set up calibre", "cài calibre cho repo này", "set up the task lifecycle", "cài task lifecycle cho repo này", "cấu hình lifecycle", "dùng OpenSpec cho spec và superpowers cho code", when a lifecycle skill reports that `.calibre/config.json` is missing, and after installing, upgrading or removing one of the libraries. Skip running a task; that is `calibre:run` or the skill for the task's state.
---

# Lifecycle setup

The lifecycle standardizes the states a task goes through and leaves the work inside each state to whichever library the team prefers. Setup is where that choice is made once, written down, and made visible on the repo's issues. It is safe to run again: it re-detects, shows what changed, and rewrites only what the user agrees to.

Everything setup writes is shown first. Three of its steps act outside the working tree or change standing instructions — creating labels, writing the config, editing the repo's instruction file — and each waits for its own yes.

## 1. Preflight

Check, and stop with a plain explanation if any fails:

- The directory is a git repo with a GitHub remote.
- `gh auth status` succeeds. Labels and issues are the lifecycle's state, so without `gh` it cannot run.
- If `.calibre/config.json` already exists, read it: this is a re-check, and its current values are the starting point instead of the defaults.

## 2. Detect the libraries

Use the "Is it available?" section of each adapter in `calibre:run`:

- [OpenSpec](../run/references/providers/openspec.md)
- [superpowers](../run/references/providers/superpowers.md)

Report what you found and how you know — a file in the repo, a command's output, a skill present in this session. Say plainly when something cannot be seen from here: a library installed per user leaves no trace in the repo, so "not detected" is not "not installed". Report the version when it is discoverable, and flag one the adapter was not written for.

## 3. Propose the mapping

Six roles each get a provider. Offer the preset that matches what was detected, as one recommendation, and ask only whether to adjust it. Walking the user through six separate questions makes a simple choice feel like a form.

| Detected | `specify` | `plan` | `implement` | `review` | `diagnose` | `explore` |
|---|---|---|---|---|---|---|
| OpenSpec and superpowers | openspec | openspec | superpowers | superpowers | superpowers | openspec |
| OpenSpec only | openspec | openspec | openspec | builtin | builtin | openspec |
| superpowers only | superpowers | superpowers | superpowers | superpowers | superpowers | builtin |
| neither | builtin | builtin | builtin | builtin | builtin | builtin |

Two constraints apply when the user adjusts it:

- **`specify`, `plan` and `implement` work best from one library**, or from the OpenSpec-to-superpowers pairing in the first row. Each library's implementation step reads its own plan format. Other mixes inside those three roles are untried: allow them, and say so.
- **A `plan` provider that differs from the `implement` provider costs a second plan file.** superpowers executes only a plan in its own format, so the pairing in the first row derives an execution plan from OpenSpec's task list, and `handoff` deletes it before the pull request opens. Say this when proposing the pairing; one library for both roles avoids it.
- **`review` is free.** It only needs a diff, so any provider can review any other's work.

A role can only be mapped to a provider whose adapter lists that role; the adapters name what each does not provide.

## 4. Confirm the policies

Show these with their defaults and change only what the user asks to change. [references/config.md](references/config.md) explains each one.

| Policy | Default |
|---|---|
| A request with no issue | ask, then create the issue |
| The handoff is accepted when | the pull request is merged |
| Merge the spec back | on the task branch, before the pull request |
| The plan of record | the `plan` provider's task list |
| Failed fix rounds before stopping | 3 |
| Issue comments | a short summary as each state finishes, plus gate decisions and moves back |
| Task branch prefix | `task/` |

Then ask the one consent the lifecycle needs up front: may it change labels and post its comments on issues that are put on the lifecycle? Record the answer as `consent.issue_writes`. Without it, the lifecycle skills will ask at every label change, which is workable but slow; say so and respect a no.

## 5. Write the config

Show the complete `.calibre/config.json` and write it on a yes. Mention that it should be committed so every session and teammate uses the same mapping; committing is the user's call.

## 6. Create the labels

Run `scripts/lifecycle.sh labels` from the `calibre:run` skill (in Claude Code: `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh labels`) and show the list: 23 labels in four groups, `state:`, `wait:`, `track:`, `resolution:`. Explain that creating them changes the repository on GitHub for everyone, and that an existing label with the same name keeps its issues but gets this color and description.

On a yes, run `lifecycle.sh init`, calling the script by its path with the working directory still in the repo being set up: `gh` creates the labels in the repository of the directory you are in. On a no, write nothing and note that no lifecycle skill can move a task until the labels exist.

## 7. Offer the instruction block

Libraries such as superpowers are built to run their whole workflow and to be consulted before anything else. A skill cannot overrule another skill, but they do defer to the repo's instruction file. [references/instruction-block.md](references/instruction-block.md) holds a short block that states the lifecycle's boundaries, with variants per provider.

Find the repo's instruction file (`CLAUDE.md`, `AGENTS.md`, or whichever the harness in use reads). Show the block trimmed to the providers actually configured, and where it would go. Add it on a yes; on a re-check, replace the existing block between its markers instead of adding a second one. If the user declines, tell them the one practical consequence: provider skills may run past the state they were invoked for, and the lifecycle skills will have to hold the line turn by turn.

## 8. Report

Close with what is now true, in a few lines: the mapping, the policies that differ from the defaults, whether the labels exist, whether the instruction block is in place, and anything that could not be verified. Then name the next step: `calibre:intake` for a new request, or `calibre:run` with an issue number to carry a task through its states.

Do not start a task from here. Setup that quietly turns into work on an issue is a surprise.
