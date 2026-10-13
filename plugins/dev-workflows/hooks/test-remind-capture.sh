#!/bin/sh
set -u

hook=$(CDPATH= cd "$(dirname "$0")" && pwd)/remind-capture.sh
fixture_dir=${TMPDIR:-/tmp}/compound-retros-hook-test-$$
umask 077
mkdir "$fixture_dir" || exit 1
trap 'rm -rf "$fixture_dir"' 0
trap 'exit 1' 1 2 3 15

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }
run() {
    printf '%s\n' "$1" | COMPOUND_RETROS_HOOK_OFF="${2:-}" TMPDIR="$fixture_dir" sh "$hook" > "$fixture_dir/output" || fail "hook exit"
}
silent() { [ ! -s "$fixture_dir/output" ] || fail "$1 printed output"; }
event() { printf '{"session_id":"%s","transcript_path":"%s","stop_hook_active":false}' "$1" "$2"; }

cat > "$fixture_dir/claude.jsonl" <<'JSONL'
{"type":"user", "message": {"role":"user", "content":"đừng làm X nữa"}}
JSONL
run "$(event vietnamese "$fixture_dir/claude.jsonl")"
[ "$(wc -l < "$fixture_dir/output" | tr -d ' ')" = 1 ] || fail "cue should print one line"
python3 -m json.tool < "$fixture_dir/output" >/dev/null || fail "cue output is not JSON"
grep -F '"hookEventName":"Stop"' "$fixture_dir/output" >/dev/null || fail "wrong event"
run "$(event vietnamese "$fixture_dir/claude.jsonl")"
silent "repeat session"
run "$(event env-off "$fixture_dir/claude.jsonl")" 1
silent "environment opt-out"
run "$(event active-compact "$fixture_dir/claude.jsonl" | sed 's/"stop_hook_active":false/"stop_hook_active":true/')"
silent "active compact"
run "$(event active-spaced "$fixture_dir/claude.jsonl" | sed 's/"stop_hook_active":false/"stop_hook_active" : true/')"
silent "active spaced"

cat > "$fixture_dir/clean.jsonl" <<'JSONL'
{"type":"user","message":{"role":"user","content":"Thanks, the task is finished."}}
JSONL
run "$(event clean "$fixture_dir/clean.jsonl")"
silent "clean session"

cat > "$fixture_dir/not-user.jsonl" <<'JSONL'
{"type":"assistant","message":{"role":"assistant","content":"đừng làm X nữa"}}
{"type":"user","isMeta":true,"message":{"role":"user","content":"<system-reminder>đừng làm X nữa</system-reminder>"}}
{"type":"user","message":{"role":"user","content":"Fine. <system-reminder>đừng làm X nữa</system-reminder> Thanks."}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"đừng làm X nữa"}]}}
{"type":"response_item","payload":{"type":"message","role":"assistant","content":[{"type":"output_text","text":"remember this"}]}}
JSONL
run "$(event not-user "$fixture_dir/not-user.jsonl")"
silent "non-user cues"

cat > "$fixture_dir/codex.jsonl" <<'JSONL'
{"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Please remember this"}]}}
JSONL
run "$(event codex "$fixture_dir/codex.jsonl")"
[ "$(wc -l < "$fixture_dir/output" | tr -d ' ')" = 1 ] || fail "Codex cue should print one line"
python3 -m json.tool < "$fixture_dir/output" >/dev/null || fail "Codex output is not JSON"

: > "$fixture_dir/.compound-retros-off"
run "$(event marker-off "$fixture_dir/claude.jsonl")"
silent "marker opt-out"
printf 'hook tests passed\n'
