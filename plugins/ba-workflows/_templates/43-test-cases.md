# Bộ Kịch bản Kiểm thử Chi tiết (Test Cases Specification)

## 1. Thông tin tổng quan
- **Phân hệ kiểm thử**: Xác thực người dùng (Authentication)
- **Tài liệu đầu vào**: SRS v1.0.0 (`FR-AUTH-LGN-001`, `FR-AUTH-LGN-002`), User Story Backlog (`US-AUTH-01`, `US-AUTH-02`), Acceptance Criteria (Gherkin BDD), Test Checklist phân hệ Auth.
- **Ngày lập**: [YYYY-MM-DD]
- **BA phụ trách**: [Tên Agent / BA]
- **Mục tiêu**: Chuyển hóa 100% Acceptance Criteria, mã lỗi `ERR-xxx` và quy tắc `BR-xxx` đã khai báo thành Test Case thực thi được, truy vết hai chiều theo Rule 14. Mỗi User Story có tối thiểu 03 loại kịch bản: Thành công (Happy Path), Lỗi nghiệp vụ (Negative) và Biên / Giới hạn (Edge / Boundary) theo Rule 08.

## 2. Quy ước định danh & phân loại
| Đối tượng | Định dạng | Ví dụ |
| :--- | :--- | :--- |
| Test Case | `TC-{MODULE}-{NNN}` | `TC-AUTH-001` |
| Yêu cầu chức năng | `FR-{MODULE}-{FLOW}-{NNN}` | `FR-AUTH-LGN-001` |
| User Story | `US-{MODULE}-{NN}` | `US-AUTH-01` |
| Acceptance Criteria | `AC-{NN}` (trong phạm vi một Story) | `AC-01` |
| Business Rule | `BR-{DOMAIN}-{NNN}` | `BR-SEC-001` |
| Mã lỗi | `ERR-{MODULE}-{HTTP}-{NN}` | `ERR-AUTH-401-01` |

- **Loại kiểm thử**: Functional / UI, Security / BR, Integration, Boundary.
- **Trạng thái**: Sẵn sàng test / Đang thực thi / Passed / Failed / Blocked.
- **Ngôn ngữ kết quả mong đợi**: bắt buộc đo lường được (số lần gọi API, mã HTTP, thời gian đếm ngược, ngưỡng khóa), cấm tính từ mơ hồ theo Rule 16.

## 3. Bảng chỉ mục Test Case (Test Case Index)
| Test Case ID | Story ID | AC | Mục tiêu kiểm thử | Loại | Ưu tiên | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `TC-AUTH-001` | `US-AUTH-01` | AC-01 | Đăng nhập thành công bằng email/mật khẩu hợp lệ (Happy Path) | Functional / UI | P0 | Sẵn sàng test |
| `TC-AUTH-002` | `US-AUTH-01` | AC-02 | Khóa tài khoản 15 phút sau 5 lần nhập sai mật khẩu liên tiếp (Negative) | Security / BR | P0 | Sẵn sàng test |
| `TC-AUTH-003` | `US-AUTH-02` | AC-01 | Đăng nhập thành công qua Google SSO (Happy Path) | Integration | P0 | Sẵn sàng test |
| `TC-AUTH-004` | `US-AUTH-01` | AC-03 | Từ chối email sai định dạng RFC 5322 ngay tại client (Edge / Boundary) | Boundary | P1 | Sẵn sàng test |
| `TC-AUTH-005` | `US-AUTH-02` | AC-02 | Từ chối Google id_token hết hạn hoặc sai chữ ký (Negative) | Integration | P1 | Sẵn sàng test |

## 4. Đặc tả chi tiết Test Case

### TC-AUTH-001 — Đăng nhập thành công bằng email và mật khẩu hợp lệ
- **Liên kết**: Story `US-AUTH-01` | AC-01 | FR nguồn `FR-AUTH-LGN-001` | Loại: Functional / UI | Ưu tiên: P0
- **Tiền điều kiện (Preconditions)**:
  1. Tài khoản `alex@example.com` tồn tại, trạng thái `ACTIVE`, bộ đếm `failed_attempts = 0`.
  2. Người dùng chưa có phiên đăng nhập nào trên trình duyệt hiện tại.
- **Dữ liệu kiểm thử (Test Data)**:

  | Trường | Giá trị |
  | :--- | :--- |
  | email | `alex@example.com` |
  | password | `Secret@123` |

- **Các bước thực thi (Test Steps)**:

  | Bước | Hành động | Dữ liệu đầu vào | Kết quả mong đợi từng bước |
  | :---: | :--- | :--- | :--- |
  | 1 | Mở màn hình Đăng nhập | — | Hiển thị form gồm ô email, ô mật khẩu và nút "Đăng nhập" đang bật |
  | 2 | Nhập email | `alex@example.com` | Ô email chấp nhận giá trị, không hiển thị lỗi định dạng |
  | 3 | Nhập mật khẩu | `Secret@123` | Ký tự mật khẩu bị che dạng dấu chấm |
  | 4 | Nhấn nút "Đăng nhập" | — | Frontend gọi `POST /api/v1/auth/login` đúng 01 lần |
  | 5 | Quan sát phản hồi API | — | API trả về `200 OK` kèm Access Token (TTL 15 phút) và Refresh Token (TTL 7 ngày) đúng `BR-SEC-002` |
  | 6 | Quan sát điều hướng | — | Hệ thống chuyển đến Dashboard, header hiển thị tên "Alex" và avatar cá nhân |

- **Kết quả mong đợi cuối cùng (Expected Results)**:
  - Hệ thống tạo phiên đăng nhập mới; bộ đếm `failed_attempts` được reset về `0`.
  - Thời gian phản hồi API P95 dưới 500ms ở tải 500 CCU; không hiển thị bất kỳ mã lỗi nào.

### TC-AUTH-002 — Khóa tài khoản sau 5 lần nhập sai mật khẩu liên tiếp
- **Liên kết**: Story `US-AUTH-01` | AC-02 | FR nguồn `FR-AUTH-LGN-001` | BR `BR-SEC-001` | Loại: Security / BR | Ưu tiên: P0
- **Tiền điều kiện (Preconditions)**:
  1. Tài khoản `alex@example.com` tồn tại, trạng thái `ACTIVE`.
  2. Bộ đếm `failed_attempts = 4` (đã nhập sai 4 lần liên tiếp trước đó).
- **Dữ liệu kiểm thử (Test Data)**:

  | Trường | Giá trị |
  | :--- | :--- |
  | email | `alex@example.com` |
  | password (sai) | `WrongPass123` |

- **Các bước thực thi (Test Steps)**:

  | Bước | Hành động | Dữ liệu đầu vào | Kết quả mong đợi từng bước |
  | :---: | :--- | :--- | :--- |
  | 1 | Mở màn hình Đăng nhập | — | Hiển thị form đăng nhập bình thường |
  | 2 | Nhập email và mật khẩu sai lần thứ 5 | `alex@example.com` / `WrongPass123` | Form chấp nhận giá trị |
  | 3 | Nhấn nút "Đăng nhập" | — | API trả về `423 Locked` kèm mã `ERR-AUTH-423-01` |
  | 4 | Quan sát giao diện | — | Hiển thị "Tài khoản bị tạm khóa 15 phút do nhập sai nhiều lần." và nút "Đăng nhập" bị vô hiệu hóa kèm đồng hồ đếm ngược 15:00 |
  | 5 | Thử đăng nhập lại với mật khẩu đúng trong thời gian khóa | `Secret@123` | API vẫn trả về `423 Locked` (`ERR-AUTH-423-01`), không tạo phiên |

- **Kết quả mong đợi cuối cùng (Expected Results)**:
  - Tài khoản chuyển sang trạng thái tạm khóa đúng 15 phút theo `BR-SEC-001`; bộ đếm `failed_attempts` dừng ở `5`.
  - Sau khi đếm ngược kết thúc, người dùng đăng nhập lại thành công và bộ đếm reset về `0`.
  - Trước lần sai thứ 5, mỗi lần sai chỉ trả về `401 Unauthorized` với thông báo chung "Email hoặc mật khẩu không chính xác." (`ERR-AUTH-401-01`), không tiết lộ email có tồn tại hay không.

### TC-AUTH-003 — Đăng nhập thành công qua Google SSO
- **Liên kết**: Story `US-AUTH-02` | AC-01 | FR nguồn `FR-AUTH-LGN-002` | Loại: Integration | Ưu tiên: P0
- **Tiền điều kiện (Preconditions)**:
  1. Tài khoản Google `alex@gmail.com` đã liên kết với tài khoản nội bộ trạng thái `ACTIVE`.
  2. Môi trường test cấu hình đúng Google OAuth Client ID của dự án.
- **Dữ liệu kiểm thử (Test Data)**:

  | Trường | Giá trị |
  | :--- | :--- |
  | google_id_token | Token hợp lệ do Google cấp cho `alex@gmail.com`, còn hạn |

- **Các bước thực thi (Test Steps)**:

  | Bước | Hành động | Dữ liệu đầu vào | Kết quả mong đợi từng bước |
  | :---: | :--- | :--- | :--- |
  | 1 | Nhấn nút "Đăng nhập bằng Google" | — | Mở pop-up OAuth của Google đúng client ID |
  | 2 | Chọn tài khoản và đồng ý cấp quyền | `alex@gmail.com` | Google trả về `id_token` cho frontend |
  | 3 | Frontend gửi token lên hệ thống | `id_token` | Frontend gọi `POST /api/v1/auth/google` đúng 01 lần |
  | 4 | Quan sát phản hồi API | — | API trả về `200 OK` kèm cặp JWT nội bộ theo `BR-SEC-002` |
  | 5 | Quan sát điều hướng | — | Chuyển đến Dashboard, header hiển thị tên và avatar lấy từ hồ sơ Google |

- **Kết quả mong đợi cuối cùng (Expected Results)**:
  - Hệ thống tạo phiên đăng nhập mới gắn với tài khoản nội bộ đã liên kết; không sinh tài khoản trùng lặp.

### TC-AUTH-004 — Từ chối email sai định dạng RFC 5322 ngay tại client
- **Liên kết**: Story `US-AUTH-01` | AC-03 | FR nguồn `FR-AUTH-LGN-001` | Loại: Boundary | Ưu tiên: P1
- **Tiền điều kiện (Preconditions)**:
  1. Người dùng đang ở màn hình Đăng nhập.
- **Dữ liệu kiểm thử (Test Data)**:

  | Bộ dữ liệu | email | password |
  | :--- | :--- | :--- |
  | TD-01 (thiếu @) | `alexexample.com` | `Secret@123` |
  | TD-02 (thiếu domain) | `alex@` | `Secret@123` |
  | TD-03 (email có dấu tiếng Việt) | `nguyễn@domain.vn` | `Secret@123` |

- **Các bước thực thi (Test Steps)**:

  | Bước | Hành động | Dữ liệu đầu vào | Kết quả mong đợi từng bước |
  | :---: | :--- | :--- | :--- |
  | 1 | Nhập email sai định dạng và mật khẩu bất kỳ | TD-01 | Hiển thị lỗi inline dưới ô email (`ERR-AUTH-422-01`) |
  | 2 | Nhấn nút "Đăng nhập" | TD-01 | Không phát sinh request nào tới API (số request ghi nhận = 0) |
  | 3 | Lặp lại bước 1-2 với từng bộ dữ liệu còn lại | TD-02, TD-03 | Kết quả giống bước 1-2 cho từng bộ dữ liệu |

- **Kết quả mong đợi cuối cùng (Expected Results)**:
  - 100% bộ dữ liệu sai định dạng bị chặn tại client; ô mật khẩu được reset trống, ô email giữ nguyên giá trị đã nhập.

### TC-AUTH-005 — Từ chối Google id_token hết hạn hoặc sai chữ ký
- **Liên kết**: Story `US-AUTH-02` | AC-02 | FR nguồn `FR-AUTH-LGN-002` | Loại: Integration | Ưu tiên: P1
- **Tiền điều kiện (Preconditions)**:
  1. Chuẩn bị sẵn 02 token: token đã hết hạn và token ký bằng private key không khớp Google public key.
- **Dữ liệu kiểm thử (Test Data)**:

  | Bộ dữ liệu | google_id_token |
  | :--- | :--- |
  | TD-01 | Token hợp lệ nhưng đã hết hạn |
  | TD-02 | Token sai chữ ký (không verify được bằng Google JWKS) |

- **Các bước thực thi (Test Steps)**:

  | Bước | Hành động | Dữ liệu đầu vào | Kết quả mong đợi từng bước |
  | :---: | :--- | :--- | :--- |
  | 1 | Gửi request đăng nhập Google trực tiếp qua API | TD-01 | API trả về `400 Bad Request` kèm mã `ERR-AUTH-400-02` |
  | 2 | Lặp lại với token sai chữ ký | TD-02 | Kết quả giống bước 1 |
  | 3 | Quan sát giao diện | — | Hiển thị "Đăng nhập Google thất bại, vui lòng thử lại." và không tạo phiên |

- **Kết quả mong đợi cuối cùng (Expected Results)**:
  - 100% token không hợp lệ bị từ chối với `ERR-AUTH-400-02`; không bản ghi phiên nào được tạo trong hệ thống.

## 5. Ma trận độ phủ Mã lỗi & Quy tắc nghiệp vụ (ERR / BR Coverage)
Toàn bộ mã `ERR-xxx` và quy tắc `BR-xxx` đã khai báo trong SRS cho phân hệ phải xuất hiện ở ít nhất 01 dòng dưới đây (độ phủ 100% theo workflow).

| Mã | Phân loại | Mô tả | Test Case bao phủ | Trạng thái phủ |
| :--- | :---: | :--- | :--- | :--- |
| `ERR-AUTH-401-01` | ERR | Sai email hoặc mật khẩu (thông báo chung chống dò tài khoản) | `TC-AUTH-002` | Đã phủ |
| `ERR-AUTH-423-01` | ERR | Tài khoản bị tạm khóa 15 phút do brute-force | `TC-AUTH-002` | Đã phủ |
| `ERR-AUTH-422-01` | ERR | Email sai định dạng RFC 5322 | `TC-AUTH-004` | Đã phủ |
| `ERR-AUTH-400-02` | ERR | Google id_token hết hạn hoặc sai chữ ký | `TC-AUTH-005` | Đã phủ |
| `BR-SEC-001` | BR | Khóa tài khoản 15 phút sau 5 lần đăng nhập sai liên tiếp | `TC-AUTH-002` | Đã phủ |
| `BR-SEC-002` | BR | Access Token sống 15 phút, Refresh Token sống 7 ngày | `TC-AUTH-001`, `TC-AUTH-003` | Đã phủ |

## 6. Ma trận Truy vết Yêu cầu (Requirement Traceability Matrix — Rule 14)
| FR ID | Tên Yêu cầu Chức năng | User Story ID | Acceptance Criteria | Test Case ID | Loại kiểm thử | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FR-AUTH-LGN-001` | Đăng nhập Email/Pass | `US-AUTH-01` | AC-01 (Happy Path) | `TC-AUTH-001` | Functional / UI | Sẵn sàng test |
| `FR-AUTH-LGN-001` | Đăng nhập Email/Pass | `US-AUTH-01` | AC-02 (Sai pass 5 lần) | `TC-AUTH-002` | Security / BR | Sẵn sàng test |
| `FR-AUTH-LGN-001` | Đăng nhập Email/Pass | `US-AUTH-01` | AC-03 (Email sai định dạng) | `TC-AUTH-004` | Boundary | Sẵn sàng test |
| `FR-AUTH-LGN-002` | Đăng nhập Google SSO | `US-AUTH-02` | AC-01 (OAuth Flow) | `TC-AUTH-003` | Integration | Sẵn sàng test |
| `FR-AUTH-LGN-002` | Đăng nhập Google SSO | `US-AUTH-02` | AC-02 (Token không hợp lệ) | `TC-AUTH-005` | Integration | Sẵn sàng test |

> **Kiểm soát hoàn thiện**: mọi FR mức ưu tiên P0 phải có ít nhất 01 Test Case ở trạng thái "Sẵn sàng test"; mọi dòng "Chưa phủ" ở Mục 5 hoặc FR thiếu Test Case ở Mục 6 phải được xử lý trước khi bàn giao cho QA.
