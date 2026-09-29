---
name: gate-review
description: Review jev-gate shadow-mode data and decide, with the user, whether to switch the gate to enforce mode, narrow a lock rule, tune a threshold, or build output pruning. Use when the user asks how jev-gate is doing, what it would have asked, reused, or allowed, whether to enable enforce mode, or whether large tool outputs justify pruning.
---

# Review jev-gate shadow data

jev-gate is a hook, not a tool: it runs on every Bash and MCP call without the agent asking. It runs a lock rule check, then a read-only fast path, a REUSE ledger, and TypeSafe Jev judgments for the gray zone. In `shadow` mode (the default), only lock rules act, and each lock hit becomes an `ask`. Everything else is logged as the decision `enforce` mode would have made. This skill turns that log into evidence the user can decide on.

## Rules

- **The user decides, you report.** Never switch the mode, edit thresholds, or change lock rules on your own. Show the numbers and the rows behind them, recommend, then wait.
- **The log is sensitive.** It holds command text, with heredoc bodies stripped and secret-looking values redacted, but it is still sensitive. Summarize it in the conversation. Never send it to an external service, Jev included.
- **Say what the sample can't show.** Fewer than 200 gated calls, or data from a single session, is not enough to switch modes; say so instead of extrapolating.

## Data

Default location: `~/.local/state/jev-gate/sessions/<session_id>.jsonl`, or `$JEV_GATE_STATE_DIR/sessions/` when that variable is set. There is one append-only JSONL file per session. Events:

- `gate`: written by the PreToolUse hook before the call runs.
  - Fields: `id` (the tool_use_id), `ts`, `agent`, `tool`, `action`, `rule`, `fast`, `fp`, `source`, `reuse`, `decision`, `why`, `applied`, `mode`, `harness`.
  - `source` is one of `lock`, `fastpath`, `ipc` (the Orca coordinator protocol, not sent to Jev), `secret` (not sent to Jev), `no-key`, or `jev`.
  - `decision` is one of `ask`, `reuse`, `allow`, `proceed`, or `pending`. `pending` means a detached shadow judge was still to decide.
- `judge`: the detached Jev judgment that shadow mode makes for a `pending` gate. It has the same `id`, plus `judgments` (the Nouls `read_only`, `destructive`, `outward`, `external_state`), `decision`, `latency_ms`, and `error`/`status` when the call failed open.
- `out`: written by PostToolUse and PostToolUseFailure with the same `id`. It holds `bytes`, `sha` (a hash of the output, never the output itself), `ok`, and `dur_ms`.
- `reset`: compaction or `/clear`. REUSE ignores everything before it; this review does not.

## Steps

1. Build the merged view once. Each judge is folded into its gate, and each output is attached as `.out`:

   ```sh
   M="${TMPDIR:-/tmp}/jev-gate-merged.json"
   cat "${JEV_GATE_STATE_DIR:-$HOME/.local/state/jev-gate}"/sessions/*.jsonl | jq -s '
     (map(select(.ev == "judge")) | INDEX(.id)) as $j
     | (map(select(.ev == "out")) | INDEX(.id)) as $o
     | map(select(.ev == "gate")
         | . + (($j[.id] // {}) | {decision, why, judgments, latency_ms, error, status, model}
                | with_entries(select(.value != null)))
         | .out = $o[.id])' > "$M"
   ```

2. Measure volume. Count rows by source, and by decision together with how many were applied:
   - `jq -c 'group_by(.source) | map({source: .[0].source, n: length})' "$M"`
   - `jq -c 'group_by(.decision) | map({decision: .[0].decision, n: length, applied: (map(select(.applied)) | length)})' "$M"`

   A large `no-key` count means Jev never ran; stop and tell the user how to set the key.

3. Check lock hits for false positives:
   - `jq -r '.[] | select(.source == "lock") | [.rule, .action] | @tsv' "$M"`
   - Group the hits by rule. A rule that mostly fires on harmless commands, such as `git push` quoted inside a commit message, is a candidate for narrowing. The fix is a tighter regex in `hooks/gate.py` plus a negative case in `hooks/test_gate.py`.

4. Have the user label Jev's calls. These are the only labels the gate needs.
   - Would-ask: `jq -r '.[] | select(.source == "jev" and .decision == "ask") | [.judgments.outward, .judgments.destructive, .action] | @tsv' "$M"`
   - Borderline non-asks: `jq -r '.[] | select(.judgments and .decision != "ask" and ([.judgments.outward, .judgments.destructive] | max) >= 0.3) | .action' "$M"`
   - Would-allow: `jq -r '.[] | select(.decision == "allow") | .action' "$M"`. This version never applies allow, but it is the evidence any future auto-allow would need.
   - Show these as short tables and ask the user to mark each row "should ask" or "fine to run". Report ask precision and every missed ask they find.

5. Check REUSE precision and what it would save:

   ```sh
   jq -c '(INDEX(.id)) as $g | map(select(.decision == "reuse"))
     | map({action, same_output: (.out.sha != null and .out.sha == $g[.reuse.id].out.sha),
            kb: ((.out.bytes // 0) / 1024 | floor), s: ((.out.dur_ms // 0) / 1000)})' "$M"
   ```

   - `same_output: true` means the re-run really was redundant; the `kb` and `s` values are what enforce mode would have saved.
   - A sha mismatch can come from timestamps or durations in the output, so the true precision may be higher than this count. Inspect mismatches before calling them misses.
   - In enforce mode a denied re-run has no `out`; its retry is the next row.

6. Check Jev's health:

   ```sh
   jq -c '[.[] | select(.source == "jev")] | {judged: length,
     errors: (map(select(.error)) | group_by(.error) | map({error: .[0].error, status: .[0].status, n: length})),
     latency: (map(.latency_ms // empty) | sort | {p50: .[length / 2 | floor], p95: .[length * 0.95 | floor]})}' "$M"
   ```

   - Enforce mode waits up to 1.5 s on each gray-zone call, and a timeout fails open.
   - A 401 means the key is wrong. A 429 means the rate limit, which every agent on the key shares.

7. Measure output sizes, which is the evidence for pruning:
   - Per tool: `jq -c '[.[] | select(.out)] | group_by(.tool) | map({tool: .[0].tool, calls: length, total_kb: (map(.out.bytes) | add / 1024 | floor), over_16kb: (map(select(.out.bytes >= 16384)) | length)})' "$M"`
   - Largest outputs: `jq -r 'map(select(.out)) | sort_by(-.out.bytes) | .[:10][] | [(.out.bytes / 1024 | floor), .tool, .action] | @tsv' "$M"`
   - Frequent outputs of 16 KB or more from the same few commands (test runs, builds, logs) are the case for PostToolUse output pruning, which is not built yet.

## Deciding

Recommend `enforce` only when all of these hold, and cite the numbers for each:

- At least 200 gated calls across several sessions.
- No lock rule fires mostly on harmless commands.
- The user accepts the labeled ask precision, and no labeled missed ask remains unexplained.
- Most would-reuse rows have `same_output: true`, or the mismatches are explained.
- Jev's error rate is under 5% and its p95 latency is under 1500 ms.

How the user switches:

- Claude Code: `/plugin configure jev-gate@agent-relay` and set `mode` to `enforce`.
- Other harnesses: `JEV_GATE_MODE=enforce` in the environment the harness starts from.
- Enforce applies `ask` and REUSE denials only. It never auto-allows.

Tuning:

- The thresholds are constants at the top of `hooks/gate.py`: `ASK_AT`, `EXTERNAL_AT`, and `REUSE_*`.
- `policy()` is a pure function, so replay logged `judgments` through it with the new value and show the user which decisions change before editing anything.
- Changing a Jev question's wording or `TYPESAFE_JEV_MODEL` invalidates the collected judgments. In that case go back to shadow mode and collect a fresh batch.
