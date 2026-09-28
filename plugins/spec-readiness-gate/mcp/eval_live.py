"""Opt-in battery re-eval: score golden.json through server.ask against the REAL TypeSafe API
(needs TYPESAFE_API_KEY, billed ~$0.00003 per case). Run after changing battery wording, the contract
string, or TYPESAFE_JEV_MODEL — evals/evals.json checks skill behavior only and never scores Jev.
uv run --with "mcp[cli]>=2.2,<3" --with "typesafe-sdk>=0.7.1,<0.8" python eval_live.py"""
import asyncio
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the plugin dir
sys.path.insert(0, str(Path(__file__).parent))
import server  # noqa: E402


async def main() -> int:
    cases = json.loads(Path(__file__).with_name("golden.json").read_text())
    outs = await asyncio.gather(*(server.ask("spec_readiness", c["task"], c.get("context")) for c in cases))
    failed = 0
    for c, out in zip(cases, outs):
        v = out["verdict"]
        acts = c["act"] if isinstance(c["act"], list) else [c["act"]]
        ok = ("error" not in out and v["act"] in acts
              and set(c.get("missing", ())) <= set(v.get("missing_fields", ()))
              and v.get("exhausted") == c.get("exhausted"))
        failed += not ok
        got = out.get("kind") or v.get("missing_fields", "")
        print(f"{'PASS' if ok else 'FAIL'} {c['name']}: {v['act']} {got} — {v['why']}")
    print(f"{len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


sys.exit(asyncio.run(main()))
