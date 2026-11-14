# `.calibre/config.json`

One file at the repo root, committed, read by every lifecycle skill before it does its state's work.

```json
{
  "version": 1,
  "providers": {
    "specify": "openspec",
    "plan": "openspec",
    "implement": "superpowers",
    "review": "superpowers",
    "diagnose": "superpowers",
    "explore": "openspec"
  },
  "intake": { "create_issue": "ask" },
  "plan": { "record": "plan-provider" },
  "verify": { "max_loops": 3 },
  "handoff": { "accepted_when": "merged", "archive": "before-pr" },
  "issue_comments": "summary",
  "branch_prefix": "task/",
  "consent": { "issue_writes": true }
}
```

## Keys

### `providers`

Which library does each role's work. Values: `openspec`, `superpowers`, `builtin`.

| Role | Used in | Does |
|---|---|---|
| `specify` | `specify`, tracks `feature` and `bug` | writes requirements and scenarios |
| `plan` | `plan` | writes the approach and the task list |
| `implement` | `implement` | builds the change |
| `review` | `review` | reviews the final change independently |
| `diagnose` | `specify`, track `bug` | finds the reproduction and root cause |
| `explore` | `specify`, track `spike` | investigates a question |

`intake`, `triage`, `verify`, `handoff` and `closed` have no provider: the lifecycle does them itself, because no surveyed library covers them and they are what makes the state trustworthy.

A role may only name a provider whose adapter (`references/providers/<name>.md` in the `calibre:run` skill) lists that role.

### `intake.create_issue`

What to do with a request that has no issue. `ask` (default) shows the issue that would be created and creates it on a yes. `never` stops and asks the user to create one.

### `plan.record`

Which plan is the one approved at G2 and tracked for progress, when the `plan` and `implement` providers each keep their own. `plan-provider` (default) makes the `plan` provider's task list the record and the `implement` provider's execution plan a derived file. `implement-provider` reverses that.

A derived plan restates the plan of record, so it is scaffolding: when it is a file of its own, `handoff` deletes it from the task branch before the pull request opens. Mapping `plan` and `implement` to the same provider avoids the second file altogether.

### `verify.max_loops`

How many times a task may go from `verify` back to `implement` before the lifecycle stops with `wait:blocked` and asks a person. Default 3. Repeated failed fixes usually mean the plan or the spec is wrong, which more fixing does not address.

### `handoff.accepted_when`

What gate G3 waits for. `merged` (default): the pull request is merged. `approved`: an approving review or the user's word is enough, for teams that merge on their own schedule. With either value, a task that has checks marked `post-deploy` is accepted only once their results are reported.

### `handoff.archive`

When the spec provider's change is merged back into the living specs. `before-pr` (default): on the task branch before the pull request opens, so the merge delivers code and specs together. `after-merge`: left for a follow-up commit on the default branch. `never`: the lifecycle does not archive.

### `issue_comments`

How much the lifecycle writes on the issue for people who follow the task there. *Issue comments* in `references/record.md` of the `calibre:run` skill defines each kind of comment.

| Value | Posts |
|---|---|
| `summary` (default) | the record comments, a short summary when each state from `specify` on finishes, and a move note for each gate decision and each move back |
| `record` | only the record comments, where the issue is the record's home: the triage verdict, a spike's answer, the pull request link, the closing note |
| `all` | everything in `summary`, plus a move note on every other move |

A config written before `summary` existed says `record` and stays quiet until it is changed.

### `branch_prefix`

Prefix for task branches, which are named `<prefix><issue>-<slug>`. Default `task/`.

### `consent.issue_writes`

`true` when the user agreed at setup that the lifecycle may change labels and post its comments on issues it runs. `false` makes the lifecycle skills ask before each. Creating issues, opening pull requests, closing for an undecided reason and deleting branches are asked every time regardless.

## Changing it later

Re-run `calibre:setup` after installing, upgrading or removing a library. Editing the file by hand is fine too; the lifecycle skills read it fresh each run. A task already under way keeps the artifacts its earlier states produced, so changing a provider mid-task means the next state may not find what it expects: finish or re-plan the task first.
