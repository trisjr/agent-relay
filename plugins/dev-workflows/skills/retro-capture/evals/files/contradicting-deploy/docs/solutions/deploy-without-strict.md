---
title: Run deploy preflight without strict mode
type: convention
area: deploy
tags: [deploy, preflight]
created: 2026-08-12
last_seen: 2026-08-12
occurrences: 1
---

## Context
The deploy preflight was used before publishing.

## Lesson
Omit `--strict` when running the deploy preflight.

## Apply
Run `npm run deploy:preflight` without `--strict`.
