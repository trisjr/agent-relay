---
name: kg
description: "Generate structured artifact dependency graphs and cross-reference maps across project documentation. Use when you need a machine-readable map of how documents, requirements, diagrams, errors, and test cases interlink across `docs/` — for impact analysis, change scoping, or cross-reference lookup; not for reconciling documentation against the codebase (use `/doc-drift`) or finding missing requirements (use `/gap`)."
metadata:
  phase: 08-quality-change
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /kg — Documentation Knowledge Graph 🌟 [CORE WORKFLOW]

Knowledge graph of all project documentation and cross-references

## Objective
Provide expert BA guidance to execute `/kg`, generating structured artifact dependency graphs and cross-reference maps.

## Mandatory Standards (Rules)
- `rules/11-error-matrix-convention.md`
- `rules/14-test-case-traceability.md`
- `rules/16-ambiguity-detection-rules.md`
- `rules/18-knowledge-graph-metadata.md`

## Reference Template
- `_templates/49-knowledge-graph-index.md`

## Default Storage Path
- `docs/knowledge-graph.json`
- `docs/knowledge-graph-index.md`

The Markdown index is written in Vietnamese, following the structure of `_templates/49-knowledge-graph-index.md`; `knowledge-graph.json` stays machine-readable per the Rule 18 schema, with labels and notes keeping the source documents' language.

## Expected Input
- All `.md` documents under `docs/` carrying Rule 18 frontmatter (`id`, `depends_on`, `related_diagrams`, ...) — source of `DOCUMENT` nodes and `depends_on` / `related_diagrams` edges. If a document lacks the required frontmatter, list it and ask the user whether to backfill metadata before generating the graph.
- SRS specifications at `docs/{feature}/srs/spec.md` (FR/BR identifiers and the error matrix per Rule 11) — source of `FR` / `BR` / `ERR` nodes and `governed_by` / `emits_error` edges. If no SRS exists, report the gap and ask the user which documents to scan instead; never invent requirements or relations.
- Test cases at `docs/{feature}/test/test-cases.md` (Traceability Matrix per Rule 14) — source of `TC` nodes and `tested_by` edges. If absent, generate the graph without `tested_by` edges and note the omission in the index.

## Execution Workflow
1. Scan YAML frontmatter across all `.md` files in `docs/` per Rule 18.
2. Extract nodes (Documents, FRs, BRs, ERRs, TCs, ERD entities) and edges covering all 5 standard relation types defined in Rule 18: `depends_on` and `related_diagrams` from document frontmatter; `governed_by`, `emits_error`, and `tested_by` inferred from SRS content, the error matrix (Rule 11), and the Traceability Matrix (Rule 14).
3. Output the knowledge graph to `docs/knowledge-graph.json` — the JSON must conform to the mandatory schema defined in Rule 18 (`version`, `generated_at`, `nodes`, `edges`, with all required node/edge fields) — and the summary index to `docs/knowledge-graph-index.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] `docs/knowledge-graph.json` validates against the Rule 18 schema: `version`, `generated_at`, `nodes`, and `edges` are present; every node carries `id`, `type` (one of the allowed values), and `label`.
- [ ] Every edge uses one of the 5 standard relations (`depends_on`, `related_diagrams`, `governed_by`, `emits_error`, `tested_by`) and both `from` / `to` resolve to existing nodes — no dangling references.
- [ ] Save output at the designated repository path.
