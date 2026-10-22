# Quy ước mã hoá Lỗi Hệ thống & Phản hồi (Error Codes - ERR)

## 1. Định dạng chuẩn
`ERR-[MODULE]-[HTTP_STATUS]-[SEQ]`

- **MODULE**: Viết tắt module (vd: `AUTH`, `PAY`, `SYS`, `VAL`).
- **HTTP_STATUS**: 3 chữ số mã HTTP status code chuẩn (vd: `400`, `401`, `403`, `404`, `409`, `422`, `500`).
- **SEQ**: 2-3 chữ số phân biệt lỗi cụ thể.

*Ví dụ:*
- `ERR-AUTH-401-01`: Token phiên đăng nhập đã hết hạn hoặc không hợp lệ.
- `ERR-AUTH-403-02`: Tài khoản đang bị khóa do vi phạm chính sách bảo mật.
- `ERR-ORD-422-05`: Số lượng sản phẩm tồn kho không đủ để đặt hàng.

## 2. Cấu trúc Ma trận Lỗi (Error Matrix Entry)
| Mã ERR | HTTP Status | Thông báo hiển thị (End-User) | Thông báo kỹ thuật (Dev/Log) | Hướng xử lý đề xuất |
| :--- | :--- | :--- | :--- | :--- |
| `ERR-AUTH-401-01` | 401 | Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại. | JWT token expired signature | Chuyển hướng về màn hình Login. |
| `ERR-AUTH-422-01` | 422 | Email không đúng định dạng. | Validation failed: email invalid format | Focus vào input Email, hiển thị inline helper text đỏ. |
