# Đặc tả Yêu cầu suy ra từ Mã nguồn (Code-derived SRS)

## 1. Thông tin phân tích (Overview)
- **Phân hệ**: [Tên phân hệ / Feature — vd: Xác thực]
- **Mã nguồn phân tích**: Branch `main`, commit `a1b2c3d` (ghi rõ hash tại thời điểm đọc code).
- **Điểm vào (entry points)**: [vd: `src/modules/auth/auth.controller.ts`]
- **Ngày phân tích**: [YYYY-MM-DD]
- **Đường dẫn lưu tài liệu**: `docs/{feature}/srs/code-derived-spec.md`
- **Lưu ý**: Tài liệu mô tả hành vi **đang chạy trong code**, chưa được Product xác nhận là hành vi mong muốn.

## 2. Bảng Yêu cầu Chức năng (Functional Requirements)
| Mã FR | Tên chức năng | Mô tả tóm tắt | Input | Output | BR tham chiếu | Mã lỗi | Trích dẫn code |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FR-AUTH-LGN-001` | Đăng nhập bằng Email/Pass | Xác thực email và mật khẩu, phát hành JWT | email, password | JWT token, user info | `BR-SEC-001` | `ERR-AUTH-401-01` | `auth.service.ts:70-112` |

## 3. Bảng Quy tắc Nghiệp vụ (Business Rules)
| Mã BR | Tên quy tắc | Lĩnh vực | Phát biểu điều kiện (When - Then) | Ngoại lệ | Trích dẫn code |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `BR-SEC-001` | Khóa đăng nhập sai | Bảo mật | KHI nhập sai quá 10 lần THÌ khóa tài khoản 5 phút | Không có | `auth.service.ts:87` |

## 4. Ma trận Mã Lỗi (Error Matrix)
| Mã ERR | HTTP Code | Điều kiện phát sinh | Thông báo trong code | Trích dẫn code | Ghi chú |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `ERR-AUTH-401-01` | 401 | Email hoặc mật khẩu không chính xác | "Invalid credentials" | `auth.service.ts:95` | — |
| `ERR-AUTH-500-01` | 500 | Exception chưa bắt khi tài khoản không tồn tại | (không có) | `auth.service.ts:102` | Code không trả mã lỗi nghiệp vụ — xem mục 5 |

## 5. Điểm cần xác nhận (Items to Confirm)
Hành vi mơ hồ, nghi là bug, magic number không rõ lý do, hoặc code không thể truy cập. BA / Product xác nhận trước khi đưa vào SRS chính thức.

| STT | Trích dẫn code | Quan sát | Câu hỏi cần xác nhận |
| :---: | :--- | :--- | :--- |
| 1 | `auth.service.ts:102` | Exception chưa bắt, trả HTTP 500 khi email không tồn tại | Đây là lỗi cần sửa hay hành vi chấp nhận được? |
