# Product Requirements Document (PRD)

## Metadata
- **Product Name**: [Tên Sản phẩm]
- **Document Version**: 1.0.0
- **Status**: Draft | In Review | Approved
- **Product Owner**: [Tên PO]
- **Lead BA**: [Tên Lead BA]
- **Last Updated**: [YYYY-MM-DD]

---

## 1. Tầm nhìn & Mục tiêu sản phẩm (Vision & Objectives)
### 1.1 Tuyên ngôn sứ mệnh (Product Vision Statement)
[Mô tả sản phẩm giải quyết nỗi đau gì, cho ai, và tạo ra sự khác biệt gì so với thị trường]

### 1.2 Mục tiêu kinh doanh (Business Goals - OKRs / KPIs)
- **Mục tiêu 1 (O1)**: [Mục tiêu định lượng] -> **KR**: [Chỉ số đo lường]
- **Mục tiêu 2 (O2)**: [Mục tiêu định lượng] -> **KR**: [Chỉ số đo lường]

## 2. Đối tượng mục tiêu & Chân dung người dùng (Target Audience & Personas)
| Persona ID | Vai trò / Nhóm người dùng | Mục tiêu chính | Nỗi đau hiện tại (Pain points) | Hành vi công nghệ |
| :--- | :--- | :--- | :--- | :--- |
| `PER-01` | [Tên Persona 1] | [Mục tiêu] | [Nỗi đau] | Mobile 80%, Desktop 20% |
| `PER-02` | [Tên Persona 2] | [Mục tiêu] | [Nỗi đau] | Desktop công sở |

## 3. Phạm vi sản phẩm (Product Scope)
### 3.1 Nằm trong phạm vi (In-Scope)
- [Phân hệ / Tính năng 1]
- [Phân hệ / Tính năng 2]

### 3.2 Nằm ngoài phạm vi (Out-of-Scope)
- [Tính năng chưa làm trong phase này]

## 4. Bóc tách danh mục tính năng (Feature Breakdown)
| Feature ID | Phân hệ (Module) | Tên tính năng | Mức độ ưu tiên | Persona phục vụ | Mô tả vắn tắt |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FEAT-001` | Xác thực (Auth) | Đăng nhập Email & Google | P0 (Must) | PER-01, PER-02 | Hỗ trợ 2 phương thức xác thực |
| `FEAT-002` | Đơn hàng (Order) | Tạo đơn và thanh toán | P0 (Must) | PER-01 | Thanh toán thẻ và QR ví |

## 5. Giả định & Ràng buộc (Assumptions & Constraints)
- **Giả định**: Người dùng đã có sẵn email hoặc tài khoản Google cá nhân.
- **Ràng buộc**: Thời hạn go-live MVP trong vòng 6 tuần.
