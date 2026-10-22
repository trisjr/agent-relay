---
name: ac
description: "Write Given / When / Then acceptance criteria for user stories. Use when user stories already exist (e.g. in `docs/{feature}/userstories/backlog.md` from the `userstory` skill) and need testable Gherkin scenarios — not for writing or refining the stories themselves (use `userstory`)."
metadata:
  phase: 04-usecase-story
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /ac — Acceptance Criteria (Gherkin BDD) 🌟 [CORE WORKFLOW]

Write Given / When / Then acceptance criteria for each user story

## Objective
Provide expert BA guidance to execute `/ac`, generating production-ready acceptance criteria without formatting rework. The output document is written in Vietnamese, following `../../_templates/28-acceptance-criteria.md`.

## Mandatory Standards (Rules)
- `../../rules/08-gherkin-acceptance-criteria.md`
- `../../rules/16-ambiguity-detection-rules.md`
- `../../rules/03-err-naming-convention.md`

## Reference Template
- `../../_templates/28-acceptance-criteria.md` — read it before writing; it defines the per-story `## Story: US-XXX` section format.

## Default Storage Path
- `docs/{feature}/userstories/acceptance-criteria.md` — ONE file aggregating all stories of the feature; each story gets its own `## Story: US-XXX` section per the template.

## Expected Input
- User stories from `docs/{feature}/userstories/backlog.md` (output of the `userstory` skill), or story content provided directly by the user.
- Optional context: the use cases / functional requirements the stories were derived from.
- If no user story is available, ask the user to supply the stories or run `/userstory` first — never invent requirements or stories on your own.

## Execution Workflow
1. Read the target User Story (from Expected Input).
2. Formulate at least 3 BDD scenarios per story:
   - Scenario 1: Happy Path (Success flow).
   - Scenario 2: Business Error / Negative Path (Controlled failure) — cite the expected error code in `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` format per Rule 03 where the system returns one.
   - Scenario 3: Boundary & Security (edge values such as max length +1 or an empty required field, plus security constraints such as injection attempts or unauthorized access) per Rule 08.
3. Adhere strictly to Given - When - Then syntax per Rule 08.
4. Append each story's scenarios under a `## Story: US-XXX` section (per `../../_templates/28-acceptance-criteria.md`) in the single shared file `docs/{feature}/userstories/acceptance-criteria.md`; do not create one file per story.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every story has at least 3 scenarios covering Happy Path, Business Error / Negative Path, and Boundary & Security (Rule 08).
- [ ] Every negative-path scenario asserts the exact `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` code (Rule 03) or the exact user-facing error message.
- [ ] Each story's criteria sit under its own `## Story: US-XXX` section in the single shared `acceptance-criteria.md` file, matching template 28.
- [ ] Save output at the designated repository path.
