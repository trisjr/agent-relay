# Quy chuẩn Use Case Specification (Alistair Cockburn Standard)

## Các trường cấu thành một Use Case chuẩn
- **Use Case ID**: `UC-[MODULE]-[SEQ]` (vd: `UC-AUTH-001`).
- **Tên Use Case**: Động từ + Danh từ (vd: `Đăng nhập hệ thống`).
- **Mức độ (Level)**: Sea level (Mục tiêu người dùng), Fish level (Sub-function), Kite level (Quy trình doanh nghiệp).
- **Tác nhân chính (Primary Actor)**: Vai trò người khởi tạo hành động (vd: `Khách hàng vãng lai`).
- **Các bên quan tâm & Kỳ vọng (Stakeholders & Interests)**: Các bên bị ảnh hưởng bởi kết quả.
- **Điều kiện tiên quyết (Pre-conditions)**: Trạng thái bắt buộc của hệ thống trước khi bắt đầu use case.
- **Điều kiện đảm bảo thành công (Post-conditions / Minimal Guarantees)**: Trạng thái hệ thống sau khi hoàn thành.
- **Kích hoạt (Trigger)**: Sự kiện khiến use case bắt đầu.
- **Luồng sự kiện chính (Main Success Scenario / Happy Path)**: Các bước tương tác tuần tự giữa Actor và System (1, 2, 3...).
- **Các luồng nhánh / Ngoại lệ (Extensions / Alternative Flows)**: Các điểm rẽ nhánh (vd: 3a. Mật khẩu không đúng -> Báo lỗi ERR-AUTH-401-01).
- **Quy tắc nghiệp vụ liên quan (Special Requirements / Business Rules)**: Trích dẫn `BR-xxx`.
