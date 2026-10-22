---
name: doc-drift
description: Audit codebase against specifications: spot missing or drifted features. Use when implementation already exists and you must reconcile it against the SRS and user-story backlog — classifying behavioral drift, unbuilt features, and out-of-spec code with severity; not for finding gaps inside requirement artifacts before handoff (use `/gap`) or assessing a requested change (use `/cr`).
metadata:
  phase: 08-quality-change
  category: business-analysis
  version: 1.0.0
  is_core: true
---

# /doc-drift — Document vs Source Code Drift Audit 🌟 [CORE WORKFLOW]

Audit codebase against specifications: spot missing or drifted features

## Objective
Provide expert BA guidance to execute `/doc-drift`, identifying behavioral discrepancies between specifications and implemented code.

## Mandatory Standards (Rules)
- `rules/14-test-case-traceability.md`
- `rules/16-ambiguity-detection-rules.md`
- `rules/20-artifact-identifier-conventions.md`

## Reference Template
- `_templates/46-doc-drift.md`

## Default Storage Path
- `docs/{feature}/doc-drift-report.md`
- Write the report in Vietnamese, following `_templates/46-doc-drift.md`.

## Expected Input
- SRS: `docs/{feature}/srs/spec.md` — source of FR / BR / NFR identifiers to reconcile.
- User story backlog: `docs/{feature}/userstories/backlog.md` — source of US / AC identifiers to reconcile.
- Read access to the codebase under audit (record branch and commit hash in the report header).
- If SRS or backlog is missing, STOP and report exactly which artifact is missing; ask the user to provide it. Do not infer or invent requirements from the code.

## Execution Workflow
1. Read SRS / User Stories and inspect codebase implementation.
2. Reconcile Functional Requirements checklist against code modules: identify completed vs unbuilt features; each in-scope FR gets exactly one implementation state from the template (`Đã hiện thực` / `Hiện thực một phần` / `Sai lệch` / `Chưa hiện thực`).
3. Flag behavioral drift and classify every finding per `_templates/46-doc-drift.md`:
   - Drift classification (pick one of 5): `Hành vi khác Spec` / `Validation lỏng hơn BR` / `Validation chặt hơn BR` / `Tính năng chưa xây` / `Tính năng ngoài Spec`.
   - Severity scale: `Critical` (blocks a core business flow or is a security hole) — `High` (produces wrong real business outcomes) — `Medium` (deviates on an exception flow) — `Low` (display / message differences).
   - Assign each finding a `DRIFT-xxx` code (see checklist).
4. Output reconciliation report to `docs/{feature}/doc-drift-report.md`, in Vietnamese per the template.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every drift finding carries a unique `DRIFT-[SEQ]` code (3-digit sequence restarting per report, per Rule 20) with one drift classification and one severity level from `_templates/46-doc-drift.md`.
- [ ] Every drift finding cites both code evidence (file path + line, or explicit "not found in code") and the governing spec identifier (FR/BR/ERR/UC/US).
- [ ] The FR vs Code reconciliation table covers every FR in the audit scope and links drifted FRs to their `DRIFT-xxx` findings.
- [ ] Save output at the designated repository path.
