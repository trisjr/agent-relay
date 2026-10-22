---
name: brainstorm
description: Capture raw ideas and conduct clarifying interviews before documenting. Use when a stakeholder brings a rough, unstructured business idea and scope or edge cases are still ambiguous — run this before /srs or any formal spec writing; not for requirements that are already clarified and agreed.
metadata:
  phase: 02-elicit-spec
  category: business-analysis
  version: 1.0.0
  is_core: true
---

# /brainstorm — Raw Business Idea Elicitation & Clarification 🌟 [CORE WORKFLOW]

Capture raw ideas and conduct clarifying interviews before documenting

## Objective
Provide expert BA guidance to execute `/brainstorm`, leading a Socratic interview to disambiguate scope before writing formal specifications. The output minutes are written in Vietnamese, following the structure of `_templates/04-brainstorm.md`.

## Mandatory Standards (Rules)
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/04-brainstorm.md`

## Default Storage Path
- `docs/{feature}/brainstorms/{concept_name}.md`

## Expected Input
- A raw business idea or problem statement from the user or stakeholders (free-form conversation, notes, or pitch).
- Optional prior context under `docs/{feature}/` (existing brainstorms or specs) to avoid re-opening settled decisions.
- If the user has not stated any concrete idea or topic, ask what business problem they want to explore — never invent requirements on their behalf.

## Execution Workflow
1. **Capture Raw Concept**:
   - Solicit unstructured business thoughts from user or stakeholders.
   - Agree with the user on `{feature}` (kebab-case slug of the product domain, e.g. `online-booking`) and `{concept_name}` (kebab-case slug for this specific idea, e.g. `loyalty-points`) before writing anything — these slugs anchor the storage path used in step 3.
2. **Socratic Interview (Critical Clarification)**:
   - Act as a Senior BA, asking 3-5 high-impact questions targeting edge conditions:
     + Exception handling during network drops or 3rd-party outages?
     + Handling duplicate data submissions?
     + User cancellation and mid-flow drop-off?
     + Role-based permissions and segregation of duties?
3. **Consolidate Scope**:
   - Produce explicit In-Scope vs Out-of-Scope boundaries.
   - Record agreed business decisions into `docs/{feature}/brainstorms/{concept_name}.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every decision in the minutes is confirmed with the stakeholder — no item left as TBD or an unanswered question.
- [ ] In-Scope vs Out-of-Scope boundaries are explicitly recorded.
- [ ] Save output at the designated repository path.
