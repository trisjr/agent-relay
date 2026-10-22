# Tiêu chuẩn Yêu cầu Phi Chức năng (Non-Functional Requirements - NFR)

Áp dụng phân loại theo tiêu chuẩn quốc tế ISO/IEC 25010:

## 1. Hiệu năng & Khả năng đáp ứng (Performance Efficiency)
- **Response Time**: Thời gian phản hồi API P95 < 500ms cho các tác vụ tra cứu, < 1.5s cho tác vụ xử lý ghi/giao dịch.
- **Throughput**: Hệ thống chịu tải tối thiểu 1.000 TPS trong giờ cao điểm.
- **Capacity**: Cơ sở dữ liệu thiết kế đáp ứng tăng trưởng dữ liệu 3 năm không giảm quá 10% hiệu năng.

## 2. Bảo mật (Security)
- Toàn bộ giao tiếp mạng bắt buộc mã hóa TLS 1.3.
- Dữ liệu nhạy cảm (PII, mật khẩu, thông tin thẻ) phải được mã hóa at-rest (AES-256) và hash chuẩn Argon2id/Bcrypt.
- Tuân thủ OWASP Top 10: Chống SQL Injection, XSS, CSRF, IDOR.

## 3. Độ tin cậy & Sẵn sàng (Reliability & Availability)
- SLA sẵn sàng hoạt động (Uptime) tối thiểu 99.9% (cho phép gián đoạn tối đa 8.76 giờ/năm).
- Cơ chế sao lưu tự động hàng ngày (Daily snapshot) và khôi phục sự cố: RPO < 15 phút, RTO < 1 giờ.

## 4. Khả năng tương thích & Sử dụng (Usability & Compatibility)
- Giao diện chuẩn Responsive hoạt động tốt trên Mobile (iOS/Android) và Desktop.
- Chuẩn Accessibility tối thiểu WCAG 2.1 Level AA (độ tương phản màu >= 4.5:1, hỗ trợ phím tab).
