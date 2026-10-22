---
name: srs
description: Software requirements specification: FR, NFR, business rules, error matrix. Use when elicited scope needs to be formalized into an engineering-ready SRS with standard FR/BR/ERR/NFR identifiers; not for exploratory ideation or scope discovery — that is `/brainstorm`, the other phase-02 skill.
metadata:
  phase: 02-elicit-spec
  category: business-analysis
  version: 1.0.0
  is_core: true
---

# /srs — Software Requirements Specification (IEEE 830) 🌟 [CORE WORKFLOW]

Software requirements specification: FR, NFR, business rules, error matrix

## Objective
Provide expert BA guidance to execute `/srs`, producing an IEEE 830 compliant SRS ready for engineering development.

## Mandatory Standards (Rules)
- `rules/01-fr-naming-convention.md`
- `rules/02-br-naming-convention.md`
- `rules/03-err-naming-convention.md`
- `rules/04-nfr-standards.md`
- `rules/05-srs-ieee-830.md`
- `rules/11-error-matrix-convention.md`
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/08-srs.md` — the commonly used core: FR / BR / Error Matrix / NFR tables.
- `rules/05-srs-ieee-830.md` defines the full IEEE 830 document structure (Introduction, Overall Description, Specific Requirements, Appendices) when a complete SRS beyond the core tables is required.

## Default Storage Path
- `docs/{feature}/srs/spec.md`
- The output document is written in Vietnamese, following the referenced template and rules.

## Expected Input
- Elicitation notes from `/brainstorm` at `docs/{feature}/brainstorms/{concept_name}.md` (agreed In-Scope/Out-of-Scope and business decisions).
- Feature requirements, stakeholder answers, or existing system constraints gathered during elicitation.
- If neither brainstorm notes nor concrete requirements exist for the feature, ask the user for the feature scope and key requirements before drafting — never invent requirements on their behalf.

## Execution Workflow
1. **Input Context**: Ingest findings from `/brainstorm` or feature requirements.
2. **Functional Requirements (FR)**:
   - Assign identifier `FR-[MODULE]-[FEATURE]-[SEQ]` per Rule 01.
   - Mandatory attributes: Inputs, Processing Logic, Outputs.
3. **Business Rules (BR)**:
   - Assign identifier `BR-[DOMAIN]-[SEQ]` per Rule 02.
   - Formulate statements using WHEN ... THEN ... UNLESS ... syntax.
4. **Error Matrix**:
   - Assign identifier `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` per Rules 03 & 11.
   - Detail user-facing messages and recommended resolution paths.
5. **Non-Functional Requirements (NFR)**:
   - Assign category-coded identifiers `NFR-PERF/SEC/REL/USA-xxx` matching the Rule 04 categories.
   - Quantify performance (P95 latency, TPS), security (OWASP, encryption), reliability (uptime, RPO/RTO) per Rule 04.
6. **Save**: Output to `docs/{feature}/srs/spec.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every FR/BR/ERR identifier matches its convention: `FR-[MODULE]-[FEATURE]-[SEQ]`, `BR-[DOMAIN]-[SEQ]`, `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` (Rules 01/02/03).
- [ ] Every NFR carries a Rule 04 category code (`NFR-PERF/SEC/REL/USA-xxx`) and a measurable target (e.g. P95 < 500ms, uptime ≥ 99.9%).
- [ ] Every FR row cross-references the BR codes and ERR codes that govern it.
- [ ] Save output at the designated repository path.
