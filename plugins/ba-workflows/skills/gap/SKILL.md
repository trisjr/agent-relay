---
name: gap
description: "Identify missing business branches, edge cases, and security gaps. Use when auditing requirement artifacts (SRS, use cases, wireframes, test cases) for unhandled branches before engineering handoff — for drift between implemented code and specs, use `/doc-drift` instead."
metadata:
  phase: 08-quality-change
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /gap — Business Logic Gap Analysis 🌟 [CORE WORKFLOW]

Identify missing business branches, edge cases, and security gaps

## Objective
Provide expert BA guidance to execute `/gap`, auditing requirements across artifacts to eliminate missing branches before engineering handoff. The output document is written in Vietnamese, following `_templates/45-gap-analysis.md`.

## Mandatory Standards (Rules)
- `rules/02-br-naming-convention.md`
- `rules/16-ambiguity-detection-rules.md`
- `rules/20-artifact-identifier-conventions.md`

## Reference Template
- `_templates/45-gap-analysis.md`

## Default Storage Path
- `docs/{feature}/gap-analysis.md`

## Expected Input
- SRS: `docs/{feature}/srs/spec.md`
- Wireframes: `docs/{feature}/html-wireframe/`
- Use Cases: `docs/{feature}/usecases/`
- Test Cases: `docs/{feature}/test/test-cases.md`
- If any artifact is missing, report which one and ask the user whether to proceed with the available set or generate the missing artifact first — never invent requirements to fill the gap.

## Execution Workflow
1. Cross-audit feature artifacts: SRS, Wireframes, Use Cases, and Test Cases.
2. Search for blind spots and gaps:
   - Missing cancellation, rollback, or timeout paths.
   - Unhandled network failures and 3rd-party integration errors.
   - Missing boundary validation, special characters, or injection hygiene.
   - Incomplete permission boundaries between roles.
3. Generate findings and actionable recommendations in `docs/{feature}/gap-analysis.md`, assigning each finding a `GAP-xxx` identifier per Rule 20 §8.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every finding carries a `GAP-[SEQ]` identifier (3-digit SEQ, restarting from `001` per report) per Rule 20 §8.
- [ ] Every finding cites the source artifact location and the related identifier (FR/BR/UC/TC) it traces to, with severity and an actionable recommendation per template `_templates/45-gap-analysis.md`.
- [ ] Save output at the designated repository path.
