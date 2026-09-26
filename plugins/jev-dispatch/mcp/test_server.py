"""Offline checks for server.py (no network, fake client): python test_server.py"""
import asyncio
import importlib.util
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the plugin dir

import httpx2
from typesafe_sdk import (SystemOneResponse, TypeSafeAPIConnectionError, TypeSafeAPITimeoutError,
                          TypeSafeInternalServerError)

for var in ("TYPESAFE_API_KEY", "TYPESAFE_JEV_MODEL", "JEV_DISPATCH_FLOOR_ROUTE", "JEV_DISPATCH_FLOOR_RISK"):
    os.environ.pop(var, None)  # never reach the real API; start from defaults

SERVER = Path(__file__).with_name("server.py")
_loads = 0


def load(**env):
    """Fresh import of server.py (env is read at import time)."""
    global _loads
    _loads += 1
    os.environ.update(env)
    try:
        spec = importlib.util.spec_from_file_location(f"jev_server_{_loads}", SERVER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        for var in env:
            os.environ.pop(var)


def response(c, r, conf_c, conf_r, tail, web, long, drop=()):
    answers = {
        "complexity": {"type": "score", "score": c, "confidence": conf_c,
                       "legend": {i: str(i) for i in range(5)}, "probabilities": {i: 0.2 for i in range(5)}},
        "risk": {"type": "score", "score": r, "confidence": conf_r,
                 "legend": {i: str(i) for i in range(3)}, "probabilities": {0: 1 - tail, 1: 0.0, 2: tail}},
        "needs_web": {"type": "noul", "noul": web},
        "needs_long_context": {"type": "noul", "noul": long},
        "needs_planning": {"type": "noul", "noul": 0.1},
    }
    for k in drop:
        del answers[k]
    return SystemOneResponse.model_validate({"model": "jev-1.13.0", "answers": answers,
                                             "usage": {"input_tokens": 1, "output_tokens": 1}})


class FakeClient:
    def __init__(self, result):
        self.result, self.states = result, []

    async def system_one(self, state, questions):
        self.states.append(state)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def ask(srv, result=None, battery="task_dispatch", task="fix the typo in README", context=None):
    if result is not None:
        srv._client = FakeClient(result)
    return asyncio.run(srv.ask(battery, task, context))


def check_error(out, kind):
    assert "error" in out and out["kind"] == kind, out
    assert out["routing"]["act"] is False and out["routing"]["harness"] == "ESCALATE", out


srv = load()
assert srv.MODEL == "jev-1.13.0" and srv.CONFIG_ERROR is None

# (c, r, conf_c, conf_r, tail, web, long) -> (harness, model, effort, act)
ROWS = {
    "a": ((0.3, 0.2, 0.9, 0.9, 0.02, 0.1, 0.1), ("gemini", "flash", "low", True)),
    "b": ((0.3, 0.2, 0.9, 0.6, 0.02, 0.1, 0.1), ("codex", "luna", "max", True)),
    "c": ((0.2, 1.9, 0.10, 0.99, 0.9, 0.1, 0.1), ("ESCALATE", "orchestrator-llm", "-", False)),
    "d": ((1.0, 0.9, 0.9, 0.9, 0.45, 0.1, 0.1), ("ESCALATE", "orchestrator-llm", "-", False)),
    "e": ((2.0, 0.3, 0.9, 0.9, 0.05, 0.8, 0.1), ("gemini", "pro", "medium", True)),
    "f": ((2.0, 0.3, 0.2, 0.9, 0.05, 0.1, 0.1), ("ESCALATE", "orchestrator-llm", "-", False)),
    "g": ((3.5, 0.5, 0.9, 0.9, 0.05, 0.1, 0.1), ("claude", "opus", "high", True)),
    "h": ((2.0, 1.2, 0.8, 0.6, 0.1, 0.2, 0.2), ("codex", "luna", "max", True)),
    "i": ((2.0, 0.3, 0.9, 0.2, 0.05, 0.1, 0.1), ("ESCALATE", "orchestrator-llm", "-", False)),
}
for name, (row, expected) in ROWS.items():
    out = ask(srv, response(*row))
    rt = out["routing"]
    assert (rt["harness"], rt["model"], rt["effort"], rt["act"]) == expected, (name, rt)
    if name in ("c", "d"):
        assert rt["requires_approval"] is True, (name, rt)
        assert rt["suggested"] == {"harness": "claude", "model": "opus", "effort": "high"}, (name, rt)
    else:
        assert "requires_approval" not in rt and "suggested" not in rt, (name, rt)
    assert out["risk_tail"] == row[4] and "context_ignored" not in out, (name, out)
    assert set(out["judgments"]) == set(srv.BATTERIES["task_dispatch"]), (name, out)

# Config: missing key (no client injected), bad floors, empty model env -> default.
check_error(ask(load()), "config")
for env in ({"JEV_DISPATCH_FLOOR_ROUTE": "nan"}, {"JEV_DISPATCH_FLOOR_ROUTE": "abc"},
            {"JEV_DISPATCH_FLOOR_RISK": "inf"}, {"JEV_DISPATCH_FLOOR_ROUTE": "-0.1"},
            {"JEV_DISPATCH_FLOOR_ROUTE": "0.9"}):  # 0.9 > default FLOOR_RISK 0.85
    bad = load(**env)
    check_error(ask(bad, response(*ROWS["a"][0])), "config")
ok = load(TYPESAFE_JEV_MODEL="", JEV_DISPATCH_FLOOR_ROUTE="", JEV_DISPATCH_FLOOR_RISK="")
assert ok.MODEL == "jev-1.13.0" and ok.CONFIG_ERROR is None and ok.FLOOR_ROUTE == 0.35

# SDK errors.
out = ask(srv, TypeSafeAPITimeoutError(5.0))
check_error(out, "timeout")
assert out["error_type"] == "TypeSafeAPITimeoutError", out
check_error(ask(srv, TypeSafeAPIConnectionError("Connection error: refused")), "connection")
out = ask(srv, TypeSafeInternalServerError(503, None, httpx2.Headers({"x-typesafe-request-id": "req_1"})))
check_error(out, "api")
assert out["status"] == 503 and out["request_id"] == "req_1", out

# Bad responses.
check_error(ask(srv, response(*ROWS["a"][0], drop=("needs_web",))), "response")
check_error(ask(srv, response(float("nan"), 0.2, 0.9, 0.9, 0.02, 0.1, 0.1)), "response")

# Input validation.
out = ask(srv, response(*ROWS["a"][0]), battery="nope")
check_error(out, "input")
assert out["available"] == ["task_dispatch"], out
check_error(ask(srv, task="x" * 8001), "input")
check_error(ask(srv, task="   "), "input")

# Context allowlist: only repo sent; harnesses stays the server default.
srv._client = fake = FakeClient(response(*ROWS["a"][0]))
out = asyncio.run(srv.ask("task_dispatch", "fix the typo", {"repo": "x", "harnesses": "y", "secret": "z"}))
sent = fake.states[-1]["context"]
assert sent == {**srv.DEFAULT_CONTEXT, "repo": "x"}, sent
assert out["context_ignored"] == ["harnesses", "secret"], out
assert out["routing"]["act"] is True, out

print("OK")
