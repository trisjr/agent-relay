---
title: Reuse the same idempotency key on checkout retries
type: convention
area: checkout
tags: [checkout, payments, retry]
created: 2026-08-14
last_seen: 2026-09-15
occurrences: 2
---

## Context
A network timeout can hide a successful payment request.

## Lesson
Retry with the original idempotency key to avoid duplicate charges.

## Apply
Persist the key with the checkout attempt and reuse it on retry.
