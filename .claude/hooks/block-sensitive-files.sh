#!/usr/bin/env bash
# PreToolUse (Edit|Write): chặn sửa file .env chứa secret.
set -u

file_path="$(jq -r '.tool_input.file_path // empty')"
[ -z "$file_path" ] && exit 0

base="$(basename "$file_path")"

case "$base" in
  .env | .env.* )
    if [ "$base" != ".env.example" ]; then
      echo "Chặn: $base chứa secret, không sửa qua agent. Anh tự sửa tay." >&2
      exit 2
    fi
    ;;
esac

exit 0
