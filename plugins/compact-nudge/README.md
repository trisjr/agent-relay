# compact-nudge

Plugin cho **Claude Code**. Khi context của session vượt một ngưỡng token, plugin nhắc người dùng chạy `/compact` và soạn sẵn lệnh `/compact <những gì cần giữ lại>` dựa trên chính cuộc hội thoại. Plugin **không bao giờ tự compact**: người dùng quyết định.

## Bối cảnh

Mỗi lượt, Claude Code gửi lại toàn bộ context. Context càng lớn thì mỗi lượt càng tốn, kể cả khi prompt cache hit gần 100%: tiền đọc cache tỉ lệ thuận với độ dài context. Audit thực tế trên khoảng 21.000 API call cho thấy:

- khoảng **51% chi phí** nằm ở các call có context trên 200K token;
- người dùng có compact thủ công, nhưng **thường quá muộn** (trung vị khoảng 300K);
- sau compact, context còn khoảng 15–18K token, nên một lần compact hoà vốn sau 3–5 lượt.

Vì vậy đòn bẩy lớn nhất là compact **đúng lúc**, chứ không phải đổi model. Plugin này nhắc đúng lúc đó.

## Cách hoạt động

Plugin có hai đường, **chỉ một đường chạy** trong mỗi session:

- **Module function hooks** (`hooks/register.tsx`): chạy khi session có surface vẽ được UI, tức terminal (`claude`) và Code tab của desktop app. Khi `session.start`/`session.attach` thấy có surface, module đặt biến `COMPACT_NUDGE_MODULE=1` cho process.
- **Command hook** (`hooks/nudge.py`): fallback cho mọi trường hợp còn lại, gồm Claude Code chưa có function hooks, `claude -p` và SDK host. Nếu thấy `COMPACT_NUDGE_MODULE=1`, script thoát ngay, nên không có chuyện nhắc hai lần.

### Mốc nhắc

Mốc đầu tiên là `threshold` (mặc định 200K), sau đó cứ mỗi `step` lại có một mốc mới: 200K → 300K → 400K… Mỗi mốc chỉ nhắc một lần. Nếu một turn lớn nhảy thẳng tới 262K thì plugin nhắc ở 262K, và mốc kế tiếp vẫn là 300K.

Mốc reset về `threshold` trong ba trường hợp: sau một lần compact thật, sau `/clear`, hoặc khi context tụt dưới ngưỡng (ví dụ sau rewind). Hai loại compact sau **không** làm reset: `precompute` (chạy nền, không thay đổi gì) và compact bị hook khác chặn (`skip`).

Với model hoặc compaction window nhỏ (ví dụ window 200K), ngưỡng tự hạ xuống **80% window**, để lời nhắc kịp đến trước auto-compact (khoảng window − 33K).

### Trên terminal và desktop (module)

| Bước | Làm gì |
| --- | --- |
| 1 | Sau mỗi turn của session chính (bỏ qua subagent và turn bị huỷ), đọc `$.session.usage()` để lấy số token context. Lời gọi này miễn phí |
| 2 | Chạm mốc thì hiện toast và mở **panel** `Compact`. Panel tự mở được vẽ khi terminal rộng từ 144 cột (110 cột nếu đã từng mở panel này bằng tay); hẹp hơn thì hiện thành **band** phía trên ô prompt. Hệ thống kiểm tra panel đã được vẽ hay chưa ngay lúc vẽ, nên khi kéo rộng terminal, band nhường chỗ cho panel |
| 3 | Gọi `$.model.fork` trên transcript đang được cache để soạn một dòng `/compact giữ lại: …; bỏ: …`. Fork không dùng được tool, không ghi vào transcript. Chi phí khoảng $0.05 ở mốc 262K trên Opus 5.5, tăng tuyến tính theo context (khoảng $0.08 ở mốc 400K) |
| 4 | Panel có hai nút **[Điền lệnh]** (phím `c`) và **[Bỏ qua]** (phím `x`). Điền lệnh đưa lệnh vào ô prompt khi ô đang trống; nếu ô đang có chữ thì không ghi đè mà hiện toast hướng dẫn. Đóng panel bằng tay hoặc Esc cũng tính là bỏ qua. Khi soạn xong, lệnh cũng hiện thành gợi ý mờ trong ô prompt, bấm Tab để lấy |
| 5 | Bỏ qua trong lúc fork đang soạn thì khi soạn xong sẽ không gợi ý nữa. Fork lỗi thì panel báo không soạn được, không gợi ý một `/compact` trống |

Lệnh `/compact-nudge` mở lại lời nhắc gần nhất, kể cả khi đã bỏ qua, ở mọi độ rộng terminal.

Lệnh fork soạn ra được dặn **giữ** cả các hướng đã thử và lý do loại, để sau compact Claude không thử lại cách đã thất bại. Phần **bỏ** chỉ gồm output/log dài đã xử lý xong.

### Khi không có module (command hook)

| Bước | Làm gì |
| --- | --- |
| 1 | Khi turn của session chính kết thúc (`Stop`), đọc usage của assistant message cuối trên **nhánh hiện tại** của transcript `.jsonl` (đi theo `parentUuid`, nên các nhánh đã rewind bị bỏ qua). Bỏ qua subagent và row có usage bằng 0, và không đọc lùi qua `compact_boundary`. Nếu call có nhiều `usage.iterations` (server-side tool loop, advisor), chỉ tính iteration thật cuối cùng |
| 2 | Chạm mốc thì hiện **một `systemMessage`** ("Claude Code notice") kèm lệnh `/compact giữ lại: …; bỏ: …` soạn theo luật. Người dùng copy lệnh, sửa nếu cần rồi Enter |

Lệnh được soạn **không qua model** (không tốn token) từ những nguồn sau:

| Phần | Nguồn |
| --- | --- |
| Tình trạng | `recap` của lần `wrap_up` gần nhất kể từ lần compact cuối |
| Task còn dở | Mục `in_progress`/`pending` của task list (`TaskCreate`/`TaskUpdate`, `TodoWrite` hoặc `update_plan`). Task list được giữ qua các lần compact |
| File chính | Tối đa 5 file được Edit/Write nhiều nhất; file trùng tên thì ghi kèm thư mục cha |
| Bối cảnh | Subject của 2 `git commit` thành công gần nhất (hiểu được kiểu heredoc `-m "$(cat <<'EOF' …)"`, `-am`, `--message=`), cùng `gitBranch` |

Script đọc tối đa 64MB cuối của transcript, nên ở các mốc 300–400K lệnh soạn vẫn còn đủ thông tin. Hook không `block` và không gửi `additionalContext`, nên không chen message vào transcript, cũng không đổi câu trả lời hay next-step box của Claude.

Script đọc `threshold`/`step` qua `CLAUDE_PLUGIN_OPTION_THRESHOLD`/`CLAUDE_PLUGIN_OPTION_STEP`, compaction window qua `CLAUDE_CODE_AUTO_COMPACT_WINDOW` nếu có. Output luôn là JSON ASCII, nên trên Windows không vướng code page của console. Tắt bằng `COMPACT_NUDGE_HOOK_OFF=1`.

## Cấu hình

Chỉnh trong `/config`, mục `compact-nudge`:

| Field | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `threshold` | `200000` | Mốc nhắc đầu tiên (token context). Bị hạ xuống 80% window nếu window nhỏ hơn |
| `step` | `100000` | Khoảng cách giữa các mốc nhắc tiếp theo |

Giá trị không hợp lệ (≤ 0, không phải số) sẽ quay về mặc định. Tăng `threshold` có hiệu lực ngay ở turn kế tiếp. Với task cần giữ nhiều chi tiết (debug dài, refactor nhiều file), nên tăng `threshold` lên khoảng 250K, hoặc bấm **Bỏ qua** để chờ mốc sau.

## Cài đặt

```text
/plugin marketplace add trisjr/agent-relay
/plugin install compact-nudge@agent-relay
```

## Giới hạn

- Chỉ chạy trên **Claude Code**. Module dùng function hooks (early access, API có thể đổi giữa các bản). Các manifest Codex/Gemini/Qoder/Kimi chỉ có để marketplace hợp lệ, không có hành vi.
- Giao diện và lệnh soạn sẵn bằng tiếng Việt.
- Command hook cần `python3`, `python` hoặc `py -3` trong `PATH` (thử lần lượt). Thiếu cả ba thì hook bỏ qua, không chặn turn.
- Command hook không biết window của model, nên chỉ tự hạ ngưỡng khi có `CLAUDE_CODE_AUTO_COMPACT_WINDOW`. Với model 200K, nên đặt `threshold` khoảng 160000.
- Phần soạn lệnh của command hook dựa vào format transcript và tên tool. Nếu Claude Code đổi format, lệnh soạn ra sẽ nghèo đi (rơi về mẫu chung) chứ không lỗi. Lệnh soạn theo luật nên không biết các quyết định chỉ được nói trong chat.
- **Lỗi im lặng:** nếu API function hooks đổi, hook lỗi chỉ bị bỏ qua (một dòng mờ trong transcript); session vẫn chạy bình thường nhưng lời nhắc sẽ không hiện nữa. Đã test trên Claude Code **2.1.312**. Sau mỗi lần cập nhật Claude Code, hoặc khi thấy context vượt ngưỡng mà không được nhắc, hãy chạy lại các lệnh ở mục Phát triển.

## Phát triển

```bash
claude plugin validate ./plugins/compact-nudge
claude plugin test ./plugins/compact-nudge
python3 plugins/compact-nudge/hooks/test_nudge.py
```
