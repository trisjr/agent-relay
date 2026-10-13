---
title: Tạo migration bằng lệnh của repo
type: pitfall
area: database
tags: [database, migration, user-correction]
created: 2026-08-15
last_seen: 2026-09-10
occurrences: 2
---

## Context
Thay đổi schema cần migration được sinh theo quy ước của repo.

## Lesson
Viết migration SQL bằng tay bỏ qua bước sinh file chuẩn và đã bị user sửa.

## Apply
Dùng `npm run migration:generate`; không tự viết migration SQL.

## Source
User correction trong lần thay đổi schema trước.
