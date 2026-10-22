# Ma trận Truy vết Yêu cầu (Requirement Traceability Matrix - RTM)

## Mục đích
Đảm bảo 100% yêu cầu chức năng (FR) đều được chuyển hóa thành User Story và được kiểm thử bởi ít nhất 01 Test Case tương ứng, không bị bỏ sót tính năng.

## Mẫu bảng RTM chuẩn:
| FR ID | Tên Yêu cầu Chức năng | User Story ID | Acceptance Criteria | Test Case ID | Loại kiểm thử | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FR-AUTH-LGN-001` | Đăng nhập Email/Pass | `US-AUTH-01` | AC-01 (Happy Path) | `TC-AUTH-001` | Functional / UI | Sẵn sàng test |
| `FR-AUTH-LGN-001` | Đăng nhập Email/Pass | `US-AUTH-01` | AC-02 (Sai pass 5 lần) | `TC-AUTH-002` | Security / BR | Sẵn sàng test |
| `FR-AUTH-LGN-002` | Đăng nhập Google SSO | `US-AUTH-02` | AC-01 (OAuth Flow) | `TC-AUTH-003` | Integration | Sẵn sàng test |
