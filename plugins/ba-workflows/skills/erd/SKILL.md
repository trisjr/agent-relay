---
name: erd
description: "Data entity relationship diagrams (Mermaid ERD) and dictionary. Use when a feature needs its persistent data modeled — entities, attributes, primary/foreign keys, and explicit cardinalities — together with a Data Dictionary; for behavioral flows (interactions, processes, lifecycles) use /sequence, /activity, or /state instead."
metadata:
  phase: 03-diagrams
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /erd — Entity Relationship Diagram (Mermaid ERD) 🌟 [CORE WORKFLOW]

Data entity relationship diagrams (Mermaid ERD) and dictionary

## Objective
Provide expert BA guidance to execute `/erd`, generating normalized relational data models and comprehensive data dictionaries. Write the output document in Vietnamese, following the structure of `../../_templates/20-erd-mermaid.md`.

## Mandatory Standards (Rules)
- `../../rules/09-data-dictionary-standard.md`
- `../../rules/16-ambiguity-detection-rules.md`

## Reference Template
- `../../_templates/20-erd-mermaid.md`

## Default Storage Path
- `docs/{feature}/srs/erd.md`

## Expected Input
- Feature name — determines the `docs/{feature}/` output path.
- Entity sources listing the feature's data: the SRS at `docs/{feature}/srs/spec.md` and/or use case specs at `docs/{feature}/usecases/{usecase_id}.md`.
- If the feature name or every entity source is missing, ask the user before proceeding — never invent entities, attributes, or relationships on your own.

## Execution Workflow
1. Enumerate core entities and attributes from the SRS and/or use case inputs.
2. Construct Mermaid `erDiagram` with explicit cardinalities (`||--o{`, `||--||`, etc.).
3. Document fields, datatypes, and primary/foreign keys (PK/FK).
4. Construct the detailed Data Dictionary per Rule 09, following the "Từ điển Dữ liệu (Data Dictionary)" section of `../../_templates/20-erd-mermaid.md` — one specification table per entity covering every field shown in the diagram.
5. Save to `docs/{feature}/srs/erd.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every entity declares an explicit primary key (PK).
- [ ] Every relationship line carries an explicit Mermaid cardinality (`||--o{`, `||--||`, `}o--o{`, …) — no bare connectors.
- [ ] Every field shown in the `erDiagram` has a matching Data Dictionary row with a defined datatype (Rule 09 / template).
- [ ] Save output at the designated repository path.
