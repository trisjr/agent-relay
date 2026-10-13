---
name: debug-root-cause
description: Debug a concrete, existing failure with method instead of guesses — reproduce and isolate it, gather evidence from logs, traces, diffs and environment, run a hypothesis ledger with the smallest possible experiments, fix the root cause only after a failing test proves it ("red"), verify the fix turns green without breaking the suite, and record a short bug report. Use this skill for any actual failure — a red test, a build or CI failure, a runtime error or stack trace, a flaky test, a "worked before, broken now" regression, "test đỏ", "lỗi chỉ fail trên CI", "sao lại lỗi" — before proposing or writing any fix. Skip it for net-new features, refactors without a failure, open-ended investigation or research breadth-first (that is research-swarm territory), code review of a healthy diff, and problems outside the codebase's control such as vendor or infrastructure outages, for which you escalate and stop.
---

# Debug root cause

Treat debugging as the scientific method applied to one failure. A fix-try loop changes the system before you know what failed, so each failed guess makes the next observation less trustworthy. Keep one agent on one concrete failure, pursue evidence depth-first, and preserve what each experiment taught you.

## 0. Right-size first

| Route | Use it when | Action |
| --- | --- | --- |
| Skip | There is no existing failure. “Export never supported UTF-16; make it work” is a feature request disguised as a bug. | Handle the feature or refactor as ordinary work. For an outage outside your control, escalate immediately. |
| Debug | A specific test, build, CI job, runtime path, benchmark, or reported behavior has failed. | Follow the phases below with one agent. |
| Route elsewhere | The question needs broad, independent research; a healthy diff needs review; or the intended behavior is unclear. | Use `research-swarm`, `parallel-review`, or `clarify-requirements`, respectively; when that skill is not installed, handle it as a single agent. |

**When not to use:** Do not turn open-ended investigation into a debugging swarm. Do not use this for ongoing monitoring, load testing, or deep profiling. For a concrete performance regression, use a repeatable benchmark as the repro. Do not force a code patch for vendor, infrastructure, DNS, quota, or runner failures; follow escalation.

Keep ceremony proportional to difficulty. If an error message points directly to a missing import or typo, confirm that one-step cause and rerun the failing command within minutes; no written ledger is needed. For uncertain failures, retain the observations and ledger so each attempt has a reason.

## The Iron Rules

- **Rule 1 — No fix before failing test.** Before changing production logic, run a test or automated repro script that fails for the reported reason. The sole exception is a one-step-obvious correction named by the error itself, such as a missing import or typo; still rerun the command afterward.
- **Rule 2 — Never claim "fixed" without verification.** Claim completion only after the original failing check turns green, the related suite passes, and you can state the root cause in one sentence. Otherwise name exactly what remains unverified.
- **Rule 3 — One hypothesis, one experiment, one change.** Write the expected result before each experiment. Change one variable, inspect its outcome, and only then decide the next step. Never bundle speculative fixes.
- **Rule 4 — Symptom patches are failure.** Trace the failure through its callers and boundaries. Repair the cause at the shared point that produces the wrong behavior; a workaround at the display point alone does not count as a fix.

## Phase 1 — Reproduce & isolate

**Entry:** You have a concrete failure report: a failing command or test, a stack trace, or observable wrong behavior.

**Work:** Run the exact failing command when possible. Record its invocation, input, output, and environment. Narrow it to the smallest test case or input that still fails, without erasing the conditions that trigger it.

| Case | Isolation move |
| --- | --- |
| Consistent failure | Run the named test or path directly; minimize input and keep the failing assertion or error. |
| Environment drift: CI fails, local passes | Compare environment variables, OS, runtime and dependency versions, timezone, locale, and test ordering. Recreate one difference at a time locally. |
| Intermittent or flaky failure | Run at least five repeats (N ≥ 5); record failures/N and failing logs. Fix the seed, time, and ordering where possible so the repro becomes repeatable. A passing rerun does not erase a failure. |
| Stack trace only | Start at the crash point, locate the first frame in this repository, then read callers backward from that frame. Do not infer root cause solely from a library frame. |

**Exit:** Either record an exact repro command with stable failure or measured frequency, or enter a data-collection branch when reproduction is unavailable. In that branch, add narrow logs or instrumentation at the suspected component boundary, state what data would distinguish hypotheses, and wait for evidence. Do not edit behavior by guess.

## Phase 2 — Gather evidence

**Entry:** You have a repro or a scoped data-collection plan from Phase 1.

**Work:** Collect observations before changing logic. Use the six sources that fit the failure:

1. **Trace and logs:** Read backward from the crash or wrong output; record the in-repo frame, file, line, input, and error.
2. **Recent changes:** Inspect `git diff` and `git log -p` around the failing path. Separate the first bad behavior from unrelated edits.
3. **Regression history:** If it worked before, bracket known good and bad revisions with `git bisect`; automate the check with `git bisect run <script>` when feasible.
4. **Environment and config:** Compare failing and passing variables, OS, timezone, locale, flags, and configuration values; protect secrets in shared output.
5. **Versions and dependencies:** Compare runtime versions and lockfile changes, not merely declared version ranges.
6. **Component boundaries:** Log or inspect values entering and leaving successive layers to find the first boundary where correct data becomes wrong.

Use [the evidence playbook](references/evidence-playbook.md) for commands and failure shapes. Prefer evidence that distinguishes competing explanations; avoid collecting logs without a question.

**Exit:** Write down the observations and non-observations you can point to, including exact commands or traces. No production behavior has changed.

## Phase 3 — Hypothesis ledger

**Entry:** You have observations from Phase 2, including what still behaves correctly.

**Work:** List testable causes in [the hypothesis ledger](references/hypothesis-ledger.md). Rank by likelihood × cost-to-test: pursue a plausible cheap experiment first, especially when likelihoods are uncertain. For each row, identify the smallest experiment that changes one variable and write **Expected if true** before running it. Record the actual outcome as `confirmed`, `refuted`, or `inconclusive` and what you learned. Refuted hypotheses should change the ranking or suggest a better candidate; inconclusive experiments need a sharper measurement.

Do not replace the ledger with “probably X” followed by a code edit. A confirmed root cause explains every relevant observation **and non-observation**: why this case fails, why nearby cases pass, and why the timing or environment matters. A correlation with a changed commit is evidence, not yet a causal explanation.

**Exit:** Identify one confirmed root cause, or invoke the stop rules or escalation below. Do not promote an untested guess into a fix.

## Phase 4 — Fix & regression

**Entry:** One root cause is confirmed and the intended behavior is known.

**Work:**

1. Write or confirm the smallest failing test for that cause. Run it **red** and check that it fails because of the bug, not a broken test setup. If no test framework exists, use an automated repro script. For a performance regression, use a repeatable benchmark.
2. Make the smallest production change at the root cause. Inspect callers so the shared path is fixed. Avoid “while I'm here” edits.
3. Rerun the same check **green**, then run the related suite. Preserve the before/after commands and results.
4. If the fix fails or reveals a different behavior, count one failed fix, update the ledger, and return to Phase 3. Do not stack another speculative patch on top.

Use manual verification only as a last resort when no automated check can run. In that case, report **“unverified by automated test”** and do not imply the automated red → green proof exists.

**Exit:** State the root cause in one sentence and show that the failing check and related suite are green. If verification cannot meet that bar, report the limit accurately rather than claiming an unqualified fix.

## Stop rules & escalation

Count refuted hypotheses and failed fixes separately. At **3 refuted hypotheses or 3 failed fixes**, stop before a fourth attempt. Summarize the ledger and question the current model of the system or its architecture; ask the user for direction when someone can answer. A silent fourth attempt is prohibited.

Escalate without force-fixing when the cause is an unpatchable dependency bug; infrastructure, vendor, quota, DNS, or CI-runner trouble; a correct repair requires an unapproved public-contract change or data migration; or a race lives in a layer outside your control. Carry the observed failure, repro or collection plan, evidence, ledger outcomes, remaining uncertainty, and a proposed next step such as a controlled workaround plus an upstream issue or ticket. Mark the short bug report `outside-our-control`.

“No root cause” is rare. Use it only after the ledger rules out software you control. Then propose bounded error handling and observability, such as a timeout, retry, or targeted log, with a way to verify whether the unexplained failure recurs. Do not label the problem mysterious and close it.

In a headless run or subagent with no one to answer, a stop or escalation ends in a full final status block: ledger summary, evidence, unresolved cause, and proposal. Do not wait indefinitely or silently proceed.

As a dispatched Orca worker (a live injected preamble with executable, handle, capability, Task ID, and Dispatch ID), the coordinator is the one who answers, so this replaces the headless ending above — never open a local question UI nobody can see. Put that same status block in a stop question sent through the preamble's `ask` command, copied verbatim (on timeout, resume the same message ID; never ask again), or in an `escalation` message built exactly as `<preamble executable> skills get orchestration --reference references/worker-contract.md` shows. Follow the coordinator's reply; if the work ends unresolved, send `worker_done` with `--outcome failed`, never `succeeded`.

## Phase 5 — Aftermath

**Entry:** The fix has been verified, or the verification limit has been stated explicitly.

**Work:** Write a short bug report using [the report template](references/hypothesis-ledger.md): Symptom; Root cause in one sentence; Fix with a commit pointer when available; Prevention naming the test that now catches it. Include the red and green evidence and related-suite result. If verification was manual, include **“unverified by automated test”**.

Keep the report in chat by default. Write a file only when the user asks or the repository already has a clear convention for one. Do not create a new solution ledger by habit.

**Exit:** The user has the report in chat or in the requested conventional file, with any remaining limitation visible.

## Anti-patterns

- Patching the visible symptom while the shared producer still emits wrong data.
- “Try this and see” without a prediction or a single-variable experiment.
- Bundling several changes, then running one test with no way to attribute the result.
- Skimming a trace and blaming the first library frame.
- Rerunning a flaky test until it passes, then closing it.
- Calling a fix done before the original check and related suite run green.
- Continuing after three refuted hypotheses or three failed fixes without stopping.
- Force-fixing a vendor or infrastructure failure with an unrelated code change.

**Red flags — STOP**

| Thought | Return to |
| --- | --- |
| “Fix it quickly; investigate later.” | Phase 1: reproduce, then Phase 2: evidence. |
| “It must be X; I'll change the code and see.” | Phase 3: write the prediction and smallest experiment. |
| “The flaky test passed on rerun, so we're done.” | Phase 1: measure frequency and control seed, time, and ordering. |
| “This patch seems fine; the suite can wait.” | Phase 4: run the original check and related suite. |
| “Three attempts failed; one more might work.” | Stop rules & escalation: summarize and ask or escalate. |
