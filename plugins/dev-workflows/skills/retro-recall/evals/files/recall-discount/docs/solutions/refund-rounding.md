---
title: Round partial refunds at the refund boundary
type: decision
area: billing
tags: [billing, refund, rounding]
created: 2026-05-03
last_seen: 2026-05-03
occurrences: 1
---

## Context
Partial refunds can include multiple returned items.

## Options considered
Round each item or round the aggregate refund.

## Lesson
Round the aggregate refund once so it matches the payment provider amount.

## Apply
Keep intermediate refund values decimal until the final amount is sent.
