# Template: Knowledge Graph Index (Markdown Summary)

## Metadata
- **Project Name**: [Tên Dự án / Phân hệ]
- **Generated Date**: [YYYY-MM-DD]
- **Graph Source**: `docs/knowledge-graph.json`
- **Total Entities**: [Số lượng entity]
- **Total Relationships**: [Số lượng quan hệ liên kết]

---

## 1. Danh mục Tài liệu & Phân hệ (Documentation Nodes)
| Module / Phân hệ | Loại tài liệu | Đường dẫn tệp | Trạng thái |
| :--- | :--- | :--- | :--- |
| `AUTH` | PRD | `docs/auth/01-prd.md` | Approved |
| `AUTH` | SRS | `docs/auth/srs/spec.md` | Approved |
| `AUTH` | Sequence Flow | `docs/auth/srs/flows.md` | In Review |
| `ORD` | SRS | `docs/order/srs/spec.md` | Draft |

---

## 2. Ma trận Liên kết Phụ thuộc (Dependency Traceability Matrix)
| Nguồn (From Node) | Loại liên kết (`relation`) | Đích đến (To Node) | Ghi chú |
| :--- | :--- | :--- | :--- |
| `FR-AUTH-LGN-001` | `governed_by` | `BR-AUTH-SEC-001` | Giới hạn 5 lần đăng nhập sai |
| `FR-AUTH-LGN-001` | `emits_error` | `ERR-AUTH-401-001` | Sai mật khẩu hoặc tài khoản bị khóa |
| `FR-AUTH-LGN-001` | `tested_by` | `TC-AUTH-001` | Test case đăng nhập thành công |
| `docs/auth/srs/spec.md` | `depends_on` | `docs/auth/brainstorms/login.md` | Brainstorming scope |

---

## 3. Bản đồ Thực thể Dữ liệu (ERD Cross-References)
| Thực thể (Entity) | Phân hệ | Tài liệu liên quan | API Spec liên quan |
| :--- | :--- | :--- | :--- |
| `users` | `AUTH` | `docs/auth/srs/erd.md` | `docs/auth/api/api-spec.md` |
| `orders` | `ORD` | `docs/order/srs/erd.md` | `docs/order/api/api-spec.md` |
