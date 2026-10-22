# Biên bản Phỏng vấn & Làm rõ Yêu cầu Nghiệp vụ (Brainstorming & Clarification)

## 1. Ý tưởng thô ban đầu (Raw Concept)
- **Người đề xuất**: [Stakeholder / Khách hàng / PO]
- **Mô tả ban đầu**: [Ghi lại nguyên văn ý tưởng thô của khách hàng]

## 2. Bảng câu hỏi phỏng vấn làm rõ của AI BA (Socratic Probing)
| STT | Vấn đề mơ hồ / Góc khuất | Câu hỏi chất vấn từ BA Agent | Phản hồi chốt từ Khách hàng / PO | Quyết định kỹ thuật / Nghiệp vụ |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Xác thực mật khẩu | "Nếu người dùng quên mật khẩu thì reset qua Email hay SMS OTP?" | "Ưu tiên email trước qua link token 15 phút" | Triển khai Magic Link Email trước, SMS phase sau |
| 2 | Trùng email Google | "Nếu email Google trùng với tài khoản đã đăng ký bằng mật khẩu thì xử lý sao?" | "Tự động link tài khoản nếu email đã verified" | Bổ sung rule Link Account, không báo lỗi trùng |

## 3. Scope đã chốt (Agreed Scope)
- **Cần làm**: [Danh sách tính năng cụ thể]
- **Không làm**: [Các yêu cầu bị loại bỏ sau phỏng vấn]
