# Quy ước mã hoá các Thực thể Tài liệu Nghiệp vụ (Artifact Identifier Conventions)

Tài liệu này chuẩn hóa các mã định danh đang được sử dụng trong `_templates/` nhưng chưa có quy ước riêng (US, AC, FEAT, PER, NFR, SCR, BRN, CHK, GAP, DRIFT, CR, DEC, AI, MM). Tài liệu **không thay thế** các rule đã ban hành: FR (Rule 01), BR (Rule 02), ERR (Rule 03), UC (Rule 06), TC (Rule 14 và quy ước tại `_templates/43-test-cases.md`), DOC/DIAG trong metadata frontmatter (Rule 18).

## 1. Nguyên tắc chung
- Mỗi thực thể nghiệp vụ mang đúng một mã định danh, bất biến trong suốt vòng đời; mã đã gán **không được tái sử dụng** cho thực thể khác kể cả khi thực thể gốc bị loại bỏ.
- Cấu trúc chung: `[PREFIX]-[SCOPE]-[SEQ]` — PREFIX viết hoa 2-5 ký tự; SCOPE là MODULE / CATEGORY / năm YYYY (tùy loại mã); SEQ là số thứ tự có padding số 0.
- **MODULE**: dùng chung bộ viết tắt với Rule 01 — viết hoa 2-4 ký tự (vd: `AUTH`, `ORD`, `PAY`) và phải nhất quán trong toàn bộ dự án.
- Khi trích dẫn chéo giữa các tài liệu, luôn dùng dạng đầy đủ của mã (không viết tắt thiếu SCOPE).

### Bảng tra nhanh toàn bộ mã định danh trong BA-Kit
| Mã | Thực thể | Định dạng | Rule quy định |
| :--- | :--- | :--- | :--- |
| FR | Yêu cầu chức năng | `FR-[MODULE]-[FEATURE]-[SEQ]` | Rule 01 |
| BR | Quy tắc nghiệp vụ | `BR-[DOMAIN]-[SEQ]` | Rule 02 |
| ERR | Mã lỗi hệ thống | `ERR-[MODULE]-[HTTP_STATUS]-[SEQ]` | Rule 03 |
| NFR | Yêu cầu phi chức năng | `NFR-[CATEGORY]-[SEQ]` | Rule 20 (mục 2), phân loại theo Rule 04 |
| UC | Use Case | `UC-[MODULE]-[SEQ]` | Rule 06 |
| US | User Story | `US-[MODULE]-[SEQ]` | Rule 20 (mục 3) |
| AC | Acceptance Criteria | `AC-[MODULE]-[SEQ]` / `AC-[SEQ]` | Rule 20 (mục 4), cú pháp theo Rule 08 |
| TC | Test Case | `TC-[MODULE]-[SEQ]` | Rule 14 & `_templates/43-test-cases.md` |
| FEAT | Tính năng sản phẩm | `FEAT-[SEQ]` | Rule 20 (mục 5) |
| PER | Persona | `PER-[SEQ]` | Rule 20 (mục 5) |
| SCR | Màn hình | `SCR-[MODULE]-[SEQ]` | Rule 20 (mục 6) |
| BRN | Nhánh nghiệp vụ | `BRN-[MODULE]-[SEQ]` | Rule 20 (mục 7) |
| CHK | Kịch bản checklist | `CHK-[MODULE]-[SEQ]` | Rule 20 (mục 7) |
| GAP | Lỗ hổng nghiệp vụ | `GAP-[SEQ]` | Rule 20 (mục 8) |
| DRIFT | Sai lệch tài liệu / code | `DRIFT-[SEQ]` | Rule 20 (mục 8) |
| CR | Yêu cầu thay đổi | `CR-[YYYY]-[SEQ]` | Rule 20 (mục 9), quy trình theo Rule 15 |
| DEC | Quyết định nghiệp vụ | `DEC-[YYYY]-[SEQ]` | Rule 20 (mục 9) |
| AI | Action Item | `AI-[YYYY]-[SEQ]` | Rule 20 (mục 9) |
| MM | Biên bản cuộc họp | `MM-[YYYY]-[SEQ]` | Rule 20 (mục 9) |
| DOC / DIAG | Tài liệu / Sơ đồ (metadata) | `DOC-[TYPE]-[MODULE]-[SEQ]`, `DIAG-[TYPE]-[MODULE]-[SEQ]` | Rule 18 |

## 2. Mã Yêu cầu Phi Chức năng (NFR)
### Định dạng chuẩn
`NFR-[CATEGORY]-[SEQ]`

- **CATEGORY**: 3-4 ký tự viết hoa viết tắt nhóm chất lượng theo ISO/IEC 25010 (Rule 04): `PERF` (Hiệu năng), `SEC` (Bảo mật), `REL` (Độ tin cậy & Sẵn sàng), `USA` (Tương thích & Sử dụng).
- **SEQ**: Số thứ tự 3 chữ số, đánh lại từ `001` trong phạm vi từng CATEGORY.

*Ví dụ (theo `_templates/08-srs.md`):*
- `NFR-PERF-001`: Thời gian phản hồi API tác vụ tra cứu P95 < 500ms.
- `NFR-SEC-001`: Bắt buộc TLS 1.3 cho toàn bộ kết nối.
- `NFR-REL-001`: SLA sẵn sàng hoạt động tối thiểu 99.9%.

## 3. Mã User Story (US)
### Định dạng chuẩn
`US-[MODULE]-[SEQ]`

- **MODULE**: Viết tắt phân hệ theo Rule 01 (vd: `AUTH`, `ORD`).
- **SEQ**: Số thứ tự 2 chữ số bắt đầu từ `01`, đánh số liên tục trong phạm vi module.

*Ví dụ (theo `_templates/27-userstory.md`):*
- `US-AUTH-01`: Đăng nhập bằng email và mật khẩu.
- `US-AUTH-02`: Đăng nhập nhanh bằng tài khoản Google (SSO).
- `US-ORD-05`: Áp dụng mã giảm giá khi thanh toán.

## 4. Mã Tiêu chí Chấp nhận (AC)
### Định dạng chuẩn
`AC-[MODULE]-[SEQ]` (dạng đầy đủ) hoặc `AC-[SEQ]` (dạng rút gọn)

- **Dạng đầy đủ `AC-[MODULE]-[SEQ]`**: Bắt buộc khi truy vết chéo tài liệu (Backlog, RTM, Test Checklist, báo cáo Drift). SEQ 2 chữ số, đánh số **liên tục trong phạm vi module, không reset theo Story**.
- **Dạng rút gọn `AC-[SEQ]`**: Chỉ dùng nội bộ trong phạm vi một tài liệu Story (đặc tả Gherkin, bộ test case của riêng Story đó), đánh lại từ `01` cho mỗi Story (quy ước tại `_templates/43-test-cases.md`).
- Mỗi Story bắt buộc tối thiểu 03 AC theo Rule 08 (Happy Path, Negative, Edge/Boundary & Security).

*Ví dụ (theo `_templates/27-userstory.md` và `_templates/43-test-cases.md`):*
- `US-AUTH-01` -> `AC-AUTH-01` (Happy Path), `AC-AUTH-02` (Sai pass 5 lần); `US-AUTH-02` -> `AC-AUTH-03` (OAuth Flow) — đánh số liên tục theo module.
- Trong tài liệu riêng của Story `US-AUTH-01`: `AC-01`, `AC-02`, `AC-03` — đánh lại từ 01.

## 5. Mã Tính năng (FEAT) & Chân dung Người dùng (PER) — phạm vi PRD
### Định dạng chuẩn
`FEAT-[SEQ]` và `PER-[SEQ]`

- **FEAT**: Không gắn MODULE vì một tính năng sản phẩm có thể trải rộng nhiều phân hệ; SEQ 3 chữ số bắt đầu từ `001`, phạm vi toàn sản phẩm. Một FEAT được phân rã thành nhiều FR (Rule 01) khi sang giai đoạn đặc tả.
- **PER**: SEQ 2 chữ số bắt đầu từ `01`; mã Persona được trích dẫn trong bảng Feature Breakdown để nêu đối tượng phục vụ.

*Ví dụ (theo `_templates/01-prd.md`):*
- `FEAT-001`: Xác thực (Auth) — Đăng nhập Email & Google, phục vụ `PER-01`, `PER-02`.
- `PER-01`: Persona nhóm người dùng chính — hành vi công nghệ: Mobile 80%, Desktop 20%.

## 6. Mã Màn hình (SCR)
### Định dạng chuẩn
`SCR-[MODULE]-[SEQ]`

- **MODULE**: Viết tắt phân hệ sở hữu màn hình (vd: `AUTH`, `HOME`).
- **SEQ**: Số thứ tự 2 chữ số; cho phép bắt đầu từ `00` cho màn hình khởi động / splash, các màn còn lại đánh từ `01`.

*Ví dụ (theo `_templates/29-user-flow.md`):*
- `SCR-AUTH-00`: Splash.
- `SCR-AUTH-01`: Đăng nhập; `SCR-AUTH-02`: Quên mật khẩu; `SCR-AUTH-03`: Tài khoản tạm khóa.
- `SCR-HOME-01`: Dashboard.

Mọi node màn hình trong sơ đồ User Flow và mọi khung wireframe đều phải mang mã SCR để truy vết ngược về FR/US/UC.

## 7. Mã Nhánh nghiệp vụ (BRN) & Kịch bản Checklist (CHK)
### 7.1. Nhánh nghiệp vụ (BRN)
`BRN-[MODULE]-[SEQ]`

- **SEQ**: Số thứ tự 2 chữ số bắt đầu từ `01`.
- Mỗi nhánh rẽ ra từ SRS / User Story (liệt kê tại mục Business Branches của Test Scenario Checklist) phải mang một mã BRN, truy vết rõ nguồn `FR-xxx` / `BR-xxx` / `US-xxx`, và có ít nhất 01 kịch bản kiểm thử tương ứng.

*Ví dụ (theo `_templates/42-test-checklist.md`):*
- `BRN-AUTH-01`: Đăng nhập thành công bằng email + mật khẩu hợp lệ (nguồn `FR-AUTH-LGN-001` / `US-AUTH-01`).
- `BRN-AUTH-03`: Khóa tài khoản 15 phút sau 5 lần nhập sai liên tiếp (nguồn `BR-SEC-001` / `US-AUTH-01`).

### 7.2. Kịch bản Checklist (CHK)
`CHK-[MODULE]-[SEQ]`

- **SEQ**: Số thứ tự 3 chữ số bắt đầu từ `001` (đồng bộ độ dài với mã TC).
- Mã CHK dành cho các mục kịch bản trong Test Scenario Checklist khi đội dự án muốn tách lớp checklist khỏi test case chi tiết; khi một mục checklist được viết thành test case, gán mã TC (Rule 14) và ghi truy vết `CHK-xxx -> TC-xxx`.
- Không dùng lẫn CHK và TC cho cùng một mục checklist. Checklist hiện hữu trong BA-Kit (`_templates/42-test-checklist.md`) dùng trực tiếp mã TC làm Checklist ID — cách này vẫn hợp lệ và không cần chuyển đổi.

## 8. Mã Lỗ hổng (GAP) & Sai lệch Tài liệu (DRIFT)
### Định dạng chuẩn
`GAP-[SEQ]` và `DRIFT-[SEQ]`

- **SEQ**: Số thứ tự 3 chữ số, đánh lại từ `001` trong phạm vi một báo cáo (một lần rà soát Gap Analysis hoặc một lần kiểm định Doc Drift).
- Vì SEQ reset theo báo cáo, khi trích dẫn GAP/DRIFT từ tài liệu khác (biên bản họp, checklist) phải nêu kèm báo cáo nguồn (vd: *Báo cáo Gap Analysis ngày 2026-10-22 — `GAP-001`*).

*Ví dụ (theo `_templates/45-gap-analysis.md` và `_templates/46-doc-drift.md`):*
- `GAP-001`: Chưa có phương án xử lý khi tài khoản Google không trả về email (chỉ trả sub ID).
- `GAP-003`: Đơn hàng trạng thái `SHIPPING` chưa có quy tắc chặn nút Hủy.
- `DRIFT-001`: Code cho phép 10 lần sai và chỉ khóa 5 phút, trong khi `BR-SEC-002` quy định 5 lần / 15 phút.
- `DRIFT-004`: API `POST /api/v1/auth/reset-password` có trong spec nhưng chưa tồn tại trong code.

## 9. Nhóm mã gắn năm: CR, DEC, AI, MM
### Định dạng chuẩn
`[PREFIX]-[YYYY]-[SEQ]`

- **YYYY**: Năm phát sinh (vd: `2026`).
- **SEQ**: Số thứ tự 3 chữ số, đánh lại từ `001` vào đầu mỗi năm, đánh liên tục trong năm cho từng loại mã.

### Ý nghĩa từng mã
- **CR (Change Request)**: Yêu cầu thay đổi nghiệp vụ. Mọi CR bắt buộc có Báo cáo Phân tích Tác động 4 góc độ (Rule 15) trước khi phê duyệt.
- **DEC (Decision)**: Quyết định nghiệp vụ chính thức được chốt trong cuộc họp; quyết định làm thay đổi phạm vi đã chốt phải đi kèm đánh giá tác động theo Rule 15.
- **AI (Action Item)**: Công việc bàn giao phát sinh từ biên bản; vòng đời `Assigned -> InProgress -> Done -> Verified` (quá hạn chuyển `Overdue`) theo `_templates/48-meeting-minutes.md`.
- **MM (Meeting Minutes)**: Mã của chính tài liệu biên bản cuộc họp; các mã DEC/AI phát sinh trong biên bản phải truy vết được về mã MM này.

*Ví dụ (theo `_templates/47-change-request.md` và `_templates/48-meeting-minutes.md`):*
- `CR-2026-001`: Bổ sung xác thực 2 bước (2FA qua Google Authenticator TOTP).
- `MM-2026-001`: Biên bản chốt phạm vi Sprint 3 — Phân hệ Xác thực & Đặt hàng.
- `DEC-2026-003`: Chấp thuận `CR-2026-001`, triển khai trong Sprint 3.
- `AI-2026-001`: Cập nhật SRS v1.1.0 theo `DEC-2026-001`, `DEC-2026-002` — Owner: BA, deadline 2026-10-24.

## 10. Chuỗi truy vết giữa các mã (Traceability Chain)
Mọi mã phải nằm trong ít nhất một liên kết truy vết hai chiều:

- Luồng yêu cầu: `FEAT-xxx` -> `FR-xxx` -> `UC-xxx` / `US-xxx` -> `AC-xxx` -> `BRN-xxx` / `CHK-xxx` -> `TC-xxx`; với `BR-xxx`, `ERR-xxx`, `NFR-xxx`, `SCR-xxx` chi phối / bổ trợ ở từng bước.
- Luồng kiểm định & thay đổi: `GAP-xxx` / `DRIFT-xxx` -> `MM-xxx` -> `DEC-xxx` -> (`CR-xxx`) -> `AI-xxx` -> cập nhật lại `FR` / `BR` / `US` / `AC` / `TC` bị ảnh hưởng.

Một mã không tham gia bất kỳ liên kết truy vết nào được coi là mồ côi (orphan) và phải rà soát lại trong các đợt Gap Analysis (mục 8).
