---
title: Pin CI date tests to UTC
type: bug-lesson
area: ci
tags: [ci, timezone, dates]
created: 2026-03-01
last_seen: 2026-03-01
occurrences: 1
---

## Context
Runner timezone settings vary across machines.

## Problem
Local date assertions did not match CI results.

## Cause
The assertions used local time.

## Lesson
Use UTC explicitly for date tests.

## Apply
Set UTC in the test environment and compare UTC instants.
