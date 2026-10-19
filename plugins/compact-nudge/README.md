# compact-nudge

Plugin cho **Claude Code**. Khi context của session vượt một ngưỡng token, plugin nhắc người dùng chạy `/compact` và soạn sẵn lệnh `/compact <những gì cần giữ lại>` dựa trên chính cuộc hội thoại. Plugin **không bao giờ tự compact**: người dùng quyết định.

## Bối cảnh

Mỗi lượt, Claude Code gửi lại toàn bộ context. Context càng lớn thì mỗi lượt càng tốn, kể cả khi prompt cache hit gần 100%: tiền đọc cache tỉ lệ thuận với độ dài context. Audit thực tế trên khoảng 21.000 API call cho thấy:

- khoảng **51% chi phí** nằm ở các call có context trên 200K token;
- người dùng có compact thủ công, nhưng **thường quá muộn** (trung vị khoảng 300K);
- sau compact, context còn khoảng 15–18K token, nên một lần compact hoà vốn sau 3–5 lượt.

Vì vậy đòn bẩy lớn nhất là compact **đúng lúc**, chứ không phải đổi model. Plugin này nhắc đúng lúc đó.

## Cách hoạt động

| Bước | Làm gì |
| --- | --- |
| 1 | Sau mỗi turn của session chính (bỏ qua subagent), đọc `$.session.usage()` để lấy số token context. Lời gọi này miễn phí |
| 2 | Context ≥ ngưỡng thì hiện toast và band phía trên ô prompt |
| 3 | Gọi `$.model.fork` trên transcript đang được cache để soạn một dòng `/compact giữ lại: …; bỏ: …` (khoảng $0.05 mỗi lần nhắc trên Opus 5.5) |
| 4 | Band có hai nút **[Điền lệnh]** (phím `c`, đưa lệnh vào ô prompt để sửa rồi Enter) và **[Bỏ qua]** (phím `x`); lệnh cũng hiện thành gợi ý mờ, bấm Tab để lấy |
| 5 | Mỗi mốc chỉ nhắc một lần: 200K → 300K → 400K…; sau khi compact, mốc reset về ngưỡng ban đầu |

### Trên desktop app, IDE, SDK

Code tab của desktop app tự vẽ ô prompt và transcript, nên không có band, toast hay gợi ý trong ô prompt của function hooks. Ở các surface này, `hooks/nudge.py` (command hook kiểu cũ, surface nào cũng chạy) thay thế:

| Bước | Làm gì |
| --- | --- |
| 1 | Mỗi lần user gửi prompt (`UserPromptSubmit`), đọc usage của assistant message cuối trong transcript `.jsonl` (bỏ qua subagent, row có usage bằng 0) để lấy số token context |
| 2 | Context chạm mốc thì hiện `systemMessage` cho user và gửi `additionalContext` để Claude trả lời xong thì kết bằng một dòng nhắc kèm lệnh `/compact giữ lại: …; bỏ: …` soạn sẵn, anh copy vào ô prompt. Không tốn thêm API call: lệnh được soạn ngay trong lượt trả lời |
| 3 | Mốc giống bản terminal; reset bằng `SessionStart` (matcher `compact\|clear`), hoặc khi context tụt dưới ngưỡng |

Script bỏ qua entrypoint `cli` (terminal đã có function hooks nhắc), nên không bị nhắc hai lần. Nó đọc `threshold`/`step` qua biến `CLAUDE_PLUGIN_OPTION_THRESHOLD`/`CLAUDE_PLUGIN_OPTION_STEP`, nếu không có thì dùng mặc định. Tắt bằng `COMPACT_NUDGE_HOOK_OFF=1`.

Khác bản terminal: lời nhắc hiện ở **đầu lượt kế tiếp**, không phải ngay sau khi turn kết thúc. Lệnh `/compact` không tự điền vào ô prompt được, anh phải copy.

## Cấu hình

Chỉnh trong `/config`, mục `compact-nudge`:

| Field | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `threshold` | `200000` | Bắt đầu nhắc khi context đạt số token này |
| `step` | `100000` | Sau mỗi lần nhắc, chờ context tăng thêm chừng này mới nhắc lại |

Với task cần giữ nhiều chi tiết (debug dài, refactor nhiều file), nên tăng `threshold` lên khoảng 250K hoặc bấm **Bỏ qua** để chờ mốc sau.

## Cài đặt

```text
/plugin marketplace add trisjr/agent-relay
/plugin install compact-nudge@agent-relay
```

## Giới hạn

- Chỉ chạy trên **Claude Code**. Bản terminal dùng function hooks (early access, API có thể đổi giữa các bản). Các manifest Codex/Gemini/Qoder/Kimi chỉ có để marketplace hợp lệ, không có hành vi.
- Band, toast và gợi ý trong ô prompt chỉ hiện trên terminal (`claude`). Desktop app không vẽ chúng; ở đó dùng bản command hook ở trên.
- Nếu desktop vẫn nạp function hooks, `$.model.fork` có thể vẫn chạy ngầm ở mỗi mốc (khoảng $0.05) dù không ai thấy kết quả.
- `nudge.py` cần `python3` trong `PATH`. Thiếu `python3` thì hook bỏ qua, không chặn prompt.
- **Lỗi im lặng:** nếu API function hooks đổi, hook lỗi chỉ bị bỏ qua (một dòng mờ trong transcript), session vẫn chạy bình thường nhưng lời nhắc sẽ không hiện nữa. Đã test trên Claude Code **2.1.292**; sau mỗi lần cập nhật Claude Code, hoặc khi thấy context vượt ngưỡng mà không được nhắc, chạy lại `claude plugin validate` và `claude plugin test` (mục Phát triển).

## Phát triển

```bash
claude plugin validate ./plugins/compact-nudge
claude plugin test ./plugins/compact-nudge
```
