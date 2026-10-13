#!/bin/sh
# Opt out: COMPOUND_RETROS_HOOK_OFF=1 or ${TMPDIR:-/tmp}/.compound-retros-off.
# After capture, mark ${TMPDIR:-/tmp}/compound-retros-reminded-<session_id>;
# session_id contains only [A-Za-z0-9._-].

exec 2>/dev/null
[ "${COMPOUND_RETROS_HOOK_OFF:-}" = 1 ] && exit 0
tmpdir=${TMPDIR:-/tmp}
[ -f "$tmpdir/.compound-retros-off" ] && exit 0

event=$(cat) || exit 0
printf '%s\n' "$event" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true([,}[:space:]]|$)' && exit 0

session_id=$(printf '%s\n' "$event" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | sed -n '1p')
transcript=$(printf '%s\n' "$event" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | sed -n '1p')
[ -n "$session_id" ] && [ -r "$transcript" ] && [ -f "$transcript" ] || exit 0
session_id=$(printf '%s' "$session_id" | LC_ALL=C tr -c 'A-Za-z0-9._-' '_') || exit 0
[ -n "$session_id" ] || exit 0
marker="$tmpdir/compound-retros-reminded-$session_id"
[ -f "$marker" ] && exit 0

# JSON parsing is needed here to distinguish real user text from tool results,
# assistant messages, metadata and injected system reminders.
tail -n 300 "$transcript" 2>/dev/null | python3 -c '
import json
import re
import sys

cue = re.compile(r"đừng|sai rồi|không phải vậy|lần sau|don[\x27\u2019]?t do|stop doing|that[\x27\u2019]?s wrong|not what i (?:asked|meant)|please remember|nhớ (?:là|đi)|lưu bài học|rút kinh nghiệm|ghi chú lại|note this|remember this", re.I)
reminder = re.compile(r"<system-reminder>.*?</system-reminder>", re.I | re.S)

for line in sys.stdin:
    try:
        row = json.loads(line)
    except (ValueError, TypeError):
        continue
    if not isinstance(row, dict):
        continue
    content = None
    if row.get("type") == "user" and not row.get("isMeta"):
        message = row.get("message")
        if isinstance(message, dict) and message.get("role") == "user":
            content = message.get("content")
            allowed = "text"
    elif row.get("type") == "response_item":
        payload = row.get("payload")
        if isinstance(payload, dict) and payload.get("type") == "message" and payload.get("role") == "user":
            content = payload.get("content")
            allowed = "input_text"
    elif row.get("type") == "event_msg":
        payload = row.get("payload")
        if isinstance(payload, dict) and payload.get("type") == "user_message":
            content = payload.get("message")
            allowed = "input_text"
    if isinstance(content, str):
        texts = [content]
    elif isinstance(content, list):
        texts = [part.get("text") for part in content if isinstance(part, dict) and part.get("type") == allowed]
    else:
        continue
    for text in texts:
        if not isinstance(text, str):
            continue
        text = reminder.sub("", text)
        text = re.sub(r"<system-reminder>.*", "", text, flags=re.I | re.S)
        if cue.search(text):
            sys.exit(0)
sys.exit(1)
' 2>/dev/null || exit 0

(set -C; : > "$marker") 2>/dev/null || exit 0
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"This session shows signs of a durable lesson (user correction or explicit request). If any survives the durable-bar in the retro-capture skill — would losing it let a future agent repeat the mistake? — capture it per that skill; otherwise do nothing."}}'
exit 0
