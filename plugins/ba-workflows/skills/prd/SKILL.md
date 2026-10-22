---
name: prd
description: "Product-wide PRD: vision, personas, and feature breakdown. Use when kicking off a new product and you need the product-wide PRD — vision, PER-xx personas, and FEAT-xxx feature breakdown — before any feature-level specification; for raw idea elicitation use /brainstorm, and for feature-level specs use /srs."
metadata:
  phase: 01-planning
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /prd — Product Requirements Document (PRD) 🌟 [CORE WORKFLOW]

Product-wide PRD: vision, personas, and feature breakdown

## Objective
Provide expert BA guidance to execute `/prd`, crafting comprehensive product requirements documents with quantitative goals and clear scopes. Write the output document in Vietnamese, following the structure and tables of `../../_templates/01-prd.md`.

## Mandatory Standards (Rules)
- `../../rules/01-fr-naming-convention.md`
- `../../rules/16-ambiguity-detection-rules.md`
- `../../rules/17-actor-role-definition.md`
- `../../rules/20-artifact-identifier-conventions.md`

## Reference Template
- `../../_templates/01-prd.md`

## Default Storage Path
- `docs/{product_name}/01-prd.md`

## Expected Input
- Product name, business context, strategic vision, and quantitative business targets (KPIs / OKRs) provided by the user or stakeholders.
- Optional: prior elicitation notes from `/brainstorm` at `docs/{feature}/brainstorms/{concept_name}.md`, if any exist.
- If any required input is missing, ask the user for it before writing — never invent product goals, personas, or scope on your own.

## Execution Workflow
1. **Gather Context**:
   - Product name, business context, strategic vision.
   - Core problem statement and primary beneficiary.
   - Quantitative business targets (KPIs / OKRs).
2. **Define Personas**:
   - Apply Rule `../../rules/17-actor-role-definition.md` only to identify the platform actors (Primary / Secondary / System) that personas map to.
   - Define personas with `PER-xx` IDs following the persona table in `../../_templates/01-prd.md` (Section 2); do not embed the RBAC permission matrix from Rule 17 into the PRD.
3. **Feature Breakdown**:
   - Define strict In-Scope vs Out-of-Scope boundaries for MVP/phase.
   - Structure feature backlog with priorities: P0 (Must), P1 (Should), P2 (Nice to have); each feature carries a `FEAT-xxx` ID and references the `PER-xx` personas it serves.
4. **Ambiguity Audit**:
   - Apply Rule `../../rules/16-ambiguity-detection-rules.md` to remove subjective phrasing ("phản hồi nhanh chóng", "thân thiện, dễ dùng", "bảo mật cao") and replace each with the measurable formulation from the rule's normalization table.
5. **Output**:
   - Populate template `../../_templates/01-prd.md` and save to `docs/{product_name}/01-prd.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Personas numbered `PER-xx` (2-digit sequence from `01`) per Rule 20 and the template's persona table.
- [ ] Every feature in the Feature Breakdown carries a `FEAT-xxx` ID (3-digit sequence from `001`), a P0/P1/P2 priority, and at least one referenced `PER-xx` persona.
- [ ] Save output at the designated repository path.
