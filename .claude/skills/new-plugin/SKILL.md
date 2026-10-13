---
name: new-plugin
description: Scaffold a new plugin in the agent-relay marketplace via scripts/new-plugin.sh and run the full validation checklist
disable-model-invocation: true
argument-hint: "<ten-plugin-kebab-case>"
allowed-tools: Bash(bash scripts/new-plugin.sh:*), Bash(bash scripts/validate.sh:*), Bash(claude plugin validate:*), Read, Edit, Glob
---

# /new-plugin

Tham số: `$ARGUMENTS` — tên plugin, **kebab-case**.

## Quy trình

1. Kiểm tra tên là kebab-case và chưa tồn tại trong `plugins/`. Nếu sai, dừng và báo anh.
2. Chạy `bash scripts/new-plugin.sh $ARGUMENTS`. Không tạo tay.
3. Xác nhận plugin đã được đăng ký đủ **ba** marketplace:
   - `.agents/plugins/marketplace.json`
   - `.claude-plugin/marketplace.json`
   - `.kimi-plugin/marketplace.json`
4. Xác nhận năm manifest đồng bộ `name` và `version`: `plugin.json`, `.claude-plugin/plugin.json`, `.qoder-plugin/plugin.json`, `gemini-extension.json`, `.kimi-plugin/plugin.json`.
5. Hướng dẫn điền `skills/<skill-name>/SKILL.md` (frontmatter bắt buộc `name`, `description`). Chỉ tạo `hooks/`, `commands/`, `mcp/` khi plugin thực sự cần.
6. Chạy `bash scripts/validate.sh`, rồi `claude plugin validate .`. Báo kết quả nguyên văn nếu có lỗi.

## Quy ước

- Docs (README) viết **tiếng Việt**; nội dung manifest JSON viết **tiếng Anh**.
- Không commit. Việc commit và release do anh quyết định (`/release`).
