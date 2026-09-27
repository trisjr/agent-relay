---
title: Generate migrations instead of writing them by hand
type: pitfall
area: database
tags: [database, migration, index, user-correction]
created: 2026-06-02
last_seen: 2026-08-01
occurrences: 2
---

## Context
The schema generator records required indexes as well as columns.

## Lesson
Hand-written migrations have repeatedly omitted a generated index.

## Apply
Use `npm run migration:generate` and inspect its diff before applying.

## Source
User correction after the second missed index.
