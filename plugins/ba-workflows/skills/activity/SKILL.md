---
name: activity
description: "Activity diagrams with branching decision logic. Use when mapping a business flow that branches on conditions (decision points, guards, retries, parallel steps) for a use case; pick /state instead when modeling an entity's lifecycle states and transitions."
metadata:
  phase: 03-diagrams
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /activity — Activity Diagram 🌟 [CORE WORKFLOW]

Activity diagrams with branching decision logic

`/activity` maps branching business-flow logic; `/state` maps an entity's state lifecycle — choose by artifact, not by feature.

## Objective
Provide expert BA guidance to execute `/activity`, generating high-quality Mermaid activity diagrams ready for technical handover. The output document is written in Vietnamese, following `_templates/16-activity-diagram.md`.

## Mandatory Standards (Rules)
- `rules/01-fr-naming-convention.md`
- `rules/02-br-naming-convention.md`
- `rules/03-err-naming-convention.md`
- `rules/16-ambiguity-detection-rules.md`
- `rules/20-artifact-identifier-conventions.md`

## Reference Template
- `_templates/16-activity-diagram.md`

## Default Storage Path
- `docs/{feature}/srs/activity.md`

## Expected Input
- Use case spec at `docs/{feature}/usecases/{usecase_id}.md` — its main flow plus alternate/exception flows are the branching source; if missing, ask the user which use case to diagram (or run `/usecase` first).
- User story backlog at `docs/{feature}/userstories/backlog.md` for the originating `US-xxx` trace and acceptance criteria.
- SRS at `docs/{feature}/srs/spec.md` for the FR/BR/ERR identifiers to cite on nodes and in the traceability matrix; if identifiers are absent, report the gap instead of inventing codes.
- Never fabricate requirements: when a flow step, guard, or rule is unknown, ask the user before drawing it.

## Execution Workflow
1. Identify the start point and terminal points; render them as stadium nodes (`S(["Start: ..."])` / `E1(["End: ..."])`), never the stateDiagram `[*]` syntax.
2. Build the diagram in one syntax only: Mermaid `flowchart TD`, with decision nodes written as `{condition}` diamonds; group actor / system / gateway steps into `subgraph` lanes as in the template.
3. Label every branch edge with its guard condition, and close each decision's branches at a merge node before the common flow continues — no dangling branches.
4. Model retries / repeat-until as loop-back edges with an explicit exit condition, and concurrent steps as fork/join pairs (one node fans out into parallel edges that rejoin at a single join node) — see the template's retry and payment examples.
5. Fill the Branch Condition & Guard Clause table and the FR/BR/ERR traceability matrix per the template.
6. Save file to `docs/{feature}/srs/activity.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Diagram uses a single Mermaid `flowchart TD` syntax with `{condition}` decision diamonds and renders without errors — no `[*]` state syntax anywhere.
- [ ] Every decision diamond has at least two labeled outgoing edges and a row in the guard table, its branches close at a merge node, and every loop carries an explicit exit condition.
- [ ] Every FR/BR/ERR code cited on nodes follows Rules 01/02/03 and appears in the traceability matrix.
- [ ] Save output at the designated repository path.
