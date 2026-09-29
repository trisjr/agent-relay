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
- **API key.** The server reads `TYPESAFE_API_KEY` from its environment:
  - Claude Code fills it from the plugin's sensitive `typesafe_api_key` option, which is stored in the keychain. The user sets it via `/plugin configure`.
  - Gemini CLI fills it from the extension setting.
  - Other harnesses need it in the host environment.

  Never read it, print it, or write it into a file. The server starts without it, but every `ask` returns `kind: "config"` until the host restarts the server with the key in its environment. A well-formed but wrong key returns `kind: "api"` with `status` 401.
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
   2. **`routing.requires_approval=true`**: the task is high risk. Ask the user before dispatching anything. You may show `routing.suggested` (the route the task would get if it were safe) and `routing.why`. Dispatch only after explicit approval, even when Jev's confidence is high, and then with `suggested` or the route the user picks.
   3. **`routing.act=false`** (ESCALATE without `requires_approval`): do NOT dispatch per the routing. Decide with the orchestrating reasoning model, or ask the user.
   4. **`routing.act=true`**:
      - Auto-routing mode: dispatch with exactly `routing.harness`, the provider id of `routing.model` (see the [model id table](#routing-policy)), and `routing.effort`, and attach `routing.why` to the dispatch log.
      - Shadow mode: log the routing and decide yourself (see below).
3. Append a `route` record to the [dispatch log](#dispatch-log) after every `ask` call, even when nothing gets dispatched. Append an `outcome` record once the task settles.

## Dispatch log

The golden set is one append-only JSONL file: `~/.local/state/jev-dispatch/dispatch-log.jsonl`. It sits outside every repo and holds task text, so the no-secrets rule for `task` applies to it too.

- One JSON object per line. Never edit or delete earlier lines.
- Use the record shapes below exactly. Replay scripts read these field names, so never rename them (`event`, never `kind`), never lift `response` fields to the top level, and never invent `outcome` values.
- Log only dispatches that went through `ask`. A task routed without calling `ask` (user-fixed model, pre-approved plan) gets no records: without judgments it is useless to the golden set.
- `mkdir -p` the directory on first use.
- Append through `jq`, never with `echo`, so quotes in task text cannot break the line. The quoted `'EOF'` disables shell interpolation; `jq` compacts the record to one line and appends nothing if the JSON is malformed:

  ```sh
  jq -c . <<'EOF' >> ~/.local/state/jev-dispatch/dispatch-log.jsonl
  { ...the record, written literally... }
  EOF
  ```

`route`, appended once per `ask` call, after the dispatch decision is final (not before, then again):

```json
{"event": "route", "id": "<task id>", "ts": "<UTC ISO 8601>", "task": "<task as sent>", "context": {"repo": "...", "budget": "..."}, "response": {"...": "the ask response, verbatim"}, "used": {"harness": "claude", "model": "claude-opus-5-5", "effort": "medium"}}
```

- `id`: unique per task, and reused by its `outcome`. Use the orchestrator's task id when there is one (e.g. the Orca task id). Otherwise generate one, such as a UTC timestamp plus a short slug.
- `task`, `context`: exactly what was sent to `ask`. The response contains neither, and re-scoring after a wording or model change needs both.
- `response`: the whole object `ask` returned, error responses included. Never trim or recompute it.
- `used`: what was actually dispatched; in shadow mode it may differ from `routing`.
  - `model`/`effort`: the concrete values the worker runs with (e.g. `claude-opus-5-5`, `gpt-6-luna`), including a harness default you can see. `null` only when truly unknown. Never fill them in from `routing`.
  - `used` is `null` when nothing was dispatched: the coordinator did the task itself, or the user declined.

`outcome`, appended once when the task settles, after any retries:

```json
{"event": "outcome", "id": "<same id>", "ts": "<UTC ISO 8601>", "outcome": "ok", "note": "<optional, one line>"}
```

- `outcome` is one of:
  - `ok`: accepted on the first worker.
  - `retried`: accepted only after a retry or a reassignment caused by the worker's result. A worker that merely failed to start (e.g. readiness timeout) and then succeeded is still `ok`; put the hiccup in `note`.
  - `failed`: never accepted.
  - `cancelled`: stopped for a reason unrelated to the worker (scope change, user abort). It is excluded from routing metrics.
- `note`: short evidence, such as the failing acceptance command. Never a log or diff dump.
- Skip the `outcome` record when `used` is `null`.

## Routing policy

Symbols: `c` = `judgments.complexity`, `r` = `judgments.risk`, `tail` = `risk_tail` (the probability of risk criterion index 2). Floor defaults: FLOOR_ROUTE 0.35, FLOOR_RISK 0.85. Rules are evaluated top to bottom, and the first match wins:

| # | Condition | `routing` |
| --- | --- | --- |
| 1 | `r >= 1.5` or `tail >= 0.2` | `ESCALATE`, `act=false`, `requires_approval=true`, `suggested` = the route rules 4–11 would pick (`claude/opus/high` when a Score confidence is below FLOOR_ROUTE; `claude/sonnet/high` instead of any codex pick when `r >= 1.5`) |
| 2 | `confidence.risk < FLOOR_ROUTE` | `ESCALATE`, `act=false` (risk unknown) |
| 3 | `confidence.complexity < FLOOR_ROUTE` | `ESCALATE`, `act=false` (complexity unknown) |
| 4 | `c >= 3.2` | `claude` / `opus` / `high` |
| 5 | `c >= 2.2` | `claude` / `sonnet` / `high` |
| 6 | `needs_web > 0.7` | `claude` / `sonnet` / `medium` |
| 7 | `needs_long_context > 0.7` | `codex` / `sol` / `high` |
| 8 | `c >= 2.0` | `codex` / `sol` / `high` |
| 9 | `c >= 1.5` | `codex` / `sol` / `medium` |
| 10 | `c < 1.2` and `r < 0.6` and `confidence.risk >= FLOOR_RISK` | `codex` / `luna` / `medium` |
| 11 | otherwise | `codex` / `luna` / `max` |

- ESCALATE is always `{"harness":"ESCALATE","model":"orchestrator-llm","effort":"-","act":false,"why":...}`.
- Only rule 1 adds `requires_approval` and `suggested`.
- Rules 4–11 return `act=true`.
- The load is split across both subscriptions: `claude` takes design-heavy (`c >= 2.2`) and web work, `sol` takes standard engineering. `sonnet` effort tops out at `high`: at `xhigh`/`max` it spends enough tokens to cost more per task than `opus`.
- Web tasks go to `claude`: Claude Code ships web search, while Codex workers launched without `--search` have none.
- Confidently risky tasks (`r >= 1.5`) are never suggested to codex: `sol` tried workarounds after an access denial in most adversarial runs, and `luna` hallucinates more.
- `luna` only takes `c < 1.5`, because it degrades on long context and ambiguous multi-file work. The 1.5 and 2.0 thresholds have not been measured; the 2.2 split gives the golden set outcomes from both `sonnet` and `sol` around it.
- `needs_planning` is scored and returned, but no rule uses it.

`routing.model` is shorthand. Map it to the provider id before dispatching; never pass the shorthand as `--model`:

| `routing.model` | Provider id |
| --- | --- |
| `opus` | `claude-opus-5-5` |
| `sonnet` | `claude-sonnet-5-5` |
| `sol` | `gpt-6-sol` |
| `luna` | `gpt-6-luna` |

A shorthand missing from this table means the table is stale: treat the routing as `act=false`.

This policy differs from the measured prototype. Re-run the golden set in shadow mode before enabling auto-routing, unless the user knowingly opts in earlier (`dag-build` in orca-workflows has).

## Reading the answers correctly

- `Score` answers are **0-based** probability-weighted positions: `complexity` spans 0..4, `risk` spans 0..2, and `criteria[0]` maps to 0. The thresholds in code use that scale, never 1-based level numbers.
- A Noul near 0.5 means yes and no are balanced ("unsure"), NOT medium intensity. Many tasks legitimately sit near 0.5 on `needs_web`/`needs_long_context`.
- Confidence gates follow the evaluation order. There is no single `min(confidence)` gate in front of the whole policy:
  - The high-risk/tail check runs first, with no confidence floor, so a confidently risky task is never auto-dispatched.
  - Only after that must both Score confidences clear FLOOR_ROUTE.
  - The high floor FLOOR_RISK guards only the cheapest `luna/medium` path, so mid-risk tasks whose `confidence.risk` sits between the floors fall through to `luna/max`.
  - The Noul branch has no confidence field.
- `risk` is a weighted mean, so it can hide a real chance of the worst case. `risk_tail` exposes that chance directly, which is why rule 1 checks it.
- Judgments are reproducible but NOT perfectly deterministic across runs on this battery. Regression tests need a tolerance band and must pin `model`.

## Operate it like a system, not a prompt

- **Shadow mode first (1–2 weeks, or until the golden set covers enough cases):** call `ask` on every dispatch but act on your own judgment, and log both your choice (`used`) and the routing. The safety signals still apply in shadow mode: `requires_approval` means ask the user, and `act=false` or `error` means never dispatch per routing. The [dispatch log](#dispatch-log) is the golden dataset; no hand labeling is needed.
- **Tune, then pin:**
  - Adjust the floors via env based on the golden set: measure escalation rate against bad-routing rate, tune on one part of the log, and verify on the rest.
  - Keep `TYPESAFE_JEV_MODEL` pinned.
  - Re-run the golden set whenever question wording, the state builder, or the model changes (Jev reads instructions literally). Enable auto-routing only after it passes, unless the user knowingly opts in earlier; routed outcomes then still feed the golden set.
- **Escalation budget:** expect ~5–10% of dispatches to escalate. Far more means the floors are too strict; far less means risk decisions are unguarded.
- **Language:** Vietnamese task descriptions were judged coherently in a small sample, but Jev performs best on English state. Measure degradation on your own golden set before assuming it is fine.

## When NOT to route with Jev

Judgments that need multi-hop reasoning, math/dates, multimodal input, or non-English nuance belong to the orchestrating reasoning model. Jev only handles the narrow, high-frequency scoring.
