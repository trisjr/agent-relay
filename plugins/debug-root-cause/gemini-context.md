# debug-root-cause

Apply to one concrete, existing test, build, CI, or runtime failure; keep one agent on the failure and investigate depth-first.
Ignore for new features, healthy-diff review, vague requirements, and open-ended research; route those to ordinary work, `parallel-review`, `clarify-requirements`, or `research-swarm` as appropriate.

- If `activate_skill` is available, activate the `debug-root-cause` skill and follow it.
- Right-size first: an obvious error can take minutes; uncertain failures need recorded evidence and a hypothesis ledger.
- Phase 1 — Reproduce & isolate: run the failing path, minimize it, or collect targeted boundary data when it cannot be reproduced.
- Phase 2 — Gather evidence: inspect traces backward, recent changes, environment, dependencies, and component boundaries before changing behavior.
- Phase 3 — Hypothesis ledger: rank testable causes; predict and run the smallest one-variable experiment, then record `confirmed`, `refuted`, or `inconclusive`.
- Phase 4 — Fix & regression: prove the bug with a failing test or automated repro script, repair the root cause, then run it green and run the related suite.
- Phase 5 — Aftermath: report Symptom, Root cause, Fix, and Prevention in chat; flag `unverified by automated test` if only manual verification was possible.
- Rule 1 — No fix before failing test: do not change production logic before a red check, except a one-step-obvious error named by its message; rerun that command afterward.
- Rule 2 — Never claim "fixed" without verification: require the original check and related suite green, plus a one-sentence root cause.
- Stop at 3 refuted hypotheses or 3 failed fixes: summarize the ledger and ask the user or question the architecture; never silently try a fourth.
- Escalate without force-fixing unpatchable dependency bugs; infra, vendor, quota, DNS, or CI-runner trouble; unapproved public-contract changes or data migrations; or races outside your control.
- In a headless run, a stop or escalation ends with a final status block containing the ledger summary, evidence, unresolved cause, and proposal.
