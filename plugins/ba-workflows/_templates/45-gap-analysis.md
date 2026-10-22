# Báo cáo Phân tích Lỗ hổng Nghiệp vụ (Gap Analysis Report)

## 1. Tổng quan kiểm tra độ phủ
- **Phân hệ kiểm tra**: [Tên phân hệ / Feature]
- **Tài liệu đối chiếu**: SRS v1.0.0, User Story Backlog v1.0, Wireframe v1.0.
- **Ngày rà soát**: [YYYY-MM-DD]
- **BA kiểm định**: [Tên Agent / BA]

## 2. Bảng phát hiện Lỗ hổng & Điểm nghẽn (Identified Gaps)
| Gap ID | Phân loại | Vị trí phát hiện | Mô tả sự thiếu sót / Rủi ro | Tác động (Severity) | Giải pháp đề xuất |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `GAP-001` | Luồng ngoại lệ | Đăng nhập Google SSO | Chưa có phương án xử lý khi tài khoản Google không trả về email (chỉ trả sub ID) | High | Bắt buộc hiển thị pop-up yêu cầu bổ sung email trước khi kích hoạt |
| `GAP-002` | Dữ liệu biên | Form đăng ký | Chưa chặn trường hợp email có dấu tiếng Việt (vd: nguyễn@domain.vn) | Medium | Bổ sung hàm normalize chuẩn Punycode/RFC trước khi lưu |
| `GAP-003` | Trạng thái FSM | Hủy đơn hàng | Đơn hàng trạng thái `SHIPPING` chưa có quy tắc chặn nút Hủy từ phía người dùng | High | Thêm guard rule: Chỉ cho phép Hủy khi trạng thái là `NEW` hoặc `PAID` |
