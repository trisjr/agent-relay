# AgentRelay

Marketplace cá nhân chứa các plugin tái sử dụng cho AI coding agents: "Reusable workflows for coding agents". Một plugin đóng gói skills (kèm hooks, commands khi cần) và cài được trên nhiều platform nhờ bộ manifest song song. Duy trì bởi AgentRelay Maintainers.

## Cấu trúc

```text
.
├── .agents/plugins/marketplace.json        # Codex marketplace manifest
├── .claude-plugin/marketplace.json         # Claude Code marketplace manifest
├── .kimi-plugin/marketplace.json           # Kimi Code marketplace manifest
├── .claude/commands/release.md             # Slash command /release
├── plugins/
│   ├── _template/                          # Template plugin mới (placeholder __PLUGIN_NAME__)
│   └── <plugin-name>/                      # Tên plugin, kebab-case
│       ├── plugin.json                     # Agent Plugins portable manifest (schema agent-plugins.org)
│       ├── .claude-plugin/plugin.json      # Claude Code manifest
│       ├── .qoder-plugin/plugin.json       # Qoder manifest
│       ├── gemini-extension.json           # Gemini CLI extension manifest
│       ├── .kimi-plugin/plugin.json        # Kimi Code manifest
│       ├── .cursor/rules/<plugin-name>.mdc # Cursor rule
│       ├── skills/<skill-name>/SKILL.md    # Skill, frontmatter gồm name + description
│       └── README.md                       # Mô tả plugin
├── scripts/new-plugin.sh                   # Tạo plugin từ template + đăng ký vào 3 marketplace.json
├── scripts/validate.sh                     # Kiểm tra toàn bộ manifest + cấu trúc
├── CHANGELOG.md
├── LICENSE
├── README.md
└── AGENTS.md
```

Mỗi plugin mang nhiều manifest để các platform nhận diện theo cách riêng của nó:

| Platform | Marketplace | Manifest plugin |
| --- | --- | --- |
| Codex | `.agents/plugins/marketplace.json` | `plugin.json` (Agent Plugins) |
| Claude Code | `.claude-plugin/marketplace.json` | `.claude-plugin/plugin.json` |
| Kimi Code | `.kimi-plugin/marketplace.json` | `.kimi-plugin/plugin.json` |
| Qoder | — | `.qoder-plugin/plugin.json` |
| Gemini CLI | — | `gemini-extension.json` |
| Cursor | — | `.cursor/rules/<plugin-name>.mdc` |
## Thêm plugin mới

Dùng script thay vì sửa tay, vì plugin mới bắt buộc đăng ký vào cả ba `marketplace.json`:

```sh
scripts/new-plugin.sh <ten-plugin>   # kebab-case
```

Script nhân bản `plugins/_template/` (thay `__PLUGIN_NAME__`) và khai báo plugin vào `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` lẫn `.kimi-plugin/marketplace.json`. Sau đó:

- Sửa `description` trong năm manifest; giữ `name` và `version` đồng bộ giữa chúng.
- Viết skill trong `skills/<skill-name>/SKILL.md` với frontmatter `name` và `description`.
- Thêm `hooks/` và `commands/` khi plugin cần — cả hai đều optional.
- Cập nhật `README.md` của plugin.
- Chạy `scripts/validate.sh` trước khi commit.

## Kiểm tra

Chạy từ thư mục repo:

```sh
scripts/validate.sh
claude plugin validate .
claude plugin validate ./plugins/<plugin-name>
```

`validate.sh` kiểm tra toàn bộ manifest và cấu trúc thư mục. Hai lệnh `claude plugin validate` chỉ chạy được khi đã cài Claude Code; không có thì bỏ qua.

## Release

Trong Claude Code, đứng ở branch `main` rồi chạy:

```text
/release [patch|minor|major|X.Y.Z] [--dry-run]
```

Command tự làm các bước:

1. Preflight: đúng branch, không bị behind so với remote, `gh` đã auth, `validate.sh` pass.
2. Chia các thay đổi thành từng commit theo nhóm (plugin, scripts, docs, ...). Mỗi plugin commit chung với entry của nó trong các `marketplace.json`.
3. Bump `version` của plugin có thay đổi (đồng bộ cả năm manifest), rồi cập nhật `CHANGELOG.md` và các docs bị lệch.
4. Tạo commit `chore(release): vX.Y.Z`, hỏi xác nhận, rồi push kèm tag `vX.Y.Z` và tạo GitHub release.

Không truyền version thì command tự suy từ commit: `feat` bump minor, `fix` bump patch, breaking bump major. `--dry-run` chỉ in plan, không sửa file.

## Cài từ bản local

Codex:

```sh
codex plugin marketplace add .
codex plugin add <plugin-name>@agent-relay
```

Claude Code:

```sh
claude plugin marketplace add .
```

rồi trong Claude Code chạy `/plugin install <plugin-name>@agent-relay`.

Kimi Code — cài trực tiếp từ thư mục:

```sh
/plugins install ./plugins/<plugin-name>
```

hoặc duyệt catalog qua `/plugins marketplace ./.kimi-plugin/marketplace.json` rồi cài từ tab Custom. Có thể trỏ biến môi trường `KIMI_CODE_PLUGIN_MARKETPLACE_URL` đến path/URL của `marketplace.json`. Sau khi cài cần `/reload` (hoặc `/new`).

Cài từ GitHub: Kimi cài plugin từ zip chứa manifest ở gốc, nên `source` trong `.kimi-plugin/marketplace.json` trỏ đến zip đính kèm GitHub Release. Người dùng thêm catalog bằng raw URL:

```sh
/plugins marketplace https://raw.githubusercontent.com/<owner>/<repo>/main/.kimi-plugin/marketplace.json
```

hoặc cài thẳng zip release:

```sh
/plugins install https://github.com/<owner>/<repo>/releases/download/vX.Y.Z/<plugin-name>-X.Y.Z.zip
```

Khi release bản mới: đóng gói lại zip plugin (manifest ở gốc zip), upload asset lên GitHub Release và cập nhật `source` trong `.kimi-plugin/marketplace.json`. Với Codex và Claude Code, sau khi đẩy repo lên GitHub chỉ cần thay `.` ở lệnh thêm marketplace bằng `owner/repo`.
