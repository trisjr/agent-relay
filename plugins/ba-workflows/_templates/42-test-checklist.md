# Bảng Kiểm tra Kịch bản Kiểm thử (Test Scenario Checklist)

## 1. Thông tin tổng quan (Overview)
- **Phân hệ / Feature**: Xác thực người dùng (Authentication)
- **Tài liệu nguồn**: SRS v1.0.0, User Story Backlog v1.0, Đặc tả Use Case `UC-AUTH-001`
- **Đường dẫn lưu trữ**: `docs/auth/test/checklist.md`
- **Ngày lập**: 2026-10-22
- **BA phụ trách**: [Tên BA]
- **QA đối ứng**: [Tên QA]

## 2. Phạm vi & Nhánh nghiệp vụ cần kiểm thử (Business Branches)
Tổng hợp toàn bộ nhánh nghiệp vụ rẽ ra từ SRS và User Story — mỗi nhánh phải có ít nhất 01 kịch bản kiểm thử ở Mục 3.

| Branch ID | Nguồn truy vết | Mô tả nhánh nghiệp vụ | Độ ưu tiên |
| :--- | :--- | :--- | :---: |
| `BRN-AUTH-01` | `FR-AUTH-LGN-001` / `US-AUTH-01` | Đăng nhập thành công bằng email + mật khẩu hợp lệ (Happy Path) | P0 |
| `BRN-AUTH-02` | `FR-AUTH-LGN-001` / `US-AUTH-01` | Đăng nhập thất bại: sai mật khẩu, đếm `failed_attempts` | P0 |
| `BRN-AUTH-03` | `BR-SEC-001` / `US-AUTH-01` | Khóa tài khoản 15 phút sau 5 lần nhập sai liên tiếp | P0 |
| `BRN-AUTH-04` | `FR-AUTH-LGN-002` / `US-AUTH-02` | Đăng nhập Google SSO, kể cả trường hợp Google không trả về email | P1 |
| `BRN-AUTH-05` | `FR-AUTH-LGN-001` / `US-AUTH-01` | Validate dữ liệu đầu vào phía client trước khi gọi API | P1 |

## 3. Checklist kịch bản theo chiều kiểm thử (Test Dimensions)
Mọi tiêu chí đạt phải **đo lường được**, tuyệt đối không dùng từ ngữ mơ hồ ("nhanh", "thân thiện", "bảo mật cao") theo Rule 16.

### 3.1 Functional (Chức năng)
| Checklist ID | Kịch bản kiểm thử | Tiêu chí đạt (đo lường được) | Truy vết | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| `TC-AUTH-001` | Đăng nhập thành công với email + mật khẩu đúng | Hệ thống trả 200 OK kèm Access Token (TTL 15 phút) và Refresh Token (TTL 7 ngày); chuyển hướng tới Dashboard | `BRN-AUTH-01` / `AC-AUTH-01` | Sẵn sàng test |
| `TC-AUTH-002` | Đăng nhập sai mật khẩu lần 1 → 4 | Trả 401 kèm `ERR-AUTH-401-01`; hiển thị "Email hoặc mật khẩu không chính xác."; counter `failed_attempts` tăng đúng 1 đơn vị mỗi lần | `BRN-AUTH-02` / `AC-AUTH-02` | Sẵn sàng test |
| `TC-AUTH-003` | Nhập sai mật khẩu lần thứ 5 liên tiếp | Tài khoản chuyển trạng thái tạm khóa 15 phút (`ERR-AUTH-423-01`); nút "Đăng nhập" bị vô hiệu hóa kèm đồng hồ đếm ngược 15:00 | `BRN-AUTH-03` / `AC-AUTH-02` | Sẵn sàng test |
| `TC-AUTH-004` | Đăng nhập Google SSO thành công | Hoàn tất OAuth flow và sinh JWT session trong tối đa 2 bước redirect | `BRN-AUTH-04` / `AC-AUTH-03` | Sẵn sàng test |

### 3.2 UI/UX (Giao diện & Trải nghiệm)
| Checklist ID | Kịch bản kiểm thử | Tiêu chí đạt (đo lường được) | Truy vết | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| `TC-AUTH-005` | Hiển thị lỗi validate inline khi email sai định dạng | Lỗi `ERR-AUTH-422-01` hiển thị ngay dưới ô nhập liệu sau khi blur, không reload trang; người dùng sửa được trong 1 lần nhập lại | `BRN-AUTH-05` | Sẵn sàng test |
| `TC-AUTH-006` | Luồng đăng nhập end-to-end trên mobile | Người dùng hoàn thành đăng nhập trong tối đa 3 thao tác chạm (nhập email → nhập mật khẩu → nhấn nút); bàn phím ảo không che ô nhập liệu ở màn hình 375px | `BRN-AUTH-01` | Sẵn sàng test |

### 3.3 Performance (Hiệu năng)
| Checklist ID | Kịch bản kiểm thử | Tiêu chí đạt (đo lường được) | Truy vết | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| `TC-AUTH-007` | Đo thời gian phản hồi API đăng nhập dưới tải | Thời gian phản hồi API `POST /api/v1/auth/login` đạt P95 dưới 500ms với 500 CCU | `BRN-AUTH-01` | Sẵn sàng test |

### 3.4 Security (Bảo mật)
| Checklist ID | Kịch bản kiểm thử | Tiêu chí đạt (đo lường được) | Truy vết | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| `TC-AUTH-008` | Kiểm tra lưu trữ mật khẩu trong CSDL | Mật khẩu được băm bằng Argon2id; không tồn tại bản ghi nào lưu plaintext hoặc hash MD5/SHA1 | `BR-SEC-001` | Sẵn sàng test |
| `TC-AUTH-009` | Kiểm tra giới hạn tần suất request (Rate Limit) | API đăng nhập chặn request thứ 11 trong cùng 1 phút từ 1 IP, trả 429 kèm mã `ERR-AUTH-429-01` | `BRN-AUTH-03` | Sẵn sàng test |

### 3.5 Boundary Data (Dữ liệu biên)
| Checklist ID | Kịch bản kiểm thử | Tiêu chí đạt (đo lường được) | Truy vết | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| `TC-AUTH-010` | Nhập email ở độ dài biên (1 ký tự và 254 ký tự) | Email 1 ký tự bị từ chối với `ERR-AUTH-422-01`; email 254 ký tự hợp lệ được chấp nhận; email 255 ký tự bị từ chối | `BRN-AUTH-05` | Sẵn sàng test |
| `TC-AUTH-011` | Nhập email chứa ký tự Unicode tiếng Việt | Email dạng `nguyễn@domain.vn` bị từ chối ở client-side với thông báo `ERR-AUTH-422-01`, không gọi API | `BRN-AUTH-05` | Sẵn sàng test |
| `TC-AUTH-012` | Nhập mật khẩu để trống hoặc toàn khoảng trắng | Nút "Đăng nhập" bị vô hiệu hóa; không phát sinh request nào tới API | `BRN-AUTH-05` | Sẵn sàng test |

## 4. Ma trận Truy vết Yêu cầu (Requirement Traceability Matrix)
Đảm bảo 100% FR được kiểm thử bởi ít nhất 01 Test Case (Rule 14).

| FR ID | Tên Yêu cầu Chức năng | User Story ID | Acceptance Criteria | Test Case ID | Loại kiểm thử | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FR-AUTH-LGN-001` | Đăng nhập Email/Pass | `US-AUTH-01` | `AC-AUTH-01` (Happy Path) | `TC-AUTH-001` | Functional / UI | Sẵn sàng test |
| `FR-AUTH-LGN-001` | Đăng nhập Email/Pass | `US-AUTH-01` | `AC-AUTH-02` (Sai pass 5 lần) | `TC-AUTH-002`, `TC-AUTH-003` | Security / BR | Sẵn sàng test |
| `FR-AUTH-LGN-002` | Đăng nhập Google SSO | `US-AUTH-02` | `AC-AUTH-03` (OAuth Flow) | `TC-AUTH-004` | Integration | Sẵn sàng test |

## 5. Biên bản Thống nhất Phạm vi BA & QA (Alignment Sign-off)
Kết quả buổi review sớm về độ phủ kiểm thử trước khi viết test case chi tiết.

| Vai trò | Họ tên | Ngày review | Kết quả | Ý kiến / Yêu cầu bổ sung |
| :--- | :--- | :--- | :--- | :--- |
| BA phụ trách | [Tên BA] | 2026-10-22 | Đồng ý | Checklist phủ kín 5/5 nhánh nghiệp vụ P0/P1 |
| QA Lead | [Tên QA] | 2026-10-22 | Đồng ý có điều kiện | Bổ sung kịch bản SSO khi Google không trả về email (liên quan `GAP-001`) trước khi viết test case chi tiết |
| Product Owner | [Tên PO] | 2026-10-22 | Chờ review | — |

## 6. Lịch sử sửa đổi (Revision History)
| Phiên bản | Ngày | Người thực hiện | Tóm tắt thay đổi |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 2026-10-22 | [Tên BA] | Khởi tạo checklist cho phân hệ Xác thực |
