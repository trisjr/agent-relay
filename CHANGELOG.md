# Changelog

Mọi thay đổi đáng chú ý của marketplace `agent-relay` được ghi tại đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), version theo [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.6.0] - 2026-09-26

### Plugins

- `clarify-requirements`: 0.1.0 (mới)
- `orca-workflows`: 0.3.1 → 0.4.0

### Added

- **clarify-requirements**: plugin mới có skill `clarify-requirements`, làm rõ yêu cầu mơ hồ hoặc rủi ro cao trước khi implement hay lên plan.
  - Agent tự tìm hiểu repo trước, chỉ hỏi những câu thực sự thay đổi cách làm: tối đa 3 câu mỗi vòng, 2 vòng, mỗi câu có option `(Recommended)`. Gap rủi ro thấp thì dùng default và ghi thành assumption; hành động không đảo ngược mà còn thiếu quyết định thì dừng lại.
  - Kết quả là một requirements brief 120–250 từ để bàn giao cho người implement: chính agent, một session mới hoặc worker trong DAG.
  - Mỗi harness có kênh hỏi riêng: Orca worker dùng `orca orchestration ask`, Claude Code/Kimi/Qoder dùng `AskUserQuestion`, Codex dùng `request_user_input` (Plan mode), Gemini dùng `ask_user`, còn lại là block plain-text. Ở chế độ headless agent không chờ trả lời mà liệt kê assumption, hoặc in block câu hỏi để chạy lại kèm câu trả lời.
  - Gemini CLI headless luôn load `gemini-context.md` (khai báo qua `contextFileName`), vì ở chế độ này `activate_skill` bị chặn. Cursor dùng rule `.cursor/rules/clarify-requirements.mdc`.
- **orca-workflows**: skill `dag-build` làm rõ yêu cầu trước khi viết spec. Nếu yêu cầu còn để ngỏ quyết định ảnh hưởng tới cách chia component, acceptance hoặc contract dùng chung, coordinator chạy `clarify-requirements` trong conversation của chính mình (không giao cho worker) rồi viết spec từ brief. Gate duyệt spec kiêm luôn bước xác nhận brief, nên người dùng chỉ duyệt một lần.
- **orca-workflows**: skill `research-swarm` chọn model cho worker theo loại góc nghiên cứu.
  - Góc thu thập fact chạy codex `gpt-6-luna` hoặc antigravity `gemini-3.8-flash-high`.
  - Góc cần phán đoán (rủi ro, trade-off, đề xuất) chạy `claude --model opus` hoặc codex `gpt-6-sol`. Mọi worker đều chạy effort `high`.
  - Coordinator kiểm tra `launch.effective` trên receipt, và kiểm lại CLI flag, model id, citation trước khi tổng hợp; điều gì không kiểm được thì đánh dấu `UNVERIFIED`.

## [0.5.1] - 2026-09-26

### Plugins

- `jev-dispatch`: 0.3.0 → 0.3.1
- `orca-workflows`: 0.3.0 → 0.3.1

### Changed

- **jev-dispatch**: skill `dispatch-routing` (kèm Cursor rule và README) chốt format log cho golden set.
  - Chỉ dùng một file JSONL append-only: `~/.local/state/jev-dispatch/dispatch-log.jsonl`.
  - Mỗi lần gọi `ask` ghi một record `route`, kể cả khi error hay không dispatch gì. Record gồm `task` và `context` đúng như đã gửi, nguyên response, và `used` là harness/model/effort thực sự đã chạy (`null` khi để mặc định).
  - Task kết thúc thì ghi một record `outcome` (`ok`, `retried`, `failed` hoặc `cancelled`), nối với `route` bằng `id`.
  - Mỗi dòng append qua `jq` để task có dấu nháy không làm hỏng log.
- **orca-workflows**: skill `dag-build` ghi shadow routing theo format log mới.
  - `id` là task id của Orca.
  - `used` là codex với model/effort mặc định.
  - Mỗi task chỉ có một `outcome`, ghi sau mọi lần `--retry-of`.

## [0.5.0] - 2026-09-26

### Plugins

- `orca-workflows`: 0.2.0 → 0.3.0

### Added

- **orca-workflows**: skill `dag-build` gọi MCP tool `ask` của jev-dispatch (shadow mode) một lần mỗi task trước khi start worker mới, khi tool có sẵn. Chỉ gửi tóm tắt 1–3 câu thay vì cả component spec, vẫn giữ `--agent codex` và không truyền `model`/`effort` từ routing. Task có `requires_approval` phải được người dùng duyệt trước khi start worker. Coordinator log routing kèm outcome của worker để tích lũy golden set.
- **orca-workflows**: skill `parallel-review` chia reviewer cho hai model family: ít nhất một reviewer `claude --model opus` và một reviewer codex Sol (`--model gpt-6-sol`), cả hai chạy effort `xhigh`. Mỗi finding khi merge ghi thêm reviewer agent đã tìm ra nó.

## [0.4.0] - 2026-09-26

### Plugins

- `jev-dispatch`: 0.2.0 → 0.3.0

### Added

- **jev-dispatch**: đổi đích route trong policy của MCP tool `ask` (skill `dispatch-routing`): task cần web hoặc long context chuyển từ `gemini/pro/medium` sang `codex/sol/medium`; task nhỏ, rủi ro thấp vẫn chạy `gemini/flash` nhưng effort tăng từ `low` lên `high`; nhánh mặc định (việc engineering thông thường) gắn thẳng model `luna` với effort `max` thay cho placeholder `gpt-default`/`medium`. Coordinator cần đảm bảo harness nhận được tên model và effort mới; policy đã đổi nên chạy lại golden set ở shadow mode trước khi bật auto-route.

## [0.3.0] - 2026-09-26

### Plugins

- `jev-dispatch`: 0.1.0 → 0.2.0

### Added

- **jev-dispatch**: Claude Code hỏi `TypeSafe API Key` khi cài hoặc enable plugin qua `/plugin`, lưu vào keychain dạng sensitive rồi tự truyền vào MCP server qua `TYPESAFE_API_KEY`. Key không còn phụ thuộc vào `export` trong shell hay cách mở Claude Code (terminal, desktop app, IDE). Đổi key bằng `/plugin configure jev-dispatch@agent-relay`; cài bằng CLI thì truyền `--config typesafe_api_key=...`. README và skill `dispatch-routing` ghi rõ cách cấp key cho từng harness.

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

[Unreleased]: https://github.com/trisjr/agent-relay/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/trisjr/agent-relay/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/trisjr/agent-relay/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/trisjr/agent-relay/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/trisjr/agent-relay/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/trisjr/agent-relay/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/trisjr/agent-relay/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/trisjr/agent-relay/releases/tag/v0.1.0
