# compound-retros

Plugin biến bài học sau mỗi phiên làm việc thành kiến thức dùng lại được trong repo: ghi note ngắn, tìm lại trước việc tương tự, rồi dọn kho để kiến thức không lỗi thời.

## Bối cảnh

Compound engineering nối việc đã làm với việc tiếp theo qua vòng **capture → recall → curate**. Thiết kế này tham khảo [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) (MIT) về note có giá trị lâu dài và dọn kho; đã kiểm tra [obra/superpowers](https://github.com/obra/superpowers) (MIT) và thấy chưa có skill memory/knowledge tương đương (gần nhất là `systematic-debugging`, không trùng phạm vi); và tham khảo nghiên cứu [Gloaguen và cộng sự, ETH Zurich, arXiv:2602.11988](https://arxiv.org/abs/2602.11988) về hiệu quả và chi phí của file hướng dẫn cấp repo. Vì vậy, plugin giữ note ngắn và chỉ đề xuất thay đổi `AGENTS.md` để người dùng duyệt.

## Các skill

| Skill | Dùng khi | Làm gì |
| --- | --- | --- |
| `retro-capture` | Sau việc có bài học khó thấy trong code, test hoặc docs; đặc biệt khi người dùng sửa agent, yêu cầu ghi nhớ, hoặc vấn đề tái diễn | Cân giá trị lâu dài, ghi một solution note có cấu trúc, cập nhật note cũ nếu trùng |
| `retro-recall` | Trước việc không tầm thường trong vùng đã có note, khi vấn đề quen thuộc, hoặc khi người dùng yêu cầu dọn kho | Lọc theo frontmatter trước, đọc vài note liên quan, áp dụng và dẫn nguồn; phân loại note khi dọn kho |

## Nguyên tắc chính

- **Chỉ ghi bài học bền.** Nếu mất note mà agent tương lai vẫn tránh được lỗi nhờ code, test, docs hoặc `AGENTS.md` hiện có thì bỏ qua; sửa typo hay nhật ký phiên không đủ giá trị.
- **Tra rẻ trước.** Tìm theo `title`, `area`, `tags` rồi chỉ đọc toàn văn tối đa vài note thực sự liên quan.
- **Tôn trọng kho sẵn có.** Dùng thư mục và template note của repo nếu đã có; mặc định là `docs/solutions/`. Note nằm trong repo của người dùng, không nằm trong plugin.
- **Chống trùng và lỗi thời.** Cùng bài học thì cập nhật note hiện có; khi tình huống tái diễn đủ `occurrences >= 3`, chỉ đề xuất một dòng convention vào `AGENTS.md` hoặc `CLAUDE.md` và chờ người dùng đồng ý. Các file hướng dẫn đó thuộc quyền người dùng.
- **Không ghi secret.** Note chỉ được nhắc tên key cấu hình, không chứa token, credential hoặc giá trị nhạy cảm.

Kho note được git theo dõi theo mặc định; thêm `docs/solutions/` vào `.gitignore` nếu muốn giữ riêng tư.

## Hook nhắc capture

Claude Code và Codex dùng Stop hook của plugin để nhận diện tín hiệu người dùng sửa agent hoặc yêu cầu ghi nhớ trong transcript. Hook chỉ nhắc cân nhắc `retro-capture`, không chặn phiên, và nhắc tối đa một lần mỗi phiên; skill vẫn quyết định có qua ngưỡng bài học bền hay không. Hook cần `python3` trên `PATH` để lọc đúng lời người dùng trong transcript; thiếu Python 3 thì hook im lặng.

Sau lần nhắc đầu, hook tạo marker `${TMPDIR:-/tmp}/compound-retros-reminded-<session_id>` để không nhắc lại trong cùng phiên.

Tắt hook bằng `COMPOUND_RETROS_HOOK_OFF=1`, hoặc tạo marker `${TMPDIR:-/tmp}/.compound-retros-off` để tắt lâu dài. Với Codex, lần đầu dùng cần xem và tin cậy plugin hook qua `/hooks`.

Kimi chưa được hỗ trợ ở v0.1.0: dù [Kimi cho phép khai báo hook trong plugin](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins), [Stop event hiện không cung cấp `transcript_path`](https://moonshotai.github.io/kimi-cli/en/customization/hooks.html) cho script đọc tín hiệu; hãy gọi `retro-capture` trực tiếp. Khả năng dùng cùng hook trên Kimi cần xác minh thêm.

Gemini CLI dùng `gemini-context.md` khi headless không tải skill; Cursor dùng `.cursor/rules/compound-retros.mdc` để giữ cùng nguyên tắc capture và recall.

## Cài đặt

Xem mục "Cài từ bản local" trong [README gốc](../../README.md) của repo.
