#!/usr/bin/env python3
"""jev-gate: gate agent tool calls before they run — rule lock, REUSE ledger, TypeSafe Jev judgments.

hooks: gate.py pre | post | reset   (hook JSON on stdin; stdlib only, Python >= 3.9)
test:  python3 test_gate.py          (offline)
env:   JEV_GATE_MODE, else CLAUDE_PLUGIN_OPTION_MODE: "shadow" (default) | "enforce"
       CLAUDE_PLUGIN_OPTION_TYPESAFE_API_KEY, else TYPESAFE_API_KEY (never logged)
       TYPESAFE_JEV_MODEL (default "jev-1.13.0" — pinned, bump only after re-reviewing shadow data)
       JEV_GATE_STATE_DIR (default ~/.local/state/jev-gate)
shadow:  only lock rules act (ask); Jev runs in a detached child and REUSE/Jev decisions are logged.
enforce: lock + Jev ask, and REUSE denies one unchanged expensive re-run. Auto-allow is never applied.
Fail-open: any error exits 0 with no output, so the host's normal permission flow applies.
"""
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.request

MODEL = os.environ.get("TYPESAFE_JEV_MODEL") or "jev-1.13.0"
API_URL = "https://api.typesafe.ai/v1/systemone"
JEV_TIMEOUT = 1.5  # s; enforce mode waits on it, shadow mode runs it detached
MAX_ACTION = 2000  # chars of action sent to Jev and logged
ASK_AT = 0.7  # outward / destructive Noul; 0.5 asked on read-only gh/orca calls in shadow data
ALLOW_AT, CALM_AT = 0.9, 0.1  # would-allow: logged only, never applied in this version
EXTERNAL_AT = 0.5  # external_state Noul at or above this -> never REUSE
REUSE_WINDOW_S, REUSE_MIN_BYTES, REUSE_MIN_MS = 900, 4096, 5000

# Lock rules run in code before Jev: a model can be persuaded, a rule can't.
# ponytail: plain regex over the command text, so `git commit -m "... git push ..."` also asks; parse argv if that noise matters.
GIT = r"\bgit(?:\s+-[Cc]\s+\S+|\s+--?[\w-]+(?:=\S+)?)*\s+"
LOCKS = [
    ("git-push", GIT + r"push\b", "pushes to a git remote"),
    ("git-discard", GIT + r"(?:reset\s+(?:\S+\s+)*--hard|clean\s+(?:\S+\s+)*-\w*f|branch\s+(?:\S+\s+)*-D"
     r"|stash\s+(?:drop|clear)|checkout\s+(?:--\s+)?\.(?:\s|$)|restore\s+(?:\S+\s+)*\.(?:\s|$))",
     "discards git work"),
    ("publish", r"\b(?:(?:npm|pnpm|yarn|bun)\s+publish|cargo\s+publish|twine\s+upload|gem\s+push)\b",
     "publishes a package"),
    ("pipe-to-shell", r"\b(?:curl|wget)\b[^\n;]*\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b", "runs a downloaded script"),
    ("sudo", r"(?:^|[;&|(]\s*)sudo\s", "runs as root"),
    ("rm-broad", r"\brm\s+(?:-\w+\s+)*-\w*[rR]\w*\s+(?:-\w+\s+)*(?:/|~|\$HOME|\.\.?|\*)/?\*?(?:\s|$)",
     "recursively deletes a root, home, or whole directory"),
]
LOCK_RES = [(rule, re.compile(rx, re.M), why) for rule, rx, why in LOCKS]
LOCK_WHY = {rule: why for rule, _, why in LOCKS}

HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_][\w-]*)\1")
SHELL_HEREDOC = re.compile(r"\b(?:(?:ba|z|k|da)?sh|ssh\s+\S+)\s+(?:-\S+\s+)*<<")  # heredoc body is code

SECRETS = re.compile("|".join([
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)",
    r"(?i:\bbearer\s+[\w.~+/=-]{8,})",
    r"\b(?:sk|pk|rk)-[\w-]{16,}",
    r"\bgh[pousr]_\w{20,}|\bgithub_pat_\w{20,}",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"\bxox[abprs]-[\w-]{10,}",
    r"\bdcap_[\w-]{20,}",  # Orca dispatch capability
    r"://[^/\s:@]+:[^/\s@]+@",
    r"(?i:[\w-]*(?:api[_-]?key|token|secret|passw(?:or)?d)[\w-]*[\"']?\s*[=:]\s*[\"']?[^\s\"']{4,})",
    r"(?i:--(?:api[_-]?key|token|secret|password)[\s=]+[\"']?[^\s\"']{4,})",
]))  # scoped (?i:...) flags: a bare mid-pattern (?i) is an error on Python >= 3.11

READ_ONLY = {"basename", "cat", "cd", "cut", "date", "df", "diff", "dirname", "du", "echo", "file", "find",
             "grep", "head", "jq", "ls", "nl", "printf", "pwd", "realpath", "rg", "sort", "stat", "tail",
             "type", "uniq", "wc", "which"}
GIT_READ = {"blame", "describe", "diff", "grep", "log", "ls-files", "rev-parse", "show", "status"}
PUNCT = ";&|<>()\n"  # shell operator characters; shlex returns a run of them as one token
WRITE_FLAGS = {"find": ("-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf", "-fls"),
               "sort": ("-o",)}
# Orca's coordinator protocol is local IPC, yet Jev scored worker heartbeats outward 0.75-0.96 in shadow data: an
# ask there stalls an unattended worker, and a Codex deny says "escalate", which is another send. Never fast: the
# result depends on other agents, so it must not earn REUSE.
ORCA_IPC = {"orca orchestration " + c for c in ("send", "check", "reply", "ask", "worker-read", "worker-list",
                                                "dispatch-show")}
MCP_READ = re.compile(r"(?:^|[_-])(?:get|list|search|read|fetch|query|find|view|describe|lookup)(?:[_-]|$)", re.I)

QUESTIONS = {
    "read_only": {"type": "noul", "instructions": (
        "Does performing `action` only read or display information, without creating, changing, or "
        "deleting any file, repository, process, or remote resource?")},
    "destructive": {"type": "noul", "instructions": (
        "Could performing `action` permanently delete or overwrite data, such as files, uncommitted work, "
        "git history or branches, databases, or cloud resources, in a way that is hard to recover?")},
    "outward": {"type": "noul", "instructions": (
        "Does performing `action` send data or make a change outside this computer, such as pushing to a "
        "git remote, publishing a package, deploying, sending a message or email, writing through a remote "
        "API, or spending money?")},
    "external_state": {"type": "noul", "instructions": (
        "Could performing `action` twice give different results even if no local file changed, because its "
        "result depends on the network, remote services, running processes, the clock, or randomness?")},
}


def strip_heredocs(cmd):
    """Replace heredoc bodies with a line count: file contents never reach Jev or the log."""
    lines, out, i = cmd.split("\n"), [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        m = HEREDOC.search(line)
        if not m:
            continue
        n = 0
        while i < len(lines) and lines[i].strip() != m.group(2):
            i, n = i + 1, n + 1
        out.append("<heredoc: %d lines>" % n)
        if i < len(lines):
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def redact(text):
    """-> (redacted text, whether anything secret-looking was found)."""
    red = SECRETS.sub("<redacted>", text)
    return red, red != text


def lock_rule(cmd):
    for rule, rx, _ in LOCK_RES:
        if rx.search(cmd):
            return rule
    return None


def fastpath_bash(cmd, ipc=False):
    """True when every segment is a known read-only command with no redirect or substitution.
    ipc=True also accepts Orca coordinator-protocol segments (ORCA_IPC). shlex splits the segments, so an
    operator inside a quoted argument, such as a message body, stays text."""
    c = re.sub(r"\d?>\s*/dev/null|2>&1", "", cmd)
    if re.search(r"`|\$\(|<\(", c):  # substitution runs even inside double quotes
        return False
    lex = shlex.shlex(c, posix=True, punctuation_chars=PUNCT)
    lex.whitespace, lex.whitespace_split, lex.commenters = " \t\r", True, ""  # newline separates; `#` is text
    segs = [[]]
    try:
        for t in lex:
            if not set(t) <= set(PUNCT):
                segs[-1].append(t)
            elif ">" in t:
                return False
            elif t.strip("<"):  # `<` and `<<<` only read input; every other operator starts a segment
                segs.append([])
    except ValueError:  # unbalanced quote
        return False
    for w in segs:
        if not w or ipc and " ".join(w[:3]) in ORCA_IPC:
            continue
        if w[0] == "git":
            sub, it = None, iter(w[1:])
            for x in it:
                if x in ("-C", "-c"):
                    next(it, None)
                elif not x.startswith("-"):
                    sub = x
                    break
            if sub not in GIT_READ:
                return False
        elif w[0] not in READ_ONLY or any(a.startswith(WRITE_FLAGS.get(w[0], ("\0",))) for a in w[1:]):
            return False
    return True


def fingerprint(cwd):
    """Hash of HEAD + working-tree status + mtimes/sizes of changed files; None outside git."""
    def git(*args):
        return subprocess.run(("git", "--no-optional-locks", "-C", cwd) + args, capture_output=True,
                              timeout=1, check=True).stdout
    try:
        top, head = git("rev-parse", "--show-toplevel", "HEAD").splitlines()[:2]
        status = git("status", "--porcelain", "-z", "-uall")
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    # ponytail: gitignored files (build output, node_modules) are invisible here; add their roots if REUSE misfires.
    h = hashlib.sha1(head + b"\0" + status)
    for entry in filter(None, status.split(b"\0")):
        try:
            st = os.stat(os.path.join(os.fsdecode(top), os.fsdecode(entry[3:])))
            h.update(b"%d:%d;" % (st.st_mtime_ns, st.st_size))
        except (OSError, ValueError):
            pass  # deleted file, or the source path of a rename
    return h.hexdigest()[:16]


def state_dir():
    return os.environ.get("JEV_GATE_STATE_DIR") or os.path.join(os.path.expanduser("~"), ".local", "state", "jev-gate")


def ledger_path(sid):
    return os.path.join(state_dir(), "sessions", re.sub(r"[^\w.-]", "_", sid or "unknown") + ".jsonl")


def append(sid, rec):
    path = ledger_path(sid)
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load(sid):
    """Events since the last reset (compaction or /clear)."""
    try:
        with open(ledger_path(sid), encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    events = []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("ev") == "reset":
            events = []
        else:
            events.append(e)
    return events


def gates(events):
    """Gate records in order, with each detached judge's decision merged in."""
    by_id = {}
    for e in events:
        if e.get("ev") == "gate":
            by_id[e["id"]] = dict(e)
        elif e.get("ev") == "judge" and e.get("id") in by_id:
            by_id[e["id"]].update(decision=e.get("decision"), judgments=e.get("judgments"))
    return list(by_id.values())


def reuse_candidate(events, rec, now):
    """The earlier identical run whose output Claude already has, or None. Nudges once per (command, state)."""
    if not rec.get("key") or not rec.get("fp"):
        return None
    same = [g for g in gates(events) if g.get("key") == rec["key"] and g.get("agent") == rec.get("agent")
            and g["id"] != rec["id"]]
    if not same or any(g.get("decision") == "reuse" and g.get("fp") == rec["fp"] for g in same):
        return None
    prev = same[-1]
    out = next((e for e in reversed(events) if e.get("ev") == "out" and e.get("id") == prev["id"]), None)
    if prev.get("fp") != rec["fp"] or out is None or now - prev["ts"] > REUSE_WINDOW_S:
        return None
    if out["bytes"] < REUSE_MIN_BYTES and (out.get("dur_ms") or 0) < REUSE_MIN_MS:
        return None
    return {"id": prev["id"], "age_s": int(now - prev["ts"]), "bytes": out["bytes"], "ok": out["ok"]}


def policy(rec, j):
    """Pure decision from code signals + Jev nouls (None when not asked or failed) -> (decision, why)."""
    if rec.get("rule"):
        return "ask", "locked by rule %s: %s" % (rec["rule"], LOCK_WHY[rec["rule"]])
    if j and (j["outward"] >= ASK_AT or j["destructive"] >= ASK_AT):
        return "ask", "Jev: outward %.2f, destructive %.2f" % (j["outward"], j["destructive"])
    cand = rec.get("reuse")
    if cand and (rec.get("fast") or (j and j["external_state"] < EXTERNAL_AT)):
        return "reuse", (
            "REUSE: you ran this exact command %ds ago and no tracked file changed since; its %.1f KB output "
            "(%s) is already in your context. Use that result instead of re-running. If it is no longer in your "
            "context, or you expect a different result, run the same command again: it will not be blocked twice."
            % (cand["age_s"], cand["bytes"] / 1024, "succeeded" if cand["ok"] else "failed"))
    if (j and j["read_only"] >= ALLOW_AT and max(j["outward"], j["destructive"]) < CALM_AT
            and "#" not in rec.get("action", "") and "\n" not in rec.get("action", "")):
        return "allow", "Jev: read-only %.2f" % j["read_only"]
    return "proceed", ""


def render(decision, why, harness):
    """Hook stdout for an applied decision. Codex has no "ask" yet, so it becomes a deny Claude/Codex can read."""
    if decision == "ask" and harness != "codex":
        out = {"permissionDecision": "ask", "permissionDecisionReason": "jev-gate: " + why}
    else:
        reason = "jev-gate: " + why
        if decision == "ask":
            reason += (" -- this needs a human decision. Do not work around it: ask the user, or, as a "
                       "dispatched worker, escalate to your coordinator.")
        out = {"permissionDecision": "deny", "permissionDecisionReason": reason}
    return {"hookSpecificOutput": dict(hookEventName="PreToolUse", **out)}


def api_key():
    return os.environ.get("CLAUDE_PLUGIN_OPTION_TYPESAFE_API_KEY") or os.environ.get("TYPESAFE_API_KEY")


def ask_jev(kind, action, key):
    """-> (nouls or None, meta). Never raises; one attempt, short timeout."""
    t = time.monotonic()
    body = json.dumps({"model": MODEL, "state": {"kind": kind, "action": action}, "questions": QUESTIONS})
    req = urllib.request.Request(API_URL, body.encode(), {"Authorization": "Bearer " + key,
                                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=JEV_TIMEOUT) as r:
            resp = json.load(r)
        j = {k: float(resp["answers"][k]["noul"]) for k in QUESTIONS}
        if not all(0 <= v <= 1 for v in j.values()):  # also rejects NaN, which would fail open silently
            raise ValueError("noul out of range")
    except Exception as e:  # network, HTTP status, malformed body: fail open
        return None, {"error": type(e).__name__, "status": getattr(e, "code", None),
                      "latency_ms": int((time.monotonic() - t) * 1000)}
    return j, {"model": resp.get("model"), "usage": resp.get("usage"),
               "latency_ms": int((time.monotonic() - t) * 1000)}


def mode():
    m = os.environ.get("JEV_GATE_MODE") or os.environ.get("CLAUDE_PLUGIN_OPTION_MODE") or "shadow"
    return m if m in ("shadow", "enforce") else "shadow"


def harness():
    return "codex" if os.environ.get("PLUGIN_ROOT") else "claude"  # Codex sets PLUGIN_ROOT; Claude Code doesn't


def pre(ev):
    tool, ti = ev.get("tool_name") or "", ev.get("tool_input") or {}
    sid, now, m = ev.get("session_id") or "unknown", time.time(), mode()
    rec = {"ev": "gate", "id": ev.get("tool_use_id") or "t%d" % time.time_ns(), "ts": round(now, 3),
           "agent": ev.get("agent_id"), "tool": tool, "mode": m, "harness": harness(), "key": None, "fp": None}
    if tool == "Bash":
        raw = ti.get("command") or ""
        stripped = strip_heredocs(raw)
        kind, (action, secret) = "shell command", redact(stripped)
        rule = lock_rule(raw if SHELL_HEREDOC.search(raw) else stripped)
        fast = fastpath_bash(stripped)
        ipc = not fast and fastpath_bash(stripped, ipc=True)
        rec["key"] = hashlib.sha1(" ".join(raw.split()).encode()).hexdigest()[:16]
        if not rule:
            rec["fp"] = fingerprint(ev.get("cwd") or os.getcwd())
    elif tool.startswith("mcp__"):
        parts = tool.split("__", 2)
        name = parts[2] if len(parts) == 3 else tool
        kind, secret, rule, ipc = "MCP tool call", False, None, False
        action = "%s.%s(%s)" % (parts[1] if len(parts) == 3 else "", name, ", ".join(sorted(map(str, ti))))
        fast = bool(MCP_READ.search(name))  # argument values never leave the machine
    else:
        return None
    rec.update(action=action[:MAX_ACTION], rule=rule, fast=fast,
               source="lock" if rule else "fastpath" if fast else "ipc" if ipc else "secret" if secret else "jev")
    rec["reuse"] = reuse_candidate(load(sid), rec, now) if rec["fp"] else None
    key, j = api_key(), None
    if rec["source"] == "jev" and not key:
        rec["source"] = "no-key"
    judge_later = rec["source"] == "jev" and m == "shadow"
    if rec["source"] == "jev" and m == "enforce":
        j, meta = ask_jev(kind, rec["action"], key)
        rec.update(meta, judgments=j)
    decision, why = ("pending", "") if judge_later else policy(rec, j)
    applied = decision == "ask" and (rule is not None or m == "enforce") or decision == "reuse" and m == "enforce"
    rec.update(decision=decision, why=why, applied=applied)
    try:
        append(sid, rec)  # the ledger never depends on the network or the child
        if judge_later:
            child = subprocess.Popen([sys.executable, os.path.abspath(__file__), "judge"], stdin=subprocess.PIPE,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            child.stdin.write(json.dumps({"sid": sid, "kind": kind, "rec": rec}).encode())
            child.stdin.close()
    except OSError:
        pass  # logging must never cost the lock
    return render(decision, why, rec["harness"]) if applied else None


def judge(job):
    """Detached shadow judgment: ask Jev, log what enforce mode would have done."""
    rec = job["rec"]
    j, meta = ask_jev(job["kind"], rec["action"], api_key() or "")
    decision, why = policy(rec, j)
    append(job["sid"], dict(meta, ev="judge", id=rec["id"], ts=round(time.time(), 3), judgments=j,
                            decision=decision, why=why))


def post(ev):
    tool = ev.get("tool_name") or ""
    if tool != "Bash" and not tool.startswith("mcp__"):
        return
    failed = ev.get("hook_event_name") == "PostToolUseFailure" or "error" in ev
    resp = ev.get("error") if failed else ev.get("tool_response")
    if isinstance(resp, dict) and tool == "Bash":
        text = (resp.get("stdout") or "") + (resp.get("stderr") or "")
        failed = failed or bool(resp.get("interrupted"))
    else:
        text = resp if isinstance(resp, str) else json.dumps(resp, ensure_ascii=False)
    data = text.encode("utf-8", "replace")
    append(ev.get("session_id") or "unknown", {
        "ev": "out", "id": ev.get("tool_use_id"), "ts": round(time.time(), 3), "tool": tool, "bytes": len(data),
        "sha": hashlib.sha1(data).hexdigest()[:12], "ok": not failed, "dur_ms": ev.get("duration_ms")})


def main(argv):
    event = json.load(sys.stdin)
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "pre":
        out = pre(event)
        if out:
            sys.stdout.write(json.dumps(out))
    elif cmd == "post":
        post(event)
    elif cmd == "reset":
        append(event.get("session_id") or "unknown",
               {"ev": "reset", "ts": round(time.time(), 3), "source": event.get("source")})
    elif cmd == "judge":
        judge(event)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except BaseException:
        pass  # fail open: no output, exit 0 -> the host's normal permission flow
    sys.exit(0)
