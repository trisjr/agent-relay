---
name: api-design
description: "Integration design: how systems cooperate and contract schemas. Use when you need to design a RESTful/webhook API contract — endpoint catalog, request/response schemas, error codes, signature verification — as opposed to field-level mapping across UI, database, and partner payloads, which is handled by /api-map."
metadata:
  phase: 06-api-integration
  category: business-analysis
  version: 1.0.0
  is_core: "true"
---

# /api-design — Integration API Contract Design 🌟 [CORE WORKFLOW]

Integration design: how systems cooperate and contract schemas

## Objective
Provide expert BA guidance to execute `/api-design`, producing comprehensive RESTful and webhook integration contracts. The output document is written in Vietnamese, following `_templates/37-api-design.md`.

## Mandatory Standards (Rules)
- `rules/01-fr-naming-convention.md`
- `rules/02-br-naming-convention.md`
- `rules/03-err-naming-convention.md`
- `rules/10-api-contract-standards.md`
- `rules/16-ambiguity-detection-rules.md`

## Reference Template
- `_templates/37-api-design.md`

## Default Storage Path
- `docs/{feature}/api/api-spec.md`

## Expected Input
- Functional requirements and business rules to expose over the API — default source: `docs/{feature}/srs/spec.md`. FR identifiers populate the endpoint catalog's traceability column; BR identifiers are cited in validation constraints.
- Use cases and/or user stories describing the integration actors and flows — default: `docs/{feature}/usecases/{usecase_id}.md` and `docs/{feature}/userstories/backlog.md`.
- If any input is missing, ask the user for it or report it as a gap — never invent requirements, endpoints, or error conditions.

## Execution Workflow
1. Design RESTful endpoint catalog per Rule 10 (plural-noun resource URLs, standard HTTP verbs, standard response envelope).
2. Specify Request Headers, Request Body, Response 200 OK, and Error Responses (including but not limited to 400, 401, 403, 404, 409, 422, 500 per Rule 03).
3. Define Webhook / Callback mechanisms and signature verification rules per the Webhook/Callback section of `rules/10-api-contract-standards.md`: event payload schema (`event`, `event_id`, `occurred_at`, `data`), HMAC-SHA256 signature via `X-Webhook-Signature` / `X-Webhook-Timestamp`, 300-second replay window, retry backoff with Dead Letter Queue, and `event_id`-based idempotency.
4. Save to `docs/{feature}/api/api-spec.md`.

## Quality Acceptance Checklist
- [ ] Use professional technical BA terminology.
- [ ] Free of vague or ambiguous qualifiers (Rule 16).
- [ ] Every error response in each endpoint spec and in the consolidated Error Matrix carries an ERR code in the `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` format (Rule 03).
- [ ] Every endpoint in the catalog traces to at least one existing FR identifier, and every validation constraint cites an existing BR identifier (Rules 01, 02) — no invented FR/BR references.
- [ ] Save output at the designated repository path.
