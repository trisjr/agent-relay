---
name: code-to-srs
description: "Reverse-engineer an SRS from legacy source code: read controllers, models, validation and services, then derive FR / BR / ERR with file:line citations. Use when a system has code but no (or outdated) specification and you must rebuild the requirements from what the code actually does — not for reconciling an existing SRS against code (use `/doc-drift`) or writing an SRS from stakeholder input (use `/srs`)."
metadata:
  phase: 02-elicit-spec
  category: business-analysis
  version: 1.0.0
  is_core: false
---

# /code-to-srs — Reverse-Engineer SRS from Source Code [STANDARD WORKFLOW]

Read legacy source code and rebuild the SRS with file and line citations.

## Objective
Provide expert BA guidance to execute `/code-to-srs`, deriving a code-backed specification of what the system actually does today, so it can be reviewed, corrected and promoted into a formal SRS.

## Mandatory Standards (Rules)
- `../../rules/01-fr-naming-convention.md`
- `../../rules/02-br-naming-convention.md`
- `../../rules/03-err-naming-convention.md`
- `../../rules/05-srs-ieee-830.md`
- `../../rules/16-ambiguity-detection-rules.md`

## Reference Template
- `../../_templates/14-code-to-srs.md`

## Default Storage Path
- `docs/{feature}/srs/code-derived-spec.md`
- Write the document in Vietnamese, following `../../_templates/14-code-to-srs.md`.

## Expected Input
- The feature / module to reverse-engineer and read access to its code (record branch and commit hash in the document header).
- If the target feature or code location is unclear, ask the user to name the module or entry points before reading — do not scan the whole repository blindly.

## Execution Workflow
1. **Locate scope**: find the entry points of the feature (routes, controllers, handlers, jobs) and follow them into services, models, validators and error handling.
2. **Extract real behavior**: record what the code does, not what it should do. Validation limits, state changes, calculations, permission checks and thrown errors are the raw material; comments and naming are hints only.
3. **Map to identifiers** with a code citation (`path/file.ext:line` or `:start-end`) on every item:
   - Functional Requirements `FR-[MODULE]-[FEATURE]-[SEQ]` per Rule 01 — Inputs, Processing Logic, Outputs.
   - Business Rules `BR-[DOMAIN]-[SEQ]` per Rule 02, stated as WHEN ... THEN ... UNLESS ....
   - Errors `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` per Rule 03. If the code returns an error with no code or message (e.g. unhandled exception → 500), record it as observed and flag it.
4. **Flag uncertainty instead of guessing**: hardcoded magic numbers with no evident business reason, dead code, feature flags, and behavior that looks like a bug go to the "Điểm cần xác nhận" section for the BA / Product to confirm. A bug reproduced as a requirement would be enshrined by the SRS.
5. **Save** to `docs/{feature}/srs/code-derived-spec.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every FR / BR / ERR carries a unique identifier matching its convention (Rules 01/02/03).
- [ ] Every FR / BR / ERR cites at least one `file:line` that exists in the audited commit; no requirement is stated without code evidence.
- [ ] Behavior that is unclear, suspicious or unreachable is listed under items to confirm, not silently promoted to a requirement.
- [ ] Header records the branch and commit hash audited.
- [ ] Save output at the designated repository path.
