---
name: parallel-scopes
description: Split one multi-part task into independent scopes (FE, BE, docs, tests, config…) and run them in parallel with plain subagents in a single working tree — no Orca needed. Use this skill whenever the user wants several parts of a change done at once or asks to "chạy song song", "chia scope", "spawn nhiều agent", "FE/BE/docs cùng lúc", and the parts touch disjoint files. Skip it for sequential dependencies, bug fixes, small tasks, or scopes that overlap heavily; use `dag-build` instead when the user wants spec approval gates or supervised Orca workers.
---

# Parallel scopes

Parallel subagents buy wall-clock time, not savings: N agents cost roughly N× the tokens. Split only when the parts are genuinely independent and big enough to repay the spawn and integration cost.

## Decide whether to split

Split when every scope can finish without waiting on another's output and owns files no other scope touches. Stay with one agent when:

- a step needs the previous step's result (BE shape decides FE work),
- it is a bug fix — depth-first, one agent on one failure (`debug-root-cause`),
- the whole change is small, or scopes overlap in most files.

## Recipe

1. **Pin the contract first.** Anything two scopes must agree on — API schema, field names, types, file paths, CLI flags — is written down by you before any spawn. Agents that guess a shared contract diverge.
2. **Write the scope table.** One row per agent: scope, files or directories it **owns**, the contract it follows, and its done-condition. Ownership must not overlap. Shared files (types, config, lockfiles, manifests, registries) get exactly one owner, or are left for you to edit at integration.
3. **Spawn the whole wave in one message** — several Agent calls in a single turn run concurrently. Each prompt is self-contained: contract, owned paths, "do not edit outside your paths", and what to report back. Set `model` and `effort` per scope by difficulty (read/lookup low, routine edits medium–high, hard design high), following the user's or project's guidance if it names one. Read-only agents never need isolation.
4. **One working tree by default.** Use `isolation: "worktree"` only for an agent that may touch shared files or runs commands that write shared state (build, format-all, generators, git operations), or for risky work that must be discardable.
5. **Integrate yourself.** Wait for the whole wave, then check each report against its done-condition, resolve anything left on shared files, run the project's validation and tests, and read the combined diff. A scope that reports success is a claim, not a result.
6. **Report once.** Say which scopes ran, what each changed, what was verified and how, and anything skipped or left unresolved. For a long task, consult the advisor before declaring done if one is available.

## Failure handling

- A scope fails or returns a partial result: fix or re-run **that scope only**; do not restart the wave.
- Two scopes turn out to need the same file: stop, assign one owner, and re-run the loser rather than hand-merging blind.
- The contract turns out wrong mid-wave: stop the affected agents, fix the contract, then re-dispatch them.
