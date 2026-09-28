# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.2,<3", "typesafe-sdk>=0.7.1,<0.8"]
# ///
"""spec-readiness-gate MCP server: score a worker task spec's readiness via TypeSafe Jev.

serve: uv run --script <PLUGIN_ROOT>/mcp/server.py   (stdio; deps from the PEP 723 block, needs uv)
test:  uv run --with "mcp[cli]>=2.2,<3" --with "typesafe-sdk>=0.7.1,<0.8" python test_server.py   (offline)
env:  TYPESAFE_API_KEY (optional; without it every ask returns kind "config" — pass through, never hardcode)
      TYPESAFE_JEV_MODEL   (default "jev-1.13.0" — pinned, bump only after re-eval)
      SPECGATE_FLOOR_FIELD (default 0.5  — a contract-field Noul below it lands in missing_fields)
      SPECGATE_FLOOR_SCORE (default 2.0  — min overall_readiness, 0..4 scale, to dispatch)
      SPECGATE_FLOOR_CONF  (default 0.35 — min overall_readiness confidence; below it -> escalate)
      SPECGATE_MODE        (default "shadow" | "enforce" — echoed in every response, never changes the verdict)
      FIELD/CONF must be in [0, 1], SCORE in [0, 4], MODE shadow|enforce; otherwise every ask returns kind "config".
      A blank value or an unexpanded host placeholder ("${user_config.x}") counts as unset.
"""
import hashlib
import math
import os
import time
from typing import Any

from mcp.server import MCPServer
from typesafe_sdk import (AsyncTypeSafeClient, Noul, Score, TypeSafeAPIConnectionError,
                          TypeSafeAPITimeoutError, TypeSafeError)

mcp = MCPServer("spec-readiness-gate", dependencies=["typesafe-sdk>=0.7.1,<0.8"])
_client: AsyncTypeSafeClient | None = None  # built on first ask so import works without a key


def _env(name: str) -> str | None:
    value = (os.environ.get(name) or "").strip()
    return None if not value or value.startswith("${") else value


def _floor(name: str, default: float) -> float:
    try:
        return float(_env(name) or default)
    except ValueError:
        return math.nan  # rejected by the range checks below


MODEL = _env("TYPESAFE_JEV_MODEL") or "jev-1.13.0"
FLOOR_FIELD = _floor("SPECGATE_FLOOR_FIELD", 0.5)
FLOOR_SCORE = _floor("SPECGATE_FLOOR_SCORE", 2.0)
FLOOR_CONF = _floor("SPECGATE_FLOOR_CONF", 0.35)
MODE = _env("SPECGATE_MODE") or "shadow"
if not (0 <= FLOOR_FIELD <= 1 and 0 <= FLOOR_CONF <= 1):
    CONFIG_ERROR = (f"invalid floors: SPECGATE_FLOOR_FIELD ({FLOOR_FIELD}) and "
                    f"SPECGATE_FLOOR_CONF ({FLOOR_CONF}) must be in [0, 1]")
elif not 0 <= FLOOR_SCORE <= 4:
    CONFIG_ERROR = f"invalid floor: SPECGATE_FLOOR_SCORE ({FLOOR_SCORE}) must be in [0, 4]"
elif MODE not in ("shadow", "enforce"):
    CONFIG_ERROR = f"invalid SPECGATE_MODE {MODE!r}: need 'shadow' or 'enforce'"
else:
    CONFIG_ERROR = None

MAX_TASK = 8000
CONTEXT_LIMITS = {"repo": 500, "siblings": 1000}  # sent to Jev; "round" is policy-only, never sent
ROUNDS = ("1", "2")

DEFAULT_CONTEXT = {
    "repo": "unspecified repo — pass context.repo to override",
    "siblings": "none — no other worker spec shares this wave",
    "contract": "A worker task spec has five fields: Target (the exact object to work on), "
                "Change (what to do and what not to do), Constraints (prohibited actions), "
                "Ownership (the files/directories this worker alone may modify), "
                "Observable acceptance (how completion is verified).",
}

BATTERIES = {
    "spec_readiness": {
        "target_specific": Noul(
            instructions="Does the Target in `task` name one exact, unambiguous object "
            "(a git ref, pinned paths, or a module) — not a vague area?"
        ),
        "change_scoped": Noul(
            instructions="Does the Change in `task` state precisely what to do AND the boundary "
            "of what not to do?"
        ),
        "constraints_stated": Noul(
            instructions="Do the Constraints in `task` list the real prohibitions (no edits, no commits, "
            "review-only...) rather than being empty when side effects could spread?"
        ),
        "ownership_clear": Noul(
            instructions="Does the Ownership in `task` state exactly which files/directories this worker "
            "owns, with no overlap against the sibling specs listed in `context.siblings`?"
        ),
        "acceptance_testable": Noul(
            instructions="Can the Acceptance in `task` be verified by a concrete command or observation "
            "(test run, file exists, report written) — not a vague assertion?"
        ),
        "overall_readiness": Score(
            instructions="How ready is the task spec in `task` to be handed to an autonomous worker agent "
            "that must complete it without follow-up questions?",
            criteria=[
                "A placeholder or draft: three or more of the five fields are missing.",
                "The idea is there, but the scope or the acceptance check is missing.",
                "All five fields are present in form, but at least one is vague or cannot be measured.",
                "Clear, with a testable acceptance check; only minor details are missing.",
                "Dispatch-ready: specific, tightly bounded, and the acceptance check can be run immediately.",
            ],
        ),
    },
}


# overall_readiness is a 0-based probability-weighted position (criteria[0] = 0, spans 0..4).
# First match wins. Every direction the policy can err is safe: clarify/escalate, never a silent dispatch.
def verdict(j: dict, conf: dict, rnd: str) -> dict[str, Any]:
    s, c, r = j["overall_readiness"], conf["overall_readiness"], int(rnd)
    if c < FLOOR_CONF:
        return {"act": "escalate", "why": f"readiness unknown: conf {c:.2f} < {FLOOR_CONF}", "round": r}
    missing = [k for k, v in j.items() if k != "overall_readiness" and v < FLOOR_FIELD]
    if s >= FLOOR_SCORE and not missing:
        return {"act": "dispatch", "why": f"ready ({s:.1f} >= {FLOOR_SCORE})", "round": r}
    why = f"readiness {s:.1f} (floor {FLOOR_SCORE}); weak fields: {', '.join(missing) or 'none'}"
    out = {"act": "clarify", "missing_fields": missing or ["overall"], "why": why, "round": r}
    if r == 2:
        out["exhausted"] = True
        out["why"] += " — already clarified once: decide yourself, mark readiness_override if dispatching"
    return out


def _error(msg: str, kind: str, exc: Exception | None = None, **extra: Any) -> dict[str, Any]:
    out = {"error": msg, "kind": kind, "mode": MODE, "verdict": {"act": "escalate", "why": msg}, **extra}
    if exc is not None:
        out["error_type"] = type(exc).__name__
        for attr in ("status", "request_id"):
            if (value := getattr(exc, attr, None)) is not None:
                out[attr] = value
    return out


@mcp.tool()
async def ask(battery: str, task: str, context: dict | None = None) -> dict[str, Any]:
    """Score a worker task spec's readiness BEFORE worker-start/task-create and return a verdict.

    The only battery is "spec_readiness". `task` is the full spec (Target / Change / Constraints /
    Ownership / Observable acceptance), non-empty, <= 8000 chars. `context` keys:
    "repo" (string <= 500), "siblings" (string <= 1000, one "<worker>: <paths>" line per other spec
    in the same wave), "round" ("1" default, or "2" after one clarify pass; anything else is an input
    error). Other keys or oversized values are dropped and listed in context_ignored.
    - verdict.act="dispatch": spec is ready.
    - verdict.act="clarify": fix verdict.missing_fields, then re-score with round "2";
      exhausted=true means stop clarifying and decide yourself.
    - verdict.act="escalate" or a top-level "error" (kind config|input|api|timeout|connection|response):
      readiness unknown — decide yourself or ask the user.
    `mode` is "shadow" (never block on the verdict, only report and log it) or "enforce" (follow it).
    `task` and `context.repo/siblings` are sent to the TypeSafe API: never include secrets,
    credentials, PII, or orchestration preambles/tokens.
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
    rnd = str(context.get("round", "1"))
    if rnd not in ROUNDS:
        return _error('context.round must be "1" or "2"', "input")
    kept = {k: v for k, v in context.items()
            if k in CONTEXT_LIMITS and isinstance(v, str) and len(v) <= CONTEXT_LIMITS[k]}
    ignored = sorted(str(k) for k in context if k not in kept and k != "round")
    if _client is None:
        if (key := _env("TYPESAFE_API_KEY")) is None:
            return _error("TYPESAFE_API_KEY is not set — use the manual checklist", "config")
        try:
            _client = AsyncTypeSafeClient(model=MODEL, api_key=key)
        except TypeSafeError as e:  # malformed key
            return _error(str(e), "config", e)
    state = {"task": task, "context": {**DEFAULT_CONTEXT, **kept}}
    started = time.monotonic()
    try:
        resp = await _client.system_one(state=state, questions=questions)
    except TypeSafeAPITimeoutError as e:  # subclass of TypeSafeAPIConnectionError, so first
        return _error(str(e), "timeout", e)
    except TypeSafeAPIConnectionError as e:
        return _error(str(e), "connection", e)
    except TypeSafeError as e:
        return _error(str(e), "api", e)
    latency_ms = round((time.monotonic() - started) * 1000)
    scores, nouls = resp.scores, resp.nouls
    missing = [k for k, q in questions.items() if k not in (scores if isinstance(q, Score) else nouls)]
    if missing:
        return _error(f"response missing answers: {missing}", "response")
    judgments = {k: nouls[k].noul if isinstance(q, Noul) else scores[k].score for k, q in questions.items()}
    conf = {k: scores[k].confidence for k, q in questions.items() if isinstance(q, Score)}
    if not all(math.isfinite(v) for v in (*judgments.values(), *conf.values())):
        return _error("response has non-finite values", "response")  # NaN would fail open
    out = {
        "model": resp.model,
        "battery": battery,
        "mode": MODE,
        "spec_hash": "sha256:" + hashlib.sha256(task.encode()).hexdigest(),
        "judgments": judgments,
        "confidence": conf,
        "score_scale": {"overall_readiness": "0..4", "note": "0-based weighted position; criteria[0] = 0"},
        "verdict": verdict(judgments, conf, rnd),
        "latency_ms": latency_ms,
        "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
    }
    if ignored:
        out["context_ignored"] = ignored
    return out


if __name__ == "__main__":
    mcp.run()
