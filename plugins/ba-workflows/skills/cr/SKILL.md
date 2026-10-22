---
name: cr
description: "Analyze change impact and synchronize affected specifications. Use when a client or Product Owner submits a change request and you must assess its impact across specs, DB schema, and APIs before any document is modified — not for auditing drift between existing docs and code (use doc-drift for that)."
metadata:
  phase: 08-quality-change
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /cr — Change Request (CR) Impact Analysis 🌟 [CORE WORKFLOW]

Analyze change impact and synchronize affected specifications

## Objective
Provide expert BA guidance to execute `/cr`, performing thorough impact analysis and syncing changes across project artifacts. Write the CR report and all updated documents in Vietnamese, following `_templates/47-change-request.md`.

## Mandatory Standards (Rules)
- `rules/01-fr-naming-convention.md`
- `rules/03-err-naming-convention.md`
- `rules/15-change-request-impact-matrix.md`
- `rules/16-ambiguity-detection-rules.md`
- `rules/19-document-versioning-rules.md`

## Reference Template
- `_templates/47-change-request.md`

## Default Storage Path
- `docs/{feature}/cr/{cr_id}.md`

## Expected Input
- Change request details from the client or Product Owner, at minimum the fields of the "Thông tin đề xuất CR" section in `_templates/47-change-request.md`: CR ID (`CR-YYYY-NNN`), change name, requester, request date, and urgency level. If any field is missing, ask the user before proceeding — never invent CR details.
- Existing specifications to analyze, by convention: `docs/{feature}/srs/spec.md`, `docs/{feature}/srs/flows.md`, `docs/{feature}/userstories/backlog.md`, and `docs/{feature}/test/test-cases.md`.
- If an expected input document is missing, report which artifact could not be assessed and continue with what exists — never fabricate requirements to fill the gap.

## Execution Workflow
1. Ingest change request details from client or Product Owner. Collect at minimum the fields of the "Thông tin đề xuất CR" section in `_templates/47-change-request.md`: CR ID (`CR-YYYY-NNN`), change name, requester, request date, and urgency level.
2. Execute Impact Analysis per Rule 15:
   - Identify affected documents (SRS, Diagrams, Stories, Test cases).
   - Assess impact on DB schemas and API contracts.
   - Estimate technical complexity, timeline, and regression risks.
3. Present CR report for approval. STOP and WAIT for the user's explicit confirmation — do not modify any document in step 4 until the user has clearly approved the report.
4. Upon explicit approval, update all referenced documentation and increment version numbers per Rule 19. New or changed functional requirements and error codes must follow the FR and ERR identifier conventions (Rules 01 and 03).

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every row of the impact matrix names the concrete affected files/components and an effort estimate, per `_templates/47-change-request.md`.
- [ ] New or modified requirements and error codes use valid FR-xxx / ERR-xxx identifiers per Rules 01 and 03.
- [ ] Save output at the designated repository path.
