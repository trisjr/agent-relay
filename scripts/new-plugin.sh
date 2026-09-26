#!/usr/bin/env bash
# new-plugin.sh — scaffold a new plugin from plugins/_template.
#
# Usage: scripts/new-plugin.sh <plugin-name>
#
#   1. Validates the kebab-case name and preconditions.
#   2. Copies plugins/_template -> plugins/<name>.
#   3. Replaces every "__PLUGIN_NAME__" in file contents and renames
#      files/dirs whose names contain the placeholder (python3, so the
#      behavior is identical on macOS and Linux).
#   4. Appends an entry to the "plugins" array of ALL THREE marketplaces:
#      .agents/plugins/marketplace.json, .claude-plugin/marketplace.json,
#      and .kimi-plugin/marketplace.json (python3, 2-space indent preserved).
#   5. Re-runs scripts/validate.sh and prints next steps.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

PLACEHOLDER="__PLUGIN_NAME__"
ENTRY_DESCRIPTION="TODO: Describe this plugin"

usage() {
  printf 'usage: scripts/new-plugin.sh <plugin-name>\n' >&2
  exit 2
}

err() {
  printf 'new-plugin.sh: error: %s\n' "$1" >&2
  exit "${2:-1}"
}

[ $# -eq 1 ] || usage
NAME="$1"

# --- 1. validate name + preconditions --------------------------------------
if ! [[ "$NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  err "invalid plugin name '$NAME' (must be kebab-case: lowercase letters, digits, hyphens)" 2
fi

TEMPLATE_DIR="$REPO_ROOT/plugins/_template"
TARGET_DIR="$REPO_ROOT/plugins/$NAME"
CODEX_MARKETPLACE="$REPO_ROOT/.agents/plugins/marketplace.json"
CLAUDE_MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
KIMI_MARKETPLACE="$REPO_ROOT/.kimi-plugin/marketplace.json"

[ -d "$TEMPLATE_DIR" ] || err "template not found: plugins/_template"
[ ! -e "$TARGET_DIR" ] || err "plugin already exists: plugins/$NAME"
[ -f "$CODEX_MARKETPLACE" ] || err "marketplace not found: .agents/plugins/marketplace.json"
[ -f "$CLAUDE_MARKETPLACE" ] || err "marketplace not found: .claude-plugin/marketplace.json"
[ -f "$KIMI_MARKETPLACE" ] || err "marketplace not found: .kimi-plugin/marketplace.json"

python3 - "$CODEX_MARKETPLACE" "$CLAUDE_MARKETPLACE" "$KIMI_MARKETPLACE" <<'PYEOF'
import json
import sys

for path in sys.argv[1:]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        sys.stderr.write("new-plugin.sh: error: %s is not valid JSON (%s)\n" % (path, exc))
        sys.exit(1)
    if not isinstance(data, dict) or not isinstance(data.get("plugins"), list):
        sys.stderr.write("new-plugin.sh: error: %s must be an object with a \"plugins\" array\n" % path)
        sys.exit(1)
PYEOF

# --- 2. copy template -------------------------------------------------------
cp -R "$TEMPLATE_DIR" "$TARGET_DIR"
printf 'Created plugins/%s from plugins/_template\n' "$NAME"

# --- 3. replace placeholder in filenames and contents -----------------------
python3 - "$TARGET_DIR" "$NAME" "$PLACEHOLDER" <<'PYEOF'
import os
import sys

target, name, placeholder = sys.argv[1], sys.argv[2], sys.argv[3]

renamed = 0
for dirpath, dirnames, filenames in os.walk(target, topdown=False):
    for filename in filenames:
        if placeholder in filename:
            os.rename(
                os.path.join(dirpath, filename),
                os.path.join(dirpath, filename.replace(placeholder, name)),
            )
            renamed += 1
    for dirname in dirnames:
        if placeholder in dirname:
            os.rename(
                os.path.join(dirpath, dirname),
                os.path.join(dirpath, dirname.replace(placeholder, name)),
            )
            renamed += 1

updated = 0
for dirpath, _dirnames, filenames in os.walk(target):
    for filename in filenames:
        path = os.path.join(dirpath, filename)
        with open(path, "rb") as fh:
            raw = fh.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if placeholder in text:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(text.replace(placeholder, name))
            updated += 1

print("Replaced %s in %d file(s); renamed %d path(s)" % (placeholder, updated, renamed))
PYEOF

# --- 4. register in all marketplaces ---------------------------------------
python3 - "$NAME" "$ENTRY_DESCRIPTION" "$TEMPLATE_DIR/plugin.json" "$CODEX_MARKETPLACE" "$CLAUDE_MARKETPLACE" "$KIMI_MARKETPLACE" <<'PYEOF'
import json
import sys

name, description, template_manifest = sys.argv[1], sys.argv[2], sys.argv[3]
with open(template_manifest, "r", encoding="utf-8") as fh:
    version = json.load(fh)["version"]

for path in sys.argv[4:]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    plugins = data["plugins"]
    already = any(
        isinstance(entry, dict) and (entry.get("name") == name or entry.get("id") == name)
        for entry in plugins
    )
    if already:
        print("Entry for %r already present in %s" % (name, path))
        continue
    if "kimi" in path:
        entry = {
            "id": name,
            "name": name,
            "displayName": " ".join(w.capitalize() for w in name.split("-")),
            "version": version,
            "description": description,
            "source": "./plugins/%s" % name,
        }
    else:
        entry = {
            "name": name,
            "source": "./plugins/%s" % name,
            "description": description,
        }
    plugins.append(entry)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("Added entry for %r to %s" % (name, path))
PYEOF

# --- 5. validate + next steps ----------------------------------------------
printf '\nRunning validate.sh...\n\n'
VALIDATE_OK=0
if "$SCRIPT_DIR/validate.sh"; then
  VALIDATE_OK=1
fi

printf '\n%s\n' "----------------------------------------"
printf 'Plugin %q scaffolded. Next steps:\n' "$NAME"
printf '  1. Edit plugins/%s/README.md and describe what the plugin does.\n' "$NAME"
printf '  2. Replace "%s" in all marketplace.json files with a real description.\n' "$ENTRY_DESCRIPTION"
printf '  3. Fill in the 5 manifests (plugin.json, .claude-plugin/plugin.json,\n'
printf '     .qoder-plugin/plugin.json, gemini-extension.json, .kimi-plugin/plugin.json) - keep name/version in sync.\n'
printf '  4. Write your skills in plugins/%s/skills/<skill-name>/SKILL.md\n' "$NAME"
printf '     (frontmatter requires name: and description:).\n'
printf '  5. Re-run scripts/validate.sh before committing.\n'
printf '\nNote: the Kimi marketplace source stays local (./plugins/%s) until /release packages the zip.\n' "$NAME"

if [ "$VALIDATE_OK" -ne 1 ]; then
  printf '\nnew-plugin.sh: warning: validate.sh reported problems - fix them before committing.\n' >&2
  exit 1
fi
