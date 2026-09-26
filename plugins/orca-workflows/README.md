# orca-workflows

Plugin đóng gói các workflow multi-agent có giám sát (supervised) cho Orca CLI: research swarm, review code song song nhiều góc nhìn, và build tính năng theo DAG có decision gate.

## Bối cảnh

Orca cung cấp hai lớp được dùng qua CLI:

- `ORCA orchestration` — điều phối có giám sát: Run / Task / Dispatch, mailbox, ask/reply blocking, task DAG, decision gate, escalation.
- `orca-cli` — vận hành trạng thái: worktree, terminal, handoff đơn giản (fire-and-forget), browser, automations.

`ORCA` là executable đã resolve: `ORCA_CLI_COMMAND` nếu có, `orca-dev` khi có `ORCA_DEV_REPO_ROOT`, `orca-ide` trên Linux ngoài Orca terminal (ở đó `orca` trần là screen reader GNOME), còn lại là `orca`.

Skill gốc của Orca chỉ là discovery stub; tài liệu thật nằm trong binary (`ORCA skills get orchestration`, `ORCA skills get orca-cli`). Plugin này tuân theo triết lý đó: mọi skill resolve executable và load guide version-matched từ binary trước khi chạy lệnh. Lệnh mẫu trong recipe khớp Orca 1.4.211; khi lệch với guide hoặc `--help` của binary thì guide thắng.

## Các skill

| Skill | Dùng khi | Làm gì |
| --- | --- | --- |
| `orca-router` | Mọi request chạm vào multi-agent Orca (điều phối, handoff, theo dõi worker, DAG) | Phân loại request, chọn đúng hệ thống (orchestration / orca-cli / worker / agent thường), load guide phù hợp, rẽ vào workflow có sẵn; giữ các quy tắc coordinator dùng chung |
| `research-swarm` | Câu hỏi nghiên cứu/phân tích rộng, so sánh nhiều phương án, khảo sát codebase theo nhiều hướng | Fan-out worker theo góc độc lập; mỗi worker ghi findings ra file trong `.orca-reports/<run_id>/` (đã exclude khỏi Git); coordinator tổng hợp từ file, có ghi nguồn theo worker |
| `parallel-review` | Review diff/branch/PR lớn hoặc rủi ro trước merge, review bảo mật, cần nhiều góc nhìn | Fan-out reviewer theo "lens" (security, correctness, consistency, simplicity); mỗi reviewer một context sạch, review-only; coordinator dedupe findings theo severity. Change nhỏ thì review trực tiếp, không tạo Run |
| `dag-build` | Build tính năng nhiều module, migration xuyên dịch vụ, cần duyệt spec trước | Plan → gate duyệt spec → task DAG với deps thật → wave song song → integrate + verify bằng test/build |

Mỗi skill kèm `evals/evals.json` — bộ test prompt mẫu kèm kỳ vọng hành vi, dùng cho vòng đánh giá/iterate của skill-creator.

## Nguyên tắc dùng chung

- **Orchestration chỉ cho việc supervised.** Handoff đơn thuần ("giao cho agent khác, không cần theo dõi") đi qua `ORCA worktree create --no-parent --agent <id> --prompt ...` và kết thúc ở `accepted: true` — không tạo Run, không `check --wait`.
- **Không có Orca thì không ép.** Máy thiếu Orca hoặc Orca chưa chạy, và user không yêu cầu Orca, thì skill làm việc như một agent đơn thay vì báo lỗi hay tự mở app.
- **Multi-agent đắt đỏ** (~15x token so với chat thường); chỉ fan-out cho việc breadth-first thực sự. Việc tuần tự phụ thuộc chặt thì một agent là đủ.
- **Quyền sở hữu rõ ràng**: reviewer không sửa code; worker không đụng phạm vi của worker khác; coordinator không tự fix sau review.

## Cài đặt

Xem mục "Cài từ bản local" trong README gốc của repo — plugin đã đăng ký vào các marketplace (`agent-relay`).
