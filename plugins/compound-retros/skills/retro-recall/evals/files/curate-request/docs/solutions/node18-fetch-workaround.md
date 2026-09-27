---
title: Use the fetch polyfill on Node 18
type: pitfall
area: runtime
tags: [runtime, node18, fetch]
created: 2025-10-01
last_seen: 2025-10-01
occurrences: 1
retire_when: package.json engines.node requires Node 20 or later
---

## Context
The old Node 18 runtime did not provide the required fetch behavior.

## Lesson
Use a fetch polyfill while Node 18 remains supported.

## Apply
Check the supported Node version before adding the polyfill.
