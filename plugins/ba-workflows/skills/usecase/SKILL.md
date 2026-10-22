---
name: usecase
description: Cockburn-style detailed use cases: actor, conditions, main, exception. Use when detailing one end-to-end system interaction (primary actor, pre/post-conditions, main success scenario, extensions citing ERR codes) for a specific use case; use `userstory` instead when decomposing requirements into INVEST backlog stories.
metadata:
  phase: 04-usecase-story
  category: business-analysis
  version: 1.0.0
  is_core: true
---

# /usecase — Cockburn Detailed Use Case Specification 🌟 [CORE WORKFLOW]

Cockburn-style detailed use cases: actor, conditions, main, exception

## Objective
Provide expert BA guidance to execute `/usecase`, producing standardized Alistair Cockburn use case specifications. Write the output document in Vietnamese, following the reference template and rules.

## Mandatory Standards (Rules)
- `rules/03-err-naming-convention.md`
- `rules/06-cockburn-use-case.md`
- `rules/16-ambiguity-detection-rules.md`
- `rules/17-actor-role-definition.md`

## Reference Template
- `_templates/26-usecase-cockburn.md`

## Default Storage Path
- `docs/{feature}/usecases/{usecase_id}.md`

## Expected Input
- Feature/module name — required to assign the `UC-[MODULE]-[SEQ]` identifier; ask the user if missing.
- Primary actor and the use case goal — ask the user if either is unclear.
- Upstream SRS at `docs/{feature}/srs/spec.md` for FR/BR/ERR context (optional); if absent, note the gap and proceed only with user-provided context — never invent requirements.

## Execution Workflow
1. Assign identifier `UC-[MODULE]-[SEQ]` and Verb + Noun title (Rule 06).
2. Define Primary Actor, Pre-conditions, and Post-conditions (Guarantees).
3. Detail Main Success Scenario numbered steps 1, 2, 3...
4. Detail Extensions & Exceptions (3a, 3b, 5a...) citing corresponding `ERR-xxx` codes per Rule 03 (`ERR-[MODULE]-[HTTP_STATUS]-[SEQ]`).
5. Save to `docs/{feature}/usecases/{usecase_id}.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Use case ID matches `UC-[MODULE]-[SEQ]` and the title is Verb + Noun (Rule 06).
- [ ] Every extension/exception step cites an `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` code consistent with Rule 03.
- [ ] Save output at the designated repository path.
