# Triage brief

The brief is what the next step starts from — `debug-root-cause`, `clarify-requirements`, or an implementer who never saw the original report. Write only the fields that carry content, in the user's language.

```markdown
## Triage brief
Category: bug | enhancement | chore
Summary: <one line>
Current behavior: <bug: what goes wrong; enhancement: what exists today that the change builds on>
Desired behavior: <what the system should do, including edge cases and the failure path>
Key interfaces: <types, functions, config shapes that change, and why>
Acceptance:
- [ ] <observable, checkable on its own>
Out of scope: <neighbouring work this request does not include>
Open decisions: <choices that belong to the user; if any, Next step is clarify-requirements>
Verification: reproduced (<code path>) | not reproduced | not attempted: <reason>
Next step: debug-root-cause | clarify-requirements | implement
Needs a human because: <only when an agent cannot take it>
```

## What makes it usable

- **Behavior, not procedure.** Say what the system does today and what it should do. "Open file X and change line Y" hands over a guess about the fix in place of the requirement.
- **Interfaces over locations** when the brief will be saved or passed to another agent: a function name, a config shape, or a check's label still means something after the code moves, while a path and line number may not. A brief used right away in the same session may cite `file:line`.
- **Acceptance the reader can run.** Each criterion is checkable without the others, and at least one covers the main failure path. Leave `Acceptance` out when it depends on a decision listed under `Open decisions`.
- **A fence.** `Out of scope` names the adjacent work an eager implementer would otherwise fold in.
- **Honest verification.** Copy the result of the quick verification as it happened; `not attempted` with the command awaiting approval is more useful than an implied "should reproduce".

## A brief that works

Illustrative, based on this marketplace's validation script; check the claims against the actual repo before reusing it.

```markdown
## Triage brief
Category: bug
Summary: Marketplace validation passes a skill whose frontmatter `description` is empty
Current behavior: The skill-frontmatter check accepts any `SKILL.md` whose first block contains a `description:` key, even with nothing after it. Such a skill installs but never triggers, because harnesses match on the description.
Desired behavior: An empty or whitespace-only `description` (and likewise `name`) fails validation with a line naming the skill. A quoted or folded multi-line description that has content still passes.
Key interfaces: the skill-frontmatter check of the validation script (check "c" in its header). Its `[PASS]`/`[FAIL]` line format and non-zero exit on any failure stay as they are.
Acceptance:
- [ ] A skill with `description:` and no value makes validation exit 1 with a `[FAIL]` line naming that skill
- [ ] A skill with a folded (`description: >`) multi-line description passes
- [ ] Every skill currently in the repo still passes
- [ ] A missing `description:` key still produces one failure line, not two
Out of scope: checks on description length or wording; validating Cursor rules or `gemini-context.md`.
Verification: reproduced (scratch copy of a skill with an empty description reports `[PASS] skill frontmatter ok`; the check only tests that a line starts with `description:`)
Next step: debug-root-cause
```

It names the behavior on both sides, points at a check by what it does, lists criteria that each pass or fail alone, includes a failure path, fences off the neighbouring checks, and says what was actually observed.

## A brief that doesn't

```markdown
## Triage brief
Summary: Fix validate
The validate script is wrong for descriptions. Open scripts/validate.sh, go to line 503 and change the awk condition. Tidy the other checks while you're there.
```

- No category, and no current versus desired behavior: "wrong" could mean anything.
- A procedure tied to a line number, which stops being true the next time the script is edited.
- No acceptance, so nobody can tell when the work is done.
- "Tidy the other checks" invites exactly the scope creep `Out of scope` exists to prevent.
- No verification status: the reader cannot tell whether anyone saw the bug happen.
