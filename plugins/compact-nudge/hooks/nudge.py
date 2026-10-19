#!/usr/bin/env python3
"""Command-hook fallback of compact-nudge for surfaces without the function-hook UI.

The function hooks in register.tsx render through the terminal UI (AbovePrompt band,
toast, prompt.suggest), which the desktop Code tab does not draw. This script runs as a
plain Stop command hook instead, which every surface executes:

- reads the context size from the usage of the last main-chain assistant row of the
  transcript (free, no API call);
- once it reaches the next milestone (threshold, then +step), emits only a systemMessage
  with a `/compact giữ lại: …; bỏ: …` command drafted by rules from the transcript
  (last wrap-up recap, open task-list items, edited files, commits, branch). It never
  blocks the stop and never adds model context, so the turn and its next-step box are
  left untouched;
- `reset` mode (SessionStart compact|clear) clears the milestone.

Skipped on the terminal (`cli` entrypoint), where register.tsx already nudges.
Opt out: COMPACT_NUDGE_HOOK_OFF=1. Always exits 0 so it can never block a turn.
"""
import json
import os
import re
import shlex
import sys
from collections import Counter

TAIL_BYTES = 2 * 1024 * 1024
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
DROP = "output test/lint, log grep/find, các file chỉ đọc qua, các hướng đã bỏ"
FALLBACK_KEEP = "task đang làm, file đang sửa, quyết định đã chốt, việc còn dở"


def option(name, default):
    try:
        return int(float(os.environ.get("CLAUDE_PLUGIN_OPTION_" + name, default)))
    except (TypeError, ValueError):
        return default


def tail_rows(path):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - TAIL_BYTES))
        chunk = f.read()
    lines = chunk.split(b"\n")
    if size > TAIL_BYTES:
        lines = lines[1:]  # first line is likely cut in half
    rows = []
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def is_boundary(row):
    return row.get("type") == "system" and row.get("subtype") == "compact_boundary"


def since_compact(rows):
    for i in range(len(rows) - 1, -1, -1):
        if is_boundary(rows[i]):
            return rows[i + 1:]
    return rows


def context_tokens(rows):
    """Context of the last real main-chain assistant call; None when unknown.

    Stops at a compact boundary with 0: rows before it measure the pre-compact context,
    and 0 also clears the milestone if the SessionStart reset did not run.
    """
    for row in reversed(rows):
        if is_boundary(row):
            return 0
        if row.get("type") != "assistant" or row.get("isSidechain"):
            continue
        message = row.get("message")
        usage = message.get("usage") if isinstance(message, dict) else None
        if not isinstance(usage, dict):
            continue
        total = sum(
            int(usage.get(k) or 0)
            for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
        )
        if total > 0:  # synthetic/error rows carry zero usage
            return total
    return None


def entrypoint(rows):
    value = os.environ.get("CLAUDE_CODE_ENTRYPOINT")
    if value:
        return value
    for row in reversed(rows):
        if isinstance(row.get("entrypoint"), str):
            return row["entrypoint"]
    return None


def tool_uses(rows):
    for row in rows:
        if row.get("type") != "assistant" or row.get("isSidechain"):
            continue
        message = row.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and part.get("type") == "tool_use":
                name = part.get("name")
                data = part.get("input")
                if isinstance(name, str) and isinstance(data, dict):
                    yield name, data


def apply_plan(plan, data):
    """Replay the desktop task list: items replaces it, advance/done/start move steps."""
    items = data.get("items")
    if isinstance(items, list):
        return [
            {"content": str(i.get("content", "")), "status": str(i.get("status", ""))}
            for i in items
            if isinstance(i, dict)
        ]
    if data.get("advance"):
        current = next((i for i in plan if i["status"] == "in_progress"), None)
        if current:
            current["status"] = "completed"
        following = next((i for i in plan if i["status"] == "pending"), None)
        if following:
            following["status"] = "in_progress"
    for n in data.get("done") or []:
        if isinstance(n, int) and 0 < n <= len(plan):
            plan[n - 1]["status"] = "completed"
    start = data.get("start")
    if isinstance(start, int) and 0 < start <= len(plan):
        plan[start - 1]["status"] = "in_progress"
    return plan


def commit_message(command):
    if "git" not in command or "commit" not in command:
        return None
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    for i, word in enumerate(words[:-1]):
        if word in ("-m", "--message"):
            return words[i + 1].splitlines()[0] if words[i + 1] else None
    return None


def clip(text, limit):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def draft_command(rows):
    recent = since_compact(rows)
    recap, plan, commits = None, [], []
    files = Counter()
    last_seen = {}
    for n, (name, data) in enumerate(tool_uses(recent)):
        if name.endswith("__wrap_up"):
            plan = []  # wrap_up checks off the task list
            if isinstance(data.get("recap"), str):
                recap = data["recap"]
        elif name.endswith("__update_plan"):
            plan = apply_plan(plan, data)
        elif name == "TodoWrite" and isinstance(data.get("todos"), list):
            plan = apply_plan(plan, {"items": data["todos"]})
        elif name in EDIT_TOOLS:
            path = data.get("file_path") or data.get("notebook_path")
            if isinstance(path, str) and path:
                base = os.path.basename(path)
                files[base] += 1
                last_seen[base] = n
        elif name == "Bash" and isinstance(data.get("command"), str):
            message = commit_message(data["command"])
            if message:
                commits.append(message)

    keep = []
    if recap:
        keep.append(clip(recap, 300).rstrip(".;"))
    open_items = [i["content"] for i in plan if i["status"] in ("in_progress", "pending") and i["content"]]
    if open_items:
        keep.append("task còn dở: " + clip(", ".join(open_items[:4]), 200))
    if files:
        top = sorted(files, key=lambda f: (-files[f], -last_seen[f]))[:5]
        keep.append("file chính: " + ", ".join(top))
    if commits:
        keep.append("commit: " + clip("; ".join(commits[-2:]), 160))
    branch = next((r["gitBranch"] for r in reversed(rows) if isinstance(r.get("gitBranch"), str) and r["gitBranch"]), None)
    if branch and keep:
        keep.append("branch " + branch)
    return "/compact giữ lại: %s; bỏ: %s" % ("; ".join(keep) or FALLBACK_KEEP, DROP)


def state_path(session_id):
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.environ.get("TMPDIR") or "/tmp"
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", session_id)
    return os.path.join(base, "compact-nudge-" + safe + ".json")


def read_next_at(path):
    try:
        with open(path) as f:
            return int(json.load(f)["nextAt"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def write_next_at(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"nextAt": value}, f)


def clear(path):
    try:
        os.remove(path)
    except OSError:
        pass


def fmt(tokens):
    return "%dK" % round(tokens / 1000)


def main():
    if os.environ.get("COMPACT_NUDGE_HOOK_OFF") == "1":
        return
    event = json.load(sys.stdin)
    session_id = event.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return
    path = state_path(session_id)

    if sys.argv[1:2] == ["reset"]:
        clear(path)
        return
    if event.get("stop_hook_active"):
        return  # another Stop hook made Claude continue; nudge when it really stops

    transcript = event.get("transcript_path")
    if not isinstance(transcript, str) or not os.path.isfile(transcript):
        return
    rows = tail_rows(transcript)
    if entrypoint(rows) == "cli":
        return

    tokens = context_tokens(rows)
    if tokens is None:
        return
    threshold = option("THRESHOLD", 200000)
    step = option("STEP", 100000)
    next_at = read_next_at(path)
    if next_at is not None and tokens < threshold:
        clear(path)  # context dropped: compacted without a SessionStart event
        return
    if tokens < (next_at or threshold):
        return

    write_next_at(path, tokens + step)
    print(json.dumps({
        "systemMessage": "compact-nudge: context %s — nên compact để giảm chi phí mỗi lượt. "
        "Lệnh gợi ý (sửa nếu cần):\n%s" % (fmt(tokens), draft_command(rows)),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
