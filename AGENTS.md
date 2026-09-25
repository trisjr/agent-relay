# AGENTS.md

Quy ước bắt buộc khi làm việc trong repo marketplace `agent-relay`.

- Tên plugin **kebab-case**, trùng với tên thư mục trong `plugins/`.
- Bốn manifest của một plugin — `plugin.json`, `.claude-plugin/plugin.json`, `.qoder-plugin/plugin.json`, `gemini-extension.json` — luôn **đồng bộ `name` và `version`**. Sửa một file thì sửa cả bốn.
- Thêm plugin mới: chạy `scripts/new-plugin.sh <ten-plugin>` thay vì sửa tay. Script tạo plugin từ `plugins/_template/` và đăng ký vào cả `.agents/plugins/marketplace.json` lẫn `.claude-plugin/marketplace.json` — plugin chưa đăng ký đủ hai marketplace coi như chưa xong.
- Skill viết trong `skills/<skill-name>/SKILL.md` với frontmatter bắt buộc: `name` và `description`.
- `hooks/` và `commands/` là optional: chỉ tạo khi plugin thực sự cần.
- Docs (README, AGENTS) viết **tiếng Việt**; nội dung manifest JSON viết **tiếng Anh**.
- Chạy `scripts/validate.sh` trước mỗi commit; có Claude Code thì chạy thêm `claude plugin validate .`.
