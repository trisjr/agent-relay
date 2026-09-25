# AgentRelay

Marketplace cá nhân chứa các plugin tái sử dụng cho AI coding agents: "Reusable workflows for coding agents". Một plugin đóng gói skills (kèm hooks, commands khi cần) và cài được trên nhiều platform nhờ bộ manifest song song. Duy trì bởi AgentRelay Maintainers.

## Cấu trúc

```text
.
├── .agents/plugins/marketplace.json        # Codex marketplace manifest
├── .claude-plugin/marketplace.json         # Claude Code marketplace manifest
├── .claude/commands/release.md             # Slash command /release
├── plugins/
│   ├── _template/                          # Template plugin mới (placeholder __PLUGIN_NAME__)
│   └── <plugin-name>/                      # Tên plugin, kebab-case
│       ├── plugin.json                     # Agent Plugins portable manifest (schema agent-plugins.org)
│       ├── .claude-plugin/plugin.json      # Claude Code manifest
│       ├── .qoder-plugin/plugin.json       # Qoder manifest
│       ├── gemini-extension.json           # Gemini CLI extension manifest
│       ├── .cursor/rules/<plugin-name>.mdc # Cursor rule
│       ├── skills/<skill-name>/SKILL.md    # Skill, frontmatter gồm name + description
│       └── README.md                       # Mô tả plugin
├── scripts/new-plugin.sh                   # Tạo plugin từ template + đăng ký vào 2 marketplace.json
├── scripts/validate.sh                     # Kiểm tra toàn bộ manifest + cấu trúc
├── README.md
└── AGENTS.md
```

Mỗi plugin mang nhiều manifest để các platform nhận diện theo cách riêng của nó:

| Platform | Marketplace | Manifest plugin |
| --- | --- | --- |
| Codex | `.agents/plugins/marketplace.json` | `plugin.json` (Agent Plugins) |
| Claude Code | `.claude-plugin/marketplace.json` | `.claude-plugin/plugin.json` |
| Qoder | — | `.qoder-plugin/plugin.json` |
| Gemini CLI | — | `gemini-extension.json` |
| Cursor | — | `.cursor/rules/<plugin-name>.mdc` |

## Thêm plugin mới

Dùng script thay vì sửa tay, vì plugin mới bắt buộc đăng ký vào cả hai `marketplace.json`:

```sh
scripts/new-plugin.sh <ten-plugin>   # kebab-case
```

Script nhân bản `plugins/_template/` (thay `__PLUGIN_NAME__`) và khai báo plugin vào `.agents/plugins/marketplace.json` lẫn `.claude-plugin/marketplace.json`. Sau đó:

- Sửa `description` trong bốn manifest; giữ `name` và `version` đồng bộ giữa chúng.
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
2. Chia các thay đổi thành từng commit theo nhóm (plugin, scripts, docs, ...). Mỗi plugin commit chung với entry của nó trong hai `marketplace.json`.
3. Bump `version` của plugin có thay đổi (đồng bộ cả bốn manifest), rồi cập nhật `CHANGELOG.md` và các docs bị lệch.
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

Sau khi đẩy repo lên GitHub, thay `.` ở lệnh thêm marketplace bằng `owner/repo`.
