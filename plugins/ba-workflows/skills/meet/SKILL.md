---
name: meet
description: Turn meeting transcripts and notes into formal decisions and action items. Use when you have a meeting transcript or raw notes to distill into structured minutes with decisions, action items, and open questions — not for analyzing the impact of a scope change agreed in a meeting (use cr for that).
metadata:
  phase: 09-handoff-ops
  category: business-analysis
  version: 1.0.0
  is_core: true
---

# /meet — Meeting Minutes, Decisions & Action Items 🌟 [CORE WORKFLOW]

Turn meeting transcripts and notes into formal decisions and action items

## Objective
Provide expert BA guidance to execute `/meet`, distilling unstructured discussion into actionable agreements, decisions, and deadlines. Write the meeting minutes in Vietnamese, following `_templates/48-meeting-minutes.md`.

## Mandatory Standards (Rules)
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/48-meeting-minutes.md`

## Default Storage Path
- `docs/meetings/{date}-meeting.md` — `{date}` uses the `YYYY-MM-DD` format (e.g. `docs/meetings/2026-10-22-meeting.md`).

## Expected Input
- Raw meeting transcript or notes from the user (any format: chat log, voice transcript, bullet summary).
- Reference documents cited in the meeting, when available by convention: `docs/{feature}/srs/spec.md`, `docs/{feature}/userstories/backlog.md`, prior minutes under `docs/meetings/`.
- If no transcript or notes are provided, ask the user to supply them — never invent discussion content, decisions, owners, or deadlines.
- If a referenced document is missing, note the gap in the minutes and continue from the transcript alone.

## Execution Workflow
1. Ingest raw notes or meeting transcript.
2. Extract 3 core components:
   - Key discussion items and context.
   - Formal agreed decisions (Decision ID, rationale, approver).
   - Action Items with assigned Owner and Target Deadline.
3. Distinguish Decisions from Open Questions:
   - Decision = explicitly agreed in the meeting → record with full rationale per template section 3.
   - Open Question = raised but not settled → log it with an explicit flag, mark unresolved fields `TBD`, and ask the user — never self-assign an Owner or Deadline to an unsettled item.
   - Normalize vague statements into measurable wording per Rule 16 (template section 5).
4. If a decision changes previously agreed scope, do not run impact analysis here — hand off to the `/cr` skill (Rule 15 applies there) and reference the resulting CR ID in the minutes.
5. Present the draft minutes to the user for confirmation before saving; save only after explicit approval.
6. Save to `docs/meetings/{date}-meeting.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every formal decision has a Decision ID, rationale, and named approver per `_templates/48-meeting-minutes.md` section 3.
- [ ] Every Action Item has an Owner and Target Deadline, or an explicit `TBD` flag with the open follow-up recorded.
- [ ] Open Questions are logged separately from Decisions — nothing unsettled is presented as agreed.
- [ ] Save output at the designated repository path.
