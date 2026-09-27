---
title: Keep cache entries short lived
type: decision
area: cache
tags: [cache, ttl]
created: 2026-07-10
last_seen: 2026-07-10
occurrences: 1
---

# Keep cache entries short lived

## Status
Accepted

## Context
Stale cache data can affect checkout totals.

## Decision
Use a short cache TTL for checkout reads.

## Consequences
More origin reads in exchange for fresher totals.
