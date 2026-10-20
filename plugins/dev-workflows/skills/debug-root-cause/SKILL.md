---
name: debug-root-cause
description: Find the root cause of a concrete test, build, CI, runtime, or performance failure using evidence and discriminating experiments, and end with a diagnosis report and proposed fix. Use for regressions, stack traces, flaky tests, "test đỏ", "sao lại lỗi", or "lỗi chỉ fail trên CI". Repairs only when the user or a delegating spec already asked for one; otherwise the user decides. Skip new features and reviews without an existing failure.
---

# Debug root cause

Find what causes the observed failure and report what the evidence actually establishes. Whether to fix it is the user's call: finding the cause does not authorize a repair, and a proposal is not approval. Work inline; no subagent or special question tool is required.

## Who decides the fix

- **Default — diagnose and report.** A failure report, a question ("sao lại lỗi"), or a pasted trace with no repair request ends with the diagnosis report and a proposed fix. Do not apply it, even an obvious typo. Keep scratch repros outside the working tree; leave tracked code, tests, and the index unchanged.
- **Repair already mandated.** An explicit repair request ("tìm và sửa", "fix it"), an approval from an earlier turn, or a delegating spec from a coordinator or caller is the user's decision. Report the cause first, then repair and verify in the same turn; finding the cause is not a new approval gate. Reuse the mandate instead of asking again.
- **The mandate covers only what it named.** When the evidenced repair goes beyond that scope, changes behavior, a public contract, data, or risk, or needs a choice the user has not made, stop at the report and name the decision. A local fix mandate does not by itself authorize deployment, destructive operations, or production access.
- If there is no concrete failure yet, inspect available evidence or request the missing artifact. Handle features and healthy-diff reviews normally; do not automatically route to another skill.
- Keep effort proportional. An obvious cause needs a short check and a few-line report — plus correction and rerun only when mandated — not a ledger. Add detail only when uncertainty, interacting causes, or repeated failed attempts make it useful.

Before changing files, inspect working-tree status and the relevant diff. Preserve pre-existing edits, including edits in the file being debugged. Avoid reset, checkout, stash, or cleanup that moves or discards others' work. Use an isolated scratch copy/worktree for destructive experiments or bisect; history inspection alone is often sufficient.

## Investigate with evidence

1. Run the reported failing path when feasible; record the command, input, environment, and actual result. Distinguish the reported failure from a broken test setup. Inspect relevant traces, callers, diffs, and boundaries to narrow where expected behavior first diverges.
2. Choose a plausible cause and a small experiment that distinguishes it from alternatives. State the predicted observation before running it; vary one factor when practical. Do not bundle unrelated guesses into one experiment.
3. Update the explanation from the result. Use [references/hypothesis-ledger.md](references/hypothesis-ledger.md) for uncertain or repeated investigations, and for flaky-test sampling. Keep the ledger in chat or scratch space unless a repo convention requires a file.

Confirm a cause only when evidence supports the causal mechanism and accounts for the relevant failures and nearby passes. A suspicious commit, a green rerun, or a failed patch alone does not establish a cause.

If reproduction is unavailable, use the evidence you have and label hypotheses as such. Logs or a deterministic local repro may still establish a mechanism; otherwise report the cause as **unconfirmed**. Missing services, credentials, or tools are verification limits, not proof about application behavior. Propose the smallest missing input, environment check, or privacy-safe instrumentation.

Infrastructure and dependency failures are not automatically outside scope. Check whether the fault is in configuration, versions, or code that could be repaired locally. Escalate only the part requiring unavailable access, an external owner, or an unapproved change.

## Propose the fix

The proposal is what the user decides on, so make it concrete:

- Target the evidenced mechanism with the smallest coherent change, preserving the intended contract. Never propose weakening assertions, skipping the failing path, or simulating success. A test may itself be wrong, but say what evidence of the intended behavior shows it.
- Retry, timeout, error handling, or a fallback can be a valid repair or **mitigation**. Check bounded cost, idempotency, terminal failure behavior, and visibility. Label containment as mitigation when the underlying cause remains, with residual risk and how to detect recurrence.
- Name the check that would prove it: the existing failing test or repro, a regression test only when coverage is missing and automation is practical, nearby tests, and for flakes a controlled reproducer plus a bounded sample (see the reference).
- When options differ in behavior or risk, give 2–3 with a one-line consequence each, the recommended one first and labeled.

## Diagnosis report

The report is the handoff. Write only fields that carry information; an obvious cause fits in a few lines.

```markdown
## Diagnosis
Symptom: <command / input → actual result>
Cause: <mechanism> — confirmed | unconfirmed
Evidence: <observations and experiments that support or refute it>
Proposed fix: <change, or options with the recommended one first>
Verification plan: <checks that would prove the fix>
Open: <none | missing evidence or access | BLOCKED: decision + affected action>
```

Without a repair mandate, end here and offer to apply the proposed fix. With one, continue below.

## Repair when mandated

- Apply the proposed change within the mandate. Run the existing failing check before and after when feasible; add a regression test only when coverage is missing. Do not duplicate coverage or require a new test for every fix.
- Rerun the original check and relevant nearby tests, scaled to the affected behavior. For flaky failures, one green run is insufficient; record all failures/N, conditions, budget, and limits. No fixed pass count proves absence of a flake.
- If only manual checking is possible, describe the exact steps and observed result. If checks cannot run, say **changed, verification blocked**, with the blocker and next command. Separate cause confidence from verification status; never claim results you did not observe.
- If the repair turns out to need more than the mandate covers, stop and report instead of widening scope.

## Reassess and stop

Keep three things distinct, including attempts from earlier turns or the user:

- **Refuted hypothesis:** a valid discriminating experiment contradicted its prediction.
- **Inconclusive experiment:** setup failed, evidence was insufficient, or the check could not distinguish explanations. It does not refute the hypothesis.
- **Failed fix:** the proposed repair did not resolve the original failure or introduced another. Reassess the mechanism and the implementation separately.

After repeated failures, pause patching and review the evidence and assumptions; do not simply stack another guess. Continue if a new observation supports a distinct, affordable experiment. There is no universal three-attempt cutoff. For expensive or repetitive work, set a time/run/cost budget before starting and honor explicit user limits. Stop the affected path when the budget is exhausted, experiments cease adding information, or a missing decision/access blocks progress. Report what remains unknown and the next useful step; an unknown cause is a valid outcome.

## Questions and handoff

Use a question tool only when available and allowed in the current mode; follow its schema. If it is asynchronous, a returned call or preselected option is not a reply. If no usable tool exists but chat is interactive, ask in plain text and end the turn before dependent work. Do not retry a denied tool. Timeout, empty answers, and missing tools grant no approval and do not establish headless mode.

Only an explicit caller/runtime indication of no reply channel makes the run non-interactive. Then finish authorized, independent work and report unresolved required decisions with affected actions **BLOCKED**; do not wait or choose a high-impact default. A headless run with a clear repair mandate can still fix and verify; without one it ends with the report.

Keep the report in chat by default. Diagnosis without a mandate ends with the report and the offer to fix; a mandated repair ends with the report, the change, and the actual verification.
