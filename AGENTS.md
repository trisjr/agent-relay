# AGENTS.md

Quy ước bắt buộc khi làm việc trong repo marketplace `agent-relay`.

- Tên plugin **kebab-case**, trùng với tên thư mục trong `plugins/`.
- Năm manifest của một plugin — `plugin.json`, `.claude-plugin/plugin.json`, `.qoder-plugin/plugin.json`, `gemini-extension.json`, `.kimi-plugin/plugin.json` — luôn **đồng bộ `name` và `version`**. Sửa một file thì sửa cả năm.
- Thêm plugin mới: chạy `scripts/new-plugin.sh <ten-plugin>` thay vì sửa tay. Script tạo plugin từ `plugins/_template/` và đăng ký vào cả ba marketplace (`.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, `.kimi-plugin/marketplace.json`) — plugin chưa đăng ký đủ ba marketplace coi như chưa xong.
- Skill viết trong `skills/<skill-name>/SKILL.md` với frontmatter bắt buộc: `name` và `description`.
- `hooks/` và `commands/` là optional: chỉ tạo khi plugin thực sự cần.
- Docs (README, AGENTS) viết **tiếng Việt**; nội dung manifest JSON viết **tiếng Anh**.
- Chạy `scripts/validate.sh` trước mỗi commit; có Claude Code thì chạy thêm `claude plugin validate .`.
