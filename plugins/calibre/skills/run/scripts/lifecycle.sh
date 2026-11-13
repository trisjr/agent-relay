#!/usr/bin/env bash
# lifecycle.sh — the only writer of calibre labels on a GitHub issue.
#
# A task's state lives on its issue as exactly one `state:*` label. This script
# owns every label change so that a transition is validated before it is
# applied and the old and new state labels are swapped in a single edit.
#
# Usage:
#   lifecycle.sh labels                         Print the label catalog (offline)
#   lifecycle.sh can <from> <to> [track]        Check a transition (offline)
#   lifecycle.sh can-close <state> <resolution> [track]
#                                               Check a close (offline)
#   lifecycle.sh init [--dry-run]               Create or update every label
#   lifecycle.sh show <issue>                   Print state, wait, track, resolution
#   lifecycle.sh state <issue> <state> [--comment <text>]
#                                               Move to a state (validated); with
#                                               --comment, post a move note
#   lifecycle.sh track <issue> <track>          Set the track
#   lifecycle.sh wait <issue> <kind>            Mark the task as waiting
#   lifecycle.sh resume <issue>                 Clear the waiting mark (deferred
#                                               work also returns to triage)
#   lifecycle.sh close <issue> <resolution> [--duplicate-of <n>] [--comment <text>]
#   lifecycle.sh reopen <issue>                 Reopen into state:triage
#
# <from> is a state name, or "none" for an issue with no state label yet.
# Requires the GitHub CLI (`gh`), authenticated, for everything except
# `labels`, `can` and `can-close`. Written for bash 3.2 (stock macOS).
#
# `gh` acts on the repository of the working directory. Call this script by
# its path and stay inside the task's repo; do not `cd` to the script.

set -euo pipefail

STATES="intake triage specify plan implement verify review handoff"
WAITS="needs-info approval blocked deferred"
TRACKS="feature bug chore spike"
RESOLUTIONS="done answered duplicate rejected already-done superseded canceled"

die() {
  printf 'lifecycle.sh: %s\n' "$1" >&2
  exit "${2:-1}"
}

in_list() { # $1 = item, $2 = space-separated list
  local item
  for item in $2; do
    [ "$item" = "$1" ] && return 0
  done
  return 1
}

need_gh() {
  command -v gh >/dev/null 2>&1 || die "the GitHub CLI (gh) is not installed"
}

# name|color|description
catalog() {
  cat <<'EOF'
state:intake|C5DEF5|Lifecycle: request recorded, not yet triaged
state:triage|C5DEF5|Lifecycle: being classified and judged worth doing or not
state:specify|BFD4F2|Lifecycle: requirements and acceptance criteria being fixed
state:plan|BFD4F2|Lifecycle: approach and tasks being planned
state:implement|D4C5F9|Lifecycle: change being built
state:verify|D4C5F9|Lifecycle: each acceptance criterion being proven with evidence
state:review|D4C5F9|Lifecycle: independent review of the final change
state:handoff|C2E0C6|Lifecycle: pull request open, waiting for acceptance
wait:needs-info|FBCA04|Lifecycle: waiting for an answer from the requester
wait:approval|FBCA04|Lifecycle: waiting for a human decision at a gate
wait:blocked|D93F0B|Lifecycle: blocked by something outside the task
wait:deferred|E4E669|Lifecycle: postponed, re-triage before resuming
track:feature|0E8A16|Lifecycle track: new or changed behavior
track:bug|B60205|Lifecycle track: existing behavior is wrong
track:chore|5319E7|Lifecycle track: small change on the fast lane
track:spike|006B75|Lifecycle track: question or investigation, ends in an answer
resolution:done|0E8A16|Lifecycle: delivered and accepted
resolution:answered|006B75|Lifecycle: question answered, no change delivered
resolution:duplicate|CFD3D7|Lifecycle: same as another issue
resolution:rejected|CFD3D7|Lifecycle: decided not to do
resolution:already-done|CFD3D7|Lifecycle: the behavior already exists
resolution:superseded|CFD3D7|Lifecycle: replaced by child issues
resolution:canceled|CFD3D7|Lifecycle: stopped before completion
EOF
}

# Echoes nothing and returns 0 when the transition is allowed; otherwise
# prints the reason on stdout and returns 1.
check_transition() { # $1 = from, $2 = to, $3 = track (may be empty)
  local from="$1" to="$2" track="${3:-}"

  if [ "$from" != "none" ] && ! in_list "$from" "$STATES"; then
    echo "unknown state '$from'"; return 1
  fi
  if ! in_list "$to" "$STATES"; then
    echo "unknown state '$to'"; return 1
  fi
  if [ "$from" = "$to" ]; then
    echo "already in state '$to'"; return 1
  fi
  if [ "$from" = "none" ]; then
    [ "$to" = "intake" ] && return 0
    echo "an issue with no state label can only enter 'intake'"; return 1
  fi
  if [ "$to" = "intake" ]; then
    echo "'intake' is only the entry state; use 'triage' to re-evaluate"; return 1
  fi
  # Re-triage is always possible: scope change, deferred work resuming.
  if [ "$to" = "triage" ]; then
    return 0
  fi
  if [ -z "$track" ]; then
    echo "the task has no track label; set it first (lifecycle.sh track <issue> <track>)"; return 1
  fi

  case "$from>$to" in
    "triage>specify")
      [ "$track" != "chore" ] && return 0
      echo "track 'chore' skips 'specify': go from 'triage' to 'implement'"; return 1 ;;
    "triage>implement")
      [ "$track" = "chore" ] && return 0
      echo "only track 'chore' goes from 'triage' straight to 'implement'"; return 1 ;;
    "specify>plan")
      if [ "$track" = "feature" ] || [ "$track" = "bug" ]; then return 0; fi
      echo "track '$track' does not have a 'plan' state"; return 1 ;;
    "plan>implement"|"plan>specify")
      return 0 ;;
    "implement>verify")
      return 0 ;;
    "implement>plan"|"implement>specify")
      [ "$track" != "chore" ] && return 0
      echo "track 'chore' has no '$to' state: go back to 'triage' to reclassify"; return 1 ;;
    "verify>implement")
      return 0 ;;
    "verify>review")
      [ "$track" != "chore" ] && return 0
      echo "track 'chore' skips 'review': go from 'verify' to 'handoff'"; return 1 ;;
    "verify>handoff")
      [ "$track" = "chore" ] && return 0
      echo "only track 'chore' goes from 'verify' straight to 'handoff'"; return 1 ;;
    "review>handoff"|"review>implement")
      return 0 ;;
    "handoff>implement")
      return 0 ;;
    "handoff>specify")
      [ "$track" != "chore" ] && return 0
      echo "track 'chore' has no 'specify' state: go back to 'triage' to reclassify"; return 1 ;;
  esac
  echo "no transition from '$from' to '$to'"
  return 1
}

check_close() { # $1 = state (or none), $2 = resolution, $3 = track (may be empty)
  local state="$1" res="$2" track="${3:-}"

  if ! in_list "$res" "$RESOLUTIONS"; then
    echo "unknown resolution '$res'"; return 1
  fi
  case "$res" in
    canceled)
      return 0 ;;
    done)
      [ "$state" = "handoff" ] && return 0
      echo "'done' closes from 'handoff' only, after the change is accepted"; return 1 ;;
    answered)
      if [ "$track" = "spike" ] && { [ "$state" = "triage" ] || [ "$state" = "specify" ]; }; then
        return 0
      fi
      echo "'answered' closes a track 'spike' task from 'triage' or 'specify'"; return 1 ;;
    rejected|duplicate|already-done)
      [ "$state" = "triage" ] && return 0
      echo "'$res' is a triage verdict: move to 'triage' first"; return 1 ;;
    superseded)
      if [ "$state" = "triage" ] || [ "$state" = "plan" ]; then return 0; fi
      echo "'superseded' closes from 'triage' or 'plan', when the task is split"; return 1 ;;
  esac
  echo "cannot close with '$res' from '$state'"
  return 1
}

# Reads an issue into ISSUE_OPEN, CUR_STATE, CUR_WAIT, CUR_TRACK, CUR_RES.
# Empty values mean "no such label". More than one label of a kind is drift
# that a person has to resolve, so it stops here instead of guessing.
read_issue() { # $1 = issue number
  local n="$1" out line value
  out="$(gh issue view "$n" --json state,labels --jq '.state, (.labels[].name)')" \
    || die "cannot read issue #$n"
  ISSUE_OPEN=""
  CUR_STATE=""; CUR_WAIT=""; CUR_TRACK=""; CUR_RES=""
  while IFS= read -r line; do
    case "$line" in
      OPEN) [ -z "$ISSUE_OPEN" ] && ISSUE_OPEN="yes" ;;
      CLOSED) [ -z "$ISSUE_OPEN" ] && ISSUE_OPEN="no" ;;
      state:*)
        value="${line#state:}"
        [ -z "$CUR_STATE" ] || die "issue #$n has more than one state label ($CUR_STATE, $value); fix it by hand first" 3
        CUR_STATE="$value" ;;
      wait:*)
        value="${line#wait:}"
        if [ -z "$CUR_WAIT" ]; then CUR_WAIT="$value"; else CUR_WAIT="$CUR_WAIT,$value"; fi ;;
      track:*)
        value="${line#track:}"
        [ -z "$CUR_TRACK" ] || die "issue #$n has more than one track label ($CUR_TRACK, $value); fix it by hand first" 3
        CUR_TRACK="$value" ;;
      resolution:*)
        value="${line#resolution:}"
        if [ -z "$CUR_RES" ]; then CUR_RES="$value"; else CUR_RES="$CUR_RES,$value"; fi ;;
    esac
  done <<EOF
$out
EOF
}

# Comma-separated label names for the given prefix and comma-separated values.
prefixed() { # $1 = prefix, $2 = "a,b"
  local prefix="$1" values="$2" result="" value
  local old_ifs="$IFS"
  IFS=','
  for value in $values; do
    if [ -z "$result" ]; then result="$prefix:$value"; else result="$result,$prefix:$value"; fi
  done
  IFS="$old_ifs"
  printf '%s' "$result"
}

join_csv() { # joins non-empty arguments with commas
  local result="" part
  for part in "$@"; do
    [ -n "$part" ] || continue
    if [ -z "$result" ]; then result="$part"; else result="$result,$part"; fi
  done
  printf '%s' "$result"
}

edit_labels() { # $1 = issue, $2 = add csv, $3 = remove csv
  local n="$1" add="$2" remove="$3"
  local hint="could not update labels on issue #$n; if the lifecycle labels do not exist yet, run: lifecycle.sh init"
  if [ -n "$add" ] && [ -n "$remove" ]; then
    gh issue edit "$n" --add-label "$add" --remove-label "$remove" >/dev/null || die "$hint"
  elif [ -n "$add" ]; then
    gh issue edit "$n" --add-label "$add" >/dev/null || die "$hint"
  elif [ -n "$remove" ]; then
    gh issue edit "$n" --remove-label "$remove" >/dev/null || die "$hint"
  fi
}

cmd_labels() {
  catalog
}

cmd_can() {
  [ $# -ge 2 ] || die "usage: lifecycle.sh can <from> <to> [track]" 2
  local reason
  if reason="$(check_transition "$1" "$2" "${3:-}")"; then
    printf 'ok: %s -> %s\n' "$1" "$2"
  else
    printf 'no: %s\n' "$reason"
    exit 1
  fi
}

cmd_can_close() {
  [ $# -ge 2 ] || die "usage: lifecycle.sh can-close <state> <resolution> [track]" 2
  local reason
  if reason="$(check_close "$1" "$2" "${3:-}")"; then
    printf 'ok: close from %s as %s\n' "$1" "$2"
  else
    printf 'no: %s\n' "$reason"
    exit 1
  fi
}

cmd_init() {
  local dry="no"
  [ "${1:-}" = "--dry-run" ] && dry="yes"
  [ "$dry" = "yes" ] || need_gh
  local name color description
  while IFS='|' read -r name color description; do
    [ -n "$name" ] || continue
    if [ "$dry" = "yes" ]; then
      printf 'would create or update: %s\n' "$name"
    else
      gh label create "$name" --color "$color" --description "$description" --force >/dev/null
      printf 'label ready: %s\n' "$name"
    fi
  done <<EOF
$(catalog)
EOF
}

cmd_show() {
  [ $# -eq 1 ] || die "usage: lifecycle.sh show <issue>" 2
  need_gh
  local repo
  # gh picks the repository from the working directory, so print it: a script
  # called from the wrong directory would otherwise act on the wrong issues.
  repo="$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null)" \
    || die "no GitHub repository found for the current directory; run this from inside the task's repo"
  read_issue "$1"
  printf 'repo=%s\nissue=%s\nopen=%s\nstate=%s\nwait=%s\ntrack=%s\nresolution=%s\n' \
    "$repo" "$1" "$ISSUE_OPEN" "${CUR_STATE:-none}" "${CUR_WAIT:-none}" "${CUR_TRACK:-none}" "${CUR_RES:-none}"
}

cmd_state() {
  [ $# -ge 2 ] || die "usage: lifecycle.sh state <issue> <state> [--comment <text>]" 2
  need_gh
  local n="$1" to="$2" comment="" from reason
  shift 2
  while [ $# -gt 0 ]; do
    case "$1" in
      --comment) [ $# -ge 2 ] || die "--comment needs text" 2; comment="$2"; shift 2 ;;
      *) die "unknown option '$1'" 2 ;;
    esac
  done
  read_issue "$n"
  [ "$ISSUE_OPEN" = "yes" ] || die "issue #$n is closed; use 'reopen' first"
  from="${CUR_STATE:-none}"
  if ! reason="$(check_transition "$from" "$to" "$CUR_TRACK")"; then
    die "refused $from -> $to on issue #$n: $reason"
  fi
  # A waiting mark belongs to the state it interrupted, so it never survives a move.
  edit_labels "$n" "state:$to" "$(join_csv "$(prefixed state "$CUR_STATE")" "$(prefixed wait "$CUR_WAIT")")"
  printf 'issue #%s: %s -> %s\n' "$n" "$from" "$to"
  if [ -n "$comment" ]; then
    # The labels have moved by now. A note that cannot be posted must not look
    # like a failed move: repeating the move would be refused as "already in".
    if ! gh issue comment "$n" --body "$(printf '**Lifecycle · %s → %s**\n\n%s' "$from" "$to" "$comment")" >/dev/null; then
      printf 'lifecycle.sh: warning: issue #%s moved, but the move note was not posted; post it by hand and do not repeat the move\n' "$n" >&2
    fi
  fi
}

cmd_track() {
  [ $# -eq 2 ] || die "usage: lifecycle.sh track <issue> <track>" 2
  need_gh
  local n="$1" track="$2"
  in_list "$track" "$TRACKS" || die "unknown track '$track' (one of: $TRACKS)"
  read_issue "$n"
  if [ "$CUR_TRACK" = "$track" ]; then
    printf 'issue #%s: track already %s\n' "$n" "$track"
    return 0
  fi
  edit_labels "$n" "track:$track" "$(prefixed track "$CUR_TRACK")"
  printf 'issue #%s: track %s -> %s\n' "$n" "${CUR_TRACK:-none}" "$track"
}

cmd_wait() {
  [ $# -eq 2 ] || die "usage: lifecycle.sh wait <issue> <kind>" 2
  need_gh
  local n="$1" kind="$2"
  in_list "$kind" "$WAITS" || die "unknown wait kind '$kind' (one of: $WAITS)"
  read_issue "$n"
  [ -n "$CUR_STATE" ] || die "issue #$n has no state label; nothing to pause"
  if [ "$CUR_WAIT" = "$kind" ]; then
    printf 'issue #%s: already waiting (%s)\n' "$n" "$kind"
    return 0
  fi
  edit_labels "$n" "wait:$kind" "$(prefixed wait "$CUR_WAIT")"
  printf 'issue #%s: waiting (%s) in %s\n' "$n" "$kind" "$CUR_STATE"
}

cmd_resume() {
  [ $# -eq 1 ] || die "usage: lifecycle.sh resume <issue>" 2
  need_gh
  local n="$1"
  read_issue "$n"
  if [ -z "$CUR_WAIT" ]; then
    printf 'issue #%s: not waiting\n' "$n"
    return 0
  fi
  # Deferred work is triaged again, because what was true when it was parked
  # may no longer hold. Every other wait resumes in the state it interrupted.
  case ",$CUR_WAIT," in
    *,deferred,*)
      if [ -n "$CUR_STATE" ] && [ "$CUR_STATE" != "triage" ]; then
        edit_labels "$n" "state:triage" "$(join_csv "$(prefixed state "$CUR_STATE")" "$(prefixed wait "$CUR_WAIT")")"
        printf 'issue #%s: resumed from deferred, %s -> triage\n' "$n" "$CUR_STATE"
        return 0
      fi ;;
  esac
  edit_labels "$n" "" "$(prefixed wait "$CUR_WAIT")"
  printf 'issue #%s: resumed in %s\n' "$n" "${CUR_STATE:-none}"
}

cmd_close() {
  [ $# -ge 2 ] || die "usage: lifecycle.sh close <issue> <resolution> [--duplicate-of <n>] [--comment <text>]" 2
  need_gh
  local n="$1" res="$2" duplicate_of="" comment="" reason state
  shift 2
  while [ $# -gt 0 ]; do
    case "$1" in
      --duplicate-of) [ $# -ge 2 ] || die "--duplicate-of needs an issue number" 2; duplicate_of="$2"; shift 2 ;;
      --comment) [ $# -ge 2 ] || die "--comment needs text" 2; comment="$2"; shift 2 ;;
      *) die "unknown option '$1'" 2 ;;
    esac
  done
  read_issue "$n"
  [ "$ISSUE_OPEN" = "yes" ] || die "issue #$n is already closed"
  state="${CUR_STATE:-none}"
  if ! reason="$(check_close "$state" "$res" "$CUR_TRACK")"; then
    die "refused to close issue #$n as $res: $reason"
  fi
  if [ "$res" = "duplicate" ] && [ -z "$duplicate_of" ]; then
    die "closing as duplicate needs --duplicate-of <issue>" 2
  fi

  local old_labels closed="yes"
  old_labels="$(join_csv "$(prefixed state "$CUR_STATE")" "$(prefixed wait "$CUR_WAIT")")"
  edit_labels "$n" "resolution:$res" "$old_labels"

  case "$res" in
    duplicate)
      if [ -n "$comment" ]; then
        gh issue close "$n" --duplicate-of "$duplicate_of" --comment "$comment" >/dev/null || closed="no"
      else
        gh issue close "$n" --duplicate-of "$duplicate_of" >/dev/null || closed="no"
      fi ;;
    done|answered)
      if [ -n "$comment" ]; then
        gh issue close "$n" --reason "completed" --comment "$comment" >/dev/null || closed="no"
      else
        gh issue close "$n" --reason "completed" >/dev/null || closed="no"
      fi ;;
    *)
      if [ -n "$comment" ]; then
        gh issue close "$n" --reason "not planned" --comment "$comment" >/dev/null || closed="no"
      else
        gh issue close "$n" --reason "not planned" >/dev/null || closed="no"
      fi ;;
  esac

  if [ "$closed" = "no" ]; then
    # Put the labels back so the issue is not left open with a resolution and no state.
    edit_labels "$n" "$old_labels" "resolution:$res"
    die "could not close issue #$n; its labels were restored to '$state'"
  fi
  printf 'issue #%s: closed from %s as %s\n' "$n" "$state" "$res"
}

cmd_reopen() {
  [ $# -eq 1 ] || die "usage: lifecycle.sh reopen <issue>" 2
  need_gh
  local n="$1"
  read_issue "$n"
  [ "$ISSUE_OPEN" = "no" ] || die "issue #$n is already open"
  gh issue reopen "$n" >/dev/null
  edit_labels "$n" "state:triage" \
    "$(join_csv "$(prefixed resolution "$CUR_RES")" "$(prefixed state "$CUR_STATE")" "$(prefixed wait "$CUR_WAIT")")"
  printf 'issue #%s: reopened into triage\n' "$n"
}

[ $# -ge 1 ] || die "usage: lifecycle.sh <labels|can|can-close|init|show|state|track|wait|resume|close|reopen> ..." 2
command="$1"
shift
case "$command" in
  labels) cmd_labels "$@" ;;
  can) cmd_can "$@" ;;
  can-close) cmd_can_close "$@" ;;
  init) cmd_init "$@" ;;
  show) cmd_show "$@" ;;
  state) cmd_state "$@" ;;
  track) cmd_track "$@" ;;
  wait) cmd_wait "$@" ;;
  resume) cmd_resume "$@" ;;
  close) cmd_close "$@" ;;
  reopen) cmd_reopen "$@" ;;
  *) die "unknown command '$command'" 2 ;;
esac
