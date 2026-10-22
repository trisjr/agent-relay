# Bộ lọc Ngôn từ Mơ hồ trong Yêu cầu Kỹ thuật (Ambiguity Filter)

BA chuyên nghiệp không bao giờ sử dụng các tính từ mang tính chủ quan, không đo đếm được.

## Bảng từ ngữ cấm & Cách chuẩn hóa:
| Từ ngữ mơ hồ (CẤM DÙNG) | Lý do từ chối | Cách chuẩn hóa kỹ thuật (ĐƯỢC DUYỆT) |
| :--- | :--- | :--- |
| "Hệ thống phải phản hồi nhanh chóng" | Không có tiêu chí đo lường cụ thể | Thời gian phản hồi API P95 phải dưới 500ms với 500 CCU |
| "Giao diện phải thân thiện, dễ dùng" | Định tính, tùy cảm nhận cá nhân | Người dùng hoàn thành tác vụ đặt hàng trong tối đa 3 bước click |
| "Hệ thống phải có tính bảo mật cao" | Vô nghĩa về mặt kiểm thử | Mật khẩu mã hóa Argon2id, áp dụng Rate Limit 10 req/min/IP |
| "Hỗ trợ tệp tin có dung lượng vừa phải" | Dev không biết giới hạn validate | Cho phép upload tệp PDF/JPG/PNG dung lượng tối đa 10MB |
| "Xử lý hầu hết các loại lỗi" | Không phủ kín edge case | Có mã lỗi ERR xác định cho toàn bộ mã phản hồi HTTP 4xx và 5xx |
