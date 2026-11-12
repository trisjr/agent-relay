---
title: Print the report summary as a plain-text table
type: decision
area: report
tags: [report, output-format]
created: 2026-07-09
last_seen: 2026-07-09
occurrences: 1
---

## Context
`linkcheck report` needed a default layout for its per-folder counts of checked, broken, and fixed links.

## Options considered
- Plain-text table: readable in a terminal and in CI logs without extra tooling.
- JSON by default: easy to parse, hard to read at a glance.

## Lesson
Plain-text table by default, with `--format json` for scripts.

## Apply
New summary columns go into both formats; keep the table within 80 columns.
