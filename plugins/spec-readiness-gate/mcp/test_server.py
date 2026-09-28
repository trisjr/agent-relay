"""Offline checks for server.py (no network, fake client):
uv run --with "mcp[cli]>=2.2,<3" --with "typesafe-sdk>=0.7.1,<0.8" python test_server.py"""
import asyncio
import hashlib
import importlib.util
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the plugin dir

import httpx2
from typesafe_sdk import (SystemOneResponse, TypeSafeAPIConnectionError, TypeSafeAPIResponseValidationError,
                          TypeSafeAPITimeoutError, TypeSafeInternalServerError)

for var in ("TYPESAFE_API_KEY", "TYPESAFE_JEV_MODEL", "SPECGATE_FLOOR_FIELD", "SPECGATE_FLOOR_SCORE",
            "SPECGATE_FLOOR_CONF", "SPECGATE_MODE"):
    os.environ.pop(var, None)  # never reach the real API; start from defaults

SERVER = Path(__file__).with_name("server.py")
FIELDS = ("target_specific", "change_scoped", "constraints_stated", "ownership_clear", "acceptance_testable")
_loads = 0


def load(**env):
    """Fresh import of server.py (env is read at import time)."""
    global _loads
    _loads += 1
    os.environ.update(env)
    try:
        spec = importlib.util.spec_from_file_location(f"specgate_server_{_loads}", SERVER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        for var in env:
            os.environ.pop(var)


def response(nouls, score, conf, drop=()):
    answers = {k: {"type": "noul", "noul": v} for k, v in zip(FIELDS, nouls)}
    answers["overall_readiness"] = {"type": "score", "score": score, "confidence": conf,
                                    "legend": {i: str(i) for i in range(5)},
                                    "probabilities": {i: 0.2 for i in range(5)}}
    for k in drop:
        del answers[k]
    return SystemOneResponse.model_validate({"model": "jev-1.13.0", "answers": answers,
                                             "usage": {"input_tokens": 1, "output_tokens": 0}})


class FakeClient:
    def __init__(self, result):
        self.result, self.states = result, []

    async def system_one(self, state, questions):
        self.states.append(state)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


TASK = "Target: src/auth/. Change: add a login test. Constraints: no commits. Ownership: tests/auth/. Acceptance: pytest tests/auth passes."


def ask(srv, result=None, battery="spec_readiness", task=TASK, context=None):
    if result is not None:
        srv._client = FakeClient(result)
    return asyncio.run(srv.ask(battery, task, context))


def check_error(out, kind):
    assert "error" in out and out["kind"] == kind, out
    assert out["verdict"]["act"] == "escalate" and out["mode"] == "shadow", out


srv = load()
assert srv.MODEL == "jev-1.13.0" and srv.CONFIG_ERROR is None and srv.MODE == "shadow"
assert tuple(k for k in srv.BATTERIES["spec_readiness"] if k != "overall_readiness") == FIELDS

GOOD = (0.9,) * 5
# (nouls, score, conf, round) -> (act, missing_fields, exhausted)
ROWS = {
    "ready": ((GOOD, 3.4, 0.8, "1"), ("dispatch", None, None)),
    "all unsure at floors": (((0.5,) * 5, 2.0, 0.35, "1"), ("clarify", list(FIELDS), None)),
    "one unsure field": (((0.9, 0.9, 0.6, 0.9, 0.9), 3.0, 0.7, "1"), ("clarify", ["constraints_stated"], None)),
    "just past unsure band": (((0.66,) * 5, 2.0, 0.35, "1"), ("dispatch", None, None)),
    "no acceptance": (((0.9, 0.9, 0.9, 0.9, 0.1), 1.6, 0.7, "1"), ("clarify", ["acceptance_testable"], None)),
    "ownership overlap": (((0.9, 0.9, 0.9, 0.2, 0.9), 3.0, 0.7, "1"), ("clarify", ["ownership_clear"], None)),
    "placeholder": (((0.1, 0.2, 0.1, 0.1, 0.1), 0.2, 0.9, "1"), ("clarify", list(FIELDS), None)),
    "low score only": ((GOOD, 1.5, 0.7, "1"), ("clarify", ["overall"], None)),
    "round 2 still weak": (((0.9, 0.9, 0.9, 0.9, 0.3), 1.8, 0.7, "2"), ("clarify", ["acceptance_testable"], True)),
    "round 2 ready": ((GOOD, 3.0, 0.7, "2"), ("dispatch", None, None)),
    "low conf": ((GOOD, 3.9, 0.2, "1"), ("escalate", None, None)),
    "low conf beats exhausted": (((0.1,) * 5, 0.5, 0.2, "2"), ("escalate", None, None)),
}
for name, ((nouls, score, conf, rnd), (act, missing, exhausted)) in ROWS.items():
    out = ask(srv, response(nouls, score, conf), context={"round": rnd})
    v = out["verdict"]
    assert (v["act"], v.get("missing_fields"), v.get("exhausted")) == (act, missing, exhausted), (name, v)
    assert v["round"] == int(rnd) and v["why"], (name, v)
    assert out["mode"] == "shadow" and "context_ignored" not in out, (name, out)
    assert set(out["judgments"]) == set(srv.BATTERIES["spec_readiness"]), (name, out)
    assert set(out["confidence"]) == {"overall_readiness"}, (name, out)
    assert out["spec_hash"] == "sha256:" + hashlib.sha256(TASK.encode()).hexdigest(), (name, out)
    assert isinstance(out["latency_ms"], int), (name, out)

# Mode is echoed, never applied: enforce returns the same verdict.
enf = load(SPECGATE_MODE="enforce")
out = ask(enf, response((0.9, 0.9, 0.9, 0.9, 0.1), 1.6, 0.7))
assert out["mode"] == "enforce" and out["verdict"]["act"] == "clarify", out

# Config: missing key, unexpanded host placeholders, bad floors, bad mode, empty env -> defaults.
check_error(ask(load()), "config")
check_error(ask(load(TYPESAFE_API_KEY="${user_config.typesafe_api_key}")), "config")
check_error(ask(load(TYPESAFE_API_KEY="   ")), "config")
for env in ({"SPECGATE_FLOOR_FIELD": "nan"}, {"SPECGATE_FLOOR_FIELD": "abc"}, {"SPECGATE_FLOOR_FIELD": "1.5"},
            {"SPECGATE_FLOOR_CONF": "-0.1"}, {"SPECGATE_FLOOR_CONF": "inf"},
            {"SPECGATE_FLOOR_SCORE": "4.5"}, {"SPECGATE_FLOOR_SCORE": "-1"}):
    bad = load(**env)
    check_error(ask(bad, response(GOOD, 3.4, 0.8)), "config")
bad = load(SPECGATE_MODE="block")
out = ask(bad, response(GOOD, 3.4, 0.8))
assert out["kind"] == "config" and out["verdict"]["act"] == "escalate" and out["mode"] == "block", out
ok = load(TYPESAFE_JEV_MODEL="", SPECGATE_FLOOR_FIELD="", SPECGATE_FLOOR_SCORE="", SPECGATE_FLOOR_CONF="",
          SPECGATE_MODE="${user_config.mode}")
assert ok.MODEL == "jev-1.13.0" and ok.CONFIG_ERROR is None and ok.MODE == "shadow", ok.CONFIG_ERROR
assert (ok.FLOOR_FIELD, ok.FLOOR_SCORE, ok.FLOOR_CONF) == (0.5, 2.0, 0.35)

# SDK errors.
out = ask(srv, TypeSafeAPITimeoutError(5.0))
check_error(out, "timeout")
assert out["error_type"] == "TypeSafeAPITimeoutError", out
check_error(ask(srv, TypeSafeAPIConnectionError("Connection error: refused")), "connection")
out = ask(srv, TypeSafeInternalServerError(503, None, httpx2.Headers({"x-typesafe-request-id": "req_1"})))
check_error(out, "api")
assert out["status"] == 503 and out["request_id"] == "req_1", out
out = ask(srv, TypeSafeAPIResponseValidationError(200, None, httpx2.Headers(), "answers.overall_readiness"))
check_error(out, "response")
assert out["error_type"] == "TypeSafeAPIResponseValidationError", out

# Bad responses: missing answer, non-finite or out-of-range Noul / score / confidence.
check_error(ask(srv, response(GOOD, 3.4, 0.8, drop=("ownership_clear",))), "response")
check_error(ask(srv, response(GOOD, 3.4, 0.8, drop=("overall_readiness",))), "response")
check_error(ask(srv, response((float("nan"),) + GOOD[1:], 3.4, 0.8)), "response")
check_error(ask(srv, response(GOOD, float("inf"), 0.8)), "response")
check_error(ask(srv, response(GOOD, 3.4, float("nan"))), "response")
for nouls, score, conf in (((2.0,) + GOOD[1:], 3.4, 0.8), ((-0.1,) + GOOD[1:], 3.4, 0.8),
                           (GOOD, 999.0, 0.8), (GOOD, -0.5, 0.8), (GOOD, 3.4, 2.0), (GOOD, 3.4, -0.1)):
    check_error(ask(srv, response(nouls, score, conf)), "response")

# Input validation.
out = ask(srv, response(GOOD, 3.4, 0.8), battery="nope")
check_error(out, "input")
assert out["available"] == ["spec_readiness"], out
check_error(ask(srv, task="x" * 8001), "input")
check_error(ask(srv, task="   "), "input")
check_error(ask(srv, context="repo=x"), "input")
for rnd in ("3", "0", None, True, "round 2"):
    check_error(ask(srv, context={"round": rnd}), "input")
assert ask(srv, response(GOOD, 3.4, 0.8), context={"round": 2})["verdict"]["round"] == 2  # int accepted

# Context allowlist: repo/siblings sent, round never sent, contract fixed server-side.
srv._client = fake = FakeClient(response(GOOD, 3.4, 0.8))
out = asyncio.run(srv.ask("spec_readiness", TASK, {"repo": "x", "siblings": "w2: docs/", "round": "1",
                                                   "contract": "y", "secret": "z"}))
sent = fake.states[-1]["context"]
assert sent == {**srv.DEFAULT_CONTEXT, "repo": "x", "siblings": "w2: docs/"}, sent
assert out["context_ignored"] == ["contract", "secret"], out
assert fake.states[-1]["task"] == TASK
out = asyncio.run(srv.ask("spec_readiness", TASK, {"siblings": "x" * 1000, "repo": "r" * 500}))
assert "error" not in out and fake.states[-1]["context"]["siblings"] == "x" * 1000, out

# Fail closed, before any request: a bad repo/siblings would otherwise read as the "none" default,
# an unencodable string would crash, a token or key would leave the machine.
sent = len(fake.states)
for ctx in ({"siblings": "x" * 1001}, {"repo": "r" * 501}, {"siblings": ["w2: src/"]}, {"repo": None}):
    out = asyncio.run(srv.ask("spec_readiness", TASK, ctx))
    check_error(out, "input")
    key = next(iter(ctx))
    assert f"context.{key}" in out["error"] and str(srv.CONTEXT_LIMITS[key]) in out["error"], out
check_error(ask(srv, task=TASK + " \ud800"), "input")
check_error(ask(srv, context={"siblings": "w2: \ud800"}), "input")
SECRETS = ("--dispatch-capability dcap__abc123", "--from term_3d7ab315-1a2b-4c3d-8e9f-0123456789ab",
           "-----BEGIN " + "RSA PRIVATE KEY-----", "TYPESAFE_API_KEY = abc", "sk-" + "a1" * 12,
           "ghp_" + "A1" * 18, "AKIA" + "ABCD1234" * 2, "xoxb-" + "1234-" * 3)
for secret in SECRETS:
    for task, ctx in ((f"{TASK}\n{secret}", None), (TASK, {"siblings": f"w2: docs/ {secret}"}),
                      (TASK, {"repo": secret})):
        out = ask(srv, task=task, context=ctx)
        check_error(out, "input")
        assert secret not in out["error"] and "secret" in out["error"], (secret, out)
assert len(fake.states) == sent, "an input error reached the client"
out = ask(srv, task=TASK + " Use task-create; risk-free; a short-term_plan; skip sk-learn.")
assert "error" not in out, out  # ordinary words are not tokens

print("OK")
