---
title: Format order amounts through the shared money helper
type: convention
area: orders
tags: [orders, money, formatting]
created: 2026-02-10
last_seen: 2026-02-10
occurrences: 1
---

## Context
Order views display prices in the customer's currency.

## Lesson
The shared money helper owns display formatting.

## Apply
Call the helper after calculation; never calculate totals from formatted strings.
