---
name: debug-root-cause
description: Debug a concrete, existing failure by evidence instead of guesses — reproduce it, test hypotheses one at a time, report a diagnosis with a proposed fix and wait for the user's approval, then fix only behind a failing test. Use this skill for any actual failure — a red test, a build or CI failure, a runtime error or stack trace, a flaky test, a "worked before, broken now" regression, "test đỏ", "lỗi chỉ fail trên CI", "sao lại lỗi" — before proposing or writing any fix. Skip it for net-new features, refactors without a failure, breadth-first investigation (research-swarm territory), review of a healthy diff, and vendor or infrastructure outages, which you escalate instead.
---

# Debug root cause

Treat debugging as the scientific method applied to one failure. Each speculative fix changes the system before you know what failed and makes the next observation less trustworthy, so keep one agent on one failure, gather evidence depth-first, and record what each experiment taught you. The investigation ends in a diagnosis the user approves; code changes come after.

## Right-size first

- No existing failure — "export never supported UTF-16; make it work" — is feature work. Handle it normally, without this skill.
- Broad investigation with no concrete failing artifact goes to `research-swarm`, a healthy diff to `parallel-review`, unclear intended behavior to `clarify-requirements`. When that skill isn't installed, handle it as a single agent.
- A one-step cause named by the error itself (a typo, a missing import) skips the ledger, Rule 0, and Rule 1: fix it, rerun the failing command, and report the result in a line or two.
- A failure the evidence already places outside your control — a vendor incident, an infrastructure outage — goes straight to Stop rules & escalation.
- A concrete performance regression is in scope, with a repeatable benchmark as the repro.

Everything else follows the phases below, with a written ledger proportional to how uncertain the cause is.

## Rules

- **Rule 0 — No edits before approval.** The user owns the choice of fix, its scope, and any contract it touches, and a confirmed diagnosis often changes what they want. So Phases 1–3 change no production code or committed tests, and Phase 4 ends with a report and a wait unless a Phase 4 Orca fix mandate applies. Investigation aids are fine — a scratch repro kept outside the committed tree, or a local log probe reverted before the report — as long as you list them under Evidence.
- **Rule 1 — No fix before failing test.** After approval, run a test or automated repro that fails for the reported reason before changing production logic; without it you can't show the fix addressed this bug.
- **Rule 2 — Never claim "fixed" without verification.** "Fixed" means the original check is green, the related suite passes, and you can state the root cause in one sentence. Short of that, say exactly what is unverified.
- **Rule 3 — One hypothesis, one experiment, one change.** Write the expected result first and change one variable, so the outcome can be attributed.
- **Rule 4 — Symptom patches are failure.** A try/catch, retry, or display-side workaround hides the failure without explaining it. Trace through callers to the shared point that produces the wrong behavior and fix it there.

## Phase 1 — Reproduce & isolate

Run the exact failing command, record what you ran and saw, and narrow it to the smallest case that still fails. For an intermittent failure, a passing rerun doesn't erase it: repeat about 3/p times for failure rate p (≈15 for a 1-in-5 flake, never fewer than five), report failures/N, and pin seed, time, and ordering until it fails reliably.

If you can't reproduce, decide what data would distinguish the hypotheses and propose narrow instrumentation at the suspected boundary, with sensitive values excluded. Shipping it to the failing environment is an edit, so it goes through the Phase 4 report.

## Phase 2 — Gather evidence

Collect observations that distinguish competing explanations, including what still works; [the evidence playbook](references/evidence-playbook.md) lists techniques by failure shape. Redact secrets from anything you share.

## Phase 3 — Hypothesis ledger

Track testable causes and their experiments in [the hypothesis ledger](references/hypothesis-ledger.md). A root cause is confirmed when it explains every relevant observation and non-observation: why this case fails, why nearby cases pass, why the environment or timing matters. A correlated commit is evidence, not yet a cause.

## Phase 4 — Diagnosis report & gate

When a cause is confirmed, a stop rule or escalation applies, or Phase 1 ended without a repro, post this report in chat, suggest the next step, and wait for the user:

```text
Symptom: <what failed, where, and the repro command>
Root cause: <one sentence explaining why it failed and nearby cases did not>
Evidence: <key observations, the ledger outcome that confirmed it, scratch repros/probes used>
Proposed fix: <where, the minimal change, callers affected>
Proposed red test: <the test or repro script that should fail for this reason>
Risks / unverified: <what the fix may affect or what could not be checked>
```

Without a repro, Root cause reads `unconfirmed` plus the leading hypotheses, Proposed fix is the instrumentation plan, and Proposed red test is what the collected data would decide. If the cause is clear but the correct behavior isn't, ask in the report (or use `clarify-requirements`) rather than choosing one. Keep the report in chat unless the user asks for a file or the repository has a convention for one.

A dispatched Orca worker whose spec orders a fix treats the spec as approval and continues to Phase 5. Without a fix mandate, a headless run or worker ends with this report as its final status block.

## Phase 5 — Fix & regression

After approval, go **red** (failing because of the bug, not the test setup), make the approved change and nothing beyond it, then go **green** and run the related suite. For a flake, green means about 20 consecutive passes for a 1-in-5 flake (0.8²⁰ ≈ 1%); report N. If the fix fails, count a failed fix and return to Phase 3 rather than stacking another patch.

Confirm briefly, without rewriting the diagnosis:

```text
Fixed: <root cause in one sentence>
Red → green: <commands, and the test now guarding it>
Related suite: <command and result>
```

If only manual verification was possible, say "unverified by automated test" and what you checked.

## Stop rules & escalation

Count refuted hypotheses and failed fixes separately, including attempts the user or an earlier session already made. At three of either, stop before a fourth: summarize the ledger, question your model of the system or its architecture, and ask for direction — more attempts on a wrong model only add noise.

Escalate rather than force a fix when the cause is an unpatchable dependency bug; infrastructure, vendor, quota, DNS, or CI-runner trouble; a repair that needs an unapproved public-contract change or data migration; or a race outside your control. Mark the report `outside-our-control` and carry the evidence, ledger outcomes, remaining uncertainty, and a next step such as a controlled workaround plus an upstream ticket. Faking a success to make tests pass hides the outage; it is not a workaround.

"No root cause" is a conclusion only after the ledger rules out software you control. Then propose containment, not a fix: a bounded timeout or retry plus a targeted log, with a way to tell whether the failure recurs.

With no one to answer — a headless run or subagent — a stop or escalation ends in a final status block: ledger summary, evidence, unresolved cause, and proposal.

As a dispatched Orca worker (a live injected preamble with executable, handle, capability, Task ID, and Dispatch ID), the coordinator answers instead, and a local question UI would go unseen. Send the same status block as a stop question through the preamble's `ask` command copied verbatim (on timeout, resume the same message ID rather than asking again), or as an `escalation` message built exactly as `<preamble executable> skills get orchestration --reference references/worker-contract.md` shows. Follow the coordinator's reply; if the work ends unresolved, send `worker_done` with `--outcome failed`, not `succeeded`.
