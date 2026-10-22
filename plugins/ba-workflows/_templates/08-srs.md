# Tài liệu Đặc tả Yêu cầu Kỹ thuật (SRS Master)

## 1. Giới thiệu (Introduction)
- **Tên dự án**: [Project Name]
- **Mục tiêu tài liệu**: Đặc tả toàn diện hành vi chức năng, phi chức năng và ràng buộc kỹ thuật của hệ thống.
- **Tiêu chuẩn áp dụng**: IEEE Std 830-1998 / ISO/IEC/IEEE 29148.

## 2. Bảng Yêu cầu Chức năng (Functional Requirements)
| Mã FR | Tên chức năng | Phân loại | Mô tả tóm tắt | Input | Output | BR tham chiếu | Mã lỗi |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `FR-AUTH-LGN-001` | Đăng nhập bằng Email/Pass | P0 | Xác thực người dùng bằng email và mật khẩu | email, password | JWT token, user info | `BR-SEC-001` | `ERR-AUTH-401-01` |
| `FR-AUTH-LGN-002` | Đăng nhập bằng Google SSO | P0 | Xác thực OAuth2 qua Google Cloud | google_id_token | JWT token, user info | `BR-SEC-003` | `ERR-AUTH-400-02` |

## 3. Bảng Quy tắc Nghiệp vụ (Business Rules Matrix)
| Mã BR | Tên quy tắc | Lĩnh vực | Phát biểu điều kiện (When - Then) | Ngoại lệ |
| :--- | :--- | :--- | :--- | :--- |
| `BR-SEC-001` | Khóa đăng nhập sai | Bảo mật | KHI nhập sai quá 5 lần THÌ khóa tài khoản 15 phút | Admin có quyền unlock thủ công |
| `BR-SEC-002` | Thời hạn phiên token | Bảo mật | Access Token sống 15 phút, Refresh Token sống 7 ngày | Thu hồi ngay nếu đổi mật khẩu |

## 4. Ma trận Mã Lỗi (Error Matrix)
| Mã ERR | HTTP Code | Điều kiện phát sinh | Localization Key | Thông báo người dùng | Severity | Hành động khuyến nghị |
| :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| `ERR-AUTH-401-01` | 401 | Email hoặc mật khẩu không chính xác | `error.auth.invalid_credentials` | "Email hoặc mật khẩu không đúng." | Medium | Yêu cầu nhập lại hoặc bấm Quên mật khẩu |
| `ERR-AUTH-423-01` | 423 | Tài khoản bị tạm khóa do brute-force | `error.auth.account_locked` | "Tài khoản bị tạm khóa 15 phút do nhập sai nhiều lần." | High | Đợi hết thời gian đếm ngược hoặc liên hệ hỗ trợ |

## 5. Yêu cầu Phi Chức năng (Non-Functional Requirements)
| Nhóm NFR | Mã NFR | Chỉ tiêu | Giá trị định lượng |
| :--- | :--- | :--- | :--- |
| Hiệu năng & Khả năng đáp ứng | `NFR-PERF-001` | Thời gian phản hồi API tác vụ tra cứu | P95 < 500ms |
| Hiệu năng & Khả năng đáp ứng | `NFR-PERF-002` | Khả năng chịu tải giờ cao điểm | Tối thiểu 1.000 TPS |
| Bảo mật | `NFR-SEC-001` | Mã hóa giao tiếp mạng | Bắt buộc TLS 1.3 cho toàn bộ kết nối |
| Bảo mật | `NFR-SEC-002` | Mã hóa dữ liệu nhạy cảm lưu trữ | AES-256 (at-rest), hash mật khẩu chuẩn Argon2id |
| Độ tin cậy & Sẵn sàng | `NFR-REL-001` | SLA sẵn sàng hoạt động (Uptime) | Tối thiểu 99.9% (gián đoạn tối đa 8.76 giờ/năm) |
| Độ tin cậy & Sẵn sàng | `NFR-REL-002` | Khôi phục sự cố | RPO < 15 phút, RTO < 1 giờ |
| Khả năng tương thích & Sử dụng | `NFR-USA-001` | Accessibility | Đạt chuẩn WCAG 2.1 Level AA (độ tương phản >= 4.5:1) |
| Khả năng tương thích & Sử dụng | `NFR-USA-002` | Tương thích thiết bị | Responsive đầy đủ trên iOS/Android và Desktop |
