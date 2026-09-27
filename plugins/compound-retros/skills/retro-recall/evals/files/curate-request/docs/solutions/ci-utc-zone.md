---
title: Set UTC explicitly in CI tests
type: bug-lesson
area: ci
tags: [ci, timezone, dates]
created: 2026-02-01
last_seen: 2026-02-01
occurrences: 1
---

## Context
Test runners have different local timezone defaults.

## Problem
A date test passed locally and failed in CI.

## Cause
The test relied on the runner's local timezone.

## Lesson
Use UTC explicitly for date tests.

## Apply
Set UTC in the test environment and compare UTC instants.
