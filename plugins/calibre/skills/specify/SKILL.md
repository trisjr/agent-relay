---
name: specify
description: Calibre lifecycle state `specify` — for an issue labeled `state:specify`, turn the accepted request into acceptance criteria someone else could check, by delegating to the configured provider (OpenSpec, superpowers or the built-in fallback); on track `bug` it finds the reproduction and root cause instead, and on track `spike` it investigates and answers. Use for "viết spec cho issue 42", "làm rõ yêu cầu issue này", "specify #42", "tìm nguyên nhân bug ở issue 42" when the issue is on the lifecycle. It writes no code and chooses no implementation. Skip issues with no `state:*` label and ordinary requests to write a spec or debug something that do not involve the lifecycle.
argument-hint: "[issue number]"
---

# specify

Turn the request into acceptance criteria that someone other than the author could check. Most "done but wrong" results trace back to a criterion nobody could have tested.

**State:** `state:specify` · **Done by:** a provider, chosen by track · **Gate:** none here; the spec is approved together with the plan at G2 · **Next:** `calibre:plan`

## Before you start

The label script is `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh` ([lifecycle.sh](../run/scripts/lifecycle.sh) in the `calibre:run` skill); the commands below write it as `lifecycle.sh`.

Follow the [shared rules](../run/references/rules.md): read the config, run `lifecycle.sh show <n>`, and continue only if the task is in `specify`.

## On entry

Tracks `feature` and `bug`: create the task branch from the default branch and start the record ([record.md](../run/references/record.md)): `task.md` with the issue, track, size and the triage verdict copied from the issue. Track `spike` gets neither; its record is the issue.

## Do

| Track | Role | What comes back |
|---|---|---|
| `feature` | `specify` | requirements and scenarios |
| `bug` | `diagnose` | the reproduction and the root cause, with the evidence for it |
| `spike` | `explore` | findings and an answer |

Read the adapter for the configured provider — [openspec.md](../run/references/providers/openspec.md), [superpowers.md](../run/references/providers/superpowers.md) or [builtin.md](../run/references/providers/builtin.md) — and invoke it for this role only.

**Bug.** Diagnosis stops at a confirmed root cause; no fix is written in this state, however small. If the fix will change behavior that is specified or visible to users, also run the `specify` role for that changed behavior. Otherwise the criteria come from the bug itself: the reproduction no longer fails, plus whatever must keep working around it.

**Spike.** Post the findings and the answer as an issue comment headed `**Lifecycle · specify**`. Ask the user whether it settles the question. If it does, close as `answered` through `calibre:close`. If it revealed work to do, show the issues you would open for it and create them on a yes; each starts its own lifecycle at `intake`.

## Produce

`spec.md` in the record, normalized from whatever the provider wrote:

- **Problem**, **In scope**, **Out of scope**. If the provider's output has no out-of-scope statement, ask the user or propose one and have it confirmed; an unstated boundary is where scope creep enters.
- **Criteria**, each with a lifecycle ID (`AC-1`, …) and a pointer to its source in the provider's files.
- **Sources**: paths to the provider's own spec files.
- Track `bug`: **Reproduction** and **Root cause**.

Open questions that only the requester can answer are not guessed: post them, run `lifecycle.sh wait <n> needs-info`, and stop.

## Exit when

- Every criterion states something observable: a person could tell pass from fail without asking the author what was meant.
- Out of scope is written down.
- No open question remains.
- Track `bug`: the reproduction steps are exact, and the root cause comes with evidence that it is the cause and not merely nearby.

Then `lifecycle.sh state <n> plan`; the next skill is `calibre:plan`.

A provider that writes the spec and the plan in one call (see the adapters) does not let you skip this check. Check the spec against these criteria first and move the label; only then look at the plan.

## Leave differently when

- The request turns out to be a different size or kind than triage judged: `lifecycle.sh state <n> triage`, then `calibre:triage`.

## Do not

- Write or change code, including "just to see if it works".
- Choose an implementation. A criterion says what must be true, not how it is achieved.
- Let the provider continue into planning or coding on its own momentum. Return here first.
