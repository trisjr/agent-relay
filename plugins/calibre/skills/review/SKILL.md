---
name: review
description: Calibre lifecycle state `review` — for an issue labeled `state:review`, have the final, already-verified change reviewed independently by the configured review provider, with the diff, spec, plan and evidence but not the author's reasoning, and record findings with severity, location and a verdict. Use for "review issue 42", "review thay đổi của issue 42 trước khi bàn giao", or after fixes changed the code since the last review. The reviewer fixes nothing; requested changes go back through `implement` and `verify`. Skipped on track `chore`. Skip issues with no `state:*` label and ordinary code review requests that do not involve the lifecycle.
argument-hint: "[issue number]"
---

# review

Have the final change read by someone who did not write it. An author reviewing their own work mostly confirms what they already believed.

**State:** `state:review` · **Done by:** provider role `review` · **Gate:** none · **Next:** `calibre:handoff` · Skipped on track `chore`

## Before you start

The label script is `${CLAUDE_SKILL_DIR}/../run/scripts/lifecycle.sh` ([lifecycle.sh](../run/scripts/lifecycle.sh) in the `calibre:run` skill); the commands below write it as `lifecycle.sh`.

Follow the [shared rules](../run/references/rules.md): read the config, run `lifecycle.sh show <n>`, and continue only if the task is in `review`.

## On entry

Confirm `evidence.md` names the current code (see *Is the evidence still current?* in [record.md](../run/references/record.md)). If the code changed since, go back through `verify` first: reviewing unproven code wastes the reviewer.

## Do

Read the adapter for the configured `review` provider — [superpowers.md](../run/references/providers/superpowers.md) or [builtin.md](../run/references/providers/builtin.md) — and request a review of the whole change — the diff from the base branch to the task branch's head — at the current commit.

Give the reviewer the diff, the spec and plan files listed under `Sources` in `task.md`, the criteria index and `evidence.md`. Do not give it the implementer's conversation or reasoning: a reviewer who has been told why each choice was made tends to agree with it. If the provider can review in a fresh context or with a different model, use that.

Ask for findings with a location and a severity, and for a verdict.

## Produce

`review.md` in the record, committed. Copy the findings in; do not link to a transcript or a temporary file, because both disappear.

```markdown
## Reviewed at
3f2a91c, by superpowers:requesting-code-review
## Findings
| Severity | Location | Finding | Status |
|---|---|---|---|
| blocking | src/export.ts:88 | amounts are formatted with the server locale | open |
| non-blocking | src/export.ts:12 | helper duplicates `formatDate` in utils | deferred to follow-up |
## Verdict
changes requested
```

Map the provider's own severity scale onto two levels: `blocking` (must be fixed before handoff) and `non-blocking`. Check each finding before accepting it; a reviewer can be wrong, and a finding you can show is mistaken is recorded as `rejected` with the reason.

## Exit when

- The review covers the current commit.
- No finding is `blocking` and `open`.
- Every non-blocking finding is either fixed or listed for `handoff` as a follow-up.
- The state's summary is on the issue, unless `issue_comments` is `record`.

Then `lifecycle.sh state <n> handoff`; the next skill is `calibre:handoff`.

## When changes are requested

`lifecycle.sh state <n> implement --comment "Review: changes requested. <the blocking findings, one line each>"` (omit `--comment` when `issue_comments` is `record`), fix through `calibre:implement`, and come back through `calibre:verify`. The evidence is bound to the old code, so the changed code has to be proven again; then review the new commit.

A blocking finding against the plan itself — a design decision or the approach, not how it was built — is a plan problem: return to `implement` and from there to `plan`, so the revised part gets G2 again, rather than letting the fix rewrite the plan on its way through.

## Do not

- Let the reviewer fix what it finds. Fixes go through `implement` so they are verified like any other change.
- Skip this state because the provider reviewed each task while building. Those reviews saw pieces; this one sees the result.
- Accept a verdict without findings you can read.
