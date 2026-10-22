# Báo cáo Đối chiếu Sai lệch Tài liệu – Mã nguồn (Document vs Source Code Drift Audit)

## 1. Thông tin kiểm định (Audit Overview)
- **Phân hệ kiểm định**: [Tên phân hệ / Feature — vd: Xác thực & Đặt hàng]
- **Tài liệu đối chiếu**: SRS v1.0.0, User Story Backlog v1.0, Đặc tả Use Case (Cockburn) v1.0.
- **Mã nguồn kiểm định**: Branch `main`, commit `a1b2c3d` (ghi rõ hash tại thời điểm audit).
- **Ngày kiểm định**: [YYYY-MM-DD]
- **BA kiểm định**: [Tên Agent / BA]
- **Đường dẫn lưu báo cáo**: `docs/{feature}/doc-drift-report.md`

## 2. Bảng Đối chiếu Yêu cầu – Hiện thực (FR vs Code Reconciliation)
Trạng thái hiện thực chỉ nhận một trong 4 giá trị: `Đã hiện thực`, `Hiện thực một phần`, `Sai lệch`, `Chưa hiện thực`.

| FR ID | Tên Yêu cầu Chức năng | User Story | Module / Source code hiện thực | Trạng thái hiện thực | Ghi chú truy vết |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `FR-AUTH-LGN-001` | Đăng nhập Email/Password | `US-AUTH-01` | `src/modules/auth/auth.service.ts` | Sai lệch | Xem `DRIFT-001`, `DRIFT-005` |
| `FR-AUTH-LGN-002` | Đăng nhập Google SSO (OAuth2) | `US-AUTH-02` | `src/modules/auth/google.strategy.ts` | Sai lệch | Xem `DRIFT-002` |
| `FR-AUTH-RST-001` | Gửi link đặt lại mật khẩu qua email | `US-AUTH-03` | — (không tìm thấy route `/auth/reset-password`) | Chưa hiện thực | Xem `DRIFT-004` |
| `FR-ORD-CHKT-001` | Áp dụng mã giảm giá khi thanh toán | `US-ORD-05` | `src/modules/order/voucher.service.ts` | Hiện thực một phần | Xem `DRIFT-003` |
| `FR-ORD-CHKT-002` | Hoàn voucher khi đơn bị hủy | `US-ORD-06` | `src/modules/order/cancel.service.ts` | Đã hiện thực | Khớp spec, không có drift |

## 3. Danh sách Sai lệch Hành vi (Behavioral Drift Findings)
Phân loại sai lệch: `Hành vi khác Spec` / `Validation lỏng hơn BR` / `Validation chặt hơn BR` / `Tính năng chưa xây` / `Tính năng ngoài Spec`.
Mức độ: `Critical` (chặn luồng nghiệp vụ chính hoặc lỗ hổng bảo mật) — `High` (sai kết quả nghiệp vụ có thật) — `Medium` (sai lệch luồng ngoại lệ) — `Low` (khác biệt hiển thị, thông báo).

| Drift ID | Phân loại | Tham chiếu | Vị trí code | Tài liệu quy định | Code hiện thực | Mức độ | Đề xuất xử lý |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `DRIFT-001` | Validation lỏng hơn BR | `FR-AUTH-LGN-001`, `BR-SEC-002` | `auth.service.ts:87` | Khóa tài khoản 15 phút sau 5 lần nhập sai mật khẩu liên tiếp | Code cho phép 10 lần sai và chỉ khóa 5 phút | High | Sửa code theo `BR-SEC-002` (5 lần / 15 phút); bổ sung `TC-AUTH-002` vào regression |
| `DRIFT-002` | Hành vi khác Spec | `FR-AUTH-LGN-002`, `UC-AUTH-002` | `google.strategy.ts:41` | Khi Google không trả về email, hệ thống phải hiển thị pop-up yêu cầu bổ sung email trước khi kích hoạt | Code tự động tạo tài khoản với trường email rỗng và kích hoạt ngay | High | Sửa code chặn kích hoạt khi email null; nếu Product chấp nhận hành vi mới thì cập nhật SRS kèm `CR-xxx` |
| `DRIFT-003` | Validation chặt hơn BR | `FR-ORD-CHKT-001`, `BR-PROMO-001` | `voucher.service.ts:58` | Voucher giảm giá áp dụng cho mọi đơn hàng, không ràng buộc giá trị tối thiểu | Code từ chối voucher khi đơn dưới 100.000đ (hardcode, không có BR nào quy định) | Medium | BA xác nhận với Product: bổ sung `BR-PROMO-002` về giá trị đơn tối thiểu, hoặc gỡ hardcode |
| `DRIFT-004` | Tính năng chưa xây | `FR-AUTH-RST-001`, `US-AUTH-03` | — | Có API `POST /api/v1/auth/reset-password` gửi link đặt lại mật khẩu, TTL link 15 phút | Không tồn tại route, service và migration liên quan | Critical | Đưa vào sprint kế tiếp; tạm ẩn nút "Quên mật khẩu" trên UI để tránh lỗi 404 |
| `DRIFT-005` | Hành vi khác Spec | `FR-AUTH-LGN-001`, `ERR-AUTH-401-01` | `auth.service.ts:102` | Sai email hoặc mật khẩu trả HTTP 401 kèm mã `ERR-AUTH-401-01` | Code ném exception chưa bắt, trả HTTP 500 không kèm mã ERR | Medium | Map exception về `ERR-AUTH-401-01`; bổ sung test case luồng lỗi |

## 4. Kiểm tra Độ phủ Truy vết (Traceability Snapshot — Rule 14)
Mọi FR trong phạm vi audit phải có ít nhất 01 Test Case; FR thiếu Test Case được gắn cờ `THIẾU TC`.

| FR ID | User Story | Acceptance Criteria | Test Case | Trạng thái truy vết |
| :--- | :--- | :--- | :--- | :--- |
| `FR-AUTH-LGN-001` | `US-AUTH-01` | `AC-AUTH-01`, `AC-AUTH-02` | `TC-AUTH-001`, `TC-AUTH-002` | Đủ phủ |
| `FR-AUTH-LGN-002` | `US-AUTH-02` | `AC-AUTH-03` | `TC-AUTH-003` | Đủ phủ |
| `FR-AUTH-RST-001` | `US-AUTH-03` | `AC-AUTH-04` | — | THIẾU TC (chưa có Test Case do tính năng chưa xây) |
| `FR-ORD-CHKT-001` | `US-ORD-05` | `AC-ORD-07` | `TC-ORD-011` | Đủ phủ |
| `FR-ORD-CHKT-002` | `US-ORD-06` | `AC-ORD-08` | `TC-ORD-012` | Đủ phủ |

## 5. Lọc Ngôn từ Mơ hồ phát hiện trong Tài liệu (Ambiguity Check — Rule 16)
Các câu văn mơ hồ phát hiện khi đối chiếu phải được chuẩn hóa trước khi ra quyết định sửa code hay sửa spec.

| Vị trí tài liệu | Câu văn mơ hồ (CẤM) | Chuẩn hóa kỹ thuật (ĐỀ XUẤT) |
| :--- | :--- | :--- |
| SRS v1.0.0, mục 3.2.1 | "Hệ thống đăng nhập phải phản hồi nhanh chóng" | Thời gian phản hồi API `POST /api/v1/auth/login` P95 dưới 500ms với 500 CCU |
| SRS v1.0.0, mục 3.2.3 | "Khóa tài khoản khi người dùng nhập sai nhiều lần" | Tài khoản bị tạm khóa 15 phút nếu nhập sai mật khẩu liên tiếp 5 lần (`BR-SEC-002`) |

## 6. Kết luận & Kiến nghị (Verdict & Recommendations)
| Chỉ số tổng hợp | Số lượng |
| :--- | :---: |
| Tổng số FR rà soát | 5 |
| Đã hiện thực đúng Spec | 1 |
| Sai lệch hành vi / validation | 3 |
| Hiện thực một phần | 1 |
| Chưa hiện thực | 1 |
| Drift mức Critical / High / Medium / Low | 1 / 2 / 2 / 0 |

- **Kết luận**: Mã nguồn **chưa khớp** tài liệu đặc tả; không đủ điều kiện đóng gói release cho đến khi xử lý xong `DRIFT-001`, `DRIFT-002`, `DRIFT-004`.
- **Kiến nghị thứ tự xử lý**: (1) `DRIFT-004` chặn release — xử lý đầu tiên; (2) `DRIFT-001`, `DRIFT-002` liên quan bảo mật — xử lý trong sprint hiện tại; (3) `DRIFT-003`, `DRIFT-005` — BA xác nhận với Product rồi quyết định sửa code hay cập nhật tài liệu kèm Change Request.
- **Hành động truy vết**: bổ sung `TC-AUTH-004` cho `FR-AUTH-RST-001` ngay khi tính năng được xây dựng; tái kiểm định (re-audit) sau khi toàn bộ drift mức Critical/High được đóng.

## 7. Lịch sử sửa đổi (Revision History)
| Phiên bản | Ngày | Người thực hiện | Tóm tắt thay đổi |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2026-10-15 | BA-Kit Generator | Khởi tạo biểu mẫu chuẩn |
