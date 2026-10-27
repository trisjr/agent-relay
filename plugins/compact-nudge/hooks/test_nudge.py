"""Offline checks for nudge.py: python3 test_nudge.py (never calls the network)."""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nudge  # noqa: E402

STATE = tempfile.mkdtemp()
ENV = {k: v for k, v in os.environ.items()
       if not k.startswith("CLAUDE_PLUGIN_OPTION_") and k not in (
           "COMPACT_NUDGE_MODULE", "COMPACT_NUDGE_HOOK_OFF", "CLAUDE_CODE_AUTO_COMPACT_WINDOW")}
ENV["CLAUDE_PLUGIN_DATA"] = STATE


class Transcript:
    """Builds a .jsonl transcript row by row, each row chained to the one before."""

    def __init__(self):
        self.rows = []
        self.head = None

    def add(self, row, parent=None):
        row.setdefault("uuid", "u%d" % len(self.rows))
        row.setdefault("parentUuid", self.head if parent is None else parent)
        row.setdefault("isSidechain", False)
        row.setdefault("gitBranch", "feat/eur")
        self.rows.append(row)
        self.head = row["uuid"]
        return row["uuid"]

    def assistant(self, tokens=0, tools=(), parent=None):
        content = [{"type": "tool_use", "id": "t%d_%d" % (len(self.rows), n), "name": name, "input": data}
                   for n, (name, data) in enumerate(tools)]
        usage = {"input_tokens": 2, "cache_creation_input_tokens": 0, "cache_read_input_tokens": max(0, tokens - 2)}
        return self.add({"type": "assistant", "message": {"content": content, "usage": usage if tokens else {}}}, parent)

    def result(self, tool_use_id, text="ok", is_error=False):
        part = {"type": "tool_result", "tool_use_id": tool_use_id, "content": text, "is_error": is_error}
        return self.add({"type": "user", "message": {"content": [part]}})

    def boundary(self):
        last = self.head
        return self.add({"type": "system", "subtype": "compact_boundary", "logicalParentUuid": last}, parent="")

    def write(self, padding=0):
        path = os.path.join(tempfile.mkdtemp(), "t.jsonl")
        with open(path, "w") as f:
            if padding:
                f.write(json.dumps({"type": "file-history-snapshot", "pad": "x" * padding}) + "\n")
            for row in self.rows:
                f.write(json.dumps(row) + "\n")
        return path


def run(path, sub=None, session="s1", **env):
    event = {"session_id": session, "transcript_path": path, "hook_event_name": "Stop"}
    args = [sys.executable, os.path.join(HERE, "nudge.py")] + ([sub] if sub else [])
    p = subprocess.run(args, input=json.dumps(event).encode(), capture_output=True, env=dict(ENV, **env), timeout=20)
    assert p.returncode == 0, p
    out = p.stdout.decode("ascii")  # stdout must stay ASCII on every console
    return json.loads(out)["systemMessage"] if out else None


def nudge_at(tokens, session, **env):
    t = Transcript()
    t.assistant(tokens)
    return run(t.write(), session=session, **env)


def test_commit_message():
    heredoc = "git commit -m \"$(cat <<'EOF'\nfeat: EUR price table\n\nbody\nEOF\n)\""
    cases = {
        heredoc: "feat: EUR price table",
        'git commit -am "fix: rounding"': "fix: rounding",
        'git commit --message="docs: readme"': "docs: readme",
        'git commit -m"short"': "short",
        'git -C repo commit -m "x: y"': "x: y",
        'python -m pytest -q && git commit -m "fix: rounding"': "fix: rounding",
        'git tag -m "release v1" v1 && git commit -m real': "real",
        'cd app && GIT_AUTHOR_NAME=a git commit -m "chore: bump"': "chore: bump",
    }
    for command, expected in cases.items():
        assert nudge.commit_message(command) == expected, (command, nudge.commit_message(command))
    for command in ('grep -m 1 "commit" log.txt && git status', "git commit-tree abc -m plumbing", "git commit",
                    "echo 'unterminated"):
        assert nudge.commit_message(command) is None, command


def test_usage_iterations():
    looped = {"input_tokens": 300000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
              "iterations": [{"type": "message", "input_tokens": 100000},
                             {"type": "message", "input_tokens": 150000},
                             {"type": "advisor_message", "input_tokens": 50000}]}
    assert nudge.usage_tokens(looped) == 150000
    assert nudge.usage_tokens({"input_tokens": 5, "cache_read_input_tokens": 10}) == 15


def test_chain_and_boundary():
    t = Transcript()
    root = t.assistant(1000)
    t.assistant(900000, [("Edit", {"file_path": "/a/abandoned.py"})])  # rewound branch
    t.assistant(250000, [("Edit", {"file_path": "/a/kept.py"})], parent=root)
    chain = nudge.active_chain(t.rows)
    assert [r["uuid"] for r in chain] == ["u0", "u2"]
    assert nudge.context_tokens(chain) == 250000
    assert "abandoned" not in nudge.draft_command(chain)

    t.boundary()
    assert nudge.context_tokens(nudge.active_chain(t.rows)) == 0


def test_plan_replay():
    assert nudge.apply_plan([], {"done": 2}) == []  # bad shape: ignored, no TypeError
    plan = nudge.apply_plan([], {"items": [{"content": "a", "status": "in_progress"}, {"content": "b", "status": "pending"}]})
    assert [i["status"] for i in nudge.apply_plan(plan, {"advance": True})] == ["completed", "in_progress"]
    assert nudge.apply_plan(plan, {"start": True})[0]["status"] == "completed"  # bool is not a step

    t = Transcript()
    a = t.assistant(1000, [("TaskCreate", {"subject": "migrate pricing"}), ("TaskCreate", {"subject": "update PDF"})])
    t.result("t%d_0" % 0, "Task #1 created successfully: migrate pricing")
    t.result("t%d_1" % 0, "Task #2 created successfully: update PDF")
    t.boundary()  # the task list survives a compaction
    t.assistant(1000, [("TaskUpdate", {"taskId": "1", "status": "completed"})])
    assert a == "u0"
    command = nudge.draft_command(nudge.active_chain(t.rows))
    assert "task còn dở: update PDF" in command, command
    assert "migrate pricing" not in command


def test_files_and_failed_calls():
    t = Transcript()
    t.assistant(1000, [("Edit", {"file_path": "/repo/src/a/index.ts"}), ("Edit", {"file_path": "/repo/src/b/index.ts"}),
                       ("Bash", {"command": 'git commit -m "feat: never landed"'})])
    t.result("t0_2", "pre-commit hook failed", is_error=True)
    command = nudge.draft_command(nudge.active_chain(t.rows))
    assert "a/index.ts" in command and "b/index.ts" in command, command
    assert "never landed" not in command
    assert "các hướng đã" not in command.split("bỏ:")[1]  # never tell the summary to drop ruled-out paths


def test_milestones():
    assert run(Transcript().write()) is None
    assert nudge_at(150000, "m") is None
    first = nudge_at(262000, "m")
    assert first and "262K" in first and "/compact giữ lại:" in first, first
    assert nudge_at(290000, "m") is None  # next milestone is 300K, not 362K
    assert nudge_at(301000, "m") is not None
    assert nudge_at(20000, "m") is None  # dropped below the threshold: state cleared
    assert nudge_at(210000, "m") is not None

    assert nudge_at(262000, "r") is not None
    run(Transcript().write(), sub="reset", session="r")
    assert nudge_at(262000, "r") is not None


def test_options_and_owner():
    assert nudge_at(262000, "own", COMPACT_NUDGE_MODULE="1") is None  # register.tsx nudges
    assert nudge_at(262000, "off", COMPACT_NUDGE_HOOK_OFF="1") is None
    assert nudge_at(120000, "th", CLAUDE_PLUGIN_OPTION_THRESHOLD="100000") is not None
    assert nudge_at(262000, "st", CLAUDE_PLUGIN_OPTION_STEP="0") is not None
    assert nudge_at(263000, "st", CLAUDE_PLUGIN_OPTION_STEP="0") is None  # step 0 falls back to 100K
    assert nudge_at(262000, "inf", CLAUDE_PLUGIN_OPTION_THRESHOLD="inf") is not None
    assert nudge_at(165000, "win", CLAUDE_CODE_AUTO_COMPACT_WINDOW="200000") is not None
    assert nudge_at(262000, "raise") is not None
    assert nudge_at(310000, "raise", CLAUDE_PLUGIN_OPTION_THRESHOLD="400000") is None  # raised threshold wins


def test_large_transcript_keeps_draft():
    t = Transcript()
    t.assistant(1000, [("TodoWrite", {"todos": [{"content": "migrate pricing", "status": "in_progress"}]}),
                       ("Edit", {"file_path": "/repo/pricing.service.ts"})])
    t.add({"type": "user", "message": {"content": "x"}, "toolUseResult": {"stdout": "y" * (3 * 1024 * 1024)}})
    t.assistant(262000)
    message = run(t.write(padding=1024 * 1024), session="big")
    assert "migrate pricing" in message and "pricing.service.ts" in message and "branch feat/eur" in message, message


def test_prune_old_states():
    old = os.path.join(STATE, "compact-nudge-old.json")
    with open(old, "w") as f:
        json.dump({"nextAt": 1}, f)
    stale = time.time() - nudge.STATE_TTL - 60
    os.utime(old, (stale, stale))
    nudge_at(1000, "prune")
    assert not os.path.exists(old)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
