---
title: Calculate amnesty discount before rounding order total
type: bug-lesson
area: billing
tags: [billing, order, discount, amnesty, rounding]
created: 2026-04-12
last_seen: 2026-04-12
occurrences: 1
---

## Context
Amnesty discounts are percentages of the eligible order subtotal.

## Problem
Rounding each line first produced a one-cent mismatch on some orders.

## Cause
The calculation rounded before applying the discount instead of rounding the final payable amount once.

## Lesson
Apply the amnesty discount to the unrounded eligible subtotal.

## Apply
Use decimal arithmetic and round the final order amount once at the billing boundary.
