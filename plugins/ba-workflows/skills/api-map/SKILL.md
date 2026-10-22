---
name: api-map
description: "3-layer field mapping: partner API, database schema, and UI. Use when the API contract already exists and every field must be reconciled across UI inputs, DB columns, and partner API payloads — unlike api-design, which authors the contract itself; run api-map after api-design."
metadata:
  phase: 06-api-integration
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /api-map — 3-Layer Data Mapping Matrix 🌟 [CORE WORKFLOW]

3-layer field mapping: partner API, database schema, and UI

## Objective
Provide expert BA guidance to execute `/api-map`, producing end-to-end data reconciliation across UI inputs, DB columns, and API payloads. The output document is written in Vietnamese, following `_templates/38-api-map.md`.

## Mandatory Standards (Rules)
- `rules/03-err-naming-convention.md`
- `rules/09-data-dictionary-standard.md`
- `rules/10-api-contract-standards.md`
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/38-api-map.md`

## Default Storage Path
- `docs/{feature}/api/data-mapping.md`

## Expected Input
- `docs/{feature}/api/api-spec.md` — API contract produced by `/api-design`; `/api-map` runs AFTER `/api-design`, never before it.
- Data Dictionary per Rule 09 in `docs/{feature}/srs/erd.md` (output of `/erd`) — source of truth for DB column names, types, and nullability.
- UI source: wireframe (`docs/{feature}/html-wireframe/{screen_name}.html`) or UI spec — source of Layer 1 screen labels and input IDs.
- If any input is missing, ask the user for it or report it as missing; never invent fields, types, or contract details.

## Execution Workflow
1. Construct 3-layer cross-reference table:
   - Layer 1: User Interface element (UI Input/Label).
   - Layer 2: Internal database attribute (Database Column).
   - Layer 3: Partner/External API JSON payload (API Field Name).
2. Explicitly document Transformation Rules (date-time formats, encoding, currency units, nullability) and the mapping error matrix with ERR-xxx codes per Rule 03.
3. Save to `docs/{feature}/api/data-mapping.md`.

## Quality Acceptance Checklist
- [ ] Every API field in the contract is mapped across the 3 layers or explicitly marked N/A.
- [ ] Every data-type mismatch between layers has a quantified Transformation Rule (TR-xxx), free of vague qualifiers (Rule 16).
- [ ] Nullability is consistent across all 3 layers; NULL ↔ omitted-key behavior is documented.
- [ ] Use professional technical BA terminology.
- [ ] Save output at the designated repository path.
