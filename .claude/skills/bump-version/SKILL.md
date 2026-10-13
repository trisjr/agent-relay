---
name: bump-version
description: Bump the version of one plugin across all five manifests in lockstep and re-validate
disable-model-invocation: true
argument-hint: "<plugin-name> <patch|minor|major|X.Y.Z>"
allowed-tools: Bash(bash scripts/validate.sh:*), Read, Edit, Glob, Grep
---

# /bump-version

Tham số: `$ARGUMENTS` — `<plugin-name> <patch|minor|major|X.Y.Z>`.

Chỉ lo phần đồng bộ manifest. Commit, CHANGELOG, tag, push do `/release` xử lý.

## Quy trình

1. Tách `$ARGUMENTS` thành tên plugin và mức bump. Xác nhận `plugins/<plugin-name>/` tồn tại.
2. Đọc `version` hiện tại ở cả năm manifest trong `plugins/<plugin-name>/`:
   - `plugin.json`
   - `.claude-plugin/plugin.json`
   - `.qoder-plugin/plugin.json`
   - `gemini-extension.json`
   - `.kimi-plugin/plugin.json`
3. Nếu năm giá trị không giống nhau, dừng và báo anh trước khi sửa.
4. Tính version mới theo semver, rồi dùng Edit để sửa `version` ở **cả năm** file.
5. Grep các marketplace (`.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, `.kimi-plugin/marketplace.json`) xem có ghi version của plugin không. Nếu có, sửa luôn.
6. Chạy `bash scripts/validate.sh`. Báo version cũ → mới và kết quả validate.
