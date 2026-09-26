---
name: dispatch-routing
description: Route a task to the right agent harness, model, and effort level by scoring it with a TypeSafe Jev judgment battery and applying a pure-code policy. Use when coordinating or dispatching agent workers (e.g. Orca orchestration) and choosing which harness/model/effort a task should get.
---

# Dispatch routing with Jev

Jev scores the task on five independent questions in ONE request (~740 input tokens, ~$0.00003). Plain code then makes the routing decision. The model never picks the harness; the policy does. This keeps the judgments reusable, the policy testable, and each call cheap.

## Setup

- **Wiring.** Installing the plugin wires the MCP server wherever the harness supports plugin-provided MCP:
  - Claude Code: `.mcp.json`
  - Gemini CLI: `gemini-extension.json`
  - Kimi Code: `.kimi-plugin/plugin.json`
  - Codex: `mcp.json`. Codex does not pass the API key through, so every call returns `kind: "config"` until you add the manual config.
  - Qoder (unverified) and Cursor may need manual config.

  The plugin README's install section has the manual snippets. The launch command is `uv run --script <PLUGIN_ROOT>/mcp/server.py` and needs `uv` on PATH.
- **API key.** `TYPESAFE_API_KEY` must be in the host environment. Never read it, print it, or write it into a file. The server starts without it, but every `ask` returns `kind: "config"` until the host restarts the server with the key in its environment. A well-formed but wrong key returns `kind: "api"` with `status` 401.
- **Optional env:**
  - `TYPESAFE_JEV_MODEL`: pinned default `jev-1.13.0`.
  - `JEV_DISPATCH_FLOOR_ROUTE`: default 0.35.
  - `JEV_DISPATCH_FLOOR_RISK`: default 0.85.
  - The floors must satisfy `0 <= ROUTE <= RISK <= 1`; otherwise every call returns `kind: "config"`.
- **No tool.** If the `ask` tool is not available, the server is not wired. Route with your own judgment, say so, and never invent scores.

## Flow per dispatch

1. BEFORE creating or dispatching a worker, call the MCP tool:
   `ask(battery="task_dispatch", task="<short task description>", context={"repo": "...", "budget": "..."})`
   - `context` accepts only `repo` and `budget`, as strings of at most 500 chars. Anything else is dropped and listed in `context_ignored`; `harnesses` is fixed server-side.
   - `task` must be non-empty and at most 8000 chars. Describe the task in a few sentences.
   - `task` and `context` are sent to the TypeSafe API on every call. NEVER include secrets, credentials, PII, source/diff/log dumps, orchestration preambles, capability tokens, or terminal handles.
2. Read the response in this order:
   1. **Top-level `error` field** (kind `config|input|api|timeout|connection|response`): treat it as `act=false`. Its `routing` is already ESCALATE. Decide with your own reasoning, and log `kind` (and `request_id` if present).
   2. **`routing.requires_approval=true`**: the task is high risk. Ask the user before dispatching anything. You may show `routing.suggested` (claude/opus/high) and `routing.why`. Dispatch only after explicit approval, even when Jev's confidence is high.
   3. **`routing.act=false`** (ESCALATE without `requires_approval`): do NOT dispatch per the routing. Decide with the orchestrating reasoning model, or ask the user.
   4. **`routing.act=true`**:
      - Auto-routing mode: dispatch with exactly `routing.harness / model / effort`, and attach `routing.why` to the dispatch log.
      - Shadow mode: log the routing and decide yourself (see below).
3. Log these fields verbatim with every dispatch: `model`, `judgments`, `confidence`, `risk_tail`, and `routing` (or `error`/`kind`). Also log the harness actually used and the worker outcome.

## Routing policy

Symbols: `c` = `judgments.complexity`, `r` = `judgments.risk`, `tail` = `risk_tail` (the probability of risk criterion index 2). Floor defaults: FLOOR_ROUTE 0.35, FLOOR_RISK 0.85. Rules are evaluated top to bottom, and the first match wins:

| # | Condition | `routing` |
| --- | --- | --- |
| 1 | `r >= 1.5` or `tail >= 0.2` | `ESCALATE`, `act=false`, `requires_approval=true`, `suggested={"harness":"claude","model":"opus","effort":"high"}` |
| 2 | `confidence.risk < FLOOR_ROUTE` | `ESCALATE`, `act=false` (risk unknown) |
| 3 | `confidence.complexity < FLOOR_ROUTE` | `ESCALATE`, `act=false` (complexity unknown) |
| 4 | `c >= 3.2` | `claude` / `opus` / `high` |
| 5 | `needs_web > 0.7` or `needs_long_context > 0.7` | `gemini` / `pro` / `medium` |
| 6 | `c < 1.2` and `r < 0.6` and `confidence.risk >= FLOOR_RISK` | `gemini` / `flash` / `low` |
| 7 | otherwise | `codex` / `gpt-default` / `medium` |

- ESCALATE is always `{"harness":"ESCALATE","model":"orchestrator-llm","effort":"-","act":false,"why":...}`.
- Only rule 1 adds `requires_approval` and `suggested`.
- Rules 4–7 return `act=true`.
- `needs_planning` is scored and returned, but no rule uses it.

This policy differs from the measured prototype. Re-run the golden set in shadow mode before enabling auto-routing.

## Reading the answers correctly

- `Score` answers are **0-based** probability-weighted positions: `complexity` spans 0..4, `risk` spans 0..2, and `criteria[0]` maps to 0. The thresholds in code use that scale, never 1-based level numbers.
- A Noul near 0.5 means yes and no are balanced ("unsure"), NOT medium intensity. Many tasks legitimately sit near 0.5 on `needs_web`/`needs_long_context`.
- Confidence gates follow the evaluation order. There is no single `min(confidence)` gate in front of the whole policy:
  - The high-risk/tail check runs first, with no confidence floor, so a confidently risky task is never auto-dispatched.
  - Only after that must both Score confidences clear FLOOR_ROUTE.
  - The high floor FLOOR_RISK guards only the cheap `gemini/flash` path, so mid-risk tasks whose `confidence.risk` sits between the floors fall through to codex.
  - The Noul branch has no confidence field.
- `risk` is a weighted mean, so it can hide a real chance of the worst case. `risk_tail` exposes that chance directly, which is why rule 1 checks it.
- Judgments are reproducible but NOT perfectly deterministic across runs on this battery. Regression tests need a tolerance band and must pin `model`.

## Operate it like a system, not a prompt

- **Shadow mode first (1–2 weeks, or until the golden set covers enough cases):** call `ask` on every dispatch but act on your own judgment, and log both your choice and the routing. The safety signals still apply in shadow mode: `requires_approval` means ask the user, and `act=false` or `error` means never dispatch per routing. This log is the golden dataset; no hand labeling is needed.
- **Keep the log out of git:**
  - Store it outside the repo (e.g. `~/.local/state/jev-dispatch/dispatch-log.jsonl`), or in a path the repo already ignores (check with `git check-ignore` first).
  - It contains task text, so the same no-secrets rule applies.
- **Tune, then pin:**
  - Adjust the floors via env based on the golden set: measure escalation rate against bad-routing rate, tune on one part of the log, and verify on the rest.
  - Keep `TYPESAFE_JEV_MODEL` pinned.
  - Re-run the golden set whenever question wording, the state builder, or the model changes (Jev reads instructions literally). Enable auto-routing only after it passes.
- **Escalation budget:** expect ~5–10% of dispatches to escalate. Far more means the floors are too strict; far less means risk decisions are unguarded.
- **Language:** Vietnamese task descriptions were judged coherently in a small sample, but Jev performs best on English state. Measure degradation on your own golden set before assuming it is fine.

## When NOT to route with Jev

Judgments that need multi-hop reasoning, math/dates, multimodal input, or non-English nuance belong to the orchestrating reasoning model. Jev only handles the narrow, high-frequency scoring.
