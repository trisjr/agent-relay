---
name: test-checklist
description: "High-level test outline and scenario checklist for early review. Use when you need to align on verification scope early — business branches and scenario coverage across the 5 test dimensions — before writing granular executable test cases with /test-cases."
metadata:
  phase: 07-testing
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /test-checklist — Test Scenario Outline & Checklist 🌟 [CORE WORKFLOW]

High-level test outline and scenario checklist for early review

## Objective
Provide expert BA guidance to execute `/test-checklist`, defining comprehensive verification boundaries before authoring granular test cases. The output document is written in Vietnamese, following the Reference Template.

## Mandatory Standards (Rules)
- `../../rules/14-test-case-traceability.md`
- `../../rules/16-ambiguity-detection-rules.md`
- `../../rules/20-artifact-identifier-conventions.md`

## Reference Template
- `../../_templates/42-test-checklist.md`

## Default Storage Path
- `docs/{feature}/test/checklist.md`

## Expected Input
- SRS at `docs/{feature}/srs/spec.md` — source of `FR-xxx` / `BR-xxx` / `NFR-xxx` requirements used to derive business branches.
- User story backlog at `docs/{feature}/userstories/backlog.md` — source of `US-xxx` / `AC-xxx` for branch and scenario traceability.
- If either input is missing or incomplete, report what is missing and ask the user whether to proceed with reduced scope or run the upstream skill (`/srs`, `/userstory`) first — never invent requirements to fill the gap.

## Execution Workflow
1. Synthesize business branches from the SRS and User Stories; assign each branch a `BRN-[MODULE]-[SEQ]` code with explicit source trace (`FR-xxx` / `BR-xxx` / `US-xxx`) per Rule 20.
2. Outline test scenarios across the 5 dimensions — Functional, UI/UX, Performance, Security, Boundary Data — assigning `CHK-[MODULE]-[SEQ]` codes (or `TC-xxx` directly as Checklist ID; never mix both schemes on the same item) per Rule 20.
3. Present the coverage-scope outline (branch list, dimension coverage, scenario count per branch) to the user for BA & QA alignment, and only save the file after the user confirms the scope; record the confirmation in the Alignment Sign-off section.
4. Save to `docs/{feature}/test/checklist.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every business branch carries a `BRN-xxx` code with source trace (`FR-xxx` / `BR-xxx` / `US-xxx`) and at least one mapped scenario; scenario items use `CHK-xxx` or `TC-xxx` consistently, never both on the same item (Rule 20).
- [ ] Checklist covers all 5 test dimensions (Functional, UI/UX, Performance, Security, Boundary Data) and the traceability matrix shows every in-scope `FR-xxx` covered by at least one scenario (Rule 14).
- [ ] Save output at the designated repository path.
