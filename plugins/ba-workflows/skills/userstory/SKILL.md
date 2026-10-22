---
name: userstory
description: "Generate INVEST-compliant user stories ready for sprint backlog. Use when use cases or functional requirements are already specified and need to be decomposed into sprint-ready user stories with story points and priorities — pick this over `usecase` (which writes detailed use case specs and flows upstream) and over acceptance-criteria detailing when the goal is backlog planning, not test design"
metadata:
  phase: 04-usecase-story
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /userstory — Backlog User Story Breakdown 🌟 [CORE WORKFLOW]

Generate INVEST-compliant user stories ready for sprint backlog

## Objective
Provide expert BA guidance to execute `/userstory`, decomposing requirements into independent, testable user stories. The backlog document is written in Vietnamese, following the reference template.

## Mandatory Standards (Rules)
- `rules/07-invest-user-story.md`
- `rules/16-ambiguity-detection-rules.md`
- `rules/20-artifact-identifier-conventions.md`

## Reference Template
- `_templates/27-userstory.md`

## Default Storage Path
- `docs/{feature}/userstories/backlog.md` (Vietnamese content per template)

## Expected Input
- Use cases from `docs/{feature}/usecases/` and/or functional requirements from `docs/{feature}/srs/spec.md` — at least one of the two must exist.
- The feature name and its module abbreviation per Rule 01 (used to build `US-[MODULE]-[SEQ]` codes).
- When input artifacts are missing or incomplete: ask the user to provide them or point to the correct paths — never invent requirements or stories on your own.

## Execution Workflow
1. Decompose Use Cases / Functional Requirements into granular stories.
2. Apply standard format: As a [Role/Actor], I want [Capability], so that [Business Benefit].
3. Verify INVEST criteria compliance per Rule 07.
4. Assign Story Points on the Fibonacci scale 1/2/3/5/8 and priority tags (P0/P1/P2). Any story estimated above 5 points must be split into smaller stories before entering the backlog.
5. Save to `docs/{feature}/userstories/backlog.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every story carries an ID in the `US-[MODULE]-[SEQ]` format per Rule 20, with a 2-digit SEQ numbered continuously within the module.
- [ ] Story points use only Fibonacci values 1/2/3/5/8; no story above 5 points remains unsplit.
- [ ] Each story traces back to its source UC and/or FR identifier.
- [ ] Save output at the designated repository path.
