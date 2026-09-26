# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.2,<3", "typesafe-sdk>=0.7.1,<0.8"]
# ///
"""jev-dispatch MCP server: route agent tasks to harness/model/effort via TypeSafe Jev.

serve: uv run --script <PLUGIN_ROOT>/mcp/server.py   (stdio; deps from the PEP 723 block, needs uv)
dev:   mcp dev server.py
test:  python test_server.py                          (offline, fake client)
env:  TYPESAFE_API_KEY (required by the first ask; pass through from the host env, never hardcode)
      TYPESAFE_JEV_MODEL (default "jev-1.13.0" — pinned, bump only after re-eval)
      JEV_DISPATCH_FLOOR_ROUTE (default 0.35 — min score confidence to route at all)
      JEV_DISPATCH_FLOOR_RISK  (default 0.85 — min risk confidence for the cheap flash path)
      Floors must satisfy 0 <= ROUTE <= RISK <= 1, otherwise every ask returns kind "config".
"""
import math
import os
from typing import Any

from mcp.server import MCPServer
from typesafe_sdk import (AsyncTypeSafeClient, Noul, Score, TypeSafeAPIConnectionError,
                          TypeSafeAPITimeoutError, TypeSafeError)

mcp = MCPServer("jev-dispatch", dependencies=["typesafe-sdk>=0.7.1,<0.8"])
MODEL = os.environ.get("TYPESAFE_JEV_MODEL") or "jev-1.13.0"
_client: AsyncTypeSafeClient | None = None  # built on first ask so import works without a key


def _floor(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name) or default)
    except ValueError:
        return math.nan  # rejected by the range check below


FLOOR_ROUTE = _floor("JEV_DISPATCH_FLOOR_ROUTE", 0.35)
FLOOR_RISK = _floor("JEV_DISPATCH_FLOOR_RISK", 0.85)
RISK_TAIL = 0.2  # P(risk criterion 2) at or above this needs user approval
CONFIG_ERROR = None if 0 <= FLOOR_ROUTE <= FLOOR_RISK <= 1 else (
    f"invalid floors: need 0 <= JEV_DISPATCH_FLOOR_ROUTE ({FLOOR_ROUTE}) "
    f"<= JEV_DISPATCH_FLOOR_RISK ({FLOOR_RISK}) <= 1")

MAX_TASK = 8000
CONTEXT_KEYS = ("repo", "budget")
MAX_CONTEXT_VALUE = 500

DEFAULT_CONTEXT = {
    "repo": "unspecified repo — pass context.repo to override",
    "harnesses": "codex (strong code agent CLI), claude (strong planning/reasoning), gemini (large context, web grounding)",
    "budget": "cost-sensitive; prefer the cheapest harness that clears the bar",
}

BATTERIES = {
    "task_dispatch": {
        "complexity": Score(
            instructions="How complex is the engineering task described in `task`?",
            criteria=[
                "A mechanical one-line change: typo, rename a literal, bump a version string.",
                "A small localized change in one or two files with an obvious correct approach and existing examples to copy.",
                "A standard feature or fix touching a few files, following established conventions in the repo, with tests or validation available.",
                "A multi-file change requiring design decisions, reading unfamiliar code, or coordinating several components.",
                "An open-ended or ambiguous task: unclear spec, cross-system refactor, or architecture decision with multiple defensible solutions.",
            ],
        ),
        "risk": Score(
            instructions="If the agent's output for `task` is wrong, how large is the blast radius?",
            criteria=[
                "Cosmetic or docs-only; a wrong answer is caught at review with no consequence.",
                "Wrong output breaks CI/tests or a dev workflow; detectable but costs a cycle to fix.",
                "Wrong output could corrupt the repo, publish something public, or cause production/user-facing damage.",
            ],
        ),
        "needs_web": Noul(
            instructions="Does `task` require current information from the internet "
            "(library docs beyond 2024, recent spec changes, external research) "
            "rather than only the local repo?"
        ),
        "needs_long_context": Noul(
            instructions="Does `task` require holding many files, long logs, or multiple "
            "large documents in context at once to do well?"
        ),
        "needs_planning": Noul(
            instructions="Does `task` require the agent to decompose it into ordered steps "
            "and coordinate them, rather than being executable in one pass?"
        ),
    },
}

# Score answers are 0-based probability-weighted positions across criteria:
# complexity spans 0..4 (criteria[0] = 0), risk spans 0..2. Verified empirically
# on jev-1.13.0 — thresholds below are in that scale, not 1-based level numbers.
# First match wins. The policy differs from the measured prototype: re-run the
# golden set (shadow mode) before enabling auto-routing.
def _escalate(why: str) -> dict[str, Any]:
    return {"harness": "ESCALATE", "model": "orchestrator-llm", "effort": "-", "why": why, "act": False}


def route(j: dict, conf: dict, tail: float) -> dict[str, Any]:
    c, r = j["complexity"], j["risk"]
    p_web, p_long = j["needs_web"], j["needs_long_context"]
    # needs_planning is scored and returned but unused; removal deferred pending golden-set re-eval.
    if r >= 1.5 or tail >= RISK_TAIL:
        return {**_escalate(f"high risk ({r:.2f}, P(risk=2)={tail:.2f}) — ask the user"),
                "requires_approval": True, "suggested": {"harness": "claude", "model": "opus", "effort": "high"}}
    if conf["risk"] < FLOOR_ROUTE:
        return _escalate(f"risk unknown: conf {conf['risk']:.2f} < {FLOOR_ROUTE}")
    if conf["complexity"] < FLOOR_ROUTE:
        return _escalate(f"complexity unknown: conf {conf['complexity']:.2f} < {FLOOR_ROUTE}")
    if c >= 3.2:
        return {"harness": "claude", "model": "opus", "effort": "high",
                "why": f"very complex ({c:.1f})", "act": True}
    if p_web > 0.7 or p_long > 0.7:
        return {"harness": "gemini", "model": "pro", "effort": "medium",
                "why": f"web ({p_web:.2f}) / long-context ({p_long:.2f}) fits gemini", "act": True}
    if c < 1.2 and r < 0.6 and conf["risk"] >= FLOOR_RISK:
        return {"harness": "gemini", "model": "flash", "effort": "low",
                "why": f"trivial ({c:.1f}) + confidently low risk ({r:.2f}) -> cheap path", "act": True}
    return {"harness": "codex", "model": "luna", "effort": "max",
            "why": "standard engineering work", "act": True}


def _error(msg: str, kind: str, exc: Exception | None = None, **extra: Any) -> dict[str, Any]:
    out = {"error": msg, "kind": kind, "routing": _escalate(msg), **extra}
    if exc is not None:
        out["error_type"] = type(exc).__name__
        for attr in ("status", "request_id"):
            if (value := getattr(exc, attr, None)) is not None:
                out[attr] = value
    return out


@mcp.tool()
async def ask(battery: str, task: str, context: dict | None = None) -> dict[str, Any]:
    """Score a task with a Jev battery and route it to (harness, model, effort).

    Call BEFORE dispatching a task to a worker. The only battery is "task_dispatch".
    - routing.act=false: do NOT dispatch per routing (ESCALATE); decide with your own reasoning.
    - routing.requires_approval=true: ask the user before dispatching; routing.suggested may be shown.
    - A top-level "error" field (kind: config|input|api|timeout|connection|response) means act=false.
    `task` (non-empty, <= 8000 chars) and `context` (only "repo"/"budget" string values <= 500 chars;
    anything else is dropped and listed in context_ignored) are sent to the TypeSafe API: never
    include secrets, credentials, PII, or orchestration preambles/tokens.
    Log judgments and routing with the worker outcome to build the golden dataset.
    """
    global _client
    if CONFIG_ERROR:
        return _error(CONFIG_ERROR, "config")
    questions = BATTERIES.get(battery)
    if questions is None:
        return _error(f"unknown battery {battery!r}", "input", available=sorted(BATTERIES))
    if not isinstance(task, str) or not task.strip() or len(task) > MAX_TASK:
        return _error(f"task must be a non-empty string of at most {MAX_TASK} chars", "input")
    if not isinstance(context, (dict, type(None))):
        return _error("context must be an object", "input")
    context = context or {}
    kept = {k: v for k, v in context.items()
            if k in CONTEXT_KEYS and isinstance(v, str) and len(v) <= MAX_CONTEXT_VALUE}
    ignored = sorted(str(k) for k in context if k not in kept)
    if _client is None:
        try:
            _client = AsyncTypeSafeClient(model=MODEL)
        except TypeSafeError as e:  # missing/invalid key
            return _error(str(e), "config", e)
    state = {"task": task, "context": {**DEFAULT_CONTEXT, **kept}}
    try:
        resp = await _client.system_one(state=state, questions=questions)
    except TypeSafeAPITimeoutError as e:  # subclass of TypeSafeAPIConnectionError, so first
        return _error(str(e), "timeout", e)
    except TypeSafeAPIConnectionError as e:
        return _error(str(e), "connection", e)
    except TypeSafeError as e:
        return _error(str(e), "api", e)
    scores, nouls = resp.scores, resp.nouls
    missing = [k for k, q in questions.items() if k not in (scores if isinstance(q, Score) else nouls)]
    if missing:
        return _error(f"response missing answers: {missing}", "response")
    if 2 not in scores["risk"].probabilities:
        return _error("risk answer has no probability for criterion 2", "response")
    judgments = {k: a.score for k, a in scores.items()}
    judgments.update({k: a.noul for k, a in nouls.items()})
    conf = {k: a.confidence for k, a in scores.items()}
    tail = scores["risk"].probabilities[2]
    if not all(math.isfinite(v) for v in (*judgments.values(), *conf.values(), tail)):
        return _error("response has non-finite values", "response")  # NaN would fail open
    out = {
        "model": resp.model,
        "battery": battery,
        "judgments": judgments,
        "confidence": conf,
        "risk_tail": tail,
        "score_scale": {"complexity": "0..4", "risk": "0..2", "note": "0-based weighted position; criteria[0] = 0"},
        "routing": route(judgments, conf, tail),
        "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
    }
    if ignored:
        out["context_ignored"] = ignored
    return out


if __name__ == "__main__":
    mcp.run()
