#!/usr/bin/env python3
"""Command-hook fallback of compact-nudge for surfaces without the function-hook UI.

The function hooks in register.tsx render through the terminal UI (AbovePrompt band,
toast, prompt.suggest), which the desktop Code tab does not draw. This script runs as a
plain UserPromptSubmit command hook instead, which every surface executes:

- reads the context size from the usage of the last main-chain assistant row of the
  transcript (free, no API call);
- once it reaches the next milestone (threshold, then +step), emits a systemMessage for
  the user and additionalContext asking Claude to end its reply with a drafted
  `/compact giữ lại: …; bỏ: …` line;
- `reset` mode (SessionStart compact|clear) clears the milestone.

Skipped on the terminal (`cli` entrypoint), where register.tsx already nudges.
Opt out: COMPACT_NUDGE_HOOK_OFF=1. Always exits 0 so it can never block a prompt.
"""
import json
import os
import re
import sys

TAIL_BYTES = 2 * 1024 * 1024


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


def context_tokens(rows):
    """Context of the last real main-chain assistant call; None when unknown."""
    for row in reversed(rows):
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

    prompt = event.get("prompt")
    if isinstance(prompt, str) and prompt.lstrip().startswith("/compact"):
        return
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
    size = fmt(tokens)
    print(json.dumps({
        "systemMessage": "compact-nudge: context %s — nên chạy /compact để giảm chi phí mỗi lượt." % size,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                "compact-nudge: the session context is about %s tokens. Handle the user's request "
                "normally, then end your reply with one short line in Vietnamese saying the context "
                "is %s and suggesting they run /compact, followed by ONE ready-to-copy command in a "
                "code block, at most 60 words: `/compact giữ lại: <current task, key files/functions, "
                "decisions made, open bugs or unfinished work>; bỏ: <long logs/outputs already handled, "
                "abandoned approaches>`. Never run /compact yourself."
            ) % (size, size),
        },
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
