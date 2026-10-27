#!/usr/bin/env python3
"""Command-hook fallback of compact-nudge for sessions where the hooks module does not nudge.

register.tsx nudges wherever a surface draws its pane/band (terminal, desktop Code tab) and
announces it by setting COMPACT_NUDGE_MODULE=1 for the process at session start. Everywhere
else (a Claude Code without function hooks, `claude -p`, SDK hosts) this script runs as a
plain Stop command hook instead:

- reads the context size from the usage of the last assistant row on the active chain of
  the transcript (free, no API call);
- once it reaches the next milestone (threshold, then every +step), emits only a
  systemMessage with a `/compact giữ lại: …; bỏ: …` command drafted by rules from the
  transcript (last wrap-up recap, open task-list items, edited files, commits, branch). It
  never blocks the stop and never adds model context, so the turn and its next-step box are
  left untouched;
- `reset` mode (SessionStart compact|clear) clears the milestone.

Opt out: COMPACT_NUDGE_HOOK_OFF=1. Always exits 0 so it can never block a turn.
"""
import json
import os
import re
import shlex
import sys
import time
from collections import Counter

READ_LIMIT = 64 * 1024 * 1024
STATE_TTL = 7 * 24 * 3600
WINDOW_SHARE = 0.8  # auto-compact runs near window - 33K: nudge before it does
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
DROP = "output test/lint và log dài đã xử lý xong"
FALLBACK_KEEP = "task đang làm, file đang sửa, quyết định đã chốt, các hướng đã thử và vì sao loại, việc còn dở"
SEPARATORS = ("&&", "||", ";", "|", "&")


def option(name, default):
    """Positive finite int from CLAUDE_PLUGIN_OPTION_<name>, else default."""
    try:
        value = float(os.environ.get("CLAUDE_PLUGIN_OPTION_" + name, default))
    except (TypeError, ValueError):
        return default
    if value != value or value <= 0 or value == float("inf"):
        return default
    return int(value)


def base_threshold(threshold):
    try:
        window = int(os.environ.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW", ""))
    except ValueError:
        return threshold
    return min(threshold, int(window * WINDOW_SHARE)) if window > 0 else threshold


def next_milestone(tokens, base, step):
    return base + step * ((tokens - base) // step + 1)


def read_rows(path):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - READ_LIMIT))
        chunk = f.read()
    lines = chunk.split(b"\n")
    if size > READ_LIMIT:
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


def active_chain(rows):
    """Rows of the branch the session is on, oldest first; rewound branches are left out.

    Follows parentUuid back from the last main-chain row, and across a compact boundary
    through logicalParentUuid. Rows without uuids (old formats) are kept in file order.
    """
    by_uuid = {r["uuid"]: r for r in rows if isinstance(r.get("uuid"), str)}
    if not by_uuid:
        return [r for r in rows if not r.get("isSidechain")]
    head = next((r for r in reversed(rows) if isinstance(r.get("uuid"), str) and not r.get("isSidechain")), None)
    chain, seen = [], set()
    while head is not None and head["uuid"] not in seen:
        seen.add(head["uuid"])
        chain.append(head)
        parent = head.get("parentUuid") or (head.get("logicalParentUuid") if is_boundary(head) else None)
        head = by_uuid.get(parent) if isinstance(parent, str) else None
    chain.reverse()
    return chain


def usage_tokens(usage):
    """Input + cache tokens of the call; the last real iteration when the call looped server-side."""
    iterations = usage.get("iterations")
    if isinstance(iterations, list):
        for it in reversed(iterations):
            if isinstance(it, dict) and it.get("type") not in ("advisor_message", "compaction"):
                usage = it
                break
    return sum(
        int(usage.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    )


def context_tokens(chain):
    """Context of the last real main-chain assistant call; None when unknown.

    Stops at a compact boundary with 0: rows before it measure the pre-compact context,
    and 0 also clears the milestone if the SessionStart reset did not run.
    """
    for row in reversed(chain):
        if is_boundary(row):
            return 0
        if row.get("type") != "assistant" or row.get("isSidechain"):
            continue
        message = row.get("message")
        usage = message.get("usage") if isinstance(message, dict) else None
        if not isinstance(usage, dict):
            continue
        total = usage_tokens(usage)
        if total > 0:  # synthetic/error rows carry zero usage
            return total
    return None


def result_text(part):
    content = part.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict) and isinstance(c.get("text"), str))
    return ""


def tool_results(chain):
    """tool_use_id -> (is_error, text) from the user rows that answer tool calls."""
    results = {}
    for row in chain:
        message = row.get("message")
        content = message.get("content") if row.get("type") == "user" and isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and part.get("type") == "tool_result" and isinstance(part.get("tool_use_id"), str):
                results[part["tool_use_id"]] = (bool(part.get("is_error")), result_text(part))
    return results


def tool_uses(chain):
    """(index in chain, id, name, input) of every main-chain tool call, in order."""
    for i, row in enumerate(chain):
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
                    yield i, part.get("id"), name, data


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
    done = data.get("done")
    for n in done if isinstance(done, list) else []:
        if isinstance(n, int) and not isinstance(n, bool) and 0 < n <= len(plan):
            plan[n - 1]["status"] = "completed"
    start = data.get("start")
    if isinstance(start, int) and not isinstance(start, bool) and 0 < start <= len(plan):
        plan[start - 1]["status"] = "in_progress"
    return plan


def apply_task(plan, name, data, result):
    """Replay TaskCreate/TaskUpdate; the id comes from 'Task #N' in the result, else the count."""
    if name == "TaskCreate":
        subject = data.get("subject")
        if not isinstance(subject, str):
            return plan
        found = re.search(r"#(\d+)", result)
        task_id = found.group(1) if found else str(sum(1 for i in plan if "id" in i) + 1)
        return plan + [{"id": task_id, "content": subject, "status": "pending"}]
    task_id = str(data.get("taskId", ""))
    status = data.get("status")
    if status == "deleted":
        return [i for i in plan if i.get("id") != task_id]
    for item in plan:
        if item.get("id") == task_id:
            if isinstance(status, str):
                item["status"] = status
            if isinstance(data.get("subject"), str):
                item["content"] = data["subject"]
    return plan


def segments(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    segment = []
    for token in lexer:
        if token in SEPARATORS:
            yield segment
            segment = []
        else:
            segment.append(token)
    yield segment


def subject(message):
    """First line of a commit message; the heredoc body for "$(cat <<'EOF' … EOF)"."""
    lines = message.splitlines()
    heredoc = re.match(r"\$\(\s*cat\s+<<-?\s*['\"]?(\w+)", lines[0]) if lines else None
    if heredoc:
        lines = [l for l in lines[1:] if l.strip() != heredoc.group(1) and l.strip() != ")"]
    first = next((l.strip() for l in lines if l.strip()), "")
    return first or None


def commit_message(command):
    """Subject of the first `git commit` in a shell command, or None."""
    if "git" not in command or "commit" not in command:
        return None
    try:
        parts = list(segments(command))
    except ValueError:
        return None
    for words in parts:
        while words and re.match(r"^\w+=", words[0]):
            words = words[1:]  # VAR=value git commit …
        if not words or os.path.basename(words[0]) != "git":
            continue
        i = 1
        while i < len(words) and words[i].startswith("-"):
            i += 2 if words[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
        if i >= len(words) or words[i] != "commit":
            continue
        args = words[i + 1:]
        for j, word in enumerate(args):
            if word in ("-m", "--message") or re.fullmatch(r"-[a-zA-Z]*m", word):
                return subject(args[j + 1]) if j + 1 < len(args) else None
            if word.startswith("--message="):
                return subject(word[len("--message="):])
            if re.fullmatch(r"-m.+", word):
                return subject(word[2:])
    return None


def short_names(paths):
    """Basename of each path, or more of the path where two basenames collide."""
    split = {path: path.replace("\\", "/").split("/") for path in paths}
    names = {}
    for path, parts in split.items():
        depth = 1
        while depth < len(parts) and sum(1 for other in split.values() if other[-depth:] == parts[-depth:]) > 1:
            depth += 1
        names[path] = "/".join(parts[-depth:])
    return names


def clip(text, limit):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def draft_command(chain):
    last_boundary = max((i for i, r in enumerate(chain) if is_boundary(r)), default=-1)
    results = tool_results(chain)
    recap, plan, commits = None, [], []
    files = Counter()
    last_seen = {}
    for n, (i, use_id, name, data) in enumerate(tool_uses(chain)):
        failed, text = results.get(use_id, (False, ""))
        if failed:
            continue
        recent = i > last_boundary
        # The task list carries over a compaction; recap, files and commits count from it.
        if name.endswith("__wrap_up"):
            plan = []  # wrap_up checks off the task list
            if recent and isinstance(data.get("recap"), str):
                recap = data["recap"]
        elif name.endswith("__update_plan"):
            plan = apply_plan(plan, data)
        elif name == "TodoWrite" and isinstance(data.get("todos"), list):
            plan = apply_plan(plan, {"items": data["todos"]})
        elif name in ("TaskCreate", "TaskUpdate"):
            plan = apply_task(plan, name, data, text)
        elif not recent:
            continue
        elif name in EDIT_TOOLS:
            path = data.get("file_path") or data.get("notebook_path")
            if isinstance(path, str) and path:
                files[path] += 1
                last_seen[path] = n
        elif name == "Bash" and isinstance(data.get("command"), str):
            message = commit_message(data["command"])
            if message and (not commits or commits[-1] != message):
                commits.append(message)

    keep = []
    if recap:
        keep.append(clip(recap, 300).rstrip(".;"))
    open_items = [i["content"] for i in plan if i["status"] in ("in_progress", "pending") and i["content"]]
    if open_items:
        keep.append("task còn dở: " + clip(", ".join(open_items[:4]), 200))
    if files:
        top = sorted(files, key=lambda f: (-files[f], -last_seen[f]))[:5]
        names = short_names(top)
        keep.append("file chính: " + ", ".join(names[f] for f in top))
    if commits:
        keep.append("commit: " + clip("; ".join(commits[-2:]), 160))
    branch = next((r["gitBranch"] for r in reversed(chain) if isinstance(r.get("gitBranch"), str) and r["gitBranch"]), None)
    if branch and keep:
        keep.append("branch " + branch)
    return "/compact giữ lại: %s; bỏ: %s" % ("; ".join(keep) or FALLBACK_KEEP, DROP)


def state_dir():
    return os.environ.get("CLAUDE_PLUGIN_DATA") or os.environ.get("TMPDIR") or "/tmp"


def state_path(session_id):
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", session_id)
    return os.path.join(state_dir(), "compact-nudge-" + safe + ".json")


def prune_states(keep):
    """Drop state files of sessions idle for a week: /clear starts a new id, so reset misses them."""
    base = state_dir()
    try:
        names = os.listdir(base)
    except OSError:
        return
    cutoff = time.time() - STATE_TTL
    for name in names:
        path = os.path.join(base, name)
        if name.startswith("compact-nudge-") and name.endswith(".json") and path != keep:
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except OSError:
                pass


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
    if os.environ.get("COMPACT_NUDGE_HOOK_OFF") == "1" or os.environ.get("COMPACT_NUDGE_MODULE") == "1":
        return
    # Read bytes: on Windows the text stdin uses the ANSI code page, not the UTF-8 Claude Code sends.
    event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    session_id = event.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return
    path = state_path(session_id)

    if sys.argv[1:2] == ["reset"]:
        clear(path)
        return

    transcript = event.get("transcript_path")
    if not isinstance(transcript, str) or not os.path.isfile(transcript):
        return
    prune_states(path)
    chain = active_chain(read_rows(transcript))
    tokens = context_tokens(chain)
    if tokens is None:
        return
    base = base_threshold(option("THRESHOLD", 200000))
    step = option("STEP", 100000)
    next_at = read_next_at(path)
    if tokens < base:
        if next_at is not None:
            clear(path)  # context dropped: compacted or rewound without a SessionStart event
        return
    if tokens < max(next_at or base, base):
        return

    try:
        command = draft_command(chain)
    except Exception:
        command = "/compact giữ lại: %s; bỏ: %s" % (FALLBACK_KEEP, DROP)
    # ensure_ascii keeps stdout ASCII, so no console code page can fail to encode it.
    print(json.dumps({
        "systemMessage": "compact-nudge: context %s — nên compact để giảm chi phí mỗi lượt. "
        "Lệnh gợi ý (sửa nếu cần):\n%s" % (fmt(tokens), command),
    }))
    sys.stdout.flush()
    write_next_at(path, next_milestone(tokens, base, step))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
