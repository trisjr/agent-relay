---
title: Recheck session expiry before privileged auth actions
type: pitfall
area: auth
tags: [auth, session, expiry]
created: 2026-01-15
last_seen: 2026-01-15
occurrences: 1
---

## Context
A session may expire after a page loads.

## Lesson
Page load authorization does not authorize a later privileged action.

## Apply
Check the session again at the action boundary.
