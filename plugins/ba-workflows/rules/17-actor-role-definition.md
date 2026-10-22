# Chuẩn định nghĩa Actor và Ma trận Phân quyền (RBAC Matrix)

## 1. Phân loại Actor
- **Primary Actor (Tác nhân chính)**: Người trực tiếp tương tác với hệ thống để đạt mục đích.
- **Secondary Actor (Tác nhân hỗ trợ)**: Tham gia hỗ trợ thực hiện quy trình (CSKH, Shipper).
- **System / Automated Actor**: Các dịch vụ bên ngoài hoặc cron job hệ thống.

## 2. Ma trận phân quyền RBAC chuẩn
| Chức năng / Tài nguyên | Guest | Registered User | Staff / Support | Admin | Super Admin |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Xem danh mục sản phẩm | View | View | View | View | Full |
| Tạo đơn hàng | - | Create | Create on behalf | Create | Full |
| Xem đơn hàng của mình | - | View | - | - | Full |
| Xem mọi đơn hàng hệ thống | - | - | View | View / Edit | Full |
| Khóa tài khoản người dùng | - | - | - | Lock | Full |
