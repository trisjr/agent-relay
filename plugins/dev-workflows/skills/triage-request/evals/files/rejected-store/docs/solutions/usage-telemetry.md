---
title: Do not collect telemetry from the CLI
type: decision
area: cli
tags: [rejected-request, telemetry, privacy]
created: 2026-08-14
last_seen: 2026-08-14
occurrences: 1
---

## Context
A contributor asked for anonymous telemetry so maintainers could see how the tool is exercised in the wild.

## Options considered
- Opt-out telemetry sent to a hosted endpoint: gives real data, but the tool would phone home from private documentation repos.
- Opt-in telemetry: little data, and still needs an endpoint, a retention policy, and a privacy notice to maintain.
- No telemetry: no data, nothing to host or explain.

## Lesson
No telemetry. The tool runs inside private repos and CI, and its promise is that it never makes a request other than checking the links it was asked to check. A two-person project cannot run a data endpoint responsibly.

## Apply
Decline requests to gather or transmit data about how people run the tool. Revisit only if the project gains a hosted service with its own privacy policy.

## Source
Feature request from a contributor, August 2026.
