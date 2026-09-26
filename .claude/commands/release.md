---
description: Release marketplace — tách commit theo nhóm, bump version plugin, cập nhật CHANGELOG/docs, push, tag và tạo GitHub release
argument-hint: "[patch|minor|major|X.Y.Z] [--dry-run]"
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git show:*), Bash(git fetch:*), Bash(git rev-parse:*), Bash(git rev-list:*), Bash(git for-each-ref:*), Bash(git branch:*), Bash(git remote:*), Bash(git ls-files:*), Bash(git ls-tree:*), Bash(git ls-remote:*), Bash(git add:*), Bash(git commit:*), Bash(git tag:*), Bash(gh auth status:*), Bash(gh repo view:*), Bash(gh release view:*), Bash(scripts/validate.sh:*), Bash(claude plugin validate:*), Bash(date:*), Bash(mktemp:*), Read, Edit, Write, Glob, Grep, AskUserQuestion
---

# /release

Tham số: `$ARGUMENTS`

## Context

- Hôm nay: !`date +%F`
- Branch: !`git branch --show-current`
- HEAD: !`git rev-parse --short HEAD`
- Tag gần nhất: !`git for-each-ref --sort=-v:refname --count=1 --format='%(refname:short)' 'refs/tags/v*'`
- Remote: !`git remote get-url origin`
- Working tree: !`git status --porcelain=v1 -uall`
- Commit gần đây: !`git log --oneline -20`

## Quy tắc bắt buộc

- Sửa file (manifest, `CHANGELOG.md`, README) **chỉ bằng Edit/Write tool**. Không dùng `sed`, `jq`, `python` hay script để đổi nội dung file.
- Commit message: `<type>(<scope>): <short summary>`, **1 dòng**, tiếng Anh, không body. **Không** thêm bất kỳ trailer nào (`Co-Authored-By`, `Signed-off-by`, ...).
- Stage bằng path cụ thể: `git add -- <paths>`. Cấm `git add -A`, `git add .`, `git commit -a`.
- Cấm `--force`, `--no-verify`, `git reset --hard`, `git stash`, xoá/ghi đè tag remote.
- Lỗi ở bất kỳ bước nào → dừng, báo trạng thái hiện tại và lệnh khôi phục. Không tự "chữa" bằng thao tác phá huỷ.
- `--dry-run`: chạy bước 1–5 ở chế độ **chỉ đọc**, in plan (nhóm commit dự kiến, version, bump plugin, bản nháp section CHANGELOG) rồi dừng — không sửa file, không commit.

## 1. Preflight — fail là dừng

1. Ghi lại `START_SHA` = `git rev-parse HEAD` để hoàn tác khi cần.
2. Branch phải là `main`. Khác → hỏi anh có chắc muốn release từ branch này không.
3. `git status` không được báo merge/rebase/cherry-pick đang dở.
4. `git fetch origin --tags`, rồi `git rev-list --left-right --count HEAD...origin/main`. Bị behind (số bên phải > 0) → dừng, nhờ anh pull/rebase trước.
5. `gh auth status` phải OK.
6. `scripts/validate.sh` phải pass trên working tree hiện tại.

## 2. Phân tích thay đổi

- Working tree sạch **và** không có commit nào sau tag gần nhất (`git log <tag>..HEAD`) → dừng: không có gì để release. Chưa có tag nào thì luôn có thứ để release.
- Đọc nội dung thay đổi của từng file: `git diff HEAD -- <path>` với file tracked, Read với file untracked.
- Không bao giờ stage: `.DS_Store`, `.env*`, file chứa secret/token/private key, `.claude/worktrees/`, `.claude/settings.local.json`, build artifact, binary lớn. Gặp file đáng ngờ → liệt kê và hỏi anh.

## 3. Chia nhóm & commit

| Nhóm | Path | Commit |
| --- | --- | --- |
| Plugin `<name>` | `plugins/<name>/**` + entry của nó trong **cả ba** `marketplace.json` | `feat\|fix\|refactor\|docs(<name>)` |
| Marketplace | `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, `.kimi-plugin/marketplace.json` — phần không thuộc plugin nào | `chore(marketplace)` |
| Template | `plugins/_template/**` | `chore(template)` |
| Scripts | `scripts/**` | `build\|fix(scripts)` |
| Claude config | `.claude/**` | `chore(claude)` |
| CI | `.github/**` | `ci` |
| Docs | `README.md`, `AGENTS.md`, docs khác | `docs` |

- Chọn `type` theo bản chất thay đổi: `feat` (plugin/skill/tính năng mới), `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`, `style`. Breaking change → commit dạng `feat(<scope>)!: ...`.
- Plugin mới đi **cùng commit** với entry của nó trong ba `marketplace.json` — plugin chưa đăng ký đủ ba marketplace coi như chưa xong. Nếu một `marketplace.json` chứa entry của nhiều plugin thì gộp các plugin đó vào một commit (scope `plugins`), vì không tách hunk được.
- Một nhóm lẫn nhiều mục đích → tách thành nhiều commit theo file. Không tách hunk trong cùng một file.
- Thứ tự: nền tảng trước (scripts, template, config), rồi plugin, rồi docs.
- Mỗi commit: `git add -- <paths>` → `git diff --cached --stat` để kiểm lại đúng file → `git commit -m "<message>"`.
- Xong bước này, `git status --porcelain` chỉ còn các file đã loại ở bước 2.

## 4. Xác định version

**Base**: `BASE` = tag gần nhất. Chưa có tag nào → first release: xét toàn bộ lịch sử, version mặc định `0.1.0`.

**Version repo** (tag `vX.Y.Z`):

- `$ARGUMENTS` có `X.Y.Z` hoặc `vX.Y.Z` → dùng đúng giá trị đó. Có `patch|minor|major` → bump theo đó.
- Không có → suy từ commit `BASE..HEAD` (với `--dry-run` thì suy từ các commit dự kiến ở bước 3): có commit dạng `type(scope)!:` hoặc `BREAKING CHANGE` → major, có `feat` → minor, còn lại → patch. Khi đang ở `0.x`, breaking chỉ bump minor.
- Version mới phải lớn hơn tag cũ. Tag chưa được tồn tại cả ở local (`git tag -l vX.Y.Z`) lẫn remote (`git ls-remote --tags origin vX.Y.Z`).

**Version plugin** — với mỗi plugin thật trong `plugins/` (bỏ qua thư mục bắt đầu bằng `_`):

- `git diff --name-only BASE..HEAD -- plugins/<name>/` rỗng → giữ nguyên.
- First release, hoặc plugin chưa tồn tại tại `BASE` (`git ls-tree -d BASE plugins/<name>` rỗng) → giữ version hiện tại, coi như ra mắt lần đầu.
- Version đã được bump tay so với `BASE` (so với `git show BASE:plugins/<name>/plugin.json`) → giữ nguyên.
- Còn lại → bump theo cùng luật trên, chỉ xét `git log BASE..HEAD -- plugins/<name>/`.
- Sửa `version` ở **cả năm** manifest bằng Edit: `plugin.json`, `.claude-plugin/plugin.json`, `.qoder-plugin/plugin.json`, `gemini-extension.json`, `.kimi-plugin/plugin.json`. Claude Code dựa vào `version` để phát hiện update — không bump thì người dùng không nhận bản mới.

## 5. CHANGELOG & docs

`CHANGELOG.md` ở root theo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Chưa có thì tạo mới:

```markdown
# Changelog

Mọi thay đổi đáng chú ý của marketplace `agent-relay` được ghi tại đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), version theo [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [X.Y.Z] - YYYY-MM-DD

### Plugins

- `<name>`: 0.1.0 → 0.2.0

### Added

- **<name>**: ...

[Unreleased]: https://github.com/<owner>/<repo>/compare/vX.Y.Z...HEAD
[X.Y.Z]: https://github.com/<owner>/<repo>/compare/vPREV...vX.Y.Z
```

- Section mới chèn ngay dưới `## [Unreleased]`. Nội dung đang có trong `[Unreleased]` thì chuyển vào section mới, để `[Unreleased]` trống.
- Map commit: `feat` → Added, `fix` → Fixed, `refactor`/`perf`/`build`/`ci`/`docs` có ảnh hưởng người dùng → Changed, xoá plugin/skill → Removed, lỗ hổng bảo mật → Security. Bỏ `chore`, `style`, `test` và commit release cũ. Chỉ giữ heading có nội dung. `### Plugins` liệt kê version của plugin đã bump hoặc mới ra mắt.
- Entry viết **tiếng Việt**, thuật ngữ IT giữ tiếng Anh, hướng người dùng (plugin/skill nào, làm được gì). Không copy nguyên commit message.
- `<owner>/<repo>`: `gh repo view --json nameWithOwner -q .nameWithOwner`. First release thì link là `.../releases/tag/vX.Y.Z`. Cập nhật dòng `[Unreleased]` để compare từ tag mới.

Docs khác — chỉ sửa khi lệch với thực tế, không viết lại:

- `plugins/<name>/README.md`: danh sách skill, command, hook khớp với `skills/`, `commands/`, `hooks/`.
- `README.md` root: cây "Cấu trúc" khớp với file/thư mục top-level (vd thêm `CHANGELOG.md` ở lần release đầu). Hướng dẫn cài đặt vẫn đúng.
- Entry `description` trong cả ba `marketplace.json` khớp với `description` trong manifest plugin.

## 6. Validate & commit release

1. Chạy `scripts/validate.sh`. Có lệnh `claude` thì chạy thêm `claude plugin validate .` và `claude plugin validate ./plugins/<name>` cho từng plugin đã bump. Fail → sửa bằng Edit rồi chạy lại. Không sửa được → dừng.
2. `git add -- CHANGELOG.md <manifest đã bump> <docs đã sửa>` → `git commit -m "chore(release): vX.Y.Z"`.

## 7. Xác nhận

In tóm tắt gồm: `git log --oneline START_SHA..HEAD` (hoặc `BASE..HEAD` nếu không có commit mới), version cũ → mới, bảng bump plugin, section CHANGELOG mới. Hỏi anh xác nhận push + tag + release bằng AskUserQuestion.

Anh từ chối → dừng. Commit local giữ nguyên. Báo lệnh hoàn tác: `git reset --soft START_SHA`, lệnh này đưa toàn bộ thay đổi về trạng thái staged.

## 8. Publish

1. `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
2. `git push --atomic origin main vX.Y.Z`: branch và tag cùng lên hoặc cùng không. Bị reject → dừng, không force. Tag local giữ nguyên để retry sau khi anh pull.
3. Lấy nội dung section `[X.Y.Z]` trong `CHANGELOG.md` (bỏ dòng heading) và Write vào file mới `<dir>/release-notes.md`, với `<dir>` tạo bằng `mktemp -d` (Write không ghi đè được file có sẵn mà chưa Read). Sau đó chạy `gh release create vX.Y.Z --verify-tag --title "vX.Y.Z" --notes-file <file>`. Version có suffix pre-release (`-rc.1`, `-beta.2`, ...) thì thêm `--prerelease`. Bước này fail thì tag đã lên remote, chỉ cần chạy lại đúng lệnh `gh release create`.

## 9. Báo cáo

Version, tag, URL release (`gh release view vX.Y.Z --json url -q .url`), danh sách commit đã tạo, plugin đã bump.
