# Plugin template

Đây là bản mẫu để tạo plugin mới cho marketplace AgentRelay. Script `scripts/new-plugin.sh` copy toàn bộ thư mục này và thay mọi placeholder `__PLUGIN_NAME__` bằng tên plugin thật (kebab-case).

## Sau khi copy, cần làm

1. Đổi tên thư mục plugin từ `_template` thành tên plugin mới.
2. Thay `__PLUGIN_NAME__` trong tất cả file, gồm cả tên file `.cursor/rules/__PLUGIN_NAME__.mdc`.
3. Thay `"TODO: Describe this plugin"` trong 4 file manifest bằng mô tả thật (tiếng Anh, 1 câu).
4. Viết skill thật trong `skills/` (có thể xoá `example-skill` hoặc sửa thành của bạn) và chỉnh `.cursor/rules/*.mdc`.
5. Nếu plugin không có skill, gỡ bỏ field `"skills"` ở `.qoder-plugin/plugin.json` và xoá thư mục `skills/`.
6. Giữ `version` ở cả 4 manifest luôn giống nhau (rule của repo).

## Các file manifest

- `plugin.json` — manifest portable chuẩn Agent Plugins (`$schema` agent-plugins.org), các platform chưa hỗ trợ riêng có thể đọc file này.
- `.claude-plugin/plugin.json` — manifest cho Claude Code.
- `.qoder-plugin/plugin.json` — manifest cho Qoder; trỏ tới `skills/` qua field `"skills"`.
- `gemini-extension.json` — manifest cho Gemini CLI extension.
- `.cursor/rules/__PLUGIN_NAME__.mdc` — rule cho Cursor (frontmatter + nội dung hướng dẫn).
- `skills/` — skill dùng chung cho các agent hỗ trợ SKILL.md.

Hooks là tuỳ chọn và không nằm trong template này; xem tài liệu repo khi cần thêm.
