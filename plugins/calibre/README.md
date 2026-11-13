# calibre

Plugin chuẩn hóa vòng đời của một task từ lúc nhận yêu cầu tới lúc bàn giao: **intake → triage → specify → plan → implement → verify → review → handoff → closed**. Mỗi task là một GitHub issue, và label `state:*` trên issue luôn cho biết task đang ở bước nào.

Plugin không viết lại quy trình làm việc trong từng bước. Phần đó giao cho thư viện sẵn có (OpenSpec, superpowers) hoặc bản dự phòng đi kèm. Plugin giữ phần mà các thư viện đó không có: thứ tự các bước, cổng duyệt của người, bằng chứng kiểm chứng và trạng thái trên issue.

## Các skill

| Skill | Dùng khi | Làm gì |
| --- | --- | --- |
| `calibre:setup` | Lần đầu dùng trong một repo, hoặc sau khi cài, nâng cấp, gỡ một thư viện | Dò thư viện đang có → đề xuất ánh xạ vai trò sang thư viện → chốt chính sách → ghi `.calibre/config.json` → tạo label → đề xuất đoạn chỉ dẫn cho `CLAUDE.md`/`AGENTS.md`. Mỗi bước ghi ra ngoài đều chờ xác nhận |
| `calibre:run` | Chạy tiếp một task mà không cần gọi tên state, hoặc xem task đang ở đâu | Đọc state từ label → gọi skill của state đó → lặp lại cho tới cổng duyệt hoặc trạng thái chờ |
| `calibre:intake` | Đưa một yêu cầu hoặc issue chưa có label vào lifecycle | Ghi yêu cầu nguyên văn lên issue, gắn `state:intake` |
| `calibre:triage` | Issue ở `state:triage` | Phân loại track và size, kiểm tra trùng, đã làm, đã từ chối → đề xuất verdict → dừng ở G1 |
| `calibre:specify` | Issue ở `state:specify` | Giao thư viện viết spec; với `bug` là tìm nguyên nhân gốc, với `spike` là trả lời câu hỏi → cấp mã tiêu chí |
| `calibre:plan` | Issue ở `state:plan` | Giao thư viện lập plan → dựng bảng tiêu chí ứng với task → dừng ở G2 |
| `calibre:implement` | Issue ở `state:implement` | Giao thư viện thực thi theo plan đã duyệt → ghi việc đã làm và chỗ lệch plan |
| `calibre:verify` | Issue ở `state:verify` | Chạy lại từng kiểm tra trên code hiện tại → ghi lệnh, kết quả thật, commit. Không giao cho thư viện |
| `calibre:review` | Issue ở `state:review` | Giao thư viện review độc lập bản cuối → ghi phát hiện và kết luận |
| `calibre:handoff` | Issue ở `state:handoff` | Gộp spec, viết bản bàn giao, mở PR sau khi được đồng ý → dừng ở G3 |
| `calibre:close` | Đóng, hủy hoặc mở lại một task | Đổi label state sang `resolution:*`, đóng issue kèm lý do; mở lại thì về `triage` |
| `calibre:audit` | Một skill lifecycle chạy sai hoặc gây bất ngờ, hoặc muốn soát lại một lần chạy | Đọc lại hội thoại → đối chiếu với lịch sử label, record và commit → báo từng chỗ lệch kèm bằng chứng và nguyên nhân → đề xuất sửa và, nếu được đồng ý, tạo issue về repo của plugin. Không đổi label, record hay file skill |

Tên skill trùng với tên state, trừ `run`, `setup` và `audit` là ba skill đứng ngoài chín state. Trong Claude Code gọi bằng `/calibre:<tên>`, ví dụ `/calibre:triage`; README này viết tên skill theo dạng đó.

Mỗi skill theo state chỉ chạy khi issue đang đúng ở state đó; sai state thì nó báo task đang ở đâu và dừng. Gọi thẳng một skill state thì nó làm xong state đó rồi dừng; gọi `calibre:run` thì các state chạy nối tiếp. Quy tắc chung cho cả chín skill nằm ở `skills/run/references/rules.md`.

## Chín state

| State | Label | Bên thực hiện | Cổng duyệt |
| --- | --- | --- | --- |
| `intake` | `state:intake` | Plugin | |
| `triage` | `state:triage` | Plugin | G1: có làm không, theo track nào |
| `specify` | `state:specify` | Thư viện | |
| `plan` | `state:plan` | Thư viện | G2: spec và plan đã đúng chưa |
| `implement` | `state:implement` | Thư viện | |
| `verify` | `state:verify` | Plugin | |
| `review` | `state:review` | Thư viện | |
| `handoff` | `state:handoff` | Plugin | G3: kết quả được chấp nhận (mặc định là PR được merge) |
| `closed` | `resolution:*`, issue đóng | Plugin | |

Bốn track quyết định task đi qua những state nào:

- `feature` và `bug`: đủ chín state. Với `bug`, state `specify` tìm bước tái hiện và nguyên nhân gốc.
- `chore`: `intake` → `triage` → `implement` → `verify` → `handoff` → `closed`, dành cho thay đổi nhỏ không còn quyết định nào về hành vi.
- `spike`: `intake` → `triage` → `specify` → `closed` với resolution `answered`, dành cho câu hỏi và việc điều tra.

Task đang dừng thì có thêm label `wait:needs-info`, `wait:approval`, `wait:blocked` hoặc `wait:deferred` bên cạnh label state. Task đóng mang một trong bảy label `resolution:*` (`done`, `answered`, `duplicate`, `rejected`, `already-done`, `superseded`, `canceled`).

## Nguyên tắc chính

- **Chỉ script của plugin đổi label.** `skills/run/scripts/lifecycle.sh` kiểm tra bước chuyển có hợp lệ không rồi mới đổi, trong một lần sửa issue. Label lệch với bản ghi thì dừng lại hỏi.
- **Lời báo "xong" của thư viện không được tính.** Mỗi state có điều kiện ra kiểm được; plugin tự kiểm rồi mới chuyển state.
- **`verify` luôn do plugin làm.** Từng tiêu chí phải có lệnh đã chạy, kết quả thật và commit. Bằng chứng gắn với code: code đổi thì phải kiểm lại.
- **Plugin tự lưu đầu ra của thư viện** vào `.calibre/tasks/<issue>/` trên nhánh của task, vì nhiều thư viện chỉ để review và ghi chú trong hội thoại hoặc file tạm.
- **Tiêu chí chấp nhận có mã riêng** (`AC-1`, `AC-2`…) do plugin cấp, dùng xuyên suốt plan, bằng chứng và bàn giao.
- **Thao tác ra bên ngoài phải được đồng ý.** Tạo issue, mở PR, đóng issue vì lý do chưa được quyết và xóa nhánh đều hỏi mỗi lần. Plugin không tự merge PR.

## Thư viện được hỗ trợ

Sáu vai trò (`specify`, `plan`, `implement`, `review`, `diagnose`, `explore`) được ánh xạ sang `openspec`, `superpowers` hoặc `builtin` trong `.calibre/config.json`.

| Thư viện | Phiên bản adapter viết theo | Vai trò đảm nhận |
| --- | --- | --- |
| OpenSpec | 2.0 | `specify`, `plan`, `explore`, `implement` |
| superpowers | 7.0.2 | `implement`, `review`, `diagnose`, `specify`, `plan` |
| `builtin` | đi kèm plugin | cả sáu, ở mức tối thiểu |

Bộ kết hợp mặc định khi có cả hai: OpenSpec cho `specify`, `plan`, `explore`; superpowers cho `implement`, `review`, `diagnose`.

Thêm thư viện khác là thêm một file adapter trong `skills/run/references/providers/` và một giá trị trong cấu hình; các skill theo state không phải sửa.

## Giới hạn hiện tại

- **Chưa chạy thử từ đầu đến cuối.** Adapter được viết từ việc đọc mã nguồn của OpenSpec 2.0 và superpowers 7.0.2. Điểm nối giữa plan của OpenSpec và bước thực thi của superpowers chưa được kiểm chứng bằng một lần chạy thật.
- **Chỉ hỗ trợ GitHub Issues**, qua GitHub CLI (`gh`) đã đăng nhập.
- **superpowers cần đoạn chỉ dẫn trong `CLAUDE.md`/`AGENTS.md`** để dừng đúng ở ranh giới state; `calibre:setup` đề xuất đoạn này. Không có nó thì các skill của superpowers có thể chạy quá phạm vi một state.
- **Chưa có bộ eval** cho các skill.
- **`calibre:audit` chưa được kiểm chứng.** Danh sách chỗ lệch nó tìm được suy ra từ quy tắc của lifecycle, chưa phải từ lỗi gặp trong một lần chạy thật. Nó chỉ soát được phần hội thoại còn trong phiên: state chạy ở phiên khác hoặc đã bị nén thì báo là chưa soát.
- Script label mới được chạy ngoại tuyến: bảng chuyển state qua `lifecycle.sh can` và `lifecycle.sh can-close`, và từng lệnh với một `gh` giả lập chỉ ghi lại lời gọi. Chưa chạy với GitHub thật.

## Theo từng platform

- **Claude Code** và các agent đọc `SKILL.md`: dùng mười hai skill trong `skills/`.
- **Cursor** không đọc `SKILL.md` của plugin; rule `.cursor/rules/calibre.mdc` tóm tắt các quy tắc bắt buộc và trỏ tới file `SKILL.md` của từng state. Rule này cần thư mục `skills/` của plugin có trên máy vì nó gọi script label.
- **Codex, Gemini CLI, Kimi Code, Qoder**: có manifest theo quy ước của repo, nhưng plugin chưa được chạy thử trên các platform này.

## Cài đặt

Claude Code:

```text
/plugin install calibre@agent-relay
```

Các platform khác (Codex, Kimi Code) xem mục "Cài từ bản local" trong [README gốc](../../README.md) của repo.

Sau khi cài, chạy `calibre:setup` một lần trong repo cần dùng.
