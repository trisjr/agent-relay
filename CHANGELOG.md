# Changelog

Mọi thay đổi đáng chú ý của marketplace `agent-relay` được ghi tại đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), version theo [Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/trisjr/agent-relay/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/trisjr/agent-relay/releases/tag/v0.1.0
