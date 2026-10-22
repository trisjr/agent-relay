# Quy ước mã hoá Yêu cầu Chức năng (Functional Requirements - FR)

## 1. Định dạng chuẩn
Mã FR phải tuân theo cấu trúc phân cấp:
`FR-[MODULE]-[FEATURE]-[SEQ]`

- **MODULE**: Viết hoa 2-4 ký tự viết tắt của phân hệ (vd: `AUTH`, `ORD`, `PAY`, `PROD`, `USER`, `RPT`).
- **FEATURE**: Viết hoa 2-4 ký tự đại diện cho tính năng con (vd: `LGN`, `REG`, `CHKT`, `SRCH`).
- **SEQ**: Số thứ tự 3 chữ số bắt đầu từ `001` đến `999`.

*Ví dụ:*
- `FR-AUTH-LGN-001`: Đăng nhập bằng Email và Mật khẩu.
- `FR-AUTH-LGN-002`: Đăng nhập thông qua Google SSO (OAuth2).
- `FR-ORD-CHKT-001`: Áp dụng mã giảm giá khi thanh toán.

## 2. Các trường bắt buộc cho mỗi FR
| Thuộc tính | Kiểu dữ liệu | Mô tả |
| :--- | :--- | :--- |
| **Mã FR** | String | Mã duy nhất theo chuẩn định dạng trên |
| **Tên yêu cầu** | String | Tên ngắn gọn dạng động từ + tân ngữ |
| **Độ ưu tiên** | Enum | P0 (Must have), P1 (Should have), P2 (Nice to have) |
| **Mô tả chi tiết** | Markdown | Mô tả hành vi hệ thống, input, processing, output |
| **Business Rules** | Reference | Danh sách các BR-xxx chi phối yêu cầu này |
| **Mã lỗi liên quan** | Reference | Danh sách các ERR-xxx có thể phát sinh |
