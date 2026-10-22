# Báo cáo Đánh giá Tác động Yêu cầu Thay đổi (Change Request Impact Report)

## Thông tin đề xuất CR
- **Mã CR**: `CR-2026-001`
- **Tên thay đổi**: Bổ sung xác thực 2 bước (2FA qua Google Authenticator TOTP)
- **Người yêu cầu**: Product Owner / Security Team
- **Ngày yêu cầu**: 2026-10-15
- **Mức độ khẩn cấp**: Cao (High)

---

## 1. Phân tích tác động chi tiết (Impact Analysis)
| Hạng mục | Mức độ tác động | Chi tiết các file / thành phần bị ảnh hưởng | Khối lượng ước tính (Effort) |
| :--- | :---: | :--- | :---: |
| **Tài liệu (SRS, Story, AC)** | Cao | Cập nhật `srs/spec.md` (thêm 3 FR, 2 BR, 3 ERR)<br>Thêm User Story `US-AUTH-05`<br>Sửa sơ đồ tuần tự `flows.md` | 1.5 ngày làm việc |
| **Cơ sở dữ liệu (Schema)** | Trung bình | Bảng `users` thêm 2 cột: `totp_secret` (VARCHAR encrypted), `is_2fa_enabled` (BOOLEAN) | 0.5 ngày làm việc |
| **API & Backend** | Cao | Thêm 2 endpoints mới: `/api/v1/auth/2fa/setup`, `/api/v1/auth/2fa/verify`<br>Sửa luồng login trả về pending 2fa token | 3 ngày làm việc |
| **Giao diện (Frontend UI)** | Trung bình | Thêm màn hình nhập mã OTP 6 số, màn hình quét mã QR trong Cài đặt bảo mật | 2 ngày làm việc |
| **Kiểm thử (QA/QC)** | Cao | Bổ sung 8 test cases mới (Happy, Wrong OTP, Expired OTP, Backup code) | 1.5 ngày làm việc |

## 2. Kế hoạch triển khai & Khuyến nghị
- **Khuyến nghị của BA**: Chấp thuận triển khai (Approved).
- **Phân bổ Sprint**: Đưa vào Sprint 3 cùng với đợt audit bảo mật tổng thể.
