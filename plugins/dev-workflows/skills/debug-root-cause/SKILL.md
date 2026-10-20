---
name: debug-root-cause
description: Investigate or fix a concrete test, build, CI, runtime, or performance failure using evidence and discriminating experiments. Use for regressions, stack traces, flaky tests, "test đỏ", or "lỗi chỉ fail trên CI". Respect diagnosis-only requests; when repair is authorized, carry it through verification. Skip new features and reviews without an existing failure.
---

# Debug root cause

Find what causes the observed failure, make only authorized changes, and report what the checks actually establish. Work inline; no subagent or special question tool is required.

## Scope and effort

- **Diagnosis only:** investigate and report evidence, uncertainty, and a proposed next step. Do not apply a repair, even an obvious typo. Keep scratch repros outside the working tree; do not modify tracked code or tests without authorization.
- **Find and fix:** the request authorizes investigation and repair within its stated scope. Reuse approval from earlier turns. Discovering the cause is not a new approval gate.
- Ask only for an unresolved decision that materially changes behavior, a public contract, data, risk, or scope, or an action lacking authorization. Prepare the concrete options and finish independent work first. A local fix mandate does not by itself authorize deployment, destructive operations, or production access.
- If there is no concrete failure yet, inspect available evidence or request the missing artifact. Handle features and healthy-diff reviews normally; do not automatically route to another skill.
- An obvious cause needs a short check → authorized correction → rerun, not a ledger or formal report. Add detail only when uncertainty, interacting causes, or repeated failed attempts make it useful.

Before changing files, inspect working-tree status and the relevant diff. Preserve pre-existing edits, including edits in the file being debugged. Avoid reset, checkout, stash, or cleanup that moves or discards others' work. Use an isolated scratch copy/worktree for destructive experiments or bisect; history inspection alone is often sufficient.

## Investigate with evidence

1. Run the reported failing path when feasible; record the command, input, environment, and actual result. Distinguish the reported failure from a broken test setup. Inspect relevant traces, callers, diffs, and boundaries to narrow where expected behavior first diverges.
2. Choose a plausible cause and a small experiment that distinguishes it from alternatives. State the predicted observation before running it; vary one factor when practical. Several edits in one causal repair are fine, but do not bundle unrelated guesses into one experiment.
3. Update the explanation from the result. Use [references/hypothesis-ledger.md](references/hypothesis-ledger.md) for uncertain or repeated investigations, and for flaky-test sampling. Keep the ledger in chat or scratch space unless a repo convention requires a file.

Confirm a cause only when evidence supports the causal mechanism and accounts for the relevant failures and nearby passes. A suspicious commit, a green rerun, or a failed patch alone does not establish a cause.

If reproduction is unavailable, use the evidence you have and label hypotheses as such. Logs or a deterministic local repro may still establish a mechanism; otherwise report the cause as **unconfirmed**. Missing services, credentials, or tools are verification limits, not proof about application behavior. Propose the smallest missing input, environment check, or privacy-safe instrumentation. Prepare or apply supported local changes when authorized; deployment and production probes still follow their own authorization.

Infrastructure and dependency failures are not automatically outside scope. Check whether the fault is in configuration, versions, or code you can repair. Escalate only the part requiring unavailable access, an external owner, or an unapproved change.

## Repair and verify

- Prefer an existing failing test or repro that exercises the actual bug; run it before and after the change when feasible. Add a regression test when coverage is missing and automation is practical. Do not duplicate coverage or require a new test for every fix.
- Fix the evidenced mechanism with the smallest coherent change. Preserve the intended contract; do not weaken assertions, skip the failing path, or simulate success to obtain green tests. A test may itself be wrong, but changing it needs evidence from the intended behavior.
- Retry, timeout, error handling, or a fallback can be a valid repair or **mitigation**. Check bounded cost, idempotency, terminal failure behavior, and visibility. Label containment as mitigation when the underlying cause remains; explain residual risk and how to detect recurrence. Do not silently turn failure into success.
- Rerun the original check and relevant nearby tests, scaled to the affected behavior. For flaky failures, prefer controlled timing/seed/order that exposes the mechanism, then a bounded representative sample. One green run is insufficient; record all failures/N, conditions, budget, and limits. See the reference for sampling assumptions; no fixed pass count proves absence of a flake.
- If only manual checking is possible, describe the exact steps and observed result. If checks cannot run, say **changed, verification blocked**, with the blocker and next command. Separate cause confidence from verification status; never claim results you did not observe.

## Reassess and stop

Keep three things distinct, including attempts from earlier turns or the user:

- **Refuted hypothesis:** a valid discriminating experiment contradicted its prediction.
- **Inconclusive experiment:** setup failed, evidence was insufficient, or the check could not distinguish explanations. It does not refute the hypothesis.
- **Failed fix:** the proposed repair did not resolve the original failure or introduced another. Reassess the mechanism and the implementation separately.

After repeated failures, pause patching and review the evidence and assumptions; do not simply stack another guess. Continue if a new observation supports a distinct, affordable experiment. There is no universal three-attempt cutoff. For expensive or repetitive work, set a time/run/cost budget before starting and honor explicit user limits. Stop the affected path when the budget is exhausted, experiments cease adding information, or a missing decision/access blocks progress. Report what remains unknown and the next useful step; an unknown cause is a valid outcome.

## Questions and handoff

Use a question tool only when available and allowed in the current mode; follow its schema. If it is asynchronous, a returned call or preselected option is not a reply. If no usable tool exists but chat is interactive, ask in plain text and end the turn before dependent work. Do not retry a denied tool. Timeout, empty answers, and missing tools grant no approval and do not establish headless mode.

Only an explicit caller/runtime indication of no reply channel makes the run non-interactive. Then finish authorized, independent work and report unresolved required decisions with affected actions **BLOCKED**; do not wait or choose a high-impact default. A headless run with a clear repair mandate can still fix and verify.

Report in proportion to the task: observed failure and cause (or uncertainty), evidence, change or proposal, actual verification, and remaining limits/next step. Keep it in chat by default. A simple verified fix can be a few lines; diagnosis-only work ends with findings, while authorized repair continues through verification.
