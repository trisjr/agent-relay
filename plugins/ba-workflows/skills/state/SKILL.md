---
name: state
description: "State transition diagrams for lifecycles (orders, accounts, items). Use when you need to model how a single business entity moves through its lifecycle — states, triggers, guards, and a transition matrix — rather than branching process logic (use /activity), time-ordered participant interactions (use /sequence), or screen-level navigation journeys (use /user-flow)."
metadata:
  phase: 03-diagrams
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /state — State Machine Diagram (Mermaid) 🌟 [CORE WORKFLOW]

State transition diagrams for lifecycles (orders, accounts, items)

## Objective
Provide expert BA guidance to execute `/state`, mapping lifecycle states, triggers, guards, and transition matrices.

## Mandatory Standards (Rules)
- `rules/12-state-transition-rules.md`
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/19-state-diagram.md`

## Default Storage Path
- `docs/{feature}/srs/states.md`
- The output document is written in Vietnamese, following the structure and column headers of `_templates/19-state-diagram.md`.

## Expected Input
- Feature name and the entity whose lifecycle is being modeled (Order, Contract, Account, Invoice, ...).
- Known states and transitions, if any, collected from upstream requirements: `docs/{feature}/srs/spec.md`, `docs/{feature}/usecases/{usecase_id}.md`, `docs/{feature}/userstories/backlog.md`.
- If the entity or its states are not yet clear, ask at most 3 clarifying questions before constructing the diagram; report missing input instead of inventing states or transitions.

## Execution Workflow
1. Identify entity managing lifecycle (Order, Contract, Account, Invoice).
2. Construct Mermaid `stateDiagram-v2`.
3. Distinguish Initial State, Intermediate States, and Terminal States.
4. Construct the 6-column State Transition Matrix per Rule 12 and `_templates/19-state-diagram.md`: Current State | Trigger | Guard | Target State | Actor | Side effects.
5. Save to `docs/{feature}/srs/states.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] All state names in UPPER_SNAKE_CASE; an Initial state and at least one Terminal state are present.
- [ ] Every transition has a snake_case trigger; automatic/system transitions carry an explicit guard or timeout.
- [ ] Transition matrix has all 6 columns (Current State | Trigger | Guard | Target State | Actor | Side effects) and matches the diagram.
- [ ] Save output at the designated repository path.
