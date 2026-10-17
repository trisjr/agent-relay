# dev-workflows

Plugin gom toàn bộ workflow chuẩn cho dev làm việc cùng coding agent vào một chỗ: **làm rõ yêu cầu → điều phối nhiều agent → debug theo bằng chứng → ghi và tái dùng bài học**. Một lần cài, đủ chín skill, mọi platform dùng chung một bộ quy trình.

## Các skill

| Nhóm | Skill | Dùng khi | Làm gì |
| --- | --- | --- | --- |
| Làm rõ yêu cầu | `clarify-requirements` | Yêu cầu mơ hồ, thiếu thông tin hoặc rủi ro cao trước khi implement/plan: "build X", "làm tính năng", "làm rõ yêu cầu", PRD/spec sẽ feed vào plan hay DAG | Right-size → tìm hiểu repo → quét gap → hỏi tối đa 3 câu mỗi vòng (mỗi câu có option đề xuất) → xuất requirements brief 120–250 từ |
| Điều phối | `orca-router` | Mọi request chạm vào multi-agent Orca (điều phối, handoff, theo dõi worker, DAG) | Phân loại request, chọn đúng hệ thống (orchestration / orca-cli / worker / agent thường), load guide từ binary, rẽ vào workflow có sẵn |
| Điều phối | `research-swarm` | Câu hỏi nghiên cứu/phân tích rộng, so sánh nhiều phương án, khảo sát codebase theo nhiều hướng | Fan-out worker theo góc độc lập, mỗi worker ghi findings ra file; coordinator tổng hợp từ file |
| Điều phối | `parallel-review` | Review diff/branch/PR lớn hoặc rủi ro trước merge, review bảo mật | Fan-out reviewer theo "lens"; mỗi reviewer một context sạch, review-only; coordinator dedupe findings theo severity |
| Điều phối | `parallel-scopes` | Một task nhiều phần độc lập (FE/BE/docs/test) muốn chạy song song bằng subagent thường, không cần Orca | Chốt contract trước → bảng scope với ownership file không chồng → spawn cả wave trong một lượt (một working tree, worktree chỉ khi đụng file chung) → tích hợp và verify ở main session |
| Điều phối | `dag-build` | Build tính năng nhiều module, migration xuyên dịch vụ, cần duyệt spec trước | Clarify → plan → gate duyệt spec → task DAG → wave song song → integrate + verify |
| Debug | `debug-root-cause` | Một test, build, CI hoặc runtime path đã fail, kể cả flaky hoặc chỉ fail trên CI | Reproduce & isolate → gather evidence → hypothesis ledger → diagnosis report (chờ user duyệt) → fix sau test đỏ |
| Bài học | `retro-capture` | Sau việc có bài học khó thấy trong code, test hoặc docs; khi người dùng sửa agent hoặc yêu cầu ghi nhớ | Cân giá trị lâu dài, ghi một solution note có cấu trúc, cập nhật note cũ nếu trùng |
| Bài học | `retro-recall` | Trước việc không tầm thường trong vùng đã có note, hoặc khi người dùng yêu cầu dọn kho | Lọc theo frontmatter, đọc vài note liên quan, áp dụng và dẫn nguồn; phân loại note khi dọn kho |

Mỗi skill kèm `evals/evals.json` (bộ prompt mẫu kèm kỳ vọng hành vi) cho vòng đánh giá của skill-creator.

## Các skill phối hợp với nhau

- `dag-build` làm rõ yêu cầu bằng `clarify-requirements` ngay trong conversation của coordinator, rồi viết spec từ brief; worker nhận việc sửa lỗi cụ thể được dặn theo `debug-root-cause`.
- `debug-root-cause` chuyển câu hỏi nghiên cứu rộng sang `research-swarm`, review diff sang `parallel-review`, yêu cầu mơ hồ sang `clarify-requirements`.
- `retro-capture` và `retro-recall` khép vòng: bài học từ debug hoặc quyết định khó được ghi lại, rồi được tra lại trước việc tương tự.

## Nguyên tắc chính theo nhóm

### Làm rõ yêu cầu

- Right-size trước: yêu cầu đã rõ hoặc tra được trong repo thì không hỏi.
- Fact thì tự tìm, preference mới hỏi; ưu tiên theo impact × uncertainty × irreversibility; hành động không đảo ngược mà thiếu quyết định thì block.
- Kênh hỏi chọn theo harness: lệnh `ask` của preamble (worker Orca), `AskUserQuestion` (Claude Code, Kimi, Qoder CLI), `request_user_input` (Codex Plan mode), `ask_user` (Gemini), tool hỏi built-in (Cursor, Qoder IDE), block plain-text đánh số (interactive không có tool), hoặc default + assumptions (headless).

### Điều phối với Orca

- `ORCA` là executable đã resolve: `ORCA_CLI_COMMAND` nếu có, `orca-dev` khi có `ORCA_DEV_REPO_ROOT`, `orca-ide` trên Linux ngoài Orca terminal, còn lại là `orca`. Mọi skill load guide version-matched từ binary (`ORCA skills get orchestration`, `ORCA skills get orca-cli`) trước khi chạy lệnh; guide hoặc `--help` thắng khi lệch với recipe.
- Orchestration chỉ cho việc supervised; handoff đơn thuần đi qua `ORCA worktree create --no-parent` và dừng ở `accepted: true`.
- Không có Orca và user không yêu cầu Orca thì làm như một agent đơn, không báo lỗi hay tự mở app. Multi-agent đắt (~15x token), chỉ fan-out cho việc breadth-first.
- Reviewer không sửa code; worker không đụng phạm vi của worker khác; coordinator không tự fix sau review.

### Debug theo bằng chứng

- **Iron Rules:** không fix trước khi có test đỏ; không báo "fixed" khi chưa verify; một giả thuyết, một thí nghiệm, một thay đổi; vá triệu chứng là thất bại.
- Dừng sau 3 giả thuyết bị bác bỏ hoặc 3 lần fix hỏng; escalate khi gặp lỗi hạ tầng/vendor, dependency bug không patch được, hoặc fix cần đổi public contract chưa duyệt.

### Ghi và tái dùng bài học

- Chỉ ghi bài học bền: mất note mà agent tương lai vẫn tránh được lỗi nhờ code, test, docs hoặc `AGENTS.md` thì bỏ qua.
- Tra rẻ trước (theo `title`, `area`, `tags`), tôn trọng kho sẵn có (mặc định `docs/solutions/`, note nằm trong repo người dùng, không nằm trong plugin).
- `occurrences >= 3` thì chỉ đề xuất một dòng convention vào `AGENTS.md`/`CLAUDE.md` và chờ người dùng đồng ý. Không bao giờ ghi secret.

## Hook nhắc capture

Claude Code và Codex dùng Stop hook của plugin (`hooks/hooks.json`) để nhận diện tín hiệu người dùng sửa agent hoặc yêu cầu ghi nhớ trong transcript. Hook chỉ nhắc cân nhắc `retro-capture`, không chặn phiên, nhắc tối đa một lần mỗi phiên; skill vẫn quyết định có qua ngưỡng bài học bền hay không. Hook cần `python3` trên `PATH`; thiếu Python 3 thì hook im lặng.

Sau lần nhắc đầu, hook tạo marker `${TMPDIR:-/tmp}/compound-retros-reminded-<session_id>` để không nhắc lại trong cùng phiên. Tắt hook bằng `COMPOUND_RETROS_HOOK_OFF=1`, hoặc tạo marker `${TMPDIR:-/tmp}/.compound-retros-off` để tắt lâu dài. Tên biến và marker giữ nguyên `compound-retros` (kế thừa từ plugin cũ) để ai đã tắt hook không bị bật lại ngoài ý muốn. Với Codex, lần đầu dùng cần xem và tin cậy plugin hook qua `/hooks`.

Kimi chưa được hỗ trợ hook này vì Stop event không cung cấp `transcript_path`; hãy gọi `retro-capture` trực tiếp.

Chạy test của hook: `sh plugins/dev-workflows/hooks/test-remind-capture.sh`.

## Theo từng platform

- **Gemini CLI headless** (`-p`, CI, không TTY) gỡ `ask_user` và chặn `activate_skill`, nên `SKILL.md` thường không được load. Extension khai báo `contextFileName: "gemini-context.md"` — file này luôn được load, gồm ba mục (`clarify-requirements`, `debug-root-cause`, `compound-retros`), mỗi mục tự giới hạn phạm vi áp dụng. Tên file cố ý khác `GEMINI.md` để Gemini không tự nhặt nó khi chạy ngay trong repo này.
- **Cursor** không đọc `SKILL.md` của plugin; dùng bốn rule riêng trong `.cursor/rules/` (`clarify-requirements.mdc`, `debug-root-cause.mdc`, `compound-retros.mdc`, `orca-workflows.mdc`), mỗi rule có `description` trigger riêng để không nạp thừa ngữ cảnh.

## Chuyển từ bốn plugin cũ

`dev-workflows` thay thế bốn plugin đã bị xoá khỏi marketplace: `clarify-requirements`, `debug-root-cause`, `compound-retros`, `orca-workflows`. Đây là breaking change:

1. Gỡ bốn plugin cũ rồi cài `dev-workflows@agent-relay` (Claude Code):

   ```text
   /plugin uninstall clarify-requirements@agent-relay
   /plugin uninstall debug-root-cause@agent-relay
   /plugin uninstall compound-retros@agent-relay
   /plugin uninstall orca-workflows@agent-relay
   /plugin install dev-workflows@agent-relay
   ```

   Chưa gỡ bản cũ thì skill xuất hiện hai lần và hai Stop hook cùng chạy.
2. Namespace của skill đổi từ `<plugin-cũ>:<skill>` sang `dev-workflows:<skill>` (ví dụ `clarify-requirements:clarify-requirements` thành `dev-workflows:clarify-requirements`). Tên skill không đổi.
3. Hành vi hook, biến môi trường `COMPOUND_RETROS_HOOK_OFF` và kho `docs/solutions/` giữ nguyên.

Các plugin add-on (`jev-dispatch`, `jev-gate`, `spec-readiness-gate`, `compact-nudge`) vẫn là plugin riêng; `spec-readiness-gate` và `jev-dispatch` hoạt động như add-on của `dev-workflows`.

## Cài đặt

Claude Code:

```text
/plugin install dev-workflows@agent-relay
```

Các platform khác (Codex, Kimi Code) xem mục "Cài từ bản local" trong [README gốc](../../README.md) của repo.
