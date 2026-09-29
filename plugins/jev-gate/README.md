# jev-gate

Plugin hook chặn **từng tool call** (Bash và MCP) của coding agent trước khi nó chạy. Có ba lớp:

- **Lock rule** viết bằng code: gặp lệnh nguy hiểm thì bắt hỏi người dùng.
- **REUSE ledger**: chặn việc chạy lại một lệnh đắt khi không có file nào đổi.
- **TypeSafe Jev**: chấm các lệnh ở vùng xám.

Mặc định plugin chạy **shadow mode**. Ở mode này chỉ lock rule có hiệu lực; mọi quyết định khác chỉ được ghi log để review bằng skill `gate-review` trước khi bật `enforce`.

## Bối cảnh

- **Khác `jev-dispatch`.** `jev-dispatch` là MCP tool mà coordinator tự gọi, mỗi task một lần, để chọn harness/model. Còn `jev-gate` là hook do harness gọi ngoài luồng. Agent không phải tự gọi gì nên không mất thêm turn hay token nào của model.
- **Rút gọn từ cơ chế "Jev inside Claude" (PROCEED / REUSE / SKIP / ASK):**
  - Giữ ASK, cộng thêm lock bằng code chạy trước Jev.
  - REUSE làm bằng code (ledger + git fingerprint). Không hỏi Jev, vì [jev-save](https://github.com/grapefruit0205/jev-save) đã bỏ câu `redundant`: câu này chấm 0.07–0.18 ngay cả khi state có đủ dữ kiện.
  - Bỏ SKIP, vì câu `necessary` của jev-save không đúng ở bất cứ đâu và model suy luận chính quyết định bước nào cần làm tốt hơn.
  - PROCEED → auto-allow chưa làm: chỉ log, chờ dữ liệu shadow.
- **Tiết kiệm token có giới hạn.** Gate chỉ tiết kiệm khi REUSE chặn được một output lớn khỏi vào context. Cộng đồng đo gate trước mỗi bước và thấy mức tiết kiệm gần bằng 0 (mẫu nhỏ). Log `out` ghi kích thước output của mọi call, để quyết định có nên làm output pruning (PostToolUse `updatedToolOutput`) hay không.

## Cách hoạt động

PreToolUse (`Bash|mcp__.*`) chạy lần lượt:

| # | Bước | Làm bằng | Ghi chú |
| --- | --- | --- | --- |
| 1 | Lock rule | Regex trong `hooks/gate.py` | Khớp thì `ask`, ở **mọi mode**, và không gửi Jev |
| 2 | Secret | Regex | Command có dấu hiệu secret thì không gửi Jev; log lưu bản đã redact |
| 3 | Fast path | Allowlist lệnh read-only (`ls`, `cat`, `rg`, `git status/diff/log`…), MCP tool dạng `get/list/read/search…` | Cho chạy theo permission flow bình thường, không gọi Jev. Tách segment bằng `shlex`, nên `;`, `\|`, `>` nằm trong quote là text; `$(…)` và backtick thì bị loại ở mọi chỗ |
| 4 | Orca IPC, git remote read | `orca orchestration send/check/reply/ask/worker-read/worker-list/dispatch-show`, `git fetch/ls-remote` (không `-c`, `--upload-pack`), các segment còn lại phải là read-only | `source: "ipc"`: không gọi Jev, không REUSE vì kết quả phụ thuộc agent khác hoặc network. Ask ở IPC sẽ làm worker không có người trông bị treo; `git fetch/ls-remote` bị Jev chấm outward 0.70–0.78 dù không đổi gì ở remote |
| 5 | REUSE | Ledger của session + git fingerprint | Chỉ áp dụng cho Bash |
| 6 | Jev | 4 Noul trong một request: `read_only`, `destructive`, `outward`, `external_state` | Chỉ chấm vùng xám |
| 7 | Policy | Hàm thuần `policy()` | Ra `ask` / `reuse` / `allow` / `proceed` |

Policy chạy từ trên xuống, gặp điều kiện đầu tiên khớp thì dừng:

| Điều kiện | `decision` | shadow | enforce |
| --- | --- | --- | --- |
| Lock rule khớp | `ask` | **áp dụng** | áp dụng |
| `outward >= 0.7` hoặc `destructive >= 0.7` | `ask` | log | áp dụng |
| Có ứng viên REUSE, và là fast path hoặc `external_state < 0.5` | `reuse` | log | deny một lần; chạy lại đúng lệnh đó thì cho qua |
| `read_only >= 0.9`, `outward` và `destructive < 0.1`, action không có `#` hay xuống dòng | `allow` | log | log (bản này **không bao giờ** auto-allow) |
| Còn lại, Jev lỗi hoặc thiếu key | `proceed` | — | — |

`proceed` nghĩa là hook không in gì, nên permission flow của harness chạy như bình thường. Hook `allow` không vượt được rule deny/ask trong settings, còn hook `ask` vẫn hiện prompt kể cả ở auto mode và bypass mode.

**Lock rule:**

| Rule | Khớp | Không khớp |
| --- | --- | --- |
| `git-push` | `git push`, `git -C repo push --force` | `git stash push`, `git commit -m "add push notifications"` |
| `git-discard` | `git reset --hard`, `git clean -f…`, `git checkout -- .`, `git restore .`, `git branch -D`, `git stash drop/clear` | `git clean -n`, `git branch -d` |
| `publish` | `npm/pnpm/yarn/bun publish`, `cargo publish`, `twine upload`, `gem push` | |
| `pipe-to-shell` | `curl … \| sh`, `wget … \| bash` | |
| `sudo` | `sudo …` ở đầu một segment | |
| `rm-broad` | `rm -rf` trỏ vào `/`, `~`, `$HOME`, `.`, `..`, `*` | `rm -rf ./build`, `rm -rf /tmp/x` |

> **Lock chạy cả ở shadow mode.** Nhiều hook bất đồng thì quyết định chặt nhất thắng, nên sau khi cài, mọi `git push` đều hỏi, kể cả ở auto mode và kể cả khi đã có allow rule. Ở headless (`claude -p`), `ask` thành deny. Muốn tắt hẳn thì disable plugin.

**REUSE** chỉ nhắc khi đủ tất cả các điều kiện sau:

- Đúng command cũ (so sau khi chuẩn hóa khoảng trắng), cùng session và cùng `agent_id`. Subagent không thấy output của agent khác.
- Git fingerprint không đổi. Fingerprint gồm HEAD, `git status --porcelain -uall`, mtime và size của các file đang thay đổi. Hook chạy git với `--no-optional-locks` để không tranh `index.lock`.
- Lần chạy trước tốn ít nhất 5s hoặc cho ít nhất 4 KB output, và cách đây không quá 15 phút.
- Chưa từng nhắc cho đúng cặp (command, fingerprint) này. Vì vậy agent chạy lại lần nữa là qua.

Mỗi lần compaction hoặc `/clear` (SessionStart `compact|clear`), hook ghi một record `reset` và ledger bỏ qua mọi thứ trước đó.

**Jev:** state gửi đi là `{"kind": "shell command" | "MCP tool call", "action": ...}`, model `jev-1.13.0` được pin. Timeout 1.5s, không retry, lỗi thì fail-open. Hook gọi thẳng HTTP API bằng python3 stdlib, không cần SDK hay `uv`.

## Mode

| Mode | Hành vi | Latency thêm |
| --- | --- | --- |
| `shadow` (mặc định) | Chỉ lock `ask` có hiệu lực. Jev chạy trong một process con tách rời, rồi ghi record `judge` về quyết định mà enforce sẽ đưa ra | Khoảng 50–100 ms mỗi call (đo trên máy dev: hook trả về sau ~97 ms, Jev xong sau đó ~0.6s) |
| `enforce` | Áp dụng thêm Jev `ask` và REUSE deny. Allow chỉ được log | Thêm ~0.3–1.5s cho Bash vùng xám, vì phải chờ Jev |

Đổi mode:

- Claude Code: `/plugin configure jev-gate@agent-relay`, sửa option `mode`.
- Harness khác: `JEV_GATE_MODE=enforce` trong env của harness. Nếu có cả hai thì `JEV_GATE_MODE` được ưu tiên.

Chỉ chuyển sang enforce sau khi review xong dữ liệu shadow bằng skill `gate-review`. Skill có tiêu chí cụ thể: ít nhất 200 call, ask precision được anh gán nhãn, REUSE `same_output`, error rate, p95 latency.

## Log

Log nằm ở `~/.local/state/jev-gate/sessions/<session_id>.jsonl` (hoặc `$JEV_GATE_STATE_DIR`). Mỗi session một file append-only, thư mục tạo với quyền `0700`.

| `ev` | Ghi khi | Nội dung chính |
| --- | --- | --- |
| `gate` | PreToolUse, **đồng bộ**, trước khi tool chạy | `id` (tool_use_id), `action`, `rule`, `source`, `fp`, `reuse`, `decision`, `applied`, `mode`, `harness` |
| `judge` | Process con Jev ở shadow mode | `judgments`, `decision`, `latency_ms`, `error`/`status` |
| `out` | PostToolUse / PostToolUseFailure | `bytes`, `sha` (hash của output), `ok`, `dur_ms` |
| `reset` | SessionStart `compact` / `clear` | `source` |

- Log **không lưu output**, chỉ lưu kích thước và hash.
- `action` đã bỏ thân heredoc (thay bằng `<heredoc: N lines>`), đã redact secret và cắt còn tối đa 2000 ký tự. Dù vậy nó vẫn là command text, nên đừng gửi log ra ngoài.

## Cài đặt

1. Cài plugin qua marketplace `agent-relay`: xem mục "Cài từ bản local" trong [README gốc](../../README.md).
2. Cần có:
   - `python3` bản 3.9 trở lên trên `PATH` (macOS có sẵn `/usr/bin/python3`).
   - `git`, dùng cho fingerprint của REUSE. Không có git thì REUSE tắt.
3. API key TypeSafe là **tùy chọn**. Không có key thì chỉ lock và REUSE chạy; Jev không chạy và log ghi `source: "no-key"`.
   - Claude Code: nhập vào dialog `TypeSafe API Key` khi cài, hoặc đặt sau bằng `/plugin configure jev-gate@agent-relay`. Key lưu dạng sensitive trong keychain và tới hook qua `CLAUDE_PLUGIN_OPTION_TYPESAFE_API_KEY`.
   - Harness khác: `TYPESAFE_API_KEY` phải có trong env khởi chạy harness.
   - Không commit key, không ghi key vào file config.

| Harness | Trạng thái |
| --- | --- |
| Claude Code | Hỗ trợ: tự wiring qua `hooks/hooks.json` với `${CLAUDE_PLUGIN_ROOT}`. Contract hook đã test offline theo docs |
| Codex | **Unverified ở runtime.** Theo docs, Codex tự load `hooks/hooks.json` của plugin, set `CLAUDE_PLUGIN_ROOT`, gọi tool shell là `Bash`, và phải review/trust hook qua `/hooks` thì hook mới chạy. Codex chưa hỗ trợ `ask`, nên gate trả `deny` kèm lý do bảo agent hỏi người dùng (worker Orca thì escalate lên coordinator). Codex không có event `PostToolUseFailure` và không có `agent_id`, nên REUSE không tách theo subagent |
| Gemini CLI | Không wiring: Gemini dùng tên event khác (`BeforeTool`…). Gemini có load `hooks/hooks.json` của extension, nhưng chỉ có `SessionStart` trùng tên, và lệnh đó fail vô hại nhờ `\|\| true` |
| Kimi Code, Qoder | Chỉ có skill `gate-review`; hook chưa wiring |
| Cursor | Chỉ có rule `.cursor/rules/jev-gate.mdc` |

Mọi command trong `hooks.json` đều kết thúc bằng `|| true`. Python exit 2 khi không tìm thấy file, mà exit 2 ở PreToolUse nghĩa là **chặn tool**, nên lỗi launcher không bao giờ được phép chặn agent.

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `JEV_GATE_MODE` | — | `shadow` hoặc `enforce`. Giá trị lạ thì dùng `shadow`. Ưu tiên hơn `CLAUDE_PLUGIN_OPTION_MODE` |
| `CLAUDE_PLUGIN_OPTION_MODE` | `shadow` | Claude Code tự đặt từ option `mode` |
| `CLAUDE_PLUGIN_OPTION_TYPESAFE_API_KEY` / `TYPESAFE_API_KEY` | — | API key; không bao giờ được log |
| `TYPESAFE_JEV_MODEL` | `jev-1.13.0` | Model đã pin. Đổi model thì phải gom lại một đợt dữ liệu shadow mới |
| `JEV_GATE_STATE_DIR` | `~/.local/state/jev-gate` | Thư mục chứa log |

Ngưỡng là hằng số ở đầu `hooks/gate.py`: `ASK_AT`, `EXTERNAL_AT`, `REUSE_*`, `JEV_TIMEOUT`. Muốn đổi thì replay judgments đã log qua `policy()` trước, như skill `gate-review` hướng dẫn.

## Data egress

- Chỉ call ở vùng xám mới gửi lên TypeSafe (`https://api.typesafe.ai/v1/systemone`, URL cố định, không đọc `TYPESAFE_BASE_URL`). Dữ liệu gửi đi là `kind` và `action`:
  - Bash: command đã bỏ thân heredoc, cắt 2000 ký tự. Command có dấu hiệu secret thì **không gửi**.
  - MCP: chỉ tên server, tên tool và **tên** các argument, không gửi giá trị.
- Lock hit, fast path và Orca IPC không bao giờ rời khỏi máy.
- TypeSafe chỉ có zero data retention ở gói enterprise.

## Giới hạn đã biết

- Lock quét text của command, nên `git commit -m "... git push ..."` cũng bị hỏi. Log sẽ cho thấy rule nào hay hỏi nhầm.
- Lock là **guardrail chống lệnh nguy hiểm vô tình**, không phải ranh giới chống attacker. Lock bị lách được trong hai trường hợp:
  - Thân heredoc của interpreter không phải shell, ví dụ `python3 - <<'EOF'`, bị bỏ có chủ đích.
  - Quote hoặc indirection, ví dụ `g''it push` hay `$(echo git) push`.

  Ranh giới thật vẫn là permission rule của harness, sandbox hoặc container.
- Orca IPC chỉ được bỏ qua Jev khi các segment còn lại đều read-only. Nếu worker gộp heartbeat với việc khác trong cùng một lệnh (vd `orca orchestration send … ; uv run …`):
  - Lệnh có capability token `dcap_…`: rơi vào nhánh secret, không bao giờ tới Jev, kể cả khi phần gộp thêm là lệnh phá hủy. Khi đó chỉ còn lock rule.
  - Lệnh không có token: vẫn đi qua Jev, và ở enforce có thể bị ask.
- Fingerprint không thấy file bị gitignore (build output, `node_modules`). Nếu REUSE nhắc sai vì lý do này thì agent chỉ cần chạy lại là qua.
- REUSE giả định output cũ vẫn còn trong context trong vòng 15 phút. Harness có thể đã dọn tool result cũ, nên luôn cho qua ở lần chạy lại.
- Jev tin text trong state. Theo Check Point, một attacker mạnh lật được verdict 25/27 lần. Vì thế Jev ở đây chỉ **thêm** ask, không bao giờ allow, và lock luôn chạy trước Jev.
- Jev 1.13 yếu với tiếng Việt và với lệnh bị obfuscate. Rate limit (khoảng 1200 request/phút) tính chung cho mọi agent dùng cùng key.

## Test

```sh
python3 plugins/jev-gate/hooks/test_gate.py
```

Test chạy offline, không gọi network. Nó kiểm lock (cả ca dương và ca âm), redact, heredoc, fast path (kể cả quote và các cách lách bằng `&`, `#`, `\"`), Orca IPC, policy, state machine của REUSE, và end-to-end qua subprocess: đúng shape `hookSpecificOutput`, deny một lần rồi cho qua, file đổi làm fingerprint đổi, reset, và fail-open khi input hỏng.

## Nguồn

[TypeSafe docs](https://docs.typesafe.ai/llms.txt), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13), [Claude Code hooks](https://code.claude.com/docs/en/hooks), [Codex hooks](https://learn.chatgpt.com/docs/hooks), [jev-save](https://github.com/grapefruit0205/jev-save), [jev-kit](https://github.com/jonathanavis96/jev-kit), Check Point, "Jev Is Not a Language Model, but It Breaks Like One".
