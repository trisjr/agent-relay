---
name: sequence
description: Sequence diagrams: participant interactions, order, and error branches. Use when you need to model time-ordered message exchanges between actors and systems for a specific use case flow or API endpoint, including failure branches — rather than a business-process flow (use /activity) or an entity lifecycle (use /state).
metadata:
  phase: 03-diagrams
  category: business-analysis
  version: 1.0.0
  is_core: true
---

# /sequence — Sequence Diagram (Mermaid) 🌟 [CORE WORKFLOW]

Sequence diagrams: participant interactions, order, and error branches

## Objective
Provide expert BA guidance to execute `/sequence`, producing detailed interaction workflows with complete happy and error branches. The output document is written in Vietnamese, following the reference template.

## Mandatory Standards (Rules)
- `rules/01-fr-naming-convention.md`
- `rules/03-err-naming-convention.md`
- `rules/10-api-contract-standards.md`
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/15-sequence-diagram.md`

## Default Storage Path
- `docs/{feature}/srs/flows.md`

## Expected Input
- Feature name and a description of the flow, or the API endpoint to model (e.g. `POST /api/v1/auth/login`).
- The list of participants (User, Frontend, API Gateway, Service, Database, 3rd Party). If any of these inputs is missing, ask the user — never invent flows or participants.
- Optional upstream artifact for identifier traceability: SRS at `docs/{feature}/srs/spec.md` (FR codes per Rule 01, Error Matrix per Rule 03). If it is absent, ask the user before proceeding.

## Execution Workflow
1. Identify Actors and Participants (User, Frontend, API Gateway, Service, Database, 3rd Party).
2. Construct Mermaid sequence diagram (`sequenceDiagram`) with `autonumber`.
3. Include both success flows (`alt Valid`) and failure flows (`else Error`).
4. Annotate corresponding `ERR-xxx` codes at error branching points and trace each diagram back to its source `FR-xxx` per Rule 01.
5. Append the diagram to `docs/{feature}/srs/flows.md` under its own heading per use case (e.g. `## Luồng <Use Case Name>`); never overwrite or delete existing content in that file.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Both success and error branches are present for every step that can fail.
- [ ] Every error branch cites an `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` code per Rule 03.
- [ ] Each diagram traces back to its source `FR-xxx` identifier per Rule 01.
- [ ] Save output at the designated repository path.
