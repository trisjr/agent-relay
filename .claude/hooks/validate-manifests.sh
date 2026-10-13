#!/usr/bin/env bash
# PostToolUse (Edit|Write): chạy scripts/validate.sh khi sửa manifest/marketplace/SKILL.md.
set -u

file_path="$(jq -r '.tool_input.file_path // empty')"
[ -z "$file_path" ] && exit 0

case "$file_path" in
  */plugin.json | */gemini-extension.json | */marketplace.json | */SKILL.md ) ;;
  * ) exit 0 ;;
esac

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

if ! output="$(bash scripts/validate.sh 2>&1)"; then
  # exit 2: đưa kết quả lại cho Claude để sửa ngay
  printf '%s\n' "$output" | grep -E 'FAIL' >&2
  exit 2
fi

exit 0
