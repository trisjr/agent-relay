#!/usr/bin/env bash
# validate.sh — structural checks for the agent-relay plugin marketplace.
#
# Checks:
#   a. All three marketplace manifests parse and have the required keys; every
#      plugins[].source points at an existing directory inside plugins/, or is
#      an http(s) URL (e.g. GitHub release zip for remote Kimi installs).
#   b. Every real plugin dir (not "_"-prefixed) has all five manifest files,
#      all of them parse, "name" matches across all five and equals the dir
#      name, "version" is identical across all five.
#   c. Every skills/*/SKILL.md of a real plugin has frontmatter containing
#      "name:" and "description:".
#   d. Every real plugin is listed by name in ALL THREE marketplace manifests.
#
# JSON work is done with python3 (no jq dependency).
# Exit 0 when everything passes, 1 otherwise.

set -u
shopt -s nullglob

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

PASS_COUNT=0
FAIL_COUNT=0

report() { # $1 = PASS|FAIL, $2 = message
  if [ "$1" = "PASS" ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    printf '[PASS] %s\n' "$2"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    printf '[FAIL] %s\n' "$2"
  fi
}

printf 'Validating repository: %s\n\n' "$REPO_ROOT"

# --------------------------------------------------------------------------
# Checks a, b, d — python3 does the JSON-heavy lifting and prints raw
# "PASS <msg>" / "FAIL <msg>" lines that we re-emit through report().
# --------------------------------------------------------------------------
PY_OUT="$(python3 - "$REPO_ROOT" <<'PYEOF'
import json
import os
import sys

root = sys.argv[1]
plugins_dir = os.path.join(root, "plugins")

def out(status, msg):
    print(status + " " + msg)

marketplaces = [
    {
        "rel": ".agents/plugins/marketplace.json",
        "label": "codex marketplace",
        "top_keys": ["name", "interface", "plugins"],
        "nested": [("interface", "displayName")],
    },
    {
        "rel": ".claude-plugin/marketplace.json",
        "label": "claude marketplace",
        "top_keys": ["name", "description", "owner", "plugins"],
        "nested": [("owner", "name")],
    },
    {
        "rel": ".kimi-plugin/marketplace.json",
        "label": "kimi marketplace",
        "top_keys": ["name", "description", "owner", "plugins"],
        "nested": [("owner", "name")],
    },
]

# ----- check a -------------------------------------------------------------
listed_names = {}  # rel marketplace path -> set of plugin names it lists

for spec in marketplaces:
    rel = spec["rel"]
    label = spec["label"]
    path = os.path.join(root, rel)
    listed_names[rel] = set()

    if not os.path.isfile(path):
        out("FAIL", "%s: missing file %s" % (label, rel))
        continue

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        out("PASS", "%s: %s parses as JSON" % (label, rel))
    except Exception as exc:
        out("FAIL", "%s: %s is not valid JSON (%s)" % (label, rel, exc))
        continue

    if not isinstance(data, dict):
        out("FAIL", "%s: %s root must be a JSON object" % (label, rel))
        continue

    missing = [k for k in spec["top_keys"] if k not in data]
    if missing:
        out("FAIL", "%s: %s missing required key(s): %s"
            % (label, rel, ", ".join(missing)))
    else:
        out("PASS", "%s: %s has required keys (%s)"
            % (label, rel, ", ".join(spec["top_keys"])))

    for parent, child in spec["nested"]:
        if isinstance(data.get(parent), dict) and \
                isinstance(data[parent].get(child), str) and \
                data[parent][child].strip():
            out("PASS", "%s: %s has %s.%s" % (label, rel, parent, child))
        else:
            out("FAIL", "%s: %s missing or empty \"%s.%s\""
                % (label, rel, parent, child))

    entries = data.get("plugins")
    if not isinstance(entries, list):
        out("FAIL", "%s: %s \"plugins\" must be an array" % (label, rel))
        continue

    listed = 0
    for idx, entry in enumerate(entries):
        where = "%s plugins[%d]" % (rel, idx)
        if not isinstance(entry, dict):
            out("FAIL", "%s: %s must be an object" % (label, where))
            continue
        bad_fields = [k for k in ("name", "source", "description")
                      if not isinstance(entry.get(k), str)
                      or not entry.get(k).strip()]
        name = entry.get("name")
        source = entry.get("source")
        if bad_fields:
            out("FAIL", "%s: %s missing/empty field(s): %s"
                % (label, where, ", ".join(bad_fields)))
        if isinstance(name, str) and name.strip():
            listed_names[rel].add(name)
        if bad_fields or not isinstance(source, str):
            continue
        if source.startswith("http://") or source.startswith("https://"):
            out("PASS", "%s: %s entry %r -> remote source: %s"
                % (label, spec["label"], name, source))
            listed += 1
            continue
        if not source.startswith("./plugins/"):
            out("FAIL", "%s: %s source %r must start with \"./plugins/\""
                % (label, where, source))
            continue
        target = os.path.normpath(os.path.join(root, source))
        plugins_norm = os.path.normpath(plugins_dir)
        if not (target == plugins_norm or
                target.startswith(plugins_norm + os.sep)):
            out("FAIL", "%s: %s source %r escapes plugins/"
                % (label, where, source))
        elif not os.path.isdir(target):
            out("FAIL", "%s: %s source %r -> directory not found: %s"
                % (label, where, source, os.path.relpath(target, root)))
        else:
            out("PASS", "%s: %s entry %r -> %s exists"
                % (label, spec["label"], name, source))
            listed += 1
    if not entries:
        out("PASS", "%s: %s \"plugins\" array present (0 entries)"
            % (label, rel))

# ----- discover real plugins ------------------------------------------------
real_plugins = []
if os.path.isdir(plugins_dir):
    for dirname in sorted(os.listdir(plugins_dir)):
        full = os.path.join(plugins_dir, dirname)
        if not os.path.isdir(full):
            continue
        if dirname.startswith("_") or dirname.startswith("."):
            continue
        real_plugins.append(dirname)
else:
    out("FAIL", "plugins/ directory not found: %s" % plugins_dir)

# ----- check b ---------------------------------------------------------------
MANIFESTS = [
    "plugin.json",
    ".claude-plugin/plugin.json",
    ".qoder-plugin/plugin.json",
    "gemini-extension.json",
    ".kimi-plugin/plugin.json",
]

for plugin in real_plugins:
    pdir = os.path.join(plugins_dir, plugin)
    parsed = {}
    for rel_manifest in MANIFESTS:
        mpath = os.path.join(pdir, rel_manifest)
        mrel = "plugins/%s/%s" % (plugin, rel_manifest)
        if not os.path.isfile(mpath):
            out("FAIL", "plugin %r: missing manifest %s" % (plugin, mrel))
            continue
        try:
            with open(mpath, "r", encoding="utf-8") as fh:
                parsed[rel_manifest] = json.load(fh)
            out("PASS", "plugin %r: %s parses as JSON" % (plugin, mrel))
        except Exception as exc:
            out("FAIL", "plugin %r: %s is not valid JSON (%s)"
                % (plugin, mrel, exc))

    if len(parsed) != len(MANIFESTS):
        continue

    names = {m: parsed[m].get("name") for m in MANIFESTS}
    no_name = [m for m, n in names.items() if not isinstance(n, str) or not n.strip()]
    if no_name:
        out("FAIL", "plugin %r: missing/empty \"name\" in: %s"
            % (plugin, ", ".join(no_name)))
    elif len(set(names.values())) != 1:
        detail = ", ".join("%s=%r" % (m, n) for m, n in sorted(names.items()))
        out("FAIL", "plugin %r: \"name\" mismatch across manifests (%s)"
            % (plugin, detail))
    elif names[MANIFESTS[0]] != plugin:
        out("FAIL", "plugin %r: manifest \"name\" %r does not match directory name"
            % (plugin, names[MANIFESTS[0]]))
    else:
        out("PASS", "plugin %r: \"name\" == %r in all 5 manifests"
            % (plugin, plugin))

    versions = {m: parsed[m].get("version") for m in MANIFESTS}
    no_ver = [m for m, v in versions.items() if not isinstance(v, str) or not v.strip()]
    if no_ver:
        out("FAIL", "plugin %r: missing/empty \"version\" in: %s"
            % (plugin, ", ".join(no_ver)))
    elif len(set(versions.values())) != 1:
        detail = ", ".join("%s=%r" % (m, v) for m, v in sorted(versions.items()))
        out("FAIL", "plugin %r: \"version\" mismatch across manifests (%s)"
            % (plugin, detail))
    else:
        out("PASS", "plugin %r: \"version\" == %r in all 5 manifests"
            % (plugin, versions[MANIFESTS[0]]))

# ----- check d ---------------------------------------------------------------
for plugin in real_plugins:
    for spec in marketplaces:
        rel = spec["rel"]
        if plugin in listed_names.get(rel, set()):
            out("PASS", "plugin %r: listed in %s" % (plugin, rel))
        else:
            out("FAIL", "plugin %r: NOT listed in %s" % (plugin, rel))
PYEOF
)"
PY_STATUS=$?

if [ "$PY_STATUS" -ne 0 ]; then
  report FAIL "internal error: python3 check engine exited with status $PY_STATUS"
fi
while IFS= read -r line; do
  [ -n "$line" ] || continue
  case "$line" in
    "PASS "*) report PASS "${line#PASS }" ;;
    "FAIL "*) report FAIL "${line#FAIL }" ;;
    *)        report FAIL "unexpected engine output: $line" ;;
  esac
done <<EOF
$PY_OUT
EOF

# --------------------------------------------------------------------------
# Check c — SKILL.md frontmatter (simple grep of the first --- block)
# --------------------------------------------------------------------------
for plugin_dir in "$REPO_ROOT"/plugins/*/; do
  plugin_name="$(basename "$plugin_dir")"
  case "$plugin_name" in
    _*|.*) continue ;;
  esac
  for skill_md in "$plugin_dir"skills/*/SKILL.md; do
    skill_rel="plugins/$plugin_name/skills/$(basename "$(dirname "$skill_md")")/SKILL.md"
    if awk '
      NR == 1 { if ($0 != "---") exit 1; next }
      $0 == "---" { closed = 1; exit (saw_name && saw_desc) ? 0 : 1 }
      /^name:/        { saw_name = 1 }
      /^description:/ { saw_desc = 1 }
      END { if (!closed) exit 1 }
    ' "$skill_md"; then
      report PASS "skill frontmatter ok (name:, description:): $skill_rel"
    else
      report FAIL "skill frontmatter missing or lacks name:/description: $skill_rel"
    fi
  done
done

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
printf '\n%s\n' "----------------------------------------"
if [ "$FAIL_COUNT" -eq 0 ]; then
  printf 'validate.sh: OK (%d checks passed, 0 failed)\n' "$PASS_COUNT"
  exit 0
else
  printf 'validate.sh: FAILED (%d failed, %d passed)\n' "$FAIL_COUNT" "$PASS_COUNT"
  exit 1
fi
