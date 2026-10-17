# Hypothesis ledger

Copy this table for an uncertain failure. Write **Expected if true** before running each experiment; change one variable, then fill in `Outcome` (`confirmed`, `refuted`, or `inconclusive`) and `Learning`. Rank plausible cheap tests first, and revise the ranking when evidence changes.

| # | Hypothesis | Why plausible | Smallest experiment | Expected if true | Outcome | Learning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | <testable cause> | <observation it explains> | <one-variable check> | <specific result predicted before the check> | <confirmed/refuted/inconclusive> | <what the result changes> |

## Filled example

Symptom: A date assertion fails on CI but passes locally near midnight. The exact input and runner command are held constant.

| # | Hypothesis | Why plausible | Smallest experiment | Expected if true | Outcome | Learning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | CI resolved a different date library version. | The failure appeared after a fresh install. | Compare lockfile and installed version on both hosts. | CI has a different resolved version. | refuted | Versions match; dependency drift does not explain the difference. |
| 2 | The formatter uses the host timezone instead of the required UTC timezone. | CI uses UTC; local machine uses another timezone, and only a midnight-boundary input fails. | Run the same assertion locally with `TZ=UTC`, then with the local timezone. | The output changes with `TZ` and reproduces the CI mismatch. | confirmed | The implicit timezone explains the failing CI case and the nearby passing dates. |

Confirm the root cause against all relevant observations and non-observations before editing the code.

## Diagnosis report

Post this in chat after the root cause is confirmed, then wait for the user's approval before editing anything. Keep it in chat unless the user requests a file or the repository has an established report location.

```text
Symptom: <what failed, where, and the repro command>
Root cause: <one sentence explaining why it failed and nearby cases did not>
Evidence: <key observations and the ledger outcome that confirmed it>
Proposed fix: <where, the minimal change, callers affected>
Proposed red test: <the test or repro script that should fail for this reason>
Risks / unverified: <what the fix may affect or what could not be checked>
```

Mark an escalated report `outside-our-control`.

## After the fix

Once the user approved and Phase 5 finished, add only a short confirmation instead of rewriting the report:

```text
Fixed: <root cause in one sentence>
Red → green: <commands, and the test now guarding it>
Related suite: <command and result>
```

If only manual verification was possible, append `unverified by automated test` and state exactly what was checked.
