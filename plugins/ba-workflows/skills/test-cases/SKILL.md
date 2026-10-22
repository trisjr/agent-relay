---
name: test-cases
description: Detailed executable test cases generated from checklist and specs. Use when turning an existing test checklist and acceptance criteria into step-by-step executable test cases with preconditions, test data and expected results — not for drafting the high-level test outline itself (use `/test-checklist` for that).
metadata:
  phase: 07-testing
  category: business-analysis
  version: 1.0.0
  is_core: true
---

# /test-cases — Detailed Test Cases Specification 🌟 [CORE WORKFLOW]

Detailed executable test cases generated from checklist and specs

## Objective
Provide expert BA guidance to execute `/test-cases`, delivering traceable test suites mapped to acceptance criteria and error matrices.

## Mandatory Standards (Rules)
- `rules/02-br-naming-convention.md`
- `rules/03-err-naming-convention.md`
- `rules/08-gherkin-acceptance-criteria.md`
- `rules/11-error-matrix-convention.md`
- `rules/14-test-case-traceability.md`
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/43-test-cases.md`

## Default Storage Path
- `docs/{feature}/test/test-cases.md`

The referenced template and rules are in Vietnamese; write the output document in Vietnamese following `_templates/43-test-cases.md`.

## Expected Input
- Acceptance Criteria (Gherkin scenarios) from `docs/{feature}/userstories/acceptance-criteria.md` (output of `/ac`).
- Test Checklist outline from `docs/{feature}/test/checklist.md` (output of `/test-checklist`).
- Declared `ERR-xxx` codes and `BR-xxx` rules from the feature's SRS / error matrix.
- If any input is missing, ask the user for it or report the gap — never invent acceptance criteria, error codes, or business rules.

## Execution Workflow
1. Ingest Acceptance Criteria scenarios and Test Checklist outlines.
2. Generate structured test cases following the field structure in `_templates/43-test-cases.md`: Test Case ID, Story ID, AC link, Preconditions, Test Data, Test Steps, Expected Results.
3. Map every test case to its FR/US/AC in the Requirement Traceability Matrix per Rule 14 (traceability only — field structure comes from the template).
4. Ensure 100% coverage for all documented `ERR-xxx` codes and `BR-xxx` rules (Rules 02, 03, 11).
5. Save to `docs/{feature}/test/test-cases.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every test case follows the `_templates/43-test-cases.md` field structure with ID format `TC-{MODULE}-{NNN}` and links to its Story ID and AC.
- [ ] Every documented `ERR-xxx` and `BR-xxx` appears in the coverage matrix, and every test case maps to an FR/US/AC in the RTM (Rule 14).
- [ ] Save output at the designated repository path.
