# Evidence playbook

Use the smallest command that distinguishes the current hypotheses. Capture the failing command, revision, relevant output, and the result; redact secrets before sharing logs or environment snapshots. Commands below are examples to adapt to the repository's runner and platform.

| Technique | Reference command or move | Failure shape it fits |
| --- | --- | --- |
| Read a stack trace backward | Start at the throw/crash line; find the first in-repo frame, then inspect its callers and values in reverse call order. Keep file and line numbers. | Runtime crash with a long library-heavy trace. |
| Increase runner detail | `<runner> <failing-test> --verbose` (or that runner's equivalent); save both stdout and stderr. | A terse test or build error hides the first bad assertion or subprocess. |
| Inspect recent changes | `git diff -- <path>`; `git log --since='2 weeks ago' -p -- <path>`; `git log --follow -p -- <file>`; `git log -S'needle' -p -- <path>` | A regression after a known edit, a renamed file, or the introduction/removal of a value (`-S` pickaxe). |
| Bisect a regression | `git bisect start`; `git bisect bad HEAD`; `git bisect good <known-good>`; `git bisect run <script>`; inspect the first-bad commit; `git bisect reset`. A script exits `0` for good, `1` for bad, `125` to skip an untestable revision. | “It worked before” with good and bad revisions and a deterministic repro. |
| Compare environments | `diff <(env \| sort) <(cat ci-env.txt \| sort)`; also compare OS, timezone, locale, runtime version, flags, and config. Save only redacted snapshots. | CI fails while local passes, or only one host fails. |
| Compare dependency resolution | `git diff <known-good>..HEAD -- <lockfile>`; compare the installed versions on both hosts. | Failure began after an install, lockfile update, or runtime upgrade. |
| Trace system calls | Linux: `strace -f -o trace.log <command>`; macOS: `sudo dtruss -f <command>` where permitted. Inspect the first relevant failed open, network, or permission call. | Suspected filesystem, process, network, or permission boundary; application logs are insufficient. |
| Instrument component boundaries | Log a request/correlation ID and sanitized input/output shape at adjacent layers; move the probe toward the first layer that changes a correct value. Remove temporary probes after use. | Data is correct at entry but wrong downstream; a layer boundary is unclear. |
| Measure intermittent failures | Run the same isolated command at least five times, e.g. `for i in 1 2 3 4 5; do <failing-command> \|\| echo "failed run $i"; done`; retain each failing log and report failures/N. | Flaky test or timing-dependent runtime failure. |
| Control nondeterminism | Set a fixed seed and timezone, e.g. `SEED=123 TZ=UTC <failing-command>`; freeze time with the runner's fake clock and fix test ordering or parallelism one variable at a time. | Random input, date boundary, timer, or ordering-dependent failure. |

When a failure cannot be reproduced, collect only the boundary data needed to split the leading hypotheses. Do not change production behavior on an untested guess.
