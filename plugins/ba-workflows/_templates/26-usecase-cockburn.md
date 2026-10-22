# Đặc tả Use Case Chi tiết (Alistair Cockburn Format)

## UC-AUTH-001: Đăng nhập Hệ thống bằng Email và Mật khẩu

- **Tác nhân chính (Primary Actor)**: Người dùng đã đăng ký tài khoản.
- **Phạm vi (Scope)**: Cổng thông tin Web / Mobile App.
- **Cấp độ (Level)**: Sea Level (Mục tiêu người dùng).
- **Các bên liên quan & Kỳ vọng**:
  - Người dùng: Đăng nhập an toàn, nhanh chóng, giữ phiên đăng nhập.
  - Bộ phận An ninh: Ngăn chặn brute-force và đánh cắp thông tin.
- **Tiền điều kiện (Pre-conditions)**:
  - Người dùng đã có tài khoản và ở trạng thái Hoạt động (`ACTIVE`).
  - Người dùng đang ở trang Đăng nhập.
- **Hậu điều kiện (Post-conditions)**:
  - Hệ thống sinh phiên làm việc hợp lệ và lưu log đăng nhập.
  - Người dùng được chuyển hướng vào trang chủ hoặc trang yêu cầu trước đó.
- **Kích hoạt (Trigger)**: Người dùng nhấn nút "Đăng nhập".

### Luồng sự kiện chính (Main Success Scenario)
1. Người dùng nhập Email và Mật khẩu.
2. Người dùng nhấn nút "Đăng nhập".
3. Hệ thống kiểm tra định dạng email và độ dài mật khẩu.
4. Hệ thống truy vấn thông tin tài khoản theo Email.
5. Hệ thống kiểm tra mật khẩu khớp với hash đã lưu.
6. Hệ thống reset bộ đếm lần đăng nhập sai về 0.
7. Hệ thống tạo Access Token và Refresh Token.
8. Hệ thống lưu cookie bảo mật và chuyển hướng người dùng đến Dashboard.

### Các luồng nhánh & Ngoại lệ (Extensions / Alternative Flows)
- **3a. Dữ liệu nhập không hợp lệ (Email sai định dạng, mật khẩu để trống)**:
  - 3a1. Hệ thống hiển thị thông báo lỗi inline dưới ô nhập liệu (`ERR-AUTH-422-01`).
  - 3a2. Use case quay lại bước 1.
- **5a. Email không tồn tại hoặc Mật khẩu không chính xác**:
  - 5a1. Hệ thống tăng bộ đếm đăng nhập sai `failed_attempts` thêm 1.
  - 5a2. Hệ thống trả về thông báo lỗi chung: "Email hoặc mật khẩu không chính xác" (`ERR-AUTH-401-01`).
  - 5a3. Nếu `failed_attempts >= 5`: Hệ thống khóa tài khoản 15 phút (`BR-SEC-001`), hiển thị thông báo `ERR-AUTH-423-01`.
- **5b. Tài khoản đang bị Khóa / Vô hiệu hóa**:
  - 5b1. Hệ thống hiển thị thông báo tài khoản bị khóa và liên kết liên hệ CSKH (`ERR-AUTH-403-02`).
