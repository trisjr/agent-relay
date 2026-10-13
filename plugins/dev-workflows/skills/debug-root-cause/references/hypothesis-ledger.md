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

## Short bug report

Keep this in chat unless the user requests a file or the repository has an established report location.

```text
Symptom: <what failed, where, and the repro command>
Root cause: <one sentence explaining why it failed and nearby cases did not>
Fix: <minimal change and commit pointer, if available>
Prevention: <which test or automated repro now catches it; include red/green and related-suite results>
```

If only manual verification was possible, append `unverified by automated test` and state exactly what was checked.
