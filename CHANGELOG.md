# Changelog

Mọi thay đổi đáng chú ý của marketplace `agent-relay` được ghi tại đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), version theo [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-09-26

### Plugins

- `orca-workflows`: 0.1.0 → 0.2.0
- `jev-dispatch`: 0.1.0 (ra mắt)

### Added

- **kimi-code**: hỗ trợ Kimi Code CLI plugin và marketplace — thêm `.kimi-plugin/marketplace.json`, manifest `.kimi-plugin/plugin.json` cho template và plugin `orca-workflows`, cập nhật `scripts/validate.sh` và `scripts/new-plugin.sh` để kiểm tra và đăng ký đồng bộ 3 marketplace và 5 manifest.
- **jev-dispatch**: plugin mới gợi ý harness, model và mức effort cho task của agent. MCP server (tool `ask`, battery `task_dispatch`) gửi mô tả task tới TypeSafe Jev để chấm độ phức tạp/rủi ro, rồi áp policy định tuyến viết bằng code; task rủi ro cao hoặc chấm không chắc chắn trả `ESCALATE` (không tự dispatch); riêng task rủi ro cao còn yêu cầu người dùng duyệt. Chạy bằng `uv run --script`, cần `uv` và biến môi trường `TYPESAFE_API_KEY`; nên chạy shadow mode trước khi bật auto-route.

### Changed

- **orca-workflows**: skill `orca-router` thêm hướng dẫn nối các recipe cho request trải từ plan → code → docs (research-swarm → dag-build → parallel-review → fix), mỗi bước là một Run riêng, liên kết bằng đường dẫn report.
- **release**: `/release` tự trỏ `source` Kimi sang zip của tag mới, đóng zip plugin bằng `git archive` (chỉ lấy file đã commit) và upload lên GitHub Release; plugin mới giữ `source` local cho tới lần release đầu. Quy ước thư mục `mcp/` optional được ghi vào `AGENTS.md`.

### Fixed

- **kimi-code**: cài từ GitHub — Kimi chỉ cài được plugin từ zip chứa manifest ở gốc nên `source` trong `.kimi-plugin/marketplace.json` trỏ tới zip asset trên GitHub Release; `scripts/validate.sh` chấp nhận `source` dạng http(s) bên cạnh path `./plugins/`.
- **scripts**: `scripts/new-plugin.sh` sinh entry Kimi có `version` và `displayName` dạng Title Case, cùng thứ tự key với các entry sẵn có.

## [0.1.0] - 2026-09-26

### Plugins

- `orca-workflows`: 0.1.0 (ra mắt)

### Added

- **marketplace**: khung marketplace đa platform (Codex, Claude Code, Qoder, Gemini CLI, Cursor) với template plugin, `scripts/new-plugin.sh` để tạo và đăng ký plugin vào cả hai `marketplace.json`, và `scripts/validate.sh` để kiểm tra manifest + cấu trúc.
- **release**: slash command `/release` trong Claude Code — tự chia commit theo nhóm, bump version plugin, cập nhật `CHANGELOG.md`, push kèm tag và tạo GitHub release.
- **orca-workflows**: plugin workflow multi-agent có giám sát cho Orca CLI, gồm 4 skill:
  - `orca-router` phân loại request và chọn đúng hệ thống (orchestration, orca-cli, worker hay agent thường).
  - `research-swarm` fan-out worker nghiên cứu theo nhiều góc độc lập rồi tổng hợp findings có ghi nguồn.
  - `parallel-review` review diff/PR song song theo lens (security, correctness, consistency, simplicity).
  - `dag-build` build tính năng theo task DAG, có gate duyệt spec và verify bằng test/build.
- **license**: phát hành theo MIT License.

[Unreleased]: https://github.com/trisjr/agent-relay/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/trisjr/agent-relay/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/trisjr/agent-relay/releases/tag/v0.1.0
