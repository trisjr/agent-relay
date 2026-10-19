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
| 2 | Context ≥ ngưỡng thì hiện toast và mở **panel** `Compact` (terminal fullscreen từ 110 cột thì dock bên cạnh transcript, còn lại nằm phía trên ô prompt) |
| 3 | Gọi `$.model.fork` trên transcript đang được cache để soạn một dòng `/compact giữ lại: …; bỏ: …` (khoảng $0.05 mỗi lần nhắc trên Opus 5.5) |
| 4 | Panel có hai nút **[Điền lệnh]** (phím `c`, đưa lệnh vào ô prompt để sửa rồi Enter) và **[Bỏ qua]** (phím `x`); đóng panel bằng tay hoặc Esc cũng tính là bỏ qua. Lệnh cũng hiện thành gợi ý mờ, bấm Tab để lấy |
| 5 | Mỗi mốc chỉ nhắc một lần: 200K → 300K → 400K…; sau khi compact, mốc reset về ngưỡng ban đầu |

### Trên desktop app, IDE, SDK

Code tab của desktop app tự vẽ ô prompt và transcript, nên không có band, toast hay gợi ý trong ô prompt của function hooks. Ở các surface này, `hooks/nudge.py` (command hook kiểu cũ, surface nào cũng chạy) thay thế:

| Bước | Làm gì |
| --- | --- |
| 1 | Khi turn của session chính kết thúc (`Stop`), đọc usage của assistant message cuối trong transcript `.jsonl` để lấy số token context. Bỏ qua subagent, row có usage bằng 0, và không đọc lùi qua `compact_boundary` |
| 2 | Context chạm mốc thì hiện **một `systemMessage`** ("Claude Code notice") kèm lệnh `/compact giữ lại: …; bỏ: …` soạn theo luật. Anh copy lệnh, sửa nếu cần, rồi Enter |
| 3 | Mốc giống bản terminal; reset bằng `SessionStart` (matcher `compact\|clear`), hoặc khi context tụt dưới ngưỡng |

Lệnh được soạn **không qua model** (không tốn token), từ những gì có trong transcript kể từ lần compact gần nhất:

| Phần | Nguồn |
| --- | --- |
| Tình trạng | `recap` của lần `wrap_up` gần nhất (do model viết sẵn) |
| Task còn dở | Mục `in_progress`/`pending` của task list (`update_plan` hoặc `TodoWrite`) sau lần `wrap_up` gần nhất |
| File chính | Tối đa 5 file được Edit/Write nhiều nhất |
| Bối cảnh | Message của 2 `git commit` gần nhất, `gitBranch` |

Hook không `block` và không gửi `additionalContext`, nên không chen message vào transcript, không đổi câu trả lời hay next-step box của Claude. Turn do side agent hay CI event kích hoạt cũng chỉ được nhắc khi đã dừng hẳn.

Script bỏ qua entrypoint `cli` (terminal đã có function hooks nhắc), nên không bị nhắc hai lần. Nó đọc `threshold`/`step` qua biến `CLAUDE_PLUGIN_OPTION_THRESHOLD`/`CLAUDE_PLUGIN_OPTION_STEP`, nếu không có thì dùng mặc định. Tắt bằng `COMPACT_NUDGE_HOOK_OFF=1`.

Khác bản terminal: lệnh soạn theo luật nên không biết các quyết định chỉ nói trong chat (không có trong recap hay task list), và không tự điền vào ô prompt được.

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
- Panel, band, toast và gợi ý trong ô prompt chỉ hiện trên terminal (`claude`). Desktop app không vẽ chúng; ở đó dùng bản command hook ở trên.
- Panel do plugin tự mở chỉ được vẽ khi terminal rộng từ 144 cột (110 cột nếu anh từng mở panel này bằng tay). Hẹp hơn thì plugin tự chuyển sang **band** phía trên ô prompt. Lệnh `/compact-nudge` mở lại panel ở mọi độ rộng khi đang có lời nhắc.
- Phím tắt `c`/`x` chỉ hoạt động khi panel đang giữ bàn phím (ô prompt trống hoặc Tab vào panel); đang gõ dở thì bấm chuột hoặc Tab.
- Nếu desktop vẫn nạp function hooks, `$.model.fork` có thể vẫn chạy ngầm ở mỗi mốc (khoảng $0.05) dù không ai thấy kết quả.
- `nudge.py` cần `python3` trong `PATH`. Thiếu `python3` thì hook bỏ qua, không chặn turn.
- Phần soạn lệnh dựa vào format transcript và tên tool của desktop (`mcp__ccd_turn__update_plan`, `mcp__ccd_turn__wrap_up`). App đổi format thì lệnh nghèo đi (rơi về mẫu chung) chứ không lỗi.
- **Lỗi im lặng:** nếu API function hooks đổi, hook lỗi chỉ bị bỏ qua (một dòng mờ trong transcript), session vẫn chạy bình thường nhưng lời nhắc sẽ không hiện nữa. Đã test trên Claude Code **2.1.292**; sau mỗi lần cập nhật Claude Code, hoặc khi thấy context vượt ngưỡng mà không được nhắc, chạy lại `claude plugin validate` và `claude plugin test` (mục Phát triển).

## Phát triển

```bash
claude plugin validate ./plugins/compact-nudge
claude plugin test ./plugins/compact-nudge
```
