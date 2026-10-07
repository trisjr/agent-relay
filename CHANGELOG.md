# Changelog

Mọi thay đổi đáng chú ý của marketplace `agent-relay` được ghi tại đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), version theo [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.16.0] - 2026-10-07

### Plugins

- `launch-video`: 0.1.0 → 0.2.0

### Added

- **launch-video**: bước render tự chọn `--workers` theo cấu hình máy (≥ 8 core và ≥ 16 GB RAM → 4, ≥ 4 core và ≥ 8 GB → 3, yếu hơn để `auto`) thay vì để `auto` mặc định vốn chỉ chạy 1–2 worker với video 15–25s, giúp render nhanh hơn. Gặp timeout hoặc worker lỗi thì giảm dần về `--workers 1`.

## [0.15.0] - 2026-10-07

### Plugins

- `launch-video`: 0.1.0 (mới)

### Added

- **launch-video**: plugin biến project vừa làm xong (hoặc một website URL) thành launch video ngắn, sẵn để chia sẻ, render bằng HyperFrames. Agent đọc code project trực tiếp, không cần URL live hay screenshot.
  - Skill `launch-video` (`/launch-video`): chọn tone, lên plan và storyboard, compose HyperFrames, mix nhạc + SFX có sẵn trong plugin, render `launch-video.mp4` kèm poster và share copy vào `launch-video-output/`.
  - Skill `launch-video-slim` (`/launch-video-slim`): bản gọn một file, không asset kèm theo, model tự dựng toàn bộ bằng tool có sẵn trên máy. `launch-video` tự chuyển sang bản này khi chạy trên Opus 5.5, trừ khi có `--full` hoặc `--voice`.
  - Vendor từ [latent-spaces/brag](https://github.com/latent-spaces/brag) v0.4.0 (MIT), đổi tên theo quy ước của marketplace.

## [0.14.0] - 2026-10-07

### Plugins

- `compact-nudge`: 0.1.0 (mới)

### Added

- **compact-nudge**: plugin function hooks cho Claude Code, nhắc `/compact` khi context vượt ngưỡng token (mặc định 200K, nhắc lại mỗi +100K) và soạn sẵn lệnh `/compact <cần giữ lại>` bằng `$.model.fork` trên transcript đang cache. Không bao giờ tự compact; ngưỡng chỉnh trong `/config`.

## [0.13.1] - 2026-09-30

### Plugins

- `orca-workflows`: 0.6.0 → 0.6.1
- `jev-gate`: 0.1.2 → 0.1.3

### Fixed

- **orca-workflows**: `orca-router` thêm cách xử lý khi `worker-start --agent codex` timeout ở `agent_readiness` (thấy trên Orca 1.4.216 với codex 0.158–0.159, kể cả khi truyền `--model`/`--effort`).
  - Codex vẫn chạy bình thường, chỉ là Orca không nhận được hook status lúc khởi động nên báo `missing_status`.
  - Nếu terminal của worker đang idle ở prompt của codex thì không relaunch `worker-start`, mà `task-create` task mới rồi `dispatch --inject` vào chính terminal đó và chờ `worker_done` như bình thường.
  - Đây là workaround có điều kiện, bỏ khi Orca hoặc codex bản mới qua được bước readiness.
- **jev-gate**: `git fetch` và `git ls-remote` không còn bị gửi Jev, `git rev-list` được thêm vào fast path read-only, nên các lệnh đồng bộ repo của worker không còn bị hỏi thừa.

## [0.13.0] - 2026-09-29

### Plugins

- `jev-dispatch`: 0.4.0 → 0.5.0
- `orca-workflows`: 0.5.0 → 0.6.0
- `jev-gate`: 0.1.1 → 0.1.2

### Added

- **jev-dispatch**: dựng lại policy routing dựa trên research tháng 9/2026 về Opus 5.5, Sonnet 5.5, GPT-6 Sol và GPT-6 Luna, chia tải giữa subscription Claude và Codex (replay shadow log: khoảng 4/11 task sang Claude).
  - `c >= 3.2` → `opus/high`, `c >= 2.2` → `sonnet/high` (không lên `xhigh`/`max` vì đắt hơn Opus mỗi task).
  - Task cần web → `sonnet/medium`, vì Claude Code có sẵn web search còn worker Codex không kèm `--search` thì không có.
  - Task long-context → `sol/high`. Việc engineering thông thường → `sol/high` từ `c` 2.0, `sol/medium` từ 1.5; Luna chỉ nhận task `c < 1.5`.
  - Bỏ nhánh `gemini/flash`: task trivial giờ đi `codex/luna/medium`, `FLOOR_RISK` gate nhánh này.
  - Task rủi ro cao: `suggested` là route task sẽ nhận nếu an toàn (`opus/high` khi Jev không chắc); khi `r >= 1.5` không bao giờ đề xuất codex, thấp nhất `sonnet/high`.
  - Bảng map tên viết tắt sang provider id (`sonnet` → `claude-sonnet-5-5`, `luna` → `gpt-6-luna`, …) đặt cạnh bảng policy trong SKILL, README và rule Cursor; gặp tên không có trong bảng thì coi như `act=false`.
  - Các ngưỡng 1.5 và 2.0 chưa được đo; user có thể chủ động opt-in auto-routing trước khi chạy lại golden set.
- **orca-workflows**: `dag-build` route worker theo `jev-dispatch` thay vì luôn chạy `--agent codex` mặc định.
  - `act=true` → launch đúng `--agent`/`--model`/`--effort` của routing (đã map sang provider id); task được user duyệt chạy `suggested` hoặc route user chọn; retry giữ nguyên route.
  - Gọi `ask` cả trước khi reuse terminal, chỉ reuse khi harness/model/effort khớp.
  - Override chỉ-nâng: coordinator được nâng worker (`luna` < `sol` < `sonnet` < `opus`) khi spec lộ độ khó kỹ thuật mà bản tóm tắt che mất, không bao giờ hạ, và ghi `override: <lý do>` vào note outcome.
  - Log `used` lấy model/effort thật từ `launch.effective` của receipt, không còn ghi cứng `null`, để golden set so được giữa các model.

### Fixed

- **jev-gate**: worker Orca không còn bị treo khi bật enforce. Các lệnh giao thức coordinator (`orca orchestration send/check/reply/ask/worker-read/worker-list/dispatch-show`) được ghi `source: "ipc"`, không gửi Jev và không REUSE.
  - Trước đây Jev chấm heartbeat của worker outward 0.75–0.96, và ở enforce, ask này làm worker không có người trông bị treo. Worker Codex thì bị deny kèm lời nhắn "escalate", mà escalate lại chính là một lệnh `send`.
  - Fast path tách segment bằng `shlex`, nên `;`, `|`, `>` nằm trong quote (vd `--body` của heartbeat, pattern `grep`/`jq`) được coi là text. `$(…)` và backtick vẫn bị loại ở mọi chỗ.
  - Replay shadow log: số Jev ask giảm từ 26 xuống 18, và 29 lệnh read-only chuyển sang fast path. Lệnh gộp heartbeat với việc khác thì chỉ được bỏ qua Jev khi phần còn lại read-only.

### Security

- **jev-gate**: redact capability token `dcap_…` của Orca. Trước đây token này bị lưu plaintext trong session log và bị gửi lên TypeSafe khi Jev chấm lệnh `orca orchestration send`. Log cũ cần tự che, vì bản này chỉ áp dụng cho call mới.
- **jev-gate**: fast path tách segment theo `&` đơn, nên `ls & rm -r build` không còn được coi là read-only và bỏ qua Jev.

## [0.12.0] - 2026-09-29

### Plugins

- `jev-dispatch`: 0.3.1 → 0.4.0

### Added

- **jev-dispatch**: policy routing có thêm nhánh Claude Sonnet 5.5. Task có complexity `2.2 <= c < 3.2` giờ route sang `claude` / `sonnet` / `high` thay vì `codex` / `luna` / `max`; Opus vẫn giữ cho task `c >= 3.2`. Nhánh mới đứng trước nhánh web/long-context. Ngưỡng 2.2 chưa được đo trên golden set, nên vẫn chạy shadow mode trước khi bật auto-routing.

### Changed

- **jev-dispatch**: siết quy tắc ghi dispatch log để replay golden set không bị lệch schema. Tên field giữ đúng như spec (`event`, không phải `kind`; `response` để nguyên), `outcome` chỉ nhận 4 giá trị trong enum, mỗi lần gọi `ask` chỉ ghi một record `route` sau khi chốt dispatch, task không qua `ask` thì không ghi. `used.model`/`used.effort` giờ ghi giá trị cụ thể worker chạy thay vì `null`. Worker lỗi lúc khởi động rồi chạy lại được vẫn tính `ok`. Đã đồng bộ SKILL, README, rule Cursor và eval.

## [0.11.0] - 2026-09-29

### Plugins

- `spec-readiness-gate`: 0.1.0 (ra mắt)
- `jev-gate`: 0.1.0 → 0.1.1

### Added

- **spec-readiness-gate**: plugin MCP mới chấm độ sẵn sàng của task spec trước khi coordinator dispatch cho worker (`worker-start --spec`, `task-create` của Orca), mặc định ở **shadow mode**.
  - Tool `ask` chạy battery TypeSafe Jev `spec_readiness` trong một request: 5 Noul cho các trường Target / Change / Constraints / Ownership / Observable acceptance, cộng điểm tổng 0..4.
  - Policy thuần trong code ra verdict `dispatch`, `clarify` (chỉ rõ trường yếu, tối đa 2 vòng) hoặc `escalate`. Jev chỉ chấm, code mới quyết.
  - Mọi lỗi trả về dict có `kind` và verdict `escalate`, không crash. Input trông như chứa secret/token bị từ chối trước khi gửi đi.
  - Skill `spec-readiness` hướng dẫn khi nào gọi, clarify loop, checklist thủ công 5 trường khi thiếu API key, format log và tiêu chí bật enforce. Cursor dùng rule riêng.
  - Là add-on: `orca-workflows` chạy bình thường khi không cài plugin này.

### Changed

- **jev-gate**: nâng ngưỡng `ASK_AT` từ 0.5 lên 0.7. Dữ liệu shadow cho thấy ở 0.5 Jev hỏi nhầm cả lệnh read-only (`gh pr view/list`, `git fetch`, lệnh quản lý worker của `orca`); replay trên log giảm số lần ask từ 33 xuống 12, các lệnh thật sự cần hỏi (`gh pr create/merge`, `rm -rf`) vẫn được hỏi.

## [0.10.0] - 2026-09-29

### Plugins

- `jev-gate`: 0.1.0 (ra mắt)

### Added

- **jev-gate**: plugin hook mới chặn từng tool call Bash/MCP trước khi chạy, mặc định ở **shadow mode**.
  - PreToolUse chạy lần lượt:
    1. Lock rule viết bằng code (`git push`, `git reset --hard`/`clean -f`/`branch -D`, publish package, `curl | sh`, `sudo`, `rm -rf` vào `/`, `~`, `.`, `*`). Khớp thì `ask`, ở mọi mode.
    2. Fast path: lệnh read-only được chạy luôn, không gọi Jev.
    3. REUSE ledger: đúng command cũ, git fingerprint không đổi, lần trước ≥ 5s hoặc ≥ 4 KB, trong vòng 15 phút; chỉ nhắc một lần.
    4. TypeSafe Jev chấm 4 Noul cho vùng xám.
  - Ở shadow mode, Jev chạy trong process tách rời nên hook không thêm latency đáng kể, và mọi quyết định khác lock chỉ được log.
  - `enforce` áp dụng thêm Jev `ask` và REUSE deny; bản này không bao giờ auto-allow.
  - Log JSONL theo session tại `~/.local/state/jev-gate/sessions/`, gồm quyết định và kích thước/hash output, không lưu output. Command đã bỏ thân heredoc và redact secret; MCP chỉ gửi tên tool và tên argument.
  - Skill `gate-review` hướng dẫn đọc dữ liệu shadow, cho người dùng gán nhãn các lần Jev hỏi, đo độ chính xác của REUSE và kích thước output, và tiêu chí trước khi bật enforce.
  - Cần `python3` ≥ 3.9 và `git`. API key TypeSafe là tùy chọn; thiếu key thì chỉ lock và REUSE chạy.
  - Claude Code được hỗ trợ. Codex chưa verify ở runtime; với Codex, `ask` được map thành `deny` vì Codex chưa hỗ trợ `ask`.

## [0.9.0] - 2026-09-28

### Plugins

- `debug-root-cause`: 0.1.0 → 0.2.0
- `orca-workflows`: 0.4.0 → 0.5.0

### Added

- **debug-root-cause**: skill `debug-root-cause` biết khi nào nó đang chạy trong một Orca worker. Khi có live preamble, chạm stop rule (3 giả thuyết bị bác bỏ hoặc 3 lần fix hỏng) hoặc cần escalate thì skill gửi ledger và bằng chứng cho coordinator qua lệnh `ask` trong preamble hoặc message `escalation`, thay vì mở UI hỏi local mà không ai trả lời. Hỏi bị timeout thì resume đúng message ID; không giải quyết được thì báo `worker_done --outcome failed`. Kèm eval mới cho tình huống này.
- **debug-root-cause**: khi cần chuyển việc sang `research-swarm`, `parallel-review` hoặc `clarify-requirements` mà skill đó chưa được cài, agent tự xử lý như một agent đơn.
- **orca-workflows**: worker được giao sửa lỗi cụ thể (test/suite đỏ, build fail, crash) nhận spec dặn làm theo `debug-root-cause`, nếu harness của worker đã cài skill này. Áp dụng ở bước Fixes của chuỗi recipe trong `orca-router` và ở bước integrate của `dag-build`, nên worker bế tắc sẽ báo coordinator bằng `question`/`escalation` chứ không thử fix mò lần thứ tư.

## [0.8.0] - 2026-09-27

### Plugins

- `compound-retros`: 0.1.0 (mới)

### Added

- **compound-retros**: plugin mới hiện thực hoá compound engineering loop — biến bài học của mỗi phiên làm việc với agent thành solution note ngắn, có cấu trúc, nằm trong repo (mặc định `docs/solutions/`, tôn trọng kho/convention sẵn có).
  - Skill `retro-capture`: ghi một bài học mỗi note (4 loại `bug-lesson`, `convention`, `decision`, `pitfall`), kể cả bài học từ việc user sửa tay hay nhắc agent. Chỉ ghi khi qua durable bar ("mất note này thì agent tương lai có lặp lại sai lầm không?"), trùng thì update-in-place và tăng `occurrences`, mâu thuẫn thì không ghi đè. Tự quét secrets trước khi ghi. Lặp lại ≥ 3 lần thì chỉ đề xuất một dòng convention vào `AGENTS.md`/`CLAUDE.md` và chờ user duyệt.
  - Skill `retro-recall`: tra note theo frontmatter (`tags`, `area`, `title`) trước khi làm việc tương tự, đọc full tối đa 3 note, cite và áp dụng; code hiện tại mâu thuẫn với note thì code thắng. Dọn kho theo yêu cầu: phân loại keep / merge / stale / contradiction và không xoá gì khi user chưa xem danh sách.
  - Stop hook cho Claude Code và Codex: chỉ nhắc (không block), tối đa một lần mỗi phiên, khi câu của user có dấu hiệu sửa agent hoặc yêu cầu ghi nhớ. Cần `python3`; tắt bằng `COMPOUND_RETROS_HOOK_OFF=1`. Kimi chưa hỗ trợ hook ở bản này.
  - Kèm `references/note-template.md` và 12 eval case. Gemini CLI headless load `gemini-context.md`; Cursor dùng rule `.cursor/rules/compound-retros.mdc`.

## [0.7.0] - 2026-09-27

### Plugins

- `debug-root-cause`: 0.1.0 (mới)

### Added

- **debug-root-cause**: plugin mới có skill `debug-root-cause`, giúp debug một failure cụ thể đã xảy ra (test đỏ, build/CI fail, lỗi runtime, stack trace, flaky test, regression "hồi trước chạy đúng") theo quy trình có phương pháp thay vì đoán rồi sửa thử.
  - 5 pha, mỗi pha có entry/exit criteria rõ ràng: Reproduce & isolate → Gather evidence → Hypothesis ledger → Fix & regression → Aftermath. Có nhánh riêng cho lỗi chỉ fail trên CI, lỗi flaky (chạy lặp tối thiểu 5 lần để đo tần suất) và trường hợp chỉ có stack trace.
  - 4 Iron Rule: không sửa code khi chưa có failing test; không nói "fixed" khi chưa verify; mỗi lần chỉ một giả thuyết, một experiment, một thay đổi; vá triệu chứng coi như chưa fix.
  - Stop rule: 3 giả thuyết bị bác bỏ hoặc 3 lần fix thất bại thì dừng, tóm tắt ledger và hỏi user. Lỗi infra/vendor/dependency ngoài tầm kiểm soát thì escalate kèm bằng chứng, không force-fix.
  - Kèm `references/` (evidence playbook, template hypothesis ledger và bug report) cùng `evals/evals.json` gồm 12 case. Gemini CLI headless load `gemini-context.md`; Cursor dùng rule `.cursor/rules/debug-root-cause.mdc`.

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

[Unreleased]: https://github.com/trisjr/agent-relay/compare/v0.16.0...HEAD
[0.16.0]: https://github.com/trisjr/agent-relay/compare/v0.15.0...v0.16.0
[0.15.0]: https://github.com/trisjr/agent-relay/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/trisjr/agent-relay/compare/v0.13.1...v0.14.0
[0.13.1]: https://github.com/trisjr/agent-relay/compare/v0.13.0...v0.13.1
[0.13.0]: https://github.com/trisjr/agent-relay/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/trisjr/agent-relay/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/trisjr/agent-relay/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/trisjr/agent-relay/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/trisjr/agent-relay/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/trisjr/agent-relay/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/trisjr/agent-relay/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/trisjr/agent-relay/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/trisjr/agent-relay/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/trisjr/agent-relay/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/trisjr/agent-relay/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/trisjr/agent-relay/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/trisjr/agent-relay/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/trisjr/agent-relay/releases/tag/v0.1.0
