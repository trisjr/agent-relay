# Transitions and labels

`scripts/lifecycle.sh` enforces this table. It is repeated here so you can plan a move before making it; when the two disagree, the script is right and this file has a bug.

## Moves between states

| From | Forward | Back or sideways |
|---|---|---|
| (no label) | `intake` | |
| `intake` | `triage` | |
| `triage` | `specify`; `implement` on track `chore` | close as `rejected`, `duplicate`, `already-done`, `superseded`; wait `deferred` or `needs-info` |
| `specify` | `plan` on tracks `feature` and `bug` | `triage` when the scope turns out different; close as `answered` on track `spike` |
| `plan` | `implement` | `specify` when a requirement is wrong; close as `superseded` when the task is split |
| `implement` | `verify` | `plan` when the plan is wrong, `specify` when the spec is wrong (not on `chore`) |
| `verify` | `review`; `handoff` on track `chore` | `implement` when a criterion fails |
| `review` | `handoff` | `implement` when changes are requested |
| `handoff` | close as `done` | `implement` or `specify` when the result is not accepted |
| closed | | `reopen` into `triage` |

From any state: `triage` (scope change) and close as `canceled`. Resuming a `deferred` task with `resume` puts it in `triage` wherever it was parked.

The track must be set before a task leaves `triage`, because the allowed moves depend on it.

## Commands

All take the issue number. Call the script by its path (`scripts/lifecycle.sh` in the `calibre:run` skill) and keep the working directory inside the task's repo: `gh` acts on the repository of the directory you are in, so changing into the script's directory would point it at the wrong one. `show` prints the repo it is acting on; check it once per session.

| Command | Effect |
|---|---|
| `lifecycle.sh show <n>` | Print `repo`, `open`, `state`, `wait`, `track`, `resolution` |
| `lifecycle.sh state <n> <state> [--comment <text>]` | Validate the move, swap the state label, clear any wait label; with `--comment`, post the text on the issue as a move note |
| `lifecycle.sh track <n> <track>` | Set `feature`, `bug`, `chore` or `spike` |
| `lifecycle.sh wait <n> <kind>` | Add `needs-info`, `approval`, `blocked` or `deferred` |
| `lifecycle.sh resume <n>` | Remove the wait label; a `deferred` task also returns to `triage` |
| `lifecycle.sh close <n> <resolution>` | Validate, swap state and wait labels for `resolution:*`, close the issue |
| `lifecycle.sh reopen <n>` | Reopen, drop the resolution label, set `state:triage` |
| `lifecycle.sh can <from> <to> [track]` | Check a move without touching GitHub |
| `lifecycle.sh can-close <state> <resolution> [track]` | Check a close without touching GitHub |
| `lifecycle.sh labels` | Print every label with its color and description |

`close` accepts `--comment <text>` and, for `duplicate`, requires `--duplicate-of <n>`.

`state --comment` posts the text under a `**Lifecycle · <from> → <to>**` line after the labels have moved. If the comment cannot be posted, the move still stands and the script exits 0 with a warning: post the note by hand instead of repeating the move, which would be refused.

A refused command exits non-zero and says why. Exit code 3 means the issue carries two labels of the same kind, which a person has to untangle.

## Labels

- `state:intake`, `state:triage`, `state:specify`, `state:plan`, `state:implement`, `state:verify`, `state:review`, `state:handoff` — exactly one on an open task.
- `wait:needs-info`, `wait:approval`, `wait:blocked`, `wait:deferred` — at most one, beside the state label.
- `track:feature`, `track:bug`, `track:chore`, `track:spike` — one, set during `triage`, kept after closing.
- `resolution:done`, `resolution:answered`, `resolution:duplicate`, `resolution:rejected`, `resolution:already-done`, `resolution:superseded`, `resolution:canceled` — one, on a closed task, replacing the state label.

GitHub accepts three close reasons, so the resolution label carries the detail:

| Resolution | GitHub close reason |
|---|---|
| `done`, `answered` | completed |
| `duplicate` | duplicate |
| `rejected`, `already-done`, `superseded`, `canceled` | not planned |
