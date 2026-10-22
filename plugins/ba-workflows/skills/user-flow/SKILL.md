---
name: user-flow
description: "User journey flow analysis covering happy, error, and edge cases. Use when wireframes or a screen inventory already exist and you need to map how screens connect — entry-to-completion sequences, transitions with triggers/guards, and per-screen UI states — not for designing static screen layouts (use /wireframe-html) or modeling a business object's lifecycle states (use /state)."
metadata:
  phase: 05-screen-design
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /user-flow — User Flow & Journey Analysis 🌟 [CORE WORKFLOW]

User journey flow analysis covering happy, error, and edge cases

## Objective
Provide expert BA guidance to execute `/user-flow`, visualizing screen transitions and interaction states across all touchpoints. The output document is written in Vietnamese, following the Reference Template.

## Mandatory Standards (Rules)
- `../../rules/12-state-transition-rules.md`
- `../../rules/16-ambiguity-detection-rules.md`
- `../../rules/20-artifact-identifier-conventions.md`

## Reference Template
- `../../_templates/29-user-flow.md`

## Default Storage Path
- `docs/{feature}/ui/user-flow.md`

## Expected Input
- Screen inventory from the HTML wireframes at `docs/{feature}/html-wireframe/{screen_name}.html` (output of `/wireframe-html`) — source of the screen list and `SCR-[MODULE]-[SEQ]` codes.
- Requirements to trace transitions against: SRS at `docs/{feature}/srs/spec.md` (`FR-xxx` / `BR-xxx` / `ERR-xxx`), use cases at `docs/{feature}/usecases/{usecase_id}.md`, and/or the user story backlog at `docs/{feature}/userstories/backlog.md`.
- If wireframes or requirements are missing, report what is missing and ask the user whether to run the upstream skill (`/wireframe-html`, `/srs`) first or proceed from a screen list the user provides — never invent screens, triggers, or requirements to fill the gap.

## Execution Workflow
1. Identify every entry point and completion point, then map the screen sequences traversed by the user from entry point to completion; assign each screen a `SCR-[MODULE]-[SEQ]` code (Rule 20 §6).
2. Draw the journey-level Mermaid `flowchart` covering all 3 scenario groups of the overall flow — happy path, error path, and edge cases — labeling transitions with the governing `FR-xxx` / `BR-xxx` / `ERR-xxx` where applicable. Journey scenarios are alternative paths through the whole flow; keep them distinct from the per-screen UI states in step 4 — the two concepts must not be merged into one list.
3. Build the Screen Transition Matrix: one row per transition with source screen, trigger (snake_case event), guard condition (`—` when none), target screen, system response / side effect, and traceability reference — applying the trigger + guard + transition-matrix discipline of Rule 12 to screen navigation.
4. Build the UI State Matrix: for every screen in the flow, declare all 5 states — Normal, Loading, Empty, Error, Offline — with measurable behavior per Rule 16; when a state does not apply to a screen, state that explicitly with the reason.
5. Save to `docs/{feature}/ui/user-flow.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every screen in the flow declares all 5 UI states (Normal, Loading, Empty, Error, Offline), or an explicit "not applicable" justification.
- [ ] Every transition has a named trigger, a guard per Rule 12, and a target screen; every screen node carries a `SCR-xxx` code traceable to `FR` / `US` / `UC` (Rule 20 §6).
- [ ] The Mermaid flowchart covers happy, error, and edge paths, and every entry point leads to a completion point.
- [ ] Save output at the designated repository path.
