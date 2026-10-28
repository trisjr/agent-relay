# ba-workflows

Plugin cung cấp bộ **22 Core AI Skills** và **20 Rules** chuẩn mực dành cho IT Business Analyst & Product Owner, tập trung vào các luồng xương sống (Core Workflows) từ làm rõ ý tưởng, đặc tả kỹ thuật, dựng sơ đồ, thiết kế prototype đến kiểm thử và quản lý thay đổi.

Nguồn skill và quy chuẩn chuẩn hóa dựa trên [OpenBA-Kit](https://github.com/trisjr/OpenBA-Kit).

---

## ⚡ Danh sách 22 Core Skills

| Phân nhóm | Skill | Mô tả | Template tham chiếu |
| :--- | :--- | :--- | :--- |
| **1. Kế hoạch & Ý tưởng** | `prd` | PRD toàn sản phẩm: tầm nhìn, người dùng, bóc tách danh sách tính năng | `01-prd.md` |
| | `brainstorm` | Ghi ý tưởng thô rồi phỏng vấn làm rõ nghiệp vụ trước khi viết tài liệu | `04-brainstorm.md` |
| **2. Đặc tả yêu cầu** | `srs` | Đặc tả kỹ thuật IEEE 830: FR, NFR, Business Rules, Error Matrix | `08-srs.md` |
| | `code-to-srs` | Đọc source code hệ thống cũ, dựng lại SRS kèm trích dẫn `file:line` | `14-code-to-srs.md` |
| | `usecase` | Use Case chi tiết chuẩn Cockburn: actor, preconditions, luồng chính, ngoại lệ | `26-usecase-cockburn.md` |
| | `userstory` | Sinh User Story chuẩn INVEST sẵn sàng đưa vào backlog | `27-userstory.md` |
| | `ac` | Acceptance Criteria cú pháp Gherkin (`Given / When / Then`) cho từng story | `28-acceptance-criteria.md` |
| **3. Sơ đồ & Dữ liệu** | `sequence` | Sơ đồ tuần tự tương tác (Sequence Diagram Mermaid) | `15-sequence-diagram.md` |
| | `activity` | Sơ đồ hoạt động có nhánh rẽ quyết định (Activity Diagram Mermaid) | `16-activity-diagram.md` |
| | `state` | Sơ đồ máy trạng thái (State Diagram Mermaid) | `19-state-diagram.md` |
| | `erd` | Sơ đồ quan hệ thực thể dữ liệu (ERD Mermaid) | `20-erd-mermaid.md` |
| **4. Thiết kế & Prototype**| `user-flow` | Phân tích luồng người dùng (User Flow), phủ kín happy / error / edge case | `29-user-flow.md` |
| | `wireframe-html`| Dựng Wireframe HTML responsive, nguyên khối độc lập, xem trên trình duyệt | `31-wireframe-html.html` |
| **5. Hợp đồng API** | `api-design` | Thiết kế hợp đồng API RESTful và Webhook chi tiết | `37-api-design.md` |
| | `api-map` | Mapping field 3 tầng: API Request/Response, Database Field, UI Screen | `38-api-map.md` |
| **6. Kiểm thử (QA/QC)** | `test-checklist`| Bảng outline checklist kịch bản kiểm thử để review sớm | `42-test-checklist.md` |
| | `test-cases` | Sinh bộ Test Cases chi tiết bám sát AC và ma trận lỗi | `43-test-cases.md` |
| **7. Quản lý chất lượng & Thay đổi** | `gap` | Soi lỗ hổng và thiếu sót nghiệp vụ giữa các tài liệu (Gap Analysis) | `45-gap-analysis.md` |
| | `doc-drift` | Đối chiếu code thực tế với tài liệu: phát hiện sai lệch | `46-doc-drift.md` |
| | `kg` | Sinh Knowledge Graph liên kết chéo giữa toàn bộ tài liệu | `49-knowledge-graph-index.md` |
| | `cr` | Xử lý Change Request, phân tích tác động và cập nhật tài liệu | `47-change-request.md` |
| | `meet` | Biến ghi chú thô cuộc họp thành biên bản kèm quyết định và action items | `48-meeting-minutes.md` |

---

## 📋 20 Quy chuẩn nghiệp vụ (Rules)

Toàn bộ 20 quy chuẩn nghiệp vụ được cấu hình trong `rules/` và `.cursor/rules/*.mdc`:

1. `01-fr-naming-convention`: Quy ước đặt mã và thuộc tính Functional Requirements (`FR-[MODULE]-[FEATURE]-[SEQ]`).
2. `02-br-naming-convention`: Quy ước đặt mã Business Rules (`BR-[MODULE]-[TOPIC]-[SEQ]`).
3. `03-err-naming-convention`: Quy ước ma trận mã lỗi hệ thống (`ERR-[MODULE]-[HTTP_STATUS]-[SEQ]`).
4. `04-nfr-standards`: Tiêu chuẩn phi chức năng theo ISO/IEC 25010.
5. `05-srs-ieee-830`: Cấu trúc tài liệu đặc tả kỹ thuật IEEE 830.
6. `06-cockburn-use-case`: Đặc tả Use Case chuẩn Alistair Cockburn.
7. `07-invest-user-story`: Quy chuẩn viết User Story tuân thủ INVEST.
8. `08-gherkin-acceptance-criteria`: Định dạng Acceptance Criteria theo Gherkin (`Given / When / Then`).
9. `09-data-dictionary-standard`: Chuẩn hóa từ điển dữ liệu.
10. `10-api-contract-standards`: Tiêu chuẩn thiết kế API RESTful, HTTP status code và JSON format.
11. `11-error-matrix-convention`: Ma trận lỗi phân cấp UI, Backend và hiển thị người dùng.
12. `12-state-transition-rules`: Quy tắc chuyển đổi trạng thái (State Transition).
13. `13-wireframe-html-guidelines`: Hướng dẫn dựng Wireframe HTML.
14. `14-test-case-traceability`: Ma trận truy vết kiểm thử (Traceability Matrix).
15. `15-change-request-impact-matrix`: Ma trận phân tích tác động thay đổi yêu cầu (Change Request).
16. `16-ambiguity-detection-rules`: Bộ quy tắc phát hiện và loại trừ từ ngữ mơ hồ, định tính.
17. `17-actor-role-definition`: Danh mục vai trò người dùng (Actor Catalog) và phân quyền (RBAC).
18. `18-knowledge-graph-metadata`: Quy chuẩn siêu dữ liệu liên kết chéo tài liệu.
19. `19-document-versioning-rules`: Quy tắc đánh số phiên bản tài liệu (Semantic Versioning).
20. `20-artifact-identifier-conventions`: Quy ước đặt mã các artifact phụ trợ (`US`, `AC`, `FEAT`, `PER`, `SCR`, `BRN`, `CHK`, `GAP`, `DRIFT`, `CR`, `DEC`, `AI`, `MM`).

---

## 🚀 Luồng Xương sống Cốt lõi (Core Spine Workflow)

Quy trình điển hình từ ý tưởng đến bàn giao:
1. `/brainstorm`: Phỏng vấn làm rõ ý tưởng thô và xác định phạm vi.
2. `/srs`: Sinh đặc tả kỹ thuật IEEE 830 với FR, BR, ERR, NFR.
3. `/sequence` + `/erd`: Trực quan hóa luồng tương tác và mô hình thực thể dữ liệu.
4. `/wireframe-html`: Dựng giao diện mẫu tương tác HTML đen trắng.
5. `/userstory` + `/ac`: Bóc tách backlog chuẩn INVEST và Acceptance Criteria Gherkin.
6. `/test-cases`: Sinh bộ kiểm thử bám sát tiêu chí nghiệm thu và ma trận lỗi.
7. `/cr`: Tiếp nhận yêu cầu thay đổi, phân tích tác động và đồng bộ tài liệu.
