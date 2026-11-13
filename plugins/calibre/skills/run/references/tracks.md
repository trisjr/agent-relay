# Tracks

The track is chosen in `triage` and decides which states a task visits. Pick by what the request needs, not by how it was phrased.

| Track | Use when | Path |
|---|---|---|
| `feature` | Behavior is added or changed and someone has to decide what "right" means | `intake` → `triage` → `specify` → `plan` → `implement` → `verify` → `review` → `handoff` → closed |
| `bug` | Existing behavior is wrong and the cause is not yet known | same nine states; `specify` finds the reproduction and root cause instead of writing requirements |
| `chore` | A small change with no behavior decision left to make | `intake` → `triage` → `implement` → `verify` → `handoff` → closed |
| `spike` | The request is a question, or a decision that needs investigation first | `intake` → `triage` → `specify` → closed as `answered` |

## Choosing

- **`chore` is narrow on purpose.** It skips the spec, the plan, gate G2 and the independent review, so it only fits work where skipping them loses nothing: a dependency bump, a typo, a config value, a rename with no behavior change. The test is whether the whole acceptance fits in one or two lines written during triage. If writing them reveals a choice, it is a `feature`.
- **A bug whose fix is obvious is still a `bug`.** The obvious fix is frequently the symptom fix. The `bug` track exists to make someone find the cause before changing code.
- **A `spike` produces an answer, not a change.** If the investigation shows work is needed, close the spike as `answered` and open that work as its own issue, which starts at `intake` with the spike linked.
- **Unsure between `feature` and `chore`: choose `feature`.** The cost of the extra states is small next to shipping an unreviewed behavior change.

## What each track reads where

Every state reads what an earlier state on the same track produced. The two short tracks need care:

- **`chore`** has no spec and no plan. `triage` therefore writes the acceptance criteria (`AC-1`, …) and how each will be checked. `implement` builds against them and `verify` proves them. The task branch and the record are created on entering `implement`.
- **`spike`** ends in `specify`. Its output is the findings and the answer, posted on the issue, which is also where the record lives: a spike never gets a branch.

## Changing track

A task that turns out to be on the wrong track goes back to `triage` (`lifecycle.sh state <n> triage`), gets a new track, and continues from there. Work already recorded stays in the record; states the new track needs and the old one skipped still have to be done.
