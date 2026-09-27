# debug-root-cause

Plugin giúp agent điều tra **một lỗi đang xảy ra** theo bằng chứng: tái hiện và cô lập lỗi, thu thập dữ liệu, kiểm tra giả thuyết bằng thí nghiệm nhỏ, sửa nguyên nhân gốc sau khi có test đỏ, xác minh test và suite liên quan xanh, rồi viết bug report ngắn. Áp dụng cho test, build, CI hoặc runtime failure cụ thể.

## Bối cảnh

- `systematic-debugging` của superpowers (MIT) là prior art gần nhất. Skill này bổ sung tiêu chí vào/ra cho từng pha, hypothesis ledger có mẫu và cách xếp hạng giả thuyết, nhánh riêng cho lỗi chập chờn hoặc chỉ xảy ra trên CI, điều kiện escalation cho hạ tầng/vendor, và bước Aftermath.
- *The Debugging Book* của Andreas Zeller (CC BY-NC-SA) gợi cấu trúc kiểm chứng từ test case đến giả thuyết, quan sát và test hồi quy; plugin chỉ kế thừa cấu trúc, không trích văn bản.
- David J. Agans, *Debugging: The 9 Indispensable Rules*, là nền cho thói quen tái hiện lỗi, quan sát hệ thống, đổi một biến mỗi lần và giữ dấu vết điều tra.

Phạm vi của plugin là **một failure cụ thể, một agent, điều tra depth-first**. Câu hỏi nghiên cứu rộng thuộc `research-swarm`; review một diff đang khỏe thuộc `parallel-review`; yêu cầu mơ hồ cần `clarify-requirements` trước.

## Các skill

| Skill | Dùng khi | Làm gì |
| --- | --- | --- |
| `debug-root-cause` | Một test, build, CI hoặc runtime path đã fail, kể cả flaky hoặc chỉ fail trên CI | Phase 1 — Reproduce & isolate → Phase 2 — Gather evidence → Phase 3 — Hypothesis ledger → Phase 4 — Fix & regression → Phase 5 — Aftermath |

Skill kèm `evals/evals.json` để kiểm tra trigger và hành vi trên các tình huống mẫu.

## Nguyên tắc chính

Các điểm cần giữ, gồm bốn **Iron Rules**:

- **Right-size first:** lỗi hiển nhiên như typo hoặc thiếu import chỉ cần xác nhận nguyên nhân và chạy lại lệnh; lỗi chưa rõ cần ghi bằng chứng và hypothesis ledger.
- **Rule 1 — No fix before failing test:** cần test đỏ đúng vì bug hoặc repro script tự động trước khi sửa production logic; ngoại lệ là lỗi một bước mà thông báo lỗi đã chỉ rõ, nhưng vẫn phải chạy lại để xác nhận.
- **Rule 2 — Never claim "fixed" without verification:** chỉ kết luận khi check ban đầu và suite liên quan xanh, đồng thời giải thích root cause trong một câu. Nếu chỉ kiểm tra thủ công, ghi `unverified by automated test`.
- **Rule 3 — One hypothesis, one experiment, one change:** ghi kết quả dự đoán trước, đổi một biến, rồi cập nhật ledger với `confirmed`, `refuted` hoặc `inconclusive`.
- **Rule 4 — Symptom patches are failure:** lần theo caller và ranh giới component để sửa tại nơi tạo ra hành vi sai.
- **Stop rule:** 3 refuted hypotheses hoặc 3 failed fixes thì dừng, tóm tắt ledger, hỏi user hoặc xem lại mô hình/kiến trúc; không âm thầm thử lần thứ tư.
- **Escalation:** dừng và báo bằng chứng, ledger cùng hướng xử lý khi gặp dependency bug không thể patch hợp lý; lỗi infra/vendor/quota/DNS/CI-runner; fix đúng cần đổi public contract hoặc migration chưa được duyệt; hoặc race ở tầng ngoài tầm kiểm soát.

`gemini-context.md` giữ bản tóm tắt vì Gemini headless (`-p`, CI) bỏ `activate_skill`, khiến `SKILL.md` thường không được load; tên file cố ý khác `GEMINI.md`. Cursor không đọc `SKILL.md` của plugin nên dùng `.cursor/rules/debug-root-cause.mdc` để áp dụng cùng quy trình.

## Cài đặt

Xem mục "Cài từ bản local" trong README gốc của repo.
