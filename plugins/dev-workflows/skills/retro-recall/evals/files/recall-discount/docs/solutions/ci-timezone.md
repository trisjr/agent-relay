---
title: Pin UTC for CI date comparisons
type: bug-lesson
area: ci
tags: [ci, timezone, dates]
created: 2026-03-20
last_seen: 2026-03-20
occurrences: 1
---

## Context
CI runners may use a different local timezone from development machines.

## Problem
A date assertion passed locally and failed in CI.

## Cause
The assertion depended on the process timezone.

## Lesson
Use an explicit UTC timezone for date comparisons.

## Apply
Set the timezone in the test and compare UTC instants.
