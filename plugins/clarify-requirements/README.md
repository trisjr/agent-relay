# clarify-requirements

Plugin giúp agent **làm rõ yêu cầu trước khi build**: tự tìm hiểu repo trước, chỉ hỏi vài câu thực sự thay đổi cách làm (mỗi câu có option đề xuất), ghi lại các assumption rủi ro thấp, rồi bàn giao một requirements brief ngắn cho người implement (chính agent, một session mới hoặc worker trong DAG).

## Bối cảnh

Skill được thiết kế từ một đợt research ba hướng: prior art (spec-kit `clarify`, superpowers `brainstorming`, Kiro, BMAD, Codex Plan Mode, Claude Code `feature-dev`…), phương pháp elicitation (ISO/IEC/IEEE 29148, EARS, INVEST, Volere), và cơ chế hỏi user của từng harness. Các nguồn thống nhất ở mấy điểm:

- Hỏi sai chỗ cũng tệ như không hỏi: câu hỏi mà repo/docs trả lời được, hoặc hỏi dồn cả checklist, là lỗi phổ biến nhất của các tool hiện có.
- Mỗi câu hỏi có default đề xuất; user không trả lời thì dùng default và ghi thành assumption.
- Cap nhỏ, chỉ hỏi điều có tác động thật, và có đường thoát nhanh khi yêu cầu đã rõ.

## Các skill

| Skill | Dùng khi | Làm gì |
| --- | --- | --- |
| `clarify-requirements` | Yêu cầu mơ hồ, thiếu thông tin hoặc rủi ro cao trước khi implement/plan: "build X", "làm tính năng", "làm rõ yêu cầu", PRD/spec sẽ feed vào plan hay DAG | Right-size → tìm hiểu repo → quét gap → quyết định hỏi / tự chọn default / block → hỏi tối đa 3 câu mỗi vòng qua đúng kênh của harness → dừng theo checklist → xuất requirements brief 120–250 từ |

Skill kèm `evals/evals.json`: bộ prompt mẫu kèm kỳ vọng hành vi, dùng cho vòng đánh giá/iterate của skill-creator.

## Nguyên tắc chính

- **Right-size trước.** Yêu cầu đã rõ, diff mô tả được trong một câu, hoặc mọi điểm mở đều tra được trong repo thì không hỏi gì cả.
- **Fact thì tự tìm, preference mới hỏi.** Tham số chuyên môn (retry, page size, TTL…) tự chọn theo convention và ghi lại.
- **Ưu tiên theo impact × uncertainty × irreversibility.** An toàn, quyền riêng tư, tiền, permission, xoá dữ liệu, public API luôn là impact cao nhất; hành động không đảo ngược mà thiếu quyết định thì block, không tự bịa default.
- **Câu hỏi rẻ để trả lời.** Tự đủ ngữ cảnh, một quyết định mỗi câu, 2–3 option, option đề xuất đứng đầu với `(Recommended)`, viết bằng ngôn ngữ của user.
- **Brief là nguồn sự thật duy nhất.** Ngắn, chỉ ghi quyết định; ghi ra file thì sửa tại chỗ, không nhân bản.

## Kênh hỏi theo harness

Skill chọn kênh đầu tiên khớp:

| Tình huống | Kênh |
| --- | --- |
| Worker Orca có live preamble | Lệnh `orca orchestration ask` trong preamble, không bao giờ mở UI hỏi local |
| Claude Code, Kimi Code, Qoder CLI | `AskUserQuestion` |
| Codex CLI | `request_user_input` (chỉ ở Plan mode; Default mode dùng block plain-text) |
| Gemini CLI | `ask_user` |
| Cursor, Qoder IDE | Tool hỏi built-in, giữ trong 3 câu / 2–3 option |
| Interactive nhưng không có tool | Block plain-text đánh số, kết thúc turn để chờ trả lời |
| Headless (CI, `-p`, `exec`, tool bị deny) | Không chờ: gap rủi ro thấp dùng default + liệt kê assumption; gap blocking thì dừng trước khi hành động và in block câu hỏi làm output cuối |

Cursor không đọc `SKILL.md` của plugin này mà dùng rule `.cursor/rules/clarify-requirements.mdc` — bản tóm tắt cùng quy trình.

## Cài đặt

Xem mục "Cài từ bản local" trong README gốc của repo — plugin đã đăng ký vào các marketplace (`agent-relay`).
