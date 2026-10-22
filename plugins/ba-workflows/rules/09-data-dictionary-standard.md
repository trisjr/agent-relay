# Tiêu chuẩn Từ điển Dữ liệu (Data Dictionary Standard)

## Khung bảng đặc tả thực thể dữ liệu
Mỗi bảng hoặc collection phải có bảng đặc tả chi tiết:

| Tên trường (Logical) | Tên cột (Physical) | Kiểu dữ liệu | Độ dài | Cho phép Null? | Khóa (PK/FK) | Ràng buộc / Giá trị mặc định | Diễn giải nghiệp vụ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Mã người dùng | user_id | UUID | 36 | Không | PK | gen_random_uuid() | Định danh duy nhất toàn hệ thống |
| Email | email | VARCHAR | 255 | Không | Unique | Regex RFC 5322 | Email dùng để đăng nhập và thông báo |
| Mật khẩu mã hoá | password_hash | VARCHAR | 255 | Không | - | Chuẩn Argon2id | Mật khẩu đã được băm an toàn |
| Trạng thái | status | ENUM | - | Không | - | Default: PENDING | ACTIVE, INACTIVE, BANNED |
| Thời điểm tạo | created_at | TIMESTAMPTZ | - | Không | - | CURRENT_TIMESTAMP | Thời điểm tạo bản ghi |
